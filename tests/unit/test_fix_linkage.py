import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helper_scripts', 'ir_processing'))

from fix_linkage import restore_private_linkage


class TestRestorePrivateLinkage:

    def test_restore_private_linkage_basic(self):

        original_ir = """
; ModuleID = 'test'
@.str = private unnamed_addr constant [5 x i8] c"test\\00", align 1
@.str.1 = internal constant [6 x i8] c"hello\\00", align 1
@public_var = external global i8*, align 8
"""

        modified_ir = """
; ModuleID = 'test'
@.str = hidden unnamed_addr constant [5 x i8] c"test\\00", align 1
@.str.1 = hidden constant [6 x i8] c"hello\\00", align 1
@public_var = external global i8*, align 8
"""

        result = restore_private_linkage(original_ir, modified_ir)

        assert "private unnamed_addr constant" in result
        assert "internal constant" in result
        assert "external global" in result
        assert "hidden" not in result or result.count("hidden") < modified_ir.count("hidden")

    def test_restore_private_linkage_no_changes_needed(self):

        ir_content = """
    ; ModuleID = 'test'
    @.str = private unnamed_addr constant [5 x i8] c"test\\00", align 1
    @public_var = external global i8*, align 8
    """

        result = restore_private_linkage(ir_content, ir_content)

        assert "private unnamed_addr constant" in result
        assert "@.str" in result
        assert "@public_var = external global" in result
        assert "c\"test\\00\"" in result

    def test_restore_private_linkage_variable_not_in_original(self):

        original_ir = """
; ModuleID = 'test'
@.str = private unnamed_addr constant [5 x i8] c"test\\00", align 1
"""

        modified_ir = """
; ModuleID = 'test'
@.str = hidden unnamed_addr constant [5 x i8] c"test\\00", align 1
@new_var = hidden constant [4 x i8] c"new\\00", align 1
"""

        result = restore_private_linkage(original_ir, modified_ir)

        assert "private unnamed_addr constant" in result
        assert "@new_var = hidden constant" in result

    def test_restore_private_linkage_variable_not_in_modified(self):

        original_ir = """
; ModuleID = 'test'
@.str = private unnamed_addr constant [5 x i8] c"test\\00", align 1
@old_var = internal constant [4 x i8] c"old\\00", align 1
"""

        modified_ir = """
; ModuleID = 'test'
@.str = hidden unnamed_addr constant [5 x i8] c"test\\00", align 1
"""

        result = restore_private_linkage(original_ir, modified_ir)

        assert "private unnamed_addr constant" in result
        assert "@old_var" not in result

    def test_restore_private_linkage_malformed_ir(self):

        original_ir = "this is not valid IR"
        modified_ir = "this is also not valid IR"

        result = restore_private_linkage(original_ir, modified_ir)

        assert result == modified_ir

    def test_restore_private_linkage_only_original_malformed(self):

        original_ir = "malformed IR"
        modified_ir = """
; ModuleID = 'test'
@.str = hidden unnamed_addr constant [5 x i8] c"test\\00", align 1
"""

        result = restore_private_linkage(original_ir, modified_ir)

        assert result == modified_ir

    def test_restore_private_linkage_only_modified_malformed(self):

        original_ir = """
; ModuleID = 'test'
@.str = private unnamed_addr constant [5 x i8] c"test\\00", align 1
"""
        modified_ir = "malformed IR"

        result = restore_private_linkage(original_ir, modified_ir)

        assert result == modified_ir

    def test_restore_private_linkage_mixed_linkage_types(self):

        original_ir = """
; ModuleID = 'test'
@private_var = private constant [5 x i8] c"priv\\00", align 1
@internal_var = internal constant [4 x i8] c"int\\00", align 1
@external_var = external global i8*, align 8
@weak_var = weak global i32 0, align 4
@common_var = common global i32 0, align 4
"""

        modified_ir = """
; ModuleID = 'test'
@private_var = hidden constant [5 x i8] c"priv\\00", align 1
@internal_var = hidden constant [4 x i8] c"int\\00", align 1
@external_var = external global i8*, align 8
@weak_var = weak global i32 0, align 4
@common_var = common global i32 0, align 4
"""

        result = restore_private_linkage(original_ir, modified_ir)

        assert "@private_var = private constant" in result
        assert "@internal_var = internal constant" in result
        assert "@external_var = external global" in result
        assert "@weak_var = weak global" in result
        assert "@common_var = common global" in result

    def test_restore_private_linkage_already_correct_linkage(self):

        original_ir = """
; ModuleID = 'test'
@.str = private unnamed_addr constant [5 x i8] c"test\\00", align 1
@.str.1 = internal constant [6 x i8] c"hello\\00", align 1
"""

        modified_ir = """
; ModuleID = 'test'
@.str = private unnamed_addr constant [5 x i8] c"test\\00", align 1
@.str.1 = internal constant [6 x i8] c"hello\\00", align 1
"""

        result = restore_private_linkage(original_ir, modified_ir)

        assert "@.str = private unnamed_addr constant" in result
        assert "@.str.1 = internal constant" in result

    def test_restore_private_linkage_no_global_variables(self):

        original_ir = """
    ; ModuleID = 'test'

    define i32 @main() {
    ret i32 0
    }
    """

        modified_ir = """
    ; ModuleID = 'test'

    define i32 @main() {
    ret i32 0
    }
    """

        result = restore_private_linkage(original_ir, modified_ir)

        assert "define i32 @main()" in result
        assert "ret i32 0" in result

        assert "@" not in result.split("define")[0]