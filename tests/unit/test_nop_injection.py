import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'helper_scripts', 'ir_processing'))

from nop_injection import ir_injection

class TestNopInjection:

    def test_empty_function_ir(self):

        function_ir = ""
        injection_code = "%nop_temp = add i32 0, 0"

        result = ir_injection(function_ir, injection_code)

        assert result == ""

    def test_empty_injection_code(self):

        function_ir = """define i32 @test() {
  ret i32 0
}"""
        injection_code = ""

        result = ir_injection(function_ir, injection_code)

        assert result == function_ir

    def test_both_empty(self):

        function_ir = ""
        injection_code = ""

        result = ir_injection(function_ir, injection_code)

        assert result == ""

    def test_simple_function_single_injection(self):

        function_ir = """define i32 @test() {
  ret i32 0
}"""
        injection_code = "%nop_temp = add i32 0, 0"

        result = ir_injection(function_ir, injection_code)

        expected = """define i32 @test() {
  %nop_temp = add i32 0, 0
  ret i32 0
}"""
        assert result == expected

    def test_function_with_parameters(self):

        function_ir = """define i32 @add(i32 %a, i32 %b) {
  %sum = add i32 %a, %b
  ret i32 %sum
}"""
        injection_code = "%nop_temp = add i32 0, 0"

        result = ir_injection(function_ir, injection_code)

        expected = """define i32 @add(i32 %a, i32 %b) {
  %nop_temp = add i32 0, 0
  %sum = add i32 %a, %b
  ret i32 %sum
}"""
        assert result == expected

    def test_multiline_injection_code(self):

        function_ir = """define i32 @test() {
  ret i32 42
}"""
        injection_code = """%nop1 = add i32 0, 0
%nop2 = mul i32 1, 1
%nop3 = sub i32 0, 0"""

        result = ir_injection(function_ir, injection_code)

        expected = """define i32 @test() {
  %nop1 = add i32 0, 0
  %nop2 = mul i32 1, 1
  %nop3 = sub i32 0, 0
  ret i32 42
}"""
        assert result == expected

    def test_multiple_functions(self):

        function_ir = """define i32 @func1() {
  ret i32 1
}

define i32 @func2() {
  ret i32 2
}"""
        injection_code = "%nop_temp = add i32 0, 0"

        result = ir_injection(function_ir, injection_code)

        expected = """define i32 @func1() {
  %nop_temp = add i32 0, 0
  ret i32 1
}

define i32 @func2() {
  %nop_temp = add i32 0, 0
  ret i32 2
}"""
        assert result == expected

    def test_function_with_attributes(self):

        function_ir = """define dso_local i32 @test() #0 {
  ret i32 0
}"""
        injection_code = "%nop_temp = add i32 0, 0"
        
        result = ir_injection(function_ir, injection_code)

        expected = """define dso_local i32 @test() #0 {
  %nop_temp = add i32 0, 0
  ret i32 0
}"""
        assert result == expected

    def test_function_definition_not_ending_with_brace(self):

        function_ir = """define i32 @test()
{
  ret i32 0
}"""
        injection_code = "%nop_temp = add i32 0, 0"

        result = ir_injection(function_ir, injection_code)

        assert result == function_ir

    def test_non_function_lines_with_define(self):

        function_ir = """; This define is in a comment: define i32 @fake() {
define i32 @real() {
  ret i32 0
}"""
        injection_code = "%nop_temp = add i32 0, 0"

        result = ir_injection(function_ir, injection_code)

        expected = """; This define is in a comment: define i32 @fake() {
define i32 @real() {
  %nop_temp = add i32 0, 0
  ret i32 0
}"""
        assert result == expected

    def test_complex_function_signature(self):

        function_ir = """define internal fastcc i32 @complex_func(i8* nocapture readonly %ptr, i32 %len) unnamed_addr #1 {
entry:
  %cmp = icmp sgt i32 %len, 0
  ret i32 %len
}"""
        injection_code = "%debug = add i32 %len, 0"

        result = ir_injection(function_ir, injection_code)

        expected = """define internal fastcc i32 @complex_func(i8* nocapture readonly %ptr, i32 %len) unnamed_addr #1 {
  %debug = add i32 %len, 0
entry:
  %cmp = icmp sgt i32 %len, 0
  ret i32 %len
}"""
        assert result == expected

    def test_no_function_definitions(self):
        """Test IR with no function definitions"""
        function_ir = """; ModuleID = 'test.c'
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@global_var = global i32 42, align 4"""
        injection_code = "%nop_temp = add i32 0, 0"
        
        result = ir_injection(function_ir, injection_code)

        assert result == function_ir

    def test_injection_with_special_characters(self):
        """Test injection code with special characters"""
        function_ir = """define i32 @test() {
  ret i32 0
}"""
        injection_code = """%str = getelementptr inbounds [13 x i8], [13 x i8]* @.str, i64 0, i64 0
%call = call i32 @puts(i8* %str)"""

        result = ir_injection(function_ir, injection_code)

        expected = """define i32 @test() {
  %str = getelementptr inbounds [13 x i8], [13 x i8]* @.str, i64 0, i64 0
  %call = call i32 @puts(i8* %str)
  ret i32 0
}"""
        assert result == expected