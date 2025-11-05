import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'datasets', 'helper_scripts', 'ir_processing'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'training'))

from IR_extractor import generate_ir_for_source_file
from ir2o import ir_to_o
from preprocess import preprocess_llvm_ir

def load_single_exec_dataset(dataset_path):
    return [os.path.join(dataset_path, f) for f in os.listdir(dataset_path) if f.endswith('.c')]

def compile_datapoint(source_file, output_dir):
    executable_path = os.path.join(output_dir, os.path.basename(source_file).replace('.c', ''))
    compilation_command = ["/usr/bin/clang", "-O0", source_file, "-o", executable_path]
    result = subprocess.run(compilation_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result, executable_path

def run_executable(executable_path):
    result = subprocess.run([executable_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout, result.stderr

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python test.py <dataset>")
        sys.exit(1)

    dataset_path = sys.argv[1]
    dataset = load_single_exec_dataset(dataset_path)
    output_dir = os.path.join(dataset_path, "output")
    preprocessed_output_dir = os.path.join(dataset_path, "preprocessed_output")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(preprocessed_output_dir, exist_ok=True)

    original_comp_return_code = []
    llvm_to_o_return_code = []

    mismatched_stdout = []
    mismatched_stderr = []

    for data_point in dataset:
        compilation_result, executable_path = compile_datapoint(data_point, output_dir)

        if compilation_result.returncode != 0:
            print(f"Compilation failed for {data_point}: {compilation_result.stderr}")
            continue

        original_comp_return_code.append(data_point)

        stdout, stderr = run_executable(executable_path)

        compilation_command = ["/usr/bin/clang", "-O0", "-S", "-emit-llvm", "-o", "-", data_point]
        llvm_IR = generate_ir_for_source_file(dataset_path, compilation_command)

        if not llvm_IR:
            print(f"IR generation failed for {data_point}")
            continue

        cleaned_LLVM_IR = preprocess_llvm_ir(llvm_IR.stdout)

        preprocessed_executable_path = os.path.join(preprocessed_output_dir, os.path.basename(data_point).replace('.c', ''))
        ir_compilation_command = ["/usr/bin/clang", "-O0", "-o", preprocessed_executable_path, "placeholder.ll"]
        ir_to_o_result = ir_to_o(cleaned_LLVM_IR, ir_compilation_command, output_file=None, src_directory=os.path.dirname(data_point))

        if ir_to_o_result.returncode != 0:
            print(f"Error converting IR to executable for {data_point}: {ir_to_o_result.stderr}")
            continue

        llvm_to_o_return_code.append(data_point)

        preprocessed_executable_path_stdout, preprocessed_executable_path_stderr = run_executable(preprocessed_executable_path)

        if stdout != preprocessed_executable_path_stdout:
            mismatched_stdout.append({
                'data_point': data_point,
                'expected': stdout,
                'actual': preprocessed_executable_path_stdout
            })

        if stderr != preprocessed_executable_path_stderr:
            mismatched_stderr.append({
                'data_point': data_point,
                'expected': stderr,
                'actual': preprocessed_executable_path_stderr
            })

        print(f"Processed {data_point}")
        print(f"  Original Compilation Return Code: {compilation_result.returncode}")
        print(f"  LLVM IR to Object Return Code: {ir_to_o_result.returncode}")
        print(f" Original stdout: {stdout}")
        print(f" Preprocessed stdout: {preprocessed_executable_path_stdout}")
        print(f" Original stderr: {stderr}")
        print(f" Preprocessed stderr: {preprocessed_executable_path_stderr}")

    print("#" * 50)
    print("Validation Summary:")
    print(f"Total data points processed: {len(dataset)}")
    print(f"Successful original compilations: {len(original_comp_return_code)}")
    print(f"Successful LLVM IR to object conversions: {len(llvm_to_o_return_code)}")
    print(f"Mismatched stdout count: {len(mismatched_stdout)}")
    print(f"Mismatched stderr count: {len(mismatched_stderr)}")
