import argparse
import orjson
import os
from static_analysis.structural_analysis.llvm_ir_verification import verify_ir
from static_analysis.structural_analysis.llvm_ir_diff import diff_llvm_ir
from static_analysis.structural_analysis.llvm_ir_canonicalization_and_normalization import canonicalize_and_normalize_ir
from static_analysis.structural_analysis.llvm_ir_function_analysis import functions_count
from static_analysis.structural_analysis.llvm_ir_cfg_comparison import compare_llvm_ir_cfgs
from static_analysis.semantic_analysis.llvm_ir_alive2_test_harness import verify_with_alive2
from functional_and_behavioural_analysis.llvm_ir_compilation_check import compilation_check
from functional_and_behavioural_analysis.llvm_ir_io_test import io_test


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

def process_batch(batch, compilation_command=None, output_file=None, src_directory=None, io_timeout=60):
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
                'cfg_isomorphic_match': False,
                'cfg_loop_count_match': False,
                'cfg_complexity_match': False,
                'cfg_dominator_match': False,
                'cfg_nodes_match': False,
                'cfg_edges_match': False,
                'cfg_similarity_score': 0.0,
                'cfg_definitive_match': False,
                'alive2_verified': False,
                'alive2_stdout': "VERIFY FAILED",
                'alive2_stderr': "VERIFY FAILED",
                'ref_compilation_success': False,
                'tgt_compilation_success': False,
                'io_both_executed': False,
                'io_stdout_match': False,
                'io_stderr_match': False,
                'io_returncode_match': False,
                'io_match': False,
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
                'cfg_isomorphic_match': False,
                'cfg_loop_count_match': False,
                'cfg_complexity_match': False,
                'cfg_dominator_match': False,
                'cfg_nodes_match': False,
                'cfg_edges_match': False,
                'cfg_similarity_score': 0.0,
                'cfg_definitive_match': False,
                'alive2_verified': False,
                'alive2_stdout': "CANONICALIZATION FAILED",
                'alive2_stderr': "CANONICALIZATION FAILED",
                'ref_compilation_success': False,
                'tgt_compilation_success': False,
                'io_both_executed': False,
                'io_stdout_match': False,
                'io_stderr_match': False,
                'io_returncode_match': False,
                'io_match': False,
            }
            results.append(result)
            continue

        # Function Analysis
        func_analysis = functions_count(ref_canon_ir, tgt_canon_ir)

        # IR Diff
        is_identical, diff_stdout, diff_stderr = diff_llvm_ir(ref_canon_ir, tgt_canon_ir)

        # CFG Comparison
        try:
            cfg_comparison = compare_llvm_ir_cfgs(ref_canon_ir, tgt_canon_ir)

            # Aggregate metrics across all functions
            comparisons = cfg_comparison.get('comparisons', {})

            if comparisons:
                cfg_isomorphic = all(r.get('is_isomorphic', False) for r in comparisons.values())
                cfg_loop_match = all(r.get('loop_count_match', False) for r in comparisons.values())
                cfg_complexity_match = all(r.get('cyclomatic_complexity_match', False) for r in comparisons.values())
                cfg_dominator_match = all(r.get('dominator_tree_match', False) for r in comparisons.values() if r.get('dominator_tree_match') is not None)
                cfg_nodes_match = all(r.get('graph1_nodes') == r.get('graph2_nodes') for r in comparisons.values())
                cfg_edges_match = all(r.get('graph1_edges') == r.get('graph2_edges') for r in comparisons.values())
                cfg_similarity_score = cfg_comparison.get('all_similarity_avg', 0.0) or 0.0
                cfg_definitive_match = cfg_comparison.get('all_match', False)
            else:
                cfg_isomorphic = False
                cfg_loop_match = False
                cfg_complexity_match = False
                cfg_dominator_match = False
                cfg_nodes_match = False
                cfg_edges_match = False
                cfg_similarity_score = 0.0
                cfg_definitive_match = False

        except Exception:
            cfg_isomorphic = False
            cfg_loop_match = False
            cfg_complexity_match = False
            cfg_dominator_match = False
            cfg_nodes_match = False
            cfg_edges_match = False
            cfg_similarity_score = 0.0
            cfg_definitive_match = False

        # Alive2 Verification
        try:
            alive2_verified, alive2_stdout, alive2_stderr = verify_with_alive2(ref_canon_ir, tgt_canon_ir)
        except Exception as e:
            alive2_verified = False
            alive2_stdout = ""
            alive2_stderr = f"Alive2 verification error: {str(e)}"

        # Compilation Check
        ref_compilation_success = False
        tgt_compilation_success = False
        ref_executable = None
        tgt_executable = None

        if compilation_command and output_file:
            try:
                ref_output = "ref_" + output_file
                ref_compilation_success = compilation_check(
                    ref_canon_ir,
                    compilation_command,
                    ref_output,
                    src_directory
                )

                if ref_compilation_success:
                    ref_executable = os.path.join(src_directory, ref_output) if src_directory else ref_output

                    tgt_output = "tgt_" + output_file
                    tgt_compilation_success = compilation_check(
                        tgt_canon_ir,
                        compilation_command,
                        tgt_output,
                        src_directory
                    )

                    if tgt_compilation_success:
                        tgt_executable = os.path.join(src_directory, tgt_output) if src_directory else tgt_output
            except Exception as e:
                ref_compilation_success = False
                tgt_compilation_success = False

        # I/O Testing
        io_both_executed = False
        io_stdout_match = False
        io_stderr_match = False
        io_returncode_match = False
        io_match = False

        if ref_compilation_success and tgt_compilation_success and ref_executable and tgt_executable:
            try:
                io_result = io_test(ref_executable, tgt_executable, io_timeout)

                io_both_executed = io_result.get('both_executed', False)
                io_stdout_match = io_result.get('stdout_match', False)
                io_stderr_match = io_result.get('stderr_match', False)
                io_returncode_match = io_result.get('returncode_match', False)
                io_match = io_result.get('match', False)
            except Exception as e:
                io_both_executed = False
                io_stdout_match = False
                io_stderr_match = False
                io_returncode_match = False
                io_match = False

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
            'cfg_isomorphic_match': cfg_isomorphic,
            'cfg_loop_count_match': cfg_loop_match,
            'cfg_complexity_match': cfg_complexity_match,
            'cfg_dominator_match': cfg_dominator_match,
            'cfg_nodes_match': cfg_nodes_match,
            'cfg_edges_match': cfg_edges_match,
            'cfg_similarity_score': cfg_similarity_score,
            'cfg_definitive_match': cfg_definitive_match,
            'alive2_verified': alive2_verified,
            'alive2_stdout': alive2_stdout,
            'alive2_stderr': alive2_stderr,
            'ref_compilation_success': ref_compilation_success,
            'tgt_compilation_success': tgt_compilation_success,
            'io_both_executed': io_both_executed,
            'io_stdout_match': io_stdout_match,
            'io_stderr_match': io_stderr_match,
            'io_returncode_match': io_returncode_match,
            'io_match': io_match,
        }

        results.append(result)

    return results

def main(args):
    compilation_command = args.compilation_command.split() if args.compilation_command else None

    for batch in load_dataset(args.dataset, args.batch_size):
        process_batch(
            batch,
            compilation_command=compilation_command,
            output_file=args.output_file,
            src_directory=args.src_directory,
            io_timeout=args.io_timeout
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runner for Source Code Analysis")

    parser.add_argument('--dataset', type=str, required=True)
    parser.add_argument('--batch_size', type=str, default=100)
    parser.add_argument('--compilation_command', type=str, default=None, help='Compilation command (space-separated)')
    parser.add_argument('--output_file', type=str, default=None)
    parser.add_argument('--src_directory', type=str, default=None)
    parser.add_argument('--io_timeout', type=int, default=60)

    args = parser.parse_args()

    main(args)
