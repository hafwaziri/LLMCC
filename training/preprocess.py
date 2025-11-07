import tempfile
import subprocess
import re

def preprocess_llvm_ir(llvm_ir):

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as temp_ir:
        temp_ir.write(llvm_ir)
        temp_ir.flush()
        temp_ir_path = temp_ir.name

    opt_command = ["opt", "--strip-debug", "--strip-named-metadata", "-S", temp_ir_path, "-o", temp_ir_path]
    debug_stripped = subprocess.run(opt_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if debug_stripped.returncode != 0:
        return False

    with open(temp_ir.name, 'r') as f:
        llvm_ir = f.read()
    
    llvm_ir = re.sub(r'^; ModuleID = .*$\n?', '', llvm_ir, flags=re.MULTILINE)
    llvm_ir = re.sub(r'^source_filename = .*$\n?', '', llvm_ir, flags=re.MULTILINE)
    llvm_ir = re.sub(r'^target datalayout = .*$\n?', '', llvm_ir, flags=re.MULTILINE)
    llvm_ir = re.sub(r'^target triple = .*$\n?', '', llvm_ir, flags=re.MULTILINE)

    return llvm_ir