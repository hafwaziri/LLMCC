import tempfile
import os
import subprocess
import shutil
from pathlib import Path

def generate_cfg(llvm_ir):
    tmp_dir = None
    tmp_file_path = None

    try:
        tmp_dir = tempfile.mkdtemp()
        tmp_file_path = os.path.join(tmp_dir, "input.ll")

        with open(tmp_file_path, 'w') as f:
            f.write(llvm_ir)

        subprocess.run([
            'opt', '-disable-output',
            '-passes=dot-cfg',
            tmp_file_path
        ], check=True, cwd=tmp_dir)

        dot_files = list(Path(tmp_dir).glob('*.dot'))

        cfg_data = {}
        for dot_file in dot_files:
            with open(dot_file, 'r') as f:
                cfg_data[dot_file.name] = f.read()
        
        return cfg_data, tmp_dir

    except Exception:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        raise

def print_cfg_details(llvm_ir):
    cfg_data, tmp_dir = generate_cfg(llvm_ir)

    try:
        print("=== CFG Details ===\n")
        for filename, dot_content in cfg_data.items():
            print(f"Function: {filename}")
            print(f"DOT file content:\n{dot_content}\n")

            lines = dot_content.split('\n')
            print("Nodes (Basic Blocks):")
            for line in lines:
                if 'label=' in line and 'Node' in line:
                    print(f" {line.strip()}")
            
            print("\nEdges (Control Flow):")
            for line in lines:
                if '->' in line:
                    print(f" {line.strip()}")
            print("-" * 50)
        
        return cfg_data, tmp_dir
    except Exception:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        raise

if __name__ == "__main__":
    test_ir = """
    define i32 @factorial(i32 %n) {
    entry:
      %cmp = icmp sgt i32 %n, 1
      br i1 %cmp, label %recurse, label %base
    
    base:
      ret i32 1
    
    recurse:
      %sub = sub i32 %n, 1
      %call = call i32 @factorial(i32 %sub)
      %mul = mul i32 %n, %call
      ret i32 %mul
    }
    """

    print_cfg_details(test_ir)
