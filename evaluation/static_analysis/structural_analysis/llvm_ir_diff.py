import sys
import subprocess
import tempfile
import os

def diff_llvm_ir(ir1, ir2):
    tmp_file1 = None
    tmp_file2 = None

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as f1:
            f1.write(ir1)
            tmp_file1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as f2:
            f2.write(ir2)
            tmp_file2 = f2.name

        result = subprocess.run(
            ['llvm-diff', tmp_file1, tmp_file2],
            capture_output=True,
            text=True,
            timeout=60
        )

        is_identical = not result.stdout.strip()

        return is_identical, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", "llvm-diff timed out"
    except Exception as e:
        return False, "", f"Error during diff: {str(e)}"
    finally:
        for path in (tmp_file1, tmp_file2):
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except:
                    pass

if __name__ == "__main__":
    # Example: Two different LLVM IR snippets
    ir1 = r"""
; ModuleID = '<stdin>'
source_filename = "zmakebas.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct._IO_FILE = type { i32, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, %struct._IO_marker*, %struct._IO_FILE*, i32, i32, i64, i16, i8, [1 x i8], i8*, i64, %struct._IO_codecvt*, %struct._IO_wide_data*, %struct._IO_FILE*, i8*, i64, i32, [20 x i8] }
%struct._IO_marker = type opaque
%struct._IO_codecvt = type opaque
%struct._IO_wide_data = type opaque

@stderr = external global %struct._IO_FILE*, align 8
@grok_block.lookup = external hidden global [17 x i8*], align 16
@.str.143 = external hidden unnamed_addr constant [40 x i8], align 1

declare i32 @fprintf(%struct._IO_FILE* noundef, i8* noundef, ...) #0

; Function Attrs: noreturn nounwind
declare void @exit(i32 noundef) #1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @grok_block(i8* noundef %0, i32 noundef %1) #2 {
  %3 = alloca i8*, align 8
  %4 = alloca i32, align 4
  %5 = alloca i8**, align 8
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  store i8* %0, i8** %3, align 8
  store i32 %1, i32* %4, align 4
  store i32 128, i32* %6, align 4
  store i32 -1, i32* %7, align 4
  store i8** getelementptr inbounds ([17 x i8*], [17 x i8*]* @grok_block.lookup, i64 0, i64 0), i8*** %5, align 8
  br label %8

8:                                                ; preds = %22, %2
  %9 = load i8**, i8*** %5, align 8
  %10 = load i8*, i8** %9, align 8
  %11 = icmp ne i8* %10, null
  br i1 %11, label %12, label %27

12:                                               ; preds = %8
  %13 = load i8*, i8** %3, align 8
  %14 = getelementptr inbounds i8, i8* %13, i64 1
  %15 = load i8**, i8*** %5, align 8
  %16 = load i8*, i8** %15, align 8
  %17 = call i32 @strncmp(i8* noundef %14, i8* noundef %16, i64 noundef 2) #4
  %18 = icmp eq i32 %17, 0
  br i1 %18, label %19, label %21

19:                                               ; preds = %12
  %20 = load i32, i32* %6, align 4
  store i32 %20, i32* %7, align 4
  br label %27

21:                                               ; preds = %12
  br label %22

22:                                               ; preds = %21
  %23 = load i8**, i8*** %5, align 8
  %24 = getelementptr inbounds i8*, i8** %23, i32 1
  store i8** %24, i8*** %5, align 8
  %25 = load i32, i32* %6, align 4
  %26 = add nsw i32 %25, 1
  store i32 %26, i32* %6, align 4
  br label %8, !llvm.loop !6

27:                                               ; preds = %19, %8
  %28 = load i32, i32* %7, align 4
  %29 = icmp eq i32 %28, -1
  br i1 %29, label %30, label %34

30:                                               ; preds = %27
  %31 = load %struct._IO_FILE*, %struct._IO_FILE** @stderr, align 8
  %32 = load i32, i32* %4, align 4
  %33 = call i32 (%struct._IO_FILE*, i8*, ...) @fprintf(%struct._IO_FILE* noundef %31, i8* noundef getelementptr inbounds ([40 x i8], [40 x i8]* @.str.143, i64 0, i64 0), i32 noundef %32)
  call void @exit(i32 noundef 1) #5
  unreachable

34:                                               ; preds = %27
  %35 = load i32, i32* %7, align 4
  ret i32 %35
}

; Function Attrs: nounwind readonly willreturn
declare i32 @strncmp(i8* noundef, i8* noundef, i64 noundef) #3

attributes #0 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { noreturn nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nounwind readonly willreturn "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind readonly willreturn }
attributes #5 = { noreturn nounwind }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Debian clang version 14.0.6"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}


"""

    ir2 = """
define i32 @add(i32 %x, i32 %y) {
  %sum = add i32 %x, %y
  ret i32 %sum
}
"""

    print("Comparing two IR snippets...\n")
    is_identical, diff_output, error = diff_llvm_ir(ir1, ir2)

    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    if is_identical:
        print("IRs are identical.")
        sys.exit(0)
    else:
        print("IRs differ:")
        print(diff_output)
        sys.exit(1)
