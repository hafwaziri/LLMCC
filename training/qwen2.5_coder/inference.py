import argparse
import torch
import orjson
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM

def generate_llvm_ir(model, tokenizer, source_code, temperature=0.7, top_p=0.9):

    messages = [
        {"role": "system", "content": "You are a compiler expert. Convert the following source code to LLVM IR."},
        {"role": "user", "content": source_code}
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=18000)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    # Dynamic max_new_tokens
    input_length = inputs["input_ids"].shape[1]
    model_max_length = 18000
    available_tokens = model_max_length - input_length
    dynamic_max_tokens = max(available_tokens - 100, 512)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=dynamic_max_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )


    generated_ids = outputs[0][inputs['input_ids'].shape[1]:]
    generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    return generated_text

def process_jsonl(input_file, output_file, model, tokenizer, temperature, top_p):

    print(f"Reading from {input_file}...")

    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        for line_num, line in enumerate(tqdm(f_in, desc="Processing samples"), 1):
            try:
                item = orjson.loads(line)

                source_code = item["source_code"]

                # Generate LLVM IR
                tgt_ir = generate_llvm_ir(
                    model,
                    tokenizer,
                    source_code,
                    temperature=temperature,
                    top_p=top_p
                )

                item["tgt_ir"] = tgt_ir

                f_out.write(orjson.dumps(item) + b'\n')

            except Exception as e:
                print(f"Error processing line {line_num}: {e}")
                continue

    print(f"Inference complete! Results saved to {output_file}")

def main(args):
    print(f"Loading model from {args.model_path}...")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path,
        trust_remote_code=True,
        padding_side="right"
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = "<|endoftext|>"
        tokenizer.pad_token_id = tokenizer.convert_tokens_to_ids("<|endoftext|>")

    # Load model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    if args.use_flash_attention and device == "cuda":
        attn_implementation = "flash_attention_2"
        print("Using Flash Attention 2")
    else:
        attn_implementation = "eager"
        print("Using standard attention implementation")

    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map="auto" if device == "cuda" else None,
        attn_implementation=attn_implementation
    )

    model.eval()
    print("Model loaded successfully!")

    process_jsonl(
        args.input_file,
        args.output_file,
        model,
        tokenizer,
        args.temperature,
        args.top_p
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Model arguments
    parser.add_argument('--model_path', type=str, required=True)
    parser.add_argument('--use_flash_attention', action='store_true')

    # Data arguments
    parser.add_argument('--input_file', type=str, required=True)
    parser.add_argument('--output_file', type=str, required=True)

    # Generation arguments
    parser.add_argument('--temperature', type=float, default=0.1)
    parser.add_argument('--top_p', type=float, default=0.95)

    args = parser.parse_args()

    main(args)
