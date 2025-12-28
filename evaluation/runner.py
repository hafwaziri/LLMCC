import argparse
import orjson
from static_analysis.structural_analysis.llvm_ir_verification import verify_ir
from static_analysis.structural_analysis.llvm_ir_diff import diff_llvm_ir
from static_analysis.structural_analysis.llvm_ir_canonicalization_and_normalization import canonicalize_and_normalize_ir
from static_analysis.structural_analysis.llvm_ir_function_analysis import functions_count

def load_dataset(path, batch_size):
    batch = []
    with open(path, "rb") as f:
        for line in f:
            batch.append(orjson.loads(line))
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

def process_batch(batch):
    results = []
    for i, item in enumerate(batch):
        src = item["src"]
        ref_ir = item["ref_ir"]
        tgt_ir = item["tgt_ir"]

        # Verify IR
        ref_ir_verification, ref_ir_verification_message = verify_ir(ref_ir)
        tgt_ir_verification, tgt_ir_verification_message = verify_ir(tgt_ir)

        if not ref_ir_verification or not tgt_ir_verification:
            result = {
                'id': i,
                'ref_ir_verification': ref_ir_verification,
                'ref_ir_verification_message': ref_ir_verification_message,
                'tgt_ir_verification': tgt_ir_verification,
                'tgt_ir_verification_message': tgt_ir_verification_message,
                'ref_canonicalization': False,
                'ref_canonicalization_error': "VERIFY FAILED",
                'tgt_canonicalization': False,
                'tgt_canonicalization_error': "VERIFY FAILED",
                'identical': False,
                'diff_stdout': "VERIFY FAILED",
                'diff_stderr': "VERIFY FAILED",
                'function_count_match': False,
                'function_signature_match': False,
            }
            results.append(result)
            continue
        
        # Canonicalize and Normalize IR
        ref_canon_success, ref_canon_ir, ref_canon_error = canonicalize_and_normalize_ir(ref_ir)
        tgt_canon_success, tgt_canon_ir, tgt_canon_error = canonicalize_and_normalize_ir(tgt_ir)

        if not ref_canon_success or not tgt_canon_success:
            result = {
                'id': i,
                'ref_ir_verification': ref_ir_verification,
                'ref_ir_verification_message': ref_ir_verification_message,
                'tgt_ir_verification': tgt_ir_verification,
                'tgt_ir_verification_message': tgt_ir_verification_message,
                'ref_canonicalization': ref_canon_success,
                'ref_canonicalization_error': ref_canon_error,
                'tgt_canonicalization': tgt_canon_success,
                'tgt_canonicalization_error': tgt_canon_error,
                'identical': False,
                'diff_stdout': "CANONICALIZATION FAILED",
                'diff_stderr': "CANONICALIZATION FAILED",
                'function_count_match': False,
                'function_signature_match': False,
            }
            results.append(result)
            continue

        # Function Analysis
        func_analysis = functions_count(ref_canon_ir, tgt_canon_ir)

        # IR Diff
        is_identical, diff_stdout, diff_stderr = diff_llvm_ir(ref_canon_ir, tgt_canon_ir)

        result = {
            'id': i,
            'ref_ir_verification': ref_ir_verification,
            'ref_ir_verification_message': ref_ir_verification_message,
            'tgt_ir_verification': tgt_ir_verification,
            'tgt_ir_verification_message': tgt_ir_verification_message,
            'ref_canonicalization': ref_canon_success,
            'ref_canonicalization_error': ref_canon_error,
            'tgt_canonicalization': tgt_canon_success,
            'tgt_canonicalization_error': tgt_canon_error,
            'identical': is_identical,
            'diff_stdout': diff_stdout,
            'diff_stderr': diff_stderr,
            'function_count_match': func_analysis.get('count_match', False),
            'function_signature_match': func_analysis.get('signature_match', False),
        }

        results.append(result)

    return results

def main(args):
    for batch in load_dataset(args.dataset, args.batch_size):
        process_batch(batch)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runner for Source Code Analysis")

    parser.add_argument('--dataset', type=str, required=True)
    parser.add_argument('--batch_size', type=str, default=100)

    args = parser.parse_args()

    main(args)
