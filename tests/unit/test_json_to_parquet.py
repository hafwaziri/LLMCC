import os
import sys
import pytest
import tempfile
import orjson
import polars as pl
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datasets.helper_scripts.package_builder.json_to_parquet import json_to_parquet

class TestJsonToParquet:

    @pytest.fixture
    def sample_package_data(self):

        return {
            "name": "test-package",
            "build_system": "cmake",
            "dh_auto_configure": "configure output",
            "dh_auto_build": "build output",
            "dh_auto_test": "test output",
            "build_stderr": "build stderr",
            "build_return_code": 0,
            "test_stdout": "test stdout",
            "test_stderr": "test stderr",
            "test_returncode": 0,
            "test_detected": True,
            "testing_framework": "pytest",
            "test_stdout_diff": "stdout diff",
            "test_stderr_diff": "stderr diff",
            "package_viable_for_test_dataset": True,
            "rebuild_stderr": "rebuild stderr",
            "rebuild_returncode": 0,
            "modified_rebuild_stderr": "modified rebuild stderr",
            "modified_rebuild_returncode": 0,
            "test_stdout_for_modified_package": "test stdout modified",
            "test_stderr_for_modified_package": "test stderr modified",
            "test_passed": True,
            "source_files": [
                {
                    "file_path": "src/main.c",
                    "compilation_command": "gcc -O2 -c src/main.c",
                    "output_file": "main.o",
                    "src_functions": ["main", "helper"],
                    "ir_functions": ["main", "helper"],
                    "random_function": "main",
                    "random_function_mangled": "_main",
                    "IR_generation_return_code": 0,
                    "LLVM_IR": "define i32 @main()",
                    "IR_generation_stderr": "",
                    "random_function_IR_generation_return_code": 0,
                    "random_function_IR": "define i32 @main()",
                    "random_function_IR_stderr": "",
                    "object_file_generation_return_code": 0,
                    "timestamp_check": True,
                    "relinked_llvm_ir": "define i32 @main()",
                    "modified_object_file_generation_return_code": 0,
                    "modified_object_file_timestamp_check": True
                }
            ]
        }

    @pytest.fixture
    def sample_package_without_source_files(self):

        return {
            "name": "empty-package",
            "build_system": "make",
            "test_detected": False,
            "package_viable_for_test_dataset": False
        }

    def test_successful_conversion(self, sample_package_data):

        with tempfile.TemporaryDirectory() as temp_dir:
            json_dir = Path(temp_dir) / "json"
            output_dir = Path(temp_dir) / "output"
            json_dir.mkdir()
            

            json_file = json_dir / "test-package.json"
            with open(json_file, 'wb') as f:
                f.write(orjson.dumps(sample_package_data))

            json_to_parquet(str(json_dir), str(output_dir))

            assert (output_dir / "packages.parquet").exists()
            assert (output_dir / "source_files.parquet").exists()

            packages_df = pl.read_parquet(output_dir / "packages.parquet")
            assert len(packages_df) == 1
            assert packages_df["name"][0] == "test-package"
            assert packages_df["build_system"][0] == "cmake"
            assert "source_files" not in packages_df.columns

            source_files_df = pl.read_parquet(output_dir / "source_files.parquet")
            assert len(source_files_df) == 1
            assert source_files_df["package_name"][0] == "test-package"
            assert source_files_df["file_path"][0] == "src/main.c"

    def test_multiple_json_files(self, sample_package_data, sample_package_without_source_files):

        with tempfile.TemporaryDirectory() as temp_dir:
            json_dir = Path(temp_dir) / "json"
            output_dir = Path(temp_dir) / "output"
            json_dir.mkdir()

            with open(json_dir / "package1.json", 'wb') as f:
                f.write(orjson.dumps(sample_package_data))

            with open(json_dir / "package2.json", 'wb') as f:
                f.write(orjson.dumps(sample_package_without_source_files))

            json_to_parquet(str(json_dir), str(output_dir))

            packages_df = pl.read_parquet(output_dir / "packages.parquet")
            assert len(packages_df) == 2
            package_names = packages_df["name"].to_list()
            assert "test-package" in package_names
            assert "empty-package" in package_names

            source_files_df = pl.read_parquet(output_dir / "source_files.parquet")
            assert len(source_files_df) == 1
            assert source_files_df["package_name"][0] == "test-package"

    def test_empty_json_directory(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            json_dir = Path(temp_dir) / "json"
            output_dir = Path(temp_dir) / "output"
            json_dir.mkdir()

            json_to_parquet(str(json_dir), str(output_dir))

            assert output_dir.exists()
            assert not (output_dir / "packages.parquet").exists()
            assert not (output_dir / "source_files.parquet").exists()

    def test_invalid_json_file(self, sample_package_data):

        with tempfile.TemporaryDirectory() as temp_dir:
            json_dir = Path(temp_dir) / "json"
            output_dir = Path(temp_dir) / "output"
            json_dir.mkdir()

            with open(json_dir / "valid.json", 'wb') as f:
                f.write(orjson.dumps(sample_package_data))

            with open(json_dir / "invalid.json", 'w') as f:
                f.write("invalid json content")

            json_to_parquet(str(json_dir), str(output_dir))

            packages_df = pl.read_parquet(output_dir / "packages.parquet")
            assert len(packages_df) == 1
            assert packages_df["name"][0] == "test-package"

    def test_package_without_source_files(self, sample_package_without_source_files):

        with tempfile.TemporaryDirectory() as temp_dir:
            json_dir = Path(temp_dir) / "json"
            output_dir = Path(temp_dir) / "output"
            json_dir.mkdir()

            with open(json_dir / "empty.json", 'wb') as f:
                f.write(orjson.dumps(sample_package_without_source_files))

            json_to_parquet(str(json_dir), str(output_dir))

            assert (output_dir / "packages.parquet").exists()
            assert not (output_dir / "source_files.parquet").exists()
            
            packages_df = pl.read_parquet(output_dir / "packages.parquet")
            assert len(packages_df) == 1
            assert packages_df["name"][0] == "empty-package"

    def test_package_with_empty_source_files_list(self):

        package_data = {
            "name": "test-package",
            "build_system": "make",
            "source_files": []
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            json_dir = Path(temp_dir) / "json"
            output_dir = Path(temp_dir) / "output"
            json_dir.mkdir()
            
            with open(json_dir / "empty_sources.json", 'wb') as f:
                f.write(orjson.dumps(package_data))
            
            json_to_parquet(str(json_dir), str(output_dir))

            assert (output_dir / "packages.parquet").exists()
            assert not (output_dir / "source_files.parquet").exists()

    def test_output_directory_creation(self, sample_package_data):

        with tempfile.TemporaryDirectory() as temp_dir:
            json_dir = Path(temp_dir) / "json"
            output_dir = Path(temp_dir) / "nested" / "output" / "dir"
            json_dir.mkdir()
            
            with open(json_dir / "test.json", 'wb') as f:
                f.write(orjson.dumps(sample_package_data))

            assert not output_dir.exists()

            json_to_parquet(str(json_dir), str(output_dir))

            assert output_dir.exists()
            assert (output_dir / "packages.parquet").exists()

    def test_non_json_files_ignored(self, sample_package_data):

        with tempfile.TemporaryDirectory() as temp_dir:
            json_dir = Path(temp_dir) / "json"
            output_dir = Path(temp_dir) / "output"
            json_dir.mkdir()

            with open(json_dir / "valid.json", 'wb') as f:
                f.write(orjson.dumps(sample_package_data))

            with open(json_dir / "readme.txt", 'w') as f:
                f.write("This is not a JSON file")
            
            with open(json_dir / "config.yaml", 'w') as f:
                f.write("key: value")

            json_to_parquet(str(json_dir), str(output_dir))

            packages_df = pl.read_parquet(output_dir / "packages.parquet")
            assert len(packages_df) == 1
            assert packages_df["name"][0] == "test-package"

    def test_source_files_get_package_name(self, sample_package_data):

        sample_package_data["source_files"].append({
            "file_path": "src/helper.c",
            "compilation_command": "gcc -O2 -c src/helper.c",
            "output_file": "helper.o"
        })

        with tempfile.TemporaryDirectory() as temp_dir:
            json_dir = Path(temp_dir) / "json"
            output_dir = Path(temp_dir) / "output"
            json_dir.mkdir()

            with open(json_dir / "test.json", 'wb') as f:
                f.write(orjson.dumps(sample_package_data))

            json_to_parquet(str(json_dir), str(output_dir))

            source_files_df = pl.read_parquet(output_dir / "source_files.parquet")
            assert len(source_files_df) == 2

            package_names = source_files_df["package_name"].to_list()
            assert all(name == "test-package" for name in package_names)

            file_paths = source_files_df["file_path"].to_list()
            assert "src/main.c" in file_paths
            assert "src/helper.c" in file_paths