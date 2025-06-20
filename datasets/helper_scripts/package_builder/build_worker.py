import sys
import json
import os
from process_package import process_package
import traceback
import debugpy

class Package:
    def __init__(self, path, name):
        self.path = path
        self.name = name

if __name__ == "__main__":
    # debugpy.listen(("0.0.0.0", 5678))
    # debugpy.wait_for_client()
    # debugpy.breakpoint()
    
    try:
        package_dir = sys.argv[1]
        sub_dir = sys.argv[2]
        
        package_name = os.path.basename(package_dir.rstrip('/'))
        
        package = Package(package_dir, package_name)
        package_subdir = Package(sub_dir, package_name)
        
        result = process_package(package, package_subdir)
        
        json.dump(result, sys.stdout)
        sys.stdout.flush()
        
    except Exception as e:
        print(f"Exception occurred: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        
        error_result = ("unknown", "", "", "", str(e), 1)
        json.dump(error_result, sys.stdout)
        sys.stdout.flush()
