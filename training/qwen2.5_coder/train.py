import argparse
import pynvml
import torch
import threading
import time
import wandb
import os
from datasets import load_dataset, load_from_disk
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback,
)

stop_monitoring = False

def gpu_monitor(interval=2):
    num_gpus = pynvml.nvmlDeviceGetCount()
    while not stop_monitoring:
        gpu_data = {}
        for i in range(num_gpus):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_data[f"gpu_{i}_vram_mb"] = info.used / 1024**2
            gpu_data[f"gpu_{i}_vram_percent"] = (info.used / info.total) * 100

        try:
            wandb.log(gpu_data)
        except Exception:
            break
        time.sleep(interval)

def preprocess_function(samples, tokenizer, max_length):
    sources = samples["source_code"]
    targets = samples["llvm_ir"]

    model_inputs = {"input_ids": [], "labels": [], "attention_mask": []}

    for source, target in zip(sources, targets):
        messages = [
            {"role": "system", "content": "You are a compiler expert. Convert the following source code to LLVM IR."},
            {"role": "user", "content": source},
            {"role": "assistant", "content": target}
        ]

        full_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )

        messages_no_response = messages[:-1]
        prompt_text = tokenizer.apply_chat_template(
            messages_no_response,
            tokenize=False,
            add_generation_prompt=True
        )

        full_tokens = tokenizer(full_text, max_length=max_length, truncation=True, add_special_tokens=False)
        prompt_tokens = tokenizer(prompt_text, max_length=max_length, truncation=True, add_special_tokens=False)

        input_ids = full_tokens["input_ids"]
        attention_mask = full_tokens["attention_mask"]

        labels = input_ids.copy()
        prompt_len = len(prompt_tokens["input_ids"])

        if prompt_len < len(labels):
            labels[:prompt_len] = [-100] * prompt_len
        else:
            labels = [-100] * len(labels)

        model_inputs["input_ids"].append(input_ids)
        model_inputs["attention_mask"].append(attention_mask)
        model_inputs["labels"].append(labels)

    return model_inputs

