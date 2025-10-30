import os
import sys
import torch
from datasets import load_dataset
from transformers import (
    RobertaTokenizer,
    EncoderDecoderModel,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq,
)

# ---------- Config ----------
MODEL_NAME = "microsoft/unixcoder-base"
WANDB_PROJECT = "UniXcoder-Finetune"

os.environ["WANDB_PROJECT"] = WANDB_PROJECT

def main():

    if len(sys.argv) < 3:
        print("Usage: python training.py <data_file> <output_dir>")
        sys.exit(1)

    data_file = sys.argv[1]
    output_dir = sys.argv[2]

    print("Loading Data...")

    dataset = load_dataset("json", data_files={"train": data_file})
    train_dataset = dataset["train"]
    print(f"Number of training samples: {len(train_dataset)}")

    print("Loading Tokenizer and Model...")
    tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)
    model = EncoderDecoderModel.from_encoder_decoder_pretrained(MODEL_NAME, MODEL_NAME)
    print("Loaded Tokenizer and Model.")

    print("Setting special tokens...")
    model.config.decoder_start_token_id = tokenizer.cls_token_id
    model.config.eos_token_id = tokenizer.sep_token_id
    model.config.pad_token_id = tokenizer.pad_token_id

    def preprocess_function(examples):
        inputs = [f"<encoder-decoder> <c> {code}" for code in examples["code"]]
        model_inputs = tokenizer(inputs, max_length=1024, padding="max_length", truncation=True)

        with tokenizer.as_target_tokenizer():
            labels = tokenizer(examples["ir"], max_length=1024, padding="max_length", truncation=True)

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    print("Tokenizing dataset...")
    tokenized_datasets = train_dataset.map(preprocess_function, batched=True, remove_columns=["code", "ir"])
    print("Tokenization completed.")

    print("Setting up trainer...")

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=1,
        num_train_epochs=100,
        learning_rate=5e-5,
        bf16=True,
        logging_strategy="steps",
        logging_steps=1,
        save_strategy="no",
        report_to="wandb",
        run_name="unixcoder-overfit-test",
        logging_first_step=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets,
        data_collator=data_collator,
    )

    print("Starting training...")
    trainer.train()
    print("Training completed.")

    print("Saving model...")
    trainer.save_model(output_dir)
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    main()
