import subprocess
import tempfile
import os

def ir_to_o(ir, compilation_command, output_file, src_directory):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as temp_ir:
        temp_ir.write(ir)
        temp_ir.flush()

    # Create a copy to avoid modifying the original
    compilation_command = compilation_command.copy()
    compilation_command[-1] = temp_ir.name

    result = subprocess.run(
        compilation_command,
        cwd=src_directory,
        check=False
    )

    os.unlink(temp_ir.name)
    return result

if __name__ == "__main__":
    ir = r'''
; ModuleID = 'src/hello.c'
source_filename = "src/hello.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.option = type { i8*, i32, i32*, i32 }
%struct._IO_FILE = type { i32, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, %struct._IO_marker*, %struct._IO_FILE*, i32, i32, i64, i16, i8, [1 x i8], i8*, i64, %struct._IO_codecvt*, %struct._IO_wide_data*, %struct._IO_FILE*, i8*, i64, i32, [20 x i8] }
%struct._IO_marker = type opaque
%struct._IO_codecvt = type opaque
%struct._IO_wide_data = type opaque
%struct.__mbstate_t = type { i32, %union.anon }
%union.anon = type { i32 }

@.str = private unnamed_addr constant [1 x i8] zeroinitializer, align 1
@.str.1 = private unnamed_addr constant [6 x i8] c"hello\00", align 1
@.str.2 = private unnamed_addr constant [18 x i8] c"/usr/share/locale\00", align 1
@.str.3 = private unnamed_addr constant [21 x i8] c"Hellooooooo, woorld!\00", align 1
@.str.4 = private unnamed_addr constant [6 x i8] c"g:htv\00", align 1
@longopts = internal constant [5 x %struct.option] [%struct.option { i8* getelementptr inbounds ([9 x i8], [9 x i8]* @.str.10, i32 0, i32 0), i32 1, i32* null, i32 103 }, %struct.option { i8* getelementptr inbounds ([5 x i8], [5 x i8]* @.str.11, i32 0, i32 0), i32 0, i32* null, i32 104 }, %struct.option { i8* getelementptr inbounds ([12 x i8], [12 x i8]* @.str.12, i32 0, i32 0), i32 0, i32* null, i32 116 }, %struct.option { i8* getelementptr inbounds ([8 x i8], [8 x i8]* @.str.13, i32 0, i32 0), i32 0, i32* null, i32 118 }, %struct.option zeroinitializer], align 16, !dbg !0
@optarg = external global i8*, align 8
@.str.5 = private unnamed_addr constant [13 x i8] c"hello, world\00", align 1
@optind = external global i32, align 4
@.str.6 = private unnamed_addr constant [7 x i8] c"%s: %s\00", align 1
@.str.7 = private unnamed_addr constant [14 x i8] c"extra operand\00", align 1
@.str.8 = private unnamed_addr constant [40 x i8] c"conversion to a multibyte string failed\00", align 1
@.str.9 = private unnamed_addr constant [5 x i32] [i32 37, i32 108, i32 115, i32 10, i32 0], align 4
@.str.10 = private unnamed_addr constant [9 x i8] c"greeting\00", align 1
@.str.11 = private unnamed_addr constant [5 x i8] c"help\00", align 1
@.str.12 = private unnamed_addr constant [12 x i8] c"traditional\00", align 1
@.str.13 = private unnamed_addr constant [8 x i8] c"version\00", align 1
@.str.14 = private unnamed_addr constant [23 x i8] c"Usage: %s [OPTION]...\0A\00", align 1
@program_name = external global i8*, align 8
@.str.15 = private unnamed_addr constant [42 x i8] c"Print a friendly, customizable greeting.\0A\00", align 1
@stdout = external global %struct._IO_FILE*, align 8
@.str.16 = private unnamed_addr constant [109 x i8] c"  -h, --help          display this help and exit\0A  -v, --version       display version information and exit\0A\00", align 1
@.str.17 = private unnamed_addr constant [111 x i8] c"  -t, --traditional       use traditional greeting\0A  -g, --greeting=TEXT     use TEXT as the greeting message\0A\00", align 1
@.str.18 = private unnamed_addr constant [2 x i8] c"\0A\00", align 1
@.str.19 = private unnamed_addr constant [20 x i8] c"Report bugs to: %s\0A\00", align 1
@.str.20 = private unnamed_addr constant [18 x i8] c"bug-hello@gnu.org\00", align 1
@.str.21 = private unnamed_addr constant [20 x i8] c"%s home page: <%s>\0A\00", align 1
@.str.22 = private unnamed_addr constant [10 x i8] c"GNU Hello\00", align 1
@.str.23 = private unnamed_addr constant [35 x i8] c"http://www.gnu.org/software/hello/\00", align 1
@.str.24 = private unnamed_addr constant [64 x i8] c"General help using GNU software: <http://www.gnu.org/gethelp/>\0A\00", align 1
@.str.25 = private unnamed_addr constant [12 x i8] c"%s (%s) %s\0A\00", align 1
@.str.26 = private unnamed_addr constant [248 x i8] c"Copyright (C) %d Free Software Foundation, Inc.\0ALicense GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>\0AThis is free software: you are free to change and redistribute it.\0AThere is NO WARRANTY, to the extent permitted by law.\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main(i32 noundef %0, i8** noundef %1) #0 !dbg !33 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i8**, align 8
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  %8 = alloca i8*, align 8
  %9 = alloca i32*, align 8
  %10 = alloca i64, align 8
  store i32 0, i32* %3, align 4
  store i32 %0, i32* %4, align 4
  call void @llvm.dbg.declare(metadata i32* %4, metadata !39, metadata !DIExpression()), !dbg !40
  store i8** %1, i8*** %5, align 8
  call void @llvm.dbg.declare(metadata i8*** %5, metadata !41, metadata !DIExpression()), !dbg !42
  call void @llvm.dbg.declare(metadata i32* %6, metadata !43, metadata !DIExpression()), !dbg !44
  call void @llvm.dbg.declare(metadata i32* %7, metadata !45, metadata !DIExpression()), !dbg !46
  store i32 0, i32* %7, align 4, !dbg !46
  call void @llvm.dbg.declare(metadata i8** %8, metadata !47, metadata !DIExpression()), !dbg !48
  call void @llvm.dbg.declare(metadata i32** %9, metadata !49, metadata !DIExpression()), !dbg !52
  call void @llvm.dbg.declare(metadata i64* %10, metadata !53, metadata !DIExpression()), !dbg !54
  %11 = load i8**, i8*** %5, align 8, !dbg !55
  %12 = getelementptr inbounds i8*, i8** %11, i64 0, !dbg !55
  %13 = load i8*, i8** %12, align 8, !dbg !55
  call void @set_program_name(i8* noundef %13), !dbg !56
  %14 = call i8* @setlocale(i32 noundef 6, i8* noundef getelementptr inbounds ([1 x i8], [1 x i8]* @.str, i64 0, i64 0)) #6, !dbg !57
  %15 = call i8* @bindtextdomain(i8* noundef getelementptr inbounds ([6 x i8], [6 x i8]* @.str.1, i64 0, i64 0), i8* noundef getelementptr inbounds ([18 x i8], [18 x i8]* @.str.2, i64 0, i64 0)) #6, !dbg !58
  %16 = call i8* @textdomain(i8* noundef getelementptr inbounds ([6 x i8], [6 x i8]* @.str.1, i64 0, i64 0)) #6, !dbg !59
  %17 = call i8* @gettext(i8* noundef getelementptr inbounds ([14 x i8], [14 x i8]* @.str.3, i64 0, i64 0)) #6, !dbg !60
  store i8* %17, i8** %8, align 8, !dbg !61
  %18 = call i32 @atexit(void ()* noundef @close_stdout) #6, !dbg !62
  br label %19, !dbg !63

19:                                               ; preds = %33, %2
  %20 = load i32, i32* %4, align 4, !dbg !64
  %21 = load i8**, i8*** %5, align 8, !dbg !65
  %22 = call i32 @getopt_long(i32 noundef %20, i8** noundef %21, i8* noundef getelementptr inbounds ([6 x i8], [6 x i8]* @.str.4, i64 0, i64 0), %struct.option* noundef getelementptr inbounds ([5 x %struct.option], [5 x %struct.option]* @longopts, i64 0, i64 0), i32* noundef null) #6, !dbg !66
  store i32 %22, i32* %6, align 4, !dbg !67
  %23 = icmp ne i32 %22, -1, !dbg !68
  br i1 %23, label %24, label %34, !dbg !63

24:                                               ; preds = %19
  %25 = load i32, i32* %6, align 4, !dbg !69
  switch i32 %25, label %32 [
    i32 118, label %26
    i32 103, label %27
    i32 104, label %29
    i32 116, label %30
  ], !dbg !70

26:                                               ; preds = %24
  call void @print_version(), !dbg !71
  call void @exit(i32 noundef 0) #7, !dbg !73
  unreachable, !dbg !73

27:                                               ; preds = %24
  %28 = load i8*, i8** @optarg, align 8, !dbg !74
  store i8* %28, i8** %8, align 8, !dbg !75
  br label %33, !dbg !76

29:                                               ; preds = %24
  call void @print_help(), !dbg !77
  call void @exit(i32 noundef 0) #7, !dbg !78
  unreachable, !dbg !78

30:                                               ; preds = %24
  %31 = call i8* @gettext(i8* noundef getelementptr inbounds ([13 x i8], [13 x i8]* @.str.5, i64 0, i64 0)) #6, !dbg !79
  store i8* %31, i8** %8, align 8, !dbg !80
  br label %33, !dbg !81

32:                                               ; preds = %24
  store i32 1, i32* %7, align 4, !dbg !82
  br label %33, !dbg !83

33:                                               ; preds = %32, %30, %27
  br label %19, !dbg !63, !llvm.loop !84

34:                                               ; preds = %19
  %35 = load i32, i32* %7, align 4, !dbg !87
  %36 = icmp ne i32 %35, 0, !dbg !87
  br i1 %36, label %41, label %37, !dbg !89

37:                                               ; preds = %34
  %38 = load i32, i32* @optind, align 4, !dbg !90
  %39 = load i32, i32* %4, align 4, !dbg !91
  %40 = icmp slt i32 %38, %39, !dbg !92
  br i1 %40, label %41, label %48, !dbg !93

41:                                               ; preds = %37, %34
  %42 = call i8* @gettext(i8* noundef getelementptr inbounds ([14 x i8], [14 x i8]* @.str.7, i64 0, i64 0)) #6, !dbg !94
  %43 = load i8**, i8*** %5, align 8, !dbg !96
  %44 = load i32, i32* @optind, align 4, !dbg !97
  %45 = sext i32 %44 to i64, !dbg !96
  %46 = getelementptr inbounds i8*, i8** %43, i64 %45, !dbg !96
  %47 = load i8*, i8** %46, align 8, !dbg !96
  call void (i32, i32, i8*, ...) @error(i32 noundef 0, i32 noundef 0, i8* noundef getelementptr inbounds ([7 x i8], [7 x i8]* @.str.6, i64 0, i64 0), i8* noundef %42, i8* noundef %47), !dbg !98
  call void @print_help(), !dbg !99
  br label %48, !dbg !100

48:                                               ; preds = %41, %37
  %49 = call i64 @mbsrtowcs(i32* noundef null, i8** noundef %8, i64 noundef 0, %struct.__mbstate_t* noundef null) #6, !dbg !101
  store i64 %49, i64* %10, align 8, !dbg !102
  %50 = load i64, i64* %10, align 8, !dbg !103
  %51 = icmp eq i64 %50, -1, !dbg !105
  br i1 %51, label %52, label %56, !dbg !106

52:                                               ; preds = %48
  %53 = call i32* @__errno_location() #8, !dbg !107
  %54 = load i32, i32* %53, align 4, !dbg !107
  %55 = call i8* @gettext(i8* noundef getelementptr inbounds ([40 x i8], [40 x i8]* @.str.8, i64 0, i64 0)) #6, !dbg !108
  call void (i32, i32, i8*, ...) @error(i32 noundef 1, i32 noundef %54, i8* noundef %55), !dbg !109
  br label %56, !dbg !109

56:                                               ; preds = %52, %48
  %57 = load i64, i64* %10, align 8, !dbg !110
  %58 = add i64 %57, 1, !dbg !111
  %59 = mul i64 %58, 4, !dbg !112
  %60 = call noalias i8* @xmalloc(i64 noundef %59), !dbg !113
  %61 = bitcast i8* %60 to i32*, !dbg !113
  store i32* %61, i32** %9, align 8, !dbg !114
  %62 = load i32*, i32** %9, align 8, !dbg !115
  %63 = load i64, i64* %10, align 8, !dbg !116
  %64 = add i64 %63, 1, !dbg !117
  %65 = call i64 @mbsrtowcs(i32* noundef %62, i8** noundef %8, i64 noundef %64, %struct.__mbstate_t* noundef null) #6, !dbg !118
  %66 = load i32*, i32** %9, align 8, !dbg !119
  %67 = call i32 (i32*, ...) @wprintf(i32* noundef getelementptr inbounds ([5 x i32], [5 x i32]* @.str.9, i64 0, i64 0), i32* noundef %66), !dbg !120
  %68 = load i32*, i32** %9, align 8, !dbg !121
  %69 = bitcast i32* %68 to i8*, !dbg !121
  call void @free(i8* noundef %69) #6, !dbg !122
  call void @exit(i32 noundef 0) #7, !dbg !123
  unreachable, !dbg !123
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

declare void @set_program_name(i8* noundef) #2

; Function Attrs: nounwind
declare i8* @setlocale(i32 noundef, i8* noundef) #3

; Function Attrs: nounwind
declare i8* @bindtextdomain(i8* noundef, i8* noundef) #3

; Function Attrs: nounwind
declare i8* @textdomain(i8* noundef) #3

; Function Attrs: nounwind
declare i8* @gettext(i8* noundef) #3

; Function Attrs: nounwind
declare i32 @atexit(void ()* noundef) #3

declare void @close_stdout() #2

; Function Attrs: nounwind
declare i32 @getopt_long(i32 noundef, i8** noundef, i8* noundef, %struct.option* noundef, i32* noundef) #3

; Function Attrs: noinline nounwind optnone uwtable
define internal void @print_version() #0 !dbg !124 {
  %1 = call i32 (i8*, ...) @printf(i8* noundef getelementptr inbounds ([12 x i8], [12 x i8]* @.str.25, i64 0, i64 0), i8* noundef getelementptr inbounds ([6 x i8], [6 x i8]* @.str.1, i64 0, i64 0), i8* noundef getelementptr inbounds ([10 x i8], [10 x i8]* @.str.22, i64 0, i64 0), i8* noundef getelementptr inbounds ([1 x i8], [1 x i8]* @.str, i64 0, i64 0)), !dbg !127
  %2 = call i32 @puts(i8* noundef getelementptr inbounds ([1 x i8], [1 x i8]* @.str, i64 0, i64 0)), !dbg !128
  %3 = call i8* @gettext(i8* noundef getelementptr inbounds ([248 x i8], [248 x i8]* @.str.26, i64 0, i64 0)) #6, !dbg !129
  %4 = call i32 (i8*, ...) @printf(i8* noundef %3, i32 noundef 2025), !dbg !130
  ret void, !dbg !131
}

; Function Attrs: noreturn nounwind
declare void @exit(i32 noundef) #4

; Function Attrs: noinline nounwind optnone uwtable
define internal void @print_help() #0 !dbg !132 {
  %1 = call i8* @gettext(i8* noundef getelementptr inbounds ([23 x i8], [23 x i8]* @.str.14, i64 0, i64 0)) #6, !dbg !133
  %2 = load i8*, i8** @program_name, align 8, !dbg !134
  %3 = call i32 (i8*, ...) @printf(i8* noundef %1, i8* noundef %2), !dbg !135
  %4 = call i8* @gettext(i8* noundef getelementptr inbounds ([42 x i8], [42 x i8]* @.str.15, i64 0, i64 0)) #6, !dbg !136
  %5 = load %struct._IO_FILE*, %struct._IO_FILE** @stdout, align 8, !dbg !137
  %6 = call i32 @fputs(i8* noundef %4, %struct._IO_FILE* noundef %5), !dbg !138
  %7 = call i32 @puts(i8* noundef getelementptr inbounds ([1 x i8], [1 x i8]* @.str, i64 0, i64 0)), !dbg !139
  %8 = call i8* @gettext(i8* noundef getelementptr inbounds ([109 x i8], [109 x i8]* @.str.16, i64 0, i64 0)) #6, !dbg !140
  %9 = load %struct._IO_FILE*, %struct._IO_FILE** @stdout, align 8, !dbg !141
  %10 = call i32 @fputs(i8* noundef %8, %struct._IO_FILE* noundef %9), !dbg !142
  %11 = call i32 @puts(i8* noundef getelementptr inbounds ([1 x i8], [1 x i8]* @.str, i64 0, i64 0)), !dbg !143
  %12 = call i8* @gettext(i8* noundef getelementptr inbounds ([111 x i8], [111 x i8]* @.str.17, i64 0, i64 0)) #6, !dbg !144
  %13 = load %struct._IO_FILE*, %struct._IO_FILE** @stdout, align 8, !dbg !145
  %14 = call i32 @fputs(i8* noundef %12, %struct._IO_FILE* noundef %13), !dbg !146
  %15 = call i32 (i8*, ...) @printf(i8* noundef getelementptr inbounds ([2 x i8], [2 x i8]* @.str.18, i64 0, i64 0)), !dbg !147
  %16 = call i8* @gettext(i8* noundef getelementptr inbounds ([20 x i8], [20 x i8]* @.str.19, i64 0, i64 0)) #6, !dbg !148
  %17 = call i32 (i8*, ...) @printf(i8* noundef %16, i8* noundef getelementptr inbounds ([18 x i8], [18 x i8]* @.str.20, i64 0, i64 0)), !dbg !149
  %18 = call i8* @gettext(i8* noundef getelementptr inbounds ([20 x i8], [20 x i8]* @.str.21, i64 0, i64 0)) #6, !dbg !150
  %19 = call i32 (i8*, ...) @printf(i8* noundef %18, i8* noundef getelementptr inbounds ([10 x i8], [10 x i8]* @.str.22, i64 0, i64 0), i8* noundef getelementptr inbounds ([35 x i8], [35 x i8]* @.str.23, i64 0, i64 0)), !dbg !151
  %20 = call i8* @gettext(i8* noundef getelementptr inbounds ([64 x i8], [64 x i8]* @.str.24, i64 0, i64 0)) #6, !dbg !152
  %21 = load %struct._IO_FILE*, %struct._IO_FILE** @stdout, align 8, !dbg !153
  %22 = call i32 @fputs(i8* noundef %20, %struct._IO_FILE* noundef %21), !dbg !154
  ret void, !dbg !155
}

declare void @error(i32 noundef, i32 noundef, i8* noundef, ...) #2

; Function Attrs: nounwind
declare i64 @mbsrtowcs(i32* noundef, i8** noundef, i64 noundef, %struct.__mbstate_t* noundef) #3

; Function Attrs: nounwind readnone willreturn
declare i32* @__errno_location() #5

declare noalias i8* @xmalloc(i64 noundef) #2

declare i32 @wprintf(i32* noundef, ...) #2

; Function Attrs: nounwind
declare void @free(i8* noundef) #3

declare i32 @printf(i8* noundef, ...) #2

declare i32 @fputs(i8* noundef, %struct._IO_FILE* noundef) #2

declare i32 @puts(i8* noundef) #2

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { noreturn nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nounwind readnone willreturn "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { nounwind }
attributes #7 = { noreturn nounwind }
attributes #8 = { nounwind readnone willreturn }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!25, !26, !27, !28, !29, !30, !31}
!llvm.ident = !{!32}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "longopts", scope: !2, file: !3, line: 27, type: !9, isLocal: true, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C99, file: !3, producer: "Debian clang version 14.0.6", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, retainedTypes: !4, globals: !8, splitDebugInlining: false, nameTableKind: None)
!3 = !DIFile(filename: "src/hello.c", directory: "/worker/hello-2.10", checksumkind: CSK_MD5, checksum: "e2151da098bff155fedd2c15836e185d")
!4 = !{!5}
!5 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !6, line: 46, baseType: !7)
!6 = !DIFile(filename: "/usr/lib/llvm-14/lib/clang/14.0.6/include/stddef.h", directory: "", checksumkind: CSK_MD5, checksum: "2499dd2361b915724b073282bea3a7bc")
!7 = !DIBasicType(name: "unsigned long", size: 64, encoding: DW_ATE_unsigned)
!8 = !{!0}
!9 = !DICompositeType(tag: DW_TAG_array_type, baseType: !10, size: 1280, elements: !23)
!10 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !11)
!11 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "option", file: !12, line: 50, size: 256, elements: !13)
!12 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/getopt_ext.h", directory: "", checksumkind: CSK_MD5, checksum: "b4f86ba96a508c530fa381ae1dafe9eb")
!13 = !{!14, !18, !20, !22}
!14 = !DIDerivedType(tag: DW_TAG_member, name: "name", scope: !11, file: !12, line: 52, baseType: !15, size: 64)
!15 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !16, size: 64)
!16 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !17)
!17 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!18 = !DIDerivedType(tag: DW_TAG_member, name: "has_arg", scope: !11, file: !12, line: 55, baseType: !19, size: 32, offset: 64)
!19 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!20 = !DIDerivedType(tag: DW_TAG_member, name: "flag", scope: !11, file: !12, line: 56, baseType: !21, size: 64, offset: 128)
!21 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !19, size: 64)
!22 = !DIDerivedType(tag: DW_TAG_member, name: "val", scope: !11, file: !12, line: 57, baseType: !19, size: 32, offset: 192)
!23 = !{!24}
!24 = !DISubrange(count: 5)
!25 = !{i32 7, !"Dwarf Version", i32 5}
!26 = !{i32 2, !"Debug Info Version", i32 3}
!27 = !{i32 1, !"wchar_size", i32 4}
!28 = !{i32 7, !"PIC Level", i32 2}
!29 = !{i32 7, !"PIE Level", i32 2}
!30 = !{i32 7, !"uwtable", i32 1}
!31 = !{i32 7, !"frame-pointer", i32 2}
!32 = !{!"Debian clang version 14.0.6"}
!33 = distinct !DISubprogram(name: "main", scope: !3, file: !3, line: 40, type: !34, scopeLine: 41, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !2, retainedNodes: !38)
!34 = !DISubroutineType(types: !35)
!35 = !{!19, !19, !36}
!36 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !37, size: 64)
!37 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !17, size: 64)
!38 = !{}
!39 = !DILocalVariable(name: "argc", arg: 1, scope: !33, file: !3, line: 40, type: !19)
!40 = !DILocation(line: 40, column: 11, scope: !33)
!41 = !DILocalVariable(name: "argv", arg: 2, scope: !33, file: !3, line: 40, type: !36)
!42 = !DILocation(line: 40, column: 23, scope: !33)
!43 = !DILocalVariable(name: "optc", scope: !33, file: !3, line: 42, type: !19)
!44 = !DILocation(line: 42, column: 7, scope: !33)
!45 = !DILocalVariable(name: "lose", scope: !33, file: !3, line: 43, type: !19)
!46 = !DILocation(line: 43, column: 7, scope: !33)
!47 = !DILocalVariable(name: "greeting_msg", scope: !33, file: !3, line: 44, type: !15)
!48 = !DILocation(line: 44, column: 15, scope: !33)
!49 = !DILocalVariable(name: "mb_greeting", scope: !33, file: !3, line: 45, type: !50)
!50 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !51, size: 64)
!51 = !DIDerivedType(tag: DW_TAG_typedef, name: "wchar_t", file: !6, line: 74, baseType: !19)
!52 = !DILocation(line: 45, column: 12, scope: !33)
!53 = !DILocalVariable(name: "len", scope: !33, file: !3, line: 46, type: !5)
!54 = !DILocation(line: 46, column: 10, scope: !33)
!55 = !DILocation(line: 48, column: 21, scope: !33)
!56 = !DILocation(line: 48, column: 3, scope: !33)
!57 = !DILocation(line: 51, column: 3, scope: !33)
!58 = !DILocation(line: 55, column: 3, scope: !33)
!59 = !DILocation(line: 56, column: 3, scope: !33)
!60 = !DILocation(line: 60, column: 18, scope: !33)
!61 = !DILocation(line: 60, column: 16, scope: !33)
!62 = !DILocation(line: 66, column: 3, scope: !33)
!63 = !DILocation(line: 68, column: 3, scope: !33)
!64 = !DILocation(line: 68, column: 31, scope: !33)
!65 = !DILocation(line: 68, column: 37, scope: !33)
!66 = !DILocation(line: 68, column: 18, scope: !33)
!67 = !DILocation(line: 68, column: 16, scope: !33)
!68 = !DILocation(line: 68, column: 69, scope: !33)
!69 = !DILocation(line: 69, column: 13, scope: !33)
!70 = !DILocation(line: 69, column: 5, scope: !33)
!71 = !DILocation(line: 73, column: 2, scope: !72)
!72 = distinct !DILexicalBlock(scope: !33, file: !3, line: 70, column: 7)
!73 = !DILocation(line: 74, column: 2, scope: !72)
!74 = !DILocation(line: 77, column: 17, scope: !72)
!75 = !DILocation(line: 77, column: 15, scope: !72)
!76 = !DILocation(line: 78, column: 2, scope: !72)
!77 = !DILocation(line: 80, column: 2, scope: !72)
!78 = !DILocation(line: 81, column: 2, scope: !72)
!79 = !DILocation(line: 84, column: 17, scope: !72)
!80 = !DILocation(line: 84, column: 15, scope: !72)
!81 = !DILocation(line: 85, column: 2, scope: !72)
!82 = !DILocation(line: 87, column: 7, scope: !72)
!83 = !DILocation(line: 88, column: 2, scope: !72)
!84 = distinct !{!84, !63, !85, !86}
!85 = !DILocation(line: 89, column: 7, scope: !33)
!86 = !{!"llvm.loop.mustprogress"}
!87 = !DILocation(line: 91, column: 7, scope: !88)
!88 = distinct !DILexicalBlock(scope: !33, file: !3, line: 91, column: 7)
!89 = !DILocation(line: 91, column: 12, scope: !88)
!90 = !DILocation(line: 91, column: 15, scope: !88)
!91 = !DILocation(line: 91, column: 24, scope: !88)
!92 = !DILocation(line: 91, column: 22, scope: !88)
!93 = !DILocation(line: 91, column: 7, scope: !33)
!94 = !DILocation(line: 94, column: 30, scope: !95)
!95 = distinct !DILexicalBlock(scope: !88, file: !3, line: 92, column: 5)
!96 = !DILocation(line: 94, column: 50, scope: !95)
!97 = !DILocation(line: 94, column: 55, scope: !95)
!98 = !DILocation(line: 94, column: 7, scope: !95)
!99 = !DILocation(line: 95, column: 7, scope: !95)
!100 = !DILocation(line: 96, column: 5, scope: !95)
!101 = !DILocation(line: 98, column: 9, scope: !33)
!102 = !DILocation(line: 98, column: 7, scope: !33)
!103 = !DILocation(line: 99, column: 7, scope: !104)
!104 = distinct !DILexicalBlock(scope: !33, file: !3, line: 99, column: 7)
!105 = !DILocation(line: 99, column: 11, scope: !104)
!106 = !DILocation(line: 99, column: 7, scope: !33)
!107 = !DILocation(line: 100, column: 26, scope: !104)
!108 = !DILocation(line: 100, column: 33, scope: !104)
!109 = !DILocation(line: 100, column: 5, scope: !104)
!110 = !DILocation(line: 101, column: 26, scope: !33)
!111 = !DILocation(line: 101, column: 30, scope: !33)
!112 = !DILocation(line: 101, column: 35, scope: !33)
!113 = !DILocation(line: 101, column: 17, scope: !33)
!114 = !DILocation(line: 101, column: 15, scope: !33)
!115 = !DILocation(line: 102, column: 13, scope: !33)
!116 = !DILocation(line: 102, column: 41, scope: !33)
!117 = !DILocation(line: 102, column: 45, scope: !33)
!118 = !DILocation(line: 102, column: 3, scope: !33)
!119 = !DILocation(line: 105, column: 22, scope: !33)
!120 = !DILocation(line: 105, column: 3, scope: !33)
!121 = !DILocation(line: 106, column: 8, scope: !33)
!122 = !DILocation(line: 106, column: 3, scope: !33)
!123 = !DILocation(line: 108, column: 3, scope: !33)
!124 = distinct !DISubprogram(name: "print_version", scope: !3, file: !3, line: 170, type: !125, scopeLine: 171, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition, unit: !2, retainedNodes: !38)
!125 = !DISubroutineType(types: !126)
!126 = !{null}
!127 = !DILocation(line: 172, column: 3, scope: !124)
!128 = !DILocation(line: 174, column: 3, scope: !124)
!129 = !DILocation(line: 179, column: 11, scope: !124)
!130 = !DILocation(line: 179, column: 3, scope: !124)
!131 = !DILocation(line: 184, column: 1, scope: !124)
!132 = distinct !DISubprogram(name: "print_help", scope: !3, file: !3, line: 117, type: !125, scopeLine: 118, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition, unit: !2, retainedNodes: !38)
!133 = !DILocation(line: 121, column: 11, scope: !132)
!134 = !DILocation(line: 122, column: 28, scope: !132)
!135 = !DILocation(line: 121, column: 3, scope: !132)
!136 = !DILocation(line: 126, column: 10, scope: !132)
!137 = !DILocation(line: 127, column: 47, scope: !132)
!138 = !DILocation(line: 126, column: 3, scope: !132)
!139 = !DILocation(line: 129, column: 3, scope: !132)
!140 = !DILocation(line: 132, column: 10, scope: !132)
!141 = !DILocation(line: 134, column: 65, scope: !132)
!142 = !DILocation(line: 132, column: 3, scope: !132)
!143 = !DILocation(line: 136, column: 3, scope: !132)
!144 = !DILocation(line: 139, column: 10, scope: !132)
!145 = !DILocation(line: 141, column: 65, scope: !132)
!146 = !DILocation(line: 139, column: 3, scope: !132)
!147 = !DILocation(line: 143, column: 3, scope: !132)
!148 = !DILocation(line: 149, column: 11, scope: !132)
!149 = !DILocation(line: 149, column: 3, scope: !132)
!150 = !DILocation(line: 156, column: 11, scope: !132)
!151 = !DILocation(line: 156, column: 3, scope: !132)
!152 = !DILocation(line: 161, column: 10, scope: !132)
!153 = !DILocation(line: 162, column: 3, scope: !132)
!154 = !DILocation(line: 161, column: 3, scope: !132)
!155 = !DILocation(line: 163, column: 1, scope: !132)

    '''

    compilation_command = [
      "clang",
      "-DLOCALEDIR=\"/usr/share/locale\"",
      "-DHAVE_CONFIG_H",
      "-I.",
      "-Ilib",
      "-I./lib",
      "-Isrc",
      "-I./src",
      "-Wdate-time",
      "-D_FORTIFY_SOURCE=2",
      "-g",
      "-O2",
      "-ffile-prefix-map=/hello/hello-2.10=.",
      "-fstack-protector-strong",
      "-Wformat",
      "-Werror=format-security",
      "-c",
      "-o",
      "src/hello.o",
      "temp_ir_file.ll"
    ]

    directory = '/hello/hello-2.10'

    output_file = 'output.o'
    result = ir_to_o(ir, compilation_command, output_file, directory)
    print(f"Return code: {result.returncode}")