def main(args):

    global stop_monitoring

    # ---- Initialize W&B ----
    wandb.init(
        project=args.wandb_project,
        name=args.run_name,
        config={
            "model_name": args.model_name,
            "batch_size": args.batch_size,
            "grad_accum": args.grad_accum,
            "epochs": args.epochs,
            "learning_rate": args.learning_rate
        }
    )

    # ---- Initialize NVML for GPU monitoring ----
    pynvml.nvmlInit()
    num_gpus = pynvml.nvmlDeviceGetCount()
    print(f"Detected {num_gpus} GPUs")
    wandb.config.update({"num_gpus": num_gpus})

    for i in range(num_gpus):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        print(f"GPU {i}: {gpu_name}")

    active_gpu = torch.cuda.current_device() if torch.cuda.is_available() else None
    if active_gpu is not None:
        print(f"Active GPU (script running on): {active_gpu}")
        wandb.config.update({"active_gpu": active_gpu})

    monitor_thread = threading.Thread(target=gpu_monitor, daemon=True)
    monitor_thread.start()
    print("GPU monitoring thread started")


    # ---- Load Tokenizer/Data ----
    print(f"Loading Tokenizer for {args.model_name} ...")
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        padding_side="right"
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = "<|endoftext|>"
        tokenizer.pad_token_id = tokenizer.convert_tokens_to_ids("<|endoftext|>")

    if args.use_pretokenized:
        print(f"Loading pre-tokenized data from {args.train_data}...")
        tokenized_train_full = load_from_disk(args.train_data)
        print(f"Loaded {len(tokenized_train_full)} training samples")

        if args.val_data:
            print(f"Loading pre-tokenized validation data from {args.val_data}...")
            tokenized_eval = load_from_disk(args.val_data)
            print(f"Loaded {len(tokenized_eval)} validation samples")
            tokenized_train = tokenized_train_full
        else:
            print(f"Splitting 10% of the training data for validation...")
            train_val_split = tokenized_train_full.train_test_split(
                test_size=0.1,
                seed=42
            )
            tokenized_train = train_val_split["train"]
            tokenized_eval = train_val_split["test"]

        if args.test_data:
            print(f"Loading pre-tokenized test data from {args.test_data}...")
            tokenized_test = load_from_disk(args.test_data)
            print(f"Loaded {len(tokenized_test)} test samples")
        else:
            tokenized_test = None

        wandb.config.update({
            "train_size": len(tokenized_train),
            "val_size": len(tokenized_eval) if tokenized_eval else 0,
            "test_size": len(tokenized_test) if tokenized_test else 0,
            "pretokenized": True
        })

    else:
        print(f"Loading raw data from {args.train_data}...")
        full_dataset = load_dataset("json", data_files={"train": args.train_data})["train"]
        print(f"Loaded {len(full_dataset)} training samples")

        if args.val_data:
            print(f"Loading validation data from {args.val_data}...")
            eval_dataset_full = load_dataset("json", data_files={"val": args.val_data})
            eval_dataset = eval_dataset_full["val"]
            print(f"Loaded {len(eval_dataset)} validation samples")
            train_dataset = full_dataset
        else:
            print(f"Splitting 10% of the training data for validation...")
            train_val_split = full_dataset.train_test_split(
                test_size=0.1,
                seed=42
            )
            train_dataset = train_val_split["train"]
            eval_dataset = train_val_split["test"]

        if args.test_data:
            test_dataset_full = load_dataset("json", data_files={"test": args.test_data})
            test_dataset = test_dataset_full["test"]
            print(f"Loaded {len(test_dataset)} test samples")
        else:
            test_dataset = None

        def filter_by_length(examples):
            keep = []
            for code, ir in zip(examples["source_code"], examples["llvm_ir"]):
                messages = [
                    {"role": "system", "content": "You are a compiler expert. Convert the following source code to LLVM IR."},
                    {"role": "user", "content": code},
                    {"role": "assistant", "content": ir}
                ]
                full_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
                # Quick length estimation (characters / 4 is rough token estimate)
                estimated_tokens = len(full_text) // 4
                keep.append(estimated_tokens <= args.max_length)
            return keep

        if args.filter_by_length:
            print(f"Filtering datasets by max_length={args.max_length}...")
            train_dataset = train_dataset.filter(filter_by_length, batched=True, batch_size=100)
            print(f"Training samples after filtering: {len(train_dataset)}")

            if eval_dataset:
                eval_dataset = eval_dataset.filter(filter_by_length, batched=True, batch_size=100)
                print(f"Validation samples after filtering: {len(eval_dataset)}")

            if test_dataset:
                test_dataset = test_dataset.filter(filter_by_length, batched=True, batch_size=100)
                print(f"Test samples after filtering: {len(test_dataset)}")

        if args.max_train_samples and len(train_dataset) > args.max_train_samples:
            print(f"Limiting training set from {len(train_dataset)} to {args.max_train_samples} samples")
            train_dataset = train_dataset.select(range(args.max_train_samples))

        if args.max_val_samples and eval_dataset and len(eval_dataset) > args.max_val_samples:
            print(f"Limiting validation set from {len(eval_dataset)} to {args.max_val_samples} samples")
            eval_dataset = eval_dataset.select(range(args.max_val_samples))

        if args.max_test_samples and test_dataset and len(test_dataset) > args.max_test_samples:
            print(f"Limiting test set from {len(test_dataset)} to {args.max_test_samples} samples")
            test_dataset = test_dataset.select(range(args.max_test_samples))

        wandb.config.update({
            "train_size": len(train_dataset),
            "val_size": len(eval_dataset) if eval_dataset else 0,
            "test_size": len(test_dataset) if test_dataset else 0,
            "pretokenized": False
        })

        print("Tokenizing and formatting dataset...")
        tokenized_train = train_dataset.map(
            lambda x: preprocess_function(x, tokenizer, args.max_length),
            batched=True,
            num_proc=8,
            remove_columns=train_dataset.column_names
        )

        tokenized_eval = None
        if eval_dataset:
            tokenized_eval = eval_dataset.map(
                lambda x: preprocess_function(x, tokenizer, args.max_length),
                batched=True,
                num_proc=8,
                remove_columns=eval_dataset.column_names
            )

        tokenized_test = None
        if test_dataset:
            tokenized_test = test_dataset.map(
                lambda x: preprocess_function(x, tokenizer, args.max_length),
                batched=True,
                num_proc=8,
                remove_columns=test_dataset.column_names
            )

    # ---- Load Model ----
    print(f"Loading Model: {args.model_name}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        dtype=torch.bfloat16,
        trust_remote_code=True,
        use_cache=False,
        attn_implementation="flash_attention_2"
    )

    # ---- Enable Gradient Checkpointing ----
    if args.gradient_checkpointing:
        model.gradient_checkpointing_enable()
        print("Gradient checkpointing enabled")
    else:
        print("Gradient checkpointing disabled")

    # ---- Create Data Collator ----
    data_collator = DataCollatorForSeq2Seq(
        tokenizer,
        model=model,
        padding="longest",
        pad_to_multiple_of=8
    )

    # ---- Training Arguments ----
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        # Batch & Gradient Accumulation
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        # Training Duration
        num_train_epochs=args.epochs,
        # Optimization
        learning_rate=args.learning_rate,
        lr_scheduler_type=args.lr_scheduler_type,
        weight_decay=args.weight_decay,
        warmup_ratio=args.warmup_ratio,
        # Precision
        bf16=True,
        # Memory Optimization
        gradient_checkpointing=args.gradient_checkpointing,
        # Logging
        logging_steps=1,
        logging_first_step=True,
        report_to="wandb",
        run_name=args.run_name,
        # Evaluation
        eval_strategy="steps" if tokenized_eval else "no",
        eval_steps=args.eval_steps if tokenized_eval else None,
        # Checkpointing
        save_strategy="steps",
        save_steps=args.save_steps,
        save_total_limit=args.save_total_limit,
        load_best_model_at_end=True if tokenized_eval else False,
        metric_for_best_model="eval_loss" if tokenized_eval else None,
        greater_is_better=False
    )

    # ---- Training  ----
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        data_collator=data_collator,
        callbacks=[EarlyStoppingCallback(
            early_stopping_patience=args.early_stopping_patience,
            early_stopping_threshold=args.early_stopping_threshold
        )] if tokenized_eval else []
    )

    # Evaluate before training
    if tokenized_test:
        print("Evaluating on test set (before training)...")
        test_results = trainer.evaluate(tokenized_test)
        print(f"Test results before training: {test_results}")
        wandb.log({"test_loss_before": test_results.get("eval_loss", None)})

    print("Starting training...")
    trainer.train()

    # Evaluate after training
    if tokenized_test:
        print("Evaluating on test set (after training)...")
        test_results = trainer.evaluate(tokenized_test)
        print(f"Test results after training: {test_results}")
        wandb.log({"test_loss_after": test_results.get("eval_loss", None)})

    # ---- SAVE FINAL MODEL ----
    print("Saving final model...")
    final_model_path = f"{args.output_dir}/final_model"
    trainer.save_model(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    print(f"Model saved to {final_model_path}")

    # ---- Cleanup ----
    stop_monitoring = True
    time.sleep(3)
    wandb.finish()
    pynvml.nvmlShutdown()
    print("Training complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # ---- Model Config ----
    parser.add_argument('--model_name', type=str, default="Qwen/Qwen2.5-Coder-0.5B-Instruct")
    parser.add_argument('--use_pretokenized', action='store_true')
    parser.add_argument('--train_data', type=str, required=True)
    parser.add_argument('--val_data', type=str, default=None)
    parser.add_argument('--test_data', type=str, default=None)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--early_stopping_patience', type=int, default=3)
    parser.add_argument('--early_stopping_threshold', type=float, default=0.001)

    # ---- Dataset Size Limits ----
    parser.add_argument('--max_train_samples', type=int, default=None)
    parser.add_argument('--max_val_samples', type=int, default=None)
    parser.add_argument('--max_test_samples', type=int, default=None)
    parser.add_argument('--filter_by_length', action='store_true')

    # ---- Hyperparameters ----
    parser.add_argument('--batch_size', type=int, default=1)
    parser.add_argument('--grad_accum', type=int, default=1)
    parser.add_argument('--epochs', type=int, default=1)
    parser.add_argument('--learning_rate', type=float, default=5e-5)
    parser.add_argument('--max_length', type=int, default=32000)
    parser.add_argument('--weight_decay', type=float, default=0.01)
    parser.add_argument('--warmup_ratio', type=float, default=0.1)
    parser.add_argument('--lr_scheduler_type', type=str, default='cosine')

    # ---- Memory Optimization ----
    parser.add_argument('--gradient_checkpointing', action='store_true')

    # ---- Logging & Checkpointing ----
    parser.add_argument('--logging_steps', type=int, default=1)
    parser.add_argument('--eval_steps', type=int, default=10)
    parser.add_argument('--save_steps', type=int, default=10)
    parser.add_argument('--save_total_limit', type=int, default=3)

    # ---- W&B Config ----
    parser.add_argument('--wandb_project', type=str, default="Qwen-Coder-2.5")
    parser.add_argument('--run_name', type=str, default="qwen_finetune")

    args = parser.parse_args()
    main(args)
