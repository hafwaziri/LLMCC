import argparse
import docker
import os
import json
import tempfile
import subprocess
import re
from pathlib import Path
import warnings
import logging
from transformers import AutoTokenizer

def find_source_files(dataset_path):
    source_files = []
    for ext in ['*.c', '*.cpp']:
        source_files.extend(Path(dataset_path).rglob(ext))
    return [str(f) for f in source_files]

def preprocess_llvm_ir(llvm_ir: str):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ll", delete=False) as temp_ir:
        temp_ir.write(llvm_ir)
        temp_ir.flush()
        temp_ir_path = temp_ir.name

    try:
        opt_command = [
            "opt",
            "--strip-debug",
            "--strip-named-metadata",
            "-S",
            temp_ir_path,
            "-o",
            temp_ir_path,
        ]
        debug_stripped = subprocess.run(
            opt_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if debug_stripped.returncode != 0:
            err = (debug_stripped.stderr or debug_stripped.stdout or "").strip()
            print(f"    opt preprocessing failed: {err or 'No output captured'}")
            return None

        with open(temp_ir_path, "r", encoding="utf-8", errors="replace") as f:
            processed = f.read()

        processed = re.sub(r"^; ModuleID = .*$\n?", "", processed, flags=re.MULTILINE)
        processed = re.sub(r"^source_filename = .*$\n?", "", processed, flags=re.MULTILINE)
        processed = re.sub(r"^target datalayout = .*$\n?", "", processed, flags=re.MULTILINE)
        processed = re.sub(r"^target triple = .*$\n?", "", processed, flags=re.MULTILINE)

        return processed
    except FileNotFoundError:
        print("    opt preprocessing failed: `opt` not found on host PATH")
        return None
    finally:
        try:
            os.unlink(temp_ir_path)
        except OSError:
            pass

def preprocess_source_strip_comments(container, source_file, dataset_path):
    rel_path = os.path.relpath(source_file, dataset_path)
    container_file_path = f"/dataset/{rel_path}"
    container_dir = os.path.dirname(container_file_path)
    file_name = os.path.basename(container_file_path)

    cmd = ["gcc", "-fpreprocessed", "-dD", "-E", "-P", file_name]

    try:
        exec_result = container.exec_run(cmd, demux=True, workdir=container_dir)
        stdout, stderr = exec_result.output

        if exec_result.exit_code != 0:
            err = stderr.decode("utf-8", errors="replace") if stderr else ""
            out = stdout.decode("utf-8", errors="replace") if stdout else ""
            msg = (err.strip() or out.strip() or "No output captured")
            print(f"    Source comment-stripping failed (exit {exec_result.exit_code}): {msg}")
            return None

        return stdout.decode("utf-8", errors="replace") if stdout else ""
    except Exception as e:
        print(f"    Source comment-stripping exception: {str(e)}")
        return None

def compile_to_llvm_ir(container, source_file, dataset_path):
    rel_path = os.path.relpath(source_file, dataset_path)
    container_file_path = f"/dataset/{rel_path}"

    container_dir = os.path.dirname(container_file_path)
    file_name = os.path.basename(container_file_path)

    ext = Path(source_file).suffix.lower()

    extra_flags = []
    if ext == ".c":
        extra_flags = [
            "-std=gnu89",
            "-Wno-error=implicit-function-declaration",
            "-Wno-error=implicit-int",
        ]

    cmd = ["clang", "-S", "-emit-llvm", "-o", "-", *extra_flags, file_name]

    try:
        exec_result = container.exec_run(cmd, demux=True, workdir=container_dir)
        stdout, stderr = exec_result.output

        if exec_result.exit_code != 0:
            err = stderr.decode("utf-8", errors="replace") if stderr else ""
            out = stdout.decode("utf-8", errors="replace") if stdout else ""
            msg = err.strip() or out.strip() or "No output captured"
            print(f"    Exit code: {exec_result.exit_code}")
            print(f"    Compilation error: {msg}")
            return None

        return stdout.decode('utf-8')
    except Exception as e:
        print(f"    Exception: {str(e)}")
        return None

def chat_full_text(tokenizer, system_prompt, source, target):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": source},
        {"role": "assistant", "content": target},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    return f"{system_prompt}\n\n[USER]\n{source}\n\n[ASSISTANT]\n{target}\n"

def num_tokens(tokenizer, text):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        toks = tokenizer(text, add_special_tokens=False, truncation=False)
    return len(toks.get("input_ids", []))

def process_dataset(docker_image, dataset_path, output_file, *, max_tokens=None, tokenizer_model=None, system_prompt=None):
    client = docker.from_env()

    dataset_path = os.path.abspath(dataset_path)

    tokenizer = None
    if max_tokens is not None:
        if not tokenizer_model:
            raise ValueError("max_tokens was provided but tokenizer_model is missing")
        print(f"Loading tokenizer: {tokenizer_model}")
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_model, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = "<|endoftext|>"
            tokenizer.pad_token_id = tokenizer.convert_tokens_to_ids("<|endoftext|>")
        system_prompt = system_prompt or "You are a compiler expert. Convert the following source code to LLVM IR."
        print(f"Filtering enabled: keeping samples with <= {max_tokens} tokens")

    print(f"Starting Docker container from image: {docker_image}")

    container = client.containers.run(
        docker_image,
        command="tail -f /dev/null",
        volumes={dataset_path: {'bind': '/dataset', 'mode': 'ro'}},
        detach=True,
        remove=True
    )

    try:
        print(f"Container started: {container.id[:12]}")
        print(f"Searching for source files in: {dataset_path}")

        source_files = find_source_files(dataset_path)
        print(f"Found {len(source_files)} source files")

        results = []
        success_count = 0

        total_c = 0
        total_cpp = 0
        success_c = 0
        success_cpp = 0
        filtered_out = 0

        for idx, source_file in enumerate(source_files, 1):
            rel_path = os.path.relpath(source_file, dataset_path)
            print(f"[{idx}/{len(source_files)}] Processing: {rel_path}")

            ext = Path(source_file).suffix.lower()
            if ext == ".c":
                total_c += 1
            elif ext == ".cpp":
                total_cpp += 1

            try:
                with open(source_file, 'r') as f:
                    source_code_raw = f.read()
            except Exception as e:
                print(f"    Failed to read file: {str(e)}")
                continue

            source_code = preprocess_source_strip_comments(container, source_file, dataset_path) or source_code_raw

            llvm_ir = compile_to_llvm_ir(container, source_file, dataset_path)
            if not llvm_ir:
                print(f"    Failed to compile")
                continue

            processed_ir = preprocess_llvm_ir(llvm_ir)
            if not processed_ir:
                print(f"    Failed to preprocess LLVM IR")
                continue

            if max_tokens is not None:
                full_text = chat_full_text(tokenizer, system_prompt, source_code, processed_ir)
                n_tok = num_tokens(tokenizer, full_text)
                if n_tok > max_tokens:
                    filtered_out += 1
                    print(f"    Filtered out (tokens={n_tok} > {max_tokens})")
                    continue

            results.append(
                {
                    "file_path": rel_path,
                    "src": source_code,
                    "ref_ir": processed_ir,
                }
            )
            success_count += 1
            if ext == ".c":
                success_c += 1
            elif ext == ".cpp":
                success_cpp += 1
            print(f"    Successfully compiled + preprocessed")

        print(f"Saving results to: {output_file}")
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

        with open(output_file, 'w') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')

        print(f"\n{'='*60}")
        print(f"Processing complete!")
        print(f"Successfully kept: {success_count}/{len(source_files)} files")
        if max_tokens is not None:
            print(f"Filtered out (too long): {filtered_out}")
            print(f"Max tokens: {max_tokens} (tokenizer={tokenizer_model})")
        print(f"  C files:   {success_c}/{total_c} kept")
        print(f"  C++ files: {success_cpp}/{total_cpp} kept")
        print(f"Output saved to: {output_file}")
        print(f"{'='*60}")

    finally:
        print("\nStopping and removing container...")
        container.stop()

def main(args):
    process_dataset(
        args.docker_image,
        args.raw_dataset_path,
        args.output_file,
        max_tokens=args.max_tokens,
        tokenizer_model=args.tokenizer_model,
        system_prompt=args.system_prompt
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--raw_dataset_path', type=str, required=True)
    parser.add_argument('--docker_image', type=str, required=True)
    parser.add_argument('--output_file', type=str, required=True)

    parser.add_argument('--max_tokens', type=int, default=None)
    parser.add_argument('--tokenizer_model', type=str, default="Qwen/Qwen2.5-Coder-0.5B-Instruct")
    parser.add_argument('--system_prompt', type=str, default="You are a compiler expert. Convert the following source code to LLVM IR.")

    args = parser.parse_args()

    main(args)