import tempfile
import subprocess
import os

def ir_linker(source_ir, modified_function_ir, function_name):

    try:
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.ll', delete=False) as source_file, \
            tempfile.NamedTemporaryFile(mode='w+', suffix='.ll', delete=False) as func_file, \
            tempfile.NamedTemporaryFile(mode='r', suffix='.ll', delete=False) as output_file:

            source_file.write(source_ir)
            source_file.flush()
            func_file.write(modified_function_ir)
            func_file.flush()
            source_file_path = source_file.name
            func_file_path = func_file.name
            output_file_path = output_file.name
            output_file.close()

            extract_command = [
                "llvm-extract",
                "--delete",
                "--func=" + function_name,
                source_file_path,
                "-o",
                source_file_path
            ]
            result = subprocess.run(extract_command)

            if result.returncode != 0:
                return None

            link_command = [
                "llvm-link",
                "-S",
                source_file_path,
                func_file_path,
                "-o",
                output_file_path]
            result = subprocess.run(link_command)

            if result.returncode != 0:
                return None

            with open(output_file_path, 'r') as f:
                merged_ir = f.read()
            return merged_ir

    except Exception as e:
        return None
    finally:
        for path in [source_file_path, func_file_path, output_file_path]:
            os.remove(path)

if __name__ == "__main__":

    source_ir = r"""
; ModuleID = 'lib/close-stream.c'
source_filename = "lib/close-stream.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct._IO_FILE = type { i32, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, %struct._IO_marker*, %struct._IO_FILE*, i32, i32, i64, i16, i8, [1 x i8], i8*, i64, %struct._IO_codecvt*, %struct._IO_wide_data*, %struct._IO_FILE*, i8*, i64, i32, [20 x i8] }
%struct._IO_marker = type opaque
%struct._IO_codecvt = type opaque
%struct._IO_wide_data = type opaque

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @close_stream(%struct._IO_FILE* noundef %0) #0 !dbg !10 {
  %2 = alloca i32, align 4
  %3 = alloca %struct._IO_FILE*, align 8
  %4 = alloca i8, align 1
  %5 = alloca i8, align 1
  %6 = alloca i8, align 1
  store %struct._IO_FILE* %0, %struct._IO_FILE** %3, align 8
  call void @llvm.dbg.declare(metadata %struct._IO_FILE** %3, metadata !77, metadata !DIExpression()), !dbg !78
  call void @llvm.dbg.declare(metadata i8* %4, metadata !79, metadata !DIExpression()), !dbg !82
  %7 = load %struct._IO_FILE*, %struct._IO_FILE** %3, align 8, !dbg !83
  %8 = call i64 @__fpending(%struct._IO_FILE* noundef %7) #5, !dbg !84
  %9 = icmp ne i64 %8, 0, !dbg !85
  %10 = zext i1 %9 to i8, !dbg !82
  store i8 %10, i8* %4, align 1, !dbg !82
  call void @llvm.dbg.declare(metadata i8* %5, metadata !86, metadata !DIExpression()), !dbg !87
  %11 = load %struct._IO_FILE*, %struct._IO_FILE** %3, align 8, !dbg !88
  %12 = call i32 @ferror(%struct._IO_FILE* noundef %11) #5, !dbg !89
  %13 = icmp ne i32 %12, 0, !dbg !90
  %14 = zext i1 %13 to i8, !dbg !87
  store i8 %14, i8* %5, align 1, !dbg !87
  call void @llvm.dbg.declare(metadata i8* %6, metadata !91, metadata !DIExpression()), !dbg !92
  %15 = load %struct._IO_FILE*, %struct._IO_FILE** %3, align 8, !dbg !93
  %16 = call i32 @fclose(%struct._IO_FILE* noundef %15), !dbg !94
  %17 = icmp ne i32 %16, 0, !dbg !95
  %18 = zext i1 %17 to i8, !dbg !92
  store i8 %18, i8* %6, align 1, !dbg !92
  %19 = load i8, i8* %5, align 1, !dbg !96
  %20 = trunc i8 %19 to i1, !dbg !96
  br i1 %20, label %31, label %21, !dbg !98

21:                                               ; preds = %1
  %22 = load i8, i8* %6, align 1, !dbg !99
  %23 = trunc i8 %22 to i1, !dbg !99
  br i1 %23, label %24, label %37, !dbg !100

24:                                               ; preds = %21
  %25 = load i8, i8* %4, align 1, !dbg !101
  %26 = trunc i8 %25 to i1, !dbg !101
  br i1 %26, label %31, label %27, !dbg !102

27:                                               ; preds = %24
  %28 = call i32* @__errno_location() #6, !dbg !103
  %29 = load i32, i32* %28, align 4, !dbg !103
  %30 = icmp ne i32 %29, 9, !dbg !104
  br i1 %30, label %31, label %37, !dbg !105

31:                                               ; preds = %27, %24, %1
  %32 = load i8, i8* %6, align 1, !dbg !106
  %33 = trunc i8 %32 to i1, !dbg !106
  br i1 %33, label %36, label %34, !dbg !109

34:                                               ; preds = %31
  %35 = call i32* @__errno_location() #6, !dbg !110
  store i32 0, i32* %35, align 4, !dbg !111
  br label %36, !dbg !110

36:                                               ; preds = %34, %31
  store i32 -1, i32* %2, align 4, !dbg !112
  br label %38, !dbg !112

37:                                               ; preds = %27, %21
  store i32 0, i32* %2, align 4, !dbg !113
  br label %38, !dbg !113

38:                                               ; preds = %37, %36
  %39 = load i32, i32* %2, align 4, !dbg !114
  ret i32 %39, !dbg !114
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: nounwind
declare i64 @__fpending(%struct._IO_FILE* noundef) #2

; Function Attrs: nounwind
declare i32 @ferror(%struct._IO_FILE* noundef) #2

declare i32 @fclose(%struct._IO_FILE* noundef) #3

; Function Attrs: nounwind readnone willreturn
declare i32* @__errno_location() #4

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind readnone willreturn "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nounwind }
attributes #6 = { nounwind readnone willreturn }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5, !6, !7, !8}
!llvm.ident = !{!9}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "Debian clang version 14.0.6", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "lib/close-stream.c", directory: "/worker/hello-2.10", checksumkind: CSK_MD5, checksum: "8f8fbb85b7bb5c062722c0d134bcfe6b")
!2 = !{i32 7, !"Dwarf Version", i32 5}
!3 = !{i32 2, !"Debug Info Version", i32 3}
!4 = !{i32 1, !"wchar_size", i32 4}
!5 = !{i32 7, !"PIC Level", i32 2}
!6 = !{i32 7, !"PIE Level", i32 2}
!7 = !{i32 7, !"uwtable", i32 1}
!8 = !{i32 7, !"frame-pointer", i32 2}
!9 = !{!"Debian clang version 14.0.6"}
!10 = distinct !DISubprogram(name: "close_stream", scope: !1, file: !1, line: 56, type: !11, scopeLine: 57, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !76)
!11 = !DISubroutineType(types: !12)
!12 = !{!13, !14}
!13 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!14 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !15, size: 64)
!15 = !DIDerivedType(tag: DW_TAG_typedef, name: "FILE", file: !16, line: 7, baseType: !17)
!16 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types/FILE.h", directory: "", checksumkind: CSK_MD5, checksum: "571f9fb6223c42439075fdde11a0de5d")
!17 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "_IO_FILE", file: !18, line: 49, size: 1728, elements: !19)
!18 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types/struct_FILE.h", directory: "", checksumkind: CSK_MD5, checksum: "1bad07471b7974df4ecc1d1c2ca207e6")
!19 = !{!20, !21, !24, !25, !26, !27, !28, !29, !30, !31, !32, !33, !34, !37, !39, !40, !41, !45, !47, !49, !53, !56, !58, !61, !64, !65, !67, !71, !72}
!20 = !DIDerivedType(tag: DW_TAG_member, name: "_flags", scope: !17, file: !18, line: 51, baseType: !13, size: 32)
!21 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_read_ptr", scope: !17, file: !18, line: 54, baseType: !22, size: 64, offset: 64)
!22 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !23, size: 64)
!23 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!24 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_read_end", scope: !17, file: !18, line: 55, baseType: !22, size: 64, offset: 128)
!25 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_read_base", scope: !17, file: !18, line: 56, baseType: !22, size: 64, offset: 192)
!26 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_write_base", scope: !17, file: !18, line: 57, baseType: !22, size: 64, offset: 256)
!27 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_write_ptr", scope: !17, file: !18, line: 58, baseType: !22, size: 64, offset: 320)
!28 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_write_end", scope: !17, file: !18, line: 59, baseType: !22, size: 64, offset: 384)
!29 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_buf_base", scope: !17, file: !18, line: 60, baseType: !22, size: 64, offset: 448)
!30 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_buf_end", scope: !17, file: !18, line: 61, baseType: !22, size: 64, offset: 512)
!31 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_save_base", scope: !17, file: !18, line: 64, baseType: !22, size: 64, offset: 576)
!32 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_backup_base", scope: !17, file: !18, line: 65, baseType: !22, size: 64, offset: 640)
!33 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_save_end", scope: !17, file: !18, line: 66, baseType: !22, size: 64, offset: 704)
!34 = !DIDerivedType(tag: DW_TAG_member, name: "_markers", scope: !17, file: !18, line: 68, baseType: !35, size: 64, offset: 768)
!35 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !36, size: 64)
!36 = !DICompositeType(tag: DW_TAG_structure_type, name: "_IO_marker", file: !18, line: 36, flags: DIFlagFwdDecl)
!37 = !DIDerivedType(tag: DW_TAG_member, name: "_chain", scope: !17, file: !18, line: 70, baseType: !38, size: 64, offset: 832)
!38 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !17, size: 64)
!39 = !DIDerivedType(tag: DW_TAG_member, name: "_fileno", scope: !17, file: !18, line: 72, baseType: !13, size: 32, offset: 896)
!40 = !DIDerivedType(tag: DW_TAG_member, name: "_flags2", scope: !17, file: !18, line: 73, baseType: !13, size: 32, offset: 928)
!41 = !DIDerivedType(tag: DW_TAG_member, name: "_old_offset", scope: !17, file: !18, line: 74, baseType: !42, size: 64, offset: 960)
!42 = !DIDerivedType(tag: DW_TAG_typedef, name: "__off_t", file: !43, line: 152, baseType: !44)
!43 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types.h", directory: "", checksumkind: CSK_MD5, checksum: "d108b5f93a74c50510d7d9bc0ab36df9")
!44 = !DIBasicType(name: "long", size: 64, encoding: DW_ATE_signed)
!45 = !DIDerivedType(tag: DW_TAG_member, name: "_cur_column", scope: !17, file: !18, line: 77, baseType: !46, size: 16, offset: 1024)
!46 = !DIBasicType(name: "unsigned short", size: 16, encoding: DW_ATE_unsigned)
!47 = !DIDerivedType(tag: DW_TAG_member, name: "_vtable_offset", scope: !17, file: !18, line: 78, baseType: !48, size: 8, offset: 1040)
!48 = !DIBasicType(name: "signed char", size: 8, encoding: DW_ATE_signed_char)
!49 = !DIDerivedType(tag: DW_TAG_member, name: "_shortbuf", scope: !17, file: !18, line: 79, baseType: !50, size: 8, offset: 1048)
!50 = !DICompositeType(tag: DW_TAG_array_type, baseType: !23, size: 8, elements: !51)
!51 = !{!52}
!52 = !DISubrange(count: 1)
!53 = !DIDerivedType(tag: DW_TAG_member, name: "_lock", scope: !17, file: !18, line: 81, baseType: !54, size: 64, offset: 1088)
!54 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !55, size: 64)
!55 = !DIDerivedType(tag: DW_TAG_typedef, name: "_IO_lock_t", file: !18, line: 43, baseType: null)
!56 = !DIDerivedType(tag: DW_TAG_member, name: "_offset", scope: !17, file: !18, line: 89, baseType: !57, size: 64, offset: 1152)
!57 = !DIDerivedType(tag: DW_TAG_typedef, name: "__off64_t", file: !43, line: 153, baseType: !44)
!58 = !DIDerivedType(tag: DW_TAG_member, name: "_codecvt", scope: !17, file: !18, line: 91, baseType: !59, size: 64, offset: 1216)
!59 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !60, size: 64)
!60 = !DICompositeType(tag: DW_TAG_structure_type, name: "_IO_codecvt", file: !18, line: 37, flags: DIFlagFwdDecl)
!61 = !DIDerivedType(tag: DW_TAG_member, name: "_wide_data", scope: !17, file: !18, line: 92, baseType: !62, size: 64, offset: 1280)
!62 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !63, size: 64)
!63 = !DICompositeType(tag: DW_TAG_structure_type, name: "_IO_wide_data", file: !18, line: 38, flags: DIFlagFwdDecl)
!64 = !DIDerivedType(tag: DW_TAG_member, name: "_freeres_list", scope: !17, file: !18, line: 93, baseType: !38, size: 64, offset: 1344)
!65 = !DIDerivedType(tag: DW_TAG_member, name: "_freeres_buf", scope: !17, file: !18, line: 94, baseType: !66, size: 64, offset: 1408)
!66 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!67 = !DIDerivedType(tag: DW_TAG_member, name: "__pad5", scope: !17, file: !18, line: 95, baseType: !68, size: 64, offset: 1472)
!68 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !69, line: 46, baseType: !70)
!69 = !DIFile(filename: "/usr/lib/llvm-14/lib/clang/14.0.6/include/stddef.h", directory: "", checksumkind: CSK_MD5, checksum: "2499dd2361b915724b073282bea3a7bc")
!70 = !DIBasicType(name: "unsigned long", size: 64, encoding: DW_ATE_unsigned)
!71 = !DIDerivedType(tag: DW_TAG_member, name: "_mode", scope: !17, file: !18, line: 96, baseType: !13, size: 32, offset: 1536)
!72 = !DIDerivedType(tag: DW_TAG_member, name: "_unused2", scope: !17, file: !18, line: 98, baseType: !73, size: 160, offset: 1568)
!73 = !DICompositeType(tag: DW_TAG_array_type, baseType: !23, size: 160, elements: !74)
!74 = !{!75}
!75 = !DISubrange(count: 20)
!76 = !{}
!77 = !DILocalVariable(name: "stream", arg: 1, scope: !10, file: !1, line: 56, type: !14)
!78 = !DILocation(line: 56, column: 21, scope: !10)
!79 = !DILocalVariable(name: "some_pending", scope: !10, file: !1, line: 58, type: !80)
!80 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !81)
!81 = !DIBasicType(name: "_Bool", size: 8, encoding: DW_ATE_boolean)
!82 = !DILocation(line: 58, column: 14, scope: !10)
!83 = !DILocation(line: 58, column: 42, scope: !10)
!84 = !DILocation(line: 58, column: 30, scope: !10)
!85 = !DILocation(line: 58, column: 50, scope: !10)
!86 = !DILocalVariable(name: "prev_fail", scope: !10, file: !1, line: 59, type: !80)
!87 = !DILocation(line: 59, column: 14, scope: !10)
!88 = !DILocation(line: 59, column: 35, scope: !10)
!89 = !DILocation(line: 59, column: 27, scope: !10)
!90 = !DILocation(line: 59, column: 43, scope: !10)
!91 = !DILocalVariable(name: "fclose_fail", scope: !10, file: !1, line: 60, type: !80)
!92 = !DILocation(line: 60, column: 14, scope: !10)
!93 = !DILocation(line: 60, column: 37, scope: !10)
!94 = !DILocation(line: 60, column: 29, scope: !10)
!95 = !DILocation(line: 60, column: 45, scope: !10)
!96 = !DILocation(line: 70, column: 7, scope: !97)
!97 = distinct !DILexicalBlock(scope: !10, file: !1, line: 70, column: 7)
!98 = !DILocation(line: 70, column: 17, scope: !97)
!99 = !DILocation(line: 70, column: 21, scope: !97)
!100 = !DILocation(line: 70, column: 33, scope: !97)
!101 = !DILocation(line: 70, column: 37, scope: !97)
!102 = !DILocation(line: 70, column: 50, scope: !97)
!103 = !DILocation(line: 70, column: 53, scope: !97)
!104 = !DILocation(line: 70, column: 59, scope: !97)
!105 = !DILocation(line: 70, column: 7, scope: !10)
!106 = !DILocation(line: 72, column: 13, scope: !107)
!107 = distinct !DILexicalBlock(scope: !108, file: !1, line: 72, column: 11)
!108 = distinct !DILexicalBlock(scope: !97, file: !1, line: 71, column: 5)
!109 = !DILocation(line: 72, column: 11, scope: !108)
!110 = !DILocation(line: 73, column: 9, scope: !107)
!111 = !DILocation(line: 73, column: 15, scope: !107)
!112 = !DILocation(line: 74, column: 7, scope: !108)
!113 = !DILocation(line: 77, column: 3, scope: !10)
!114 = !DILocation(line: 78, column: 1, scope: !10)

    """

    modified_function_ir = r"""
; ModuleID = '<stdin>'
source_filename = "lib/close-stream.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct._IO_FILE = type { i32, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, %struct._IO_marker*, %struct._IO_FILE*, i32, i32, i64, i16, i8, [1 x i8], i8*, i64, %struct._IO_codecvt*, %struct._IO_wide_data*, %struct._IO_FILE*, i8*, i64, i32, [20 x i8] }
%struct._IO_marker = type opaque
%struct._IO_codecvt = type opaque
%struct._IO_wide_data = type opaque

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @close_stream(%struct._IO_FILE* noundef %0) #0 !dbg !10 {
  %2 = alloca i32, align 4
  %3 = alloca %struct._IO_FILE*, align 8
  %4 = alloca i8, align 1
  %5 = alloca i8, align 1
  %6 = alloca i8, align 1
  store %struct._IO_FILE* %0, %struct._IO_FILE** %3, align 8
  call void @llvm.dbg.declare(metadata %struct._IO_FILE** %3, metadata !77, metadata !DIExpression()), !dbg !78
  call void @llvm.dbg.declare(metadata i8* %4, metadata !79, metadata !DIExpression()), !dbg !82
  %7 = load %struct._IO_FILE*, %struct._IO_FILE** %3, align 8, !dbg !83
  %8 = call i64 @__fpending(%struct._IO_FILE* noundef %7) #5, !dbg !84
  %9 = icmp ne i64 %8, 0, !dbg !85
  %10 = zext i1 %9 to i8, !dbg !82
  store i8 %10, i8* %4, align 1, !dbg !82
  call void @llvm.dbg.declare(metadata i8* %5, metadata !86, metadata !DIExpression()), !dbg !87
  %11 = load %struct._IO_FILE*, %struct._IO_FILE** %3, align 8, !dbg !88
  %12 = call i32 @ferror(%struct._IO_FILE* noundef %11) #5, !dbg !89
  %13 = icmp ne i32 %12, 0, !dbg !90
  %14 = zext i1 %13 to i8, !dbg !87
  store i8 %14, i8* %5, align 1, !dbg !87
  call void @llvm.dbg.declare(metadata i8* %6, metadata !91, metadata !DIExpression()), !dbg !92
  %15 = load %struct._IO_FILE*, %struct._IO_FILE** %3, align 8, !dbg !93
  %16 = call i32 @fclose(%struct._IO_FILE* noundef %15), !dbg !94
  %17 = icmp ne i32 %16, 0, !dbg !95
  %18 = zext i1 %17 to i8, !dbg !92
  store i8 %18, i8* %6, align 1, !dbg !92
  %19 = load i8, i8* %5, align 1, !dbg !96
  %20 = trunc i8 %19 to i1, !dbg !96
  br i1 %20, label %31, label %21, !dbg !98

21:                                               ; preds = %1
  %22 = load i8, i8* %6, align 1, !dbg !99
  %23 = trunc i8 %22 to i1, !dbg !99
  br i1 %23, label %24, label %37, !dbg !100

24:                                               ; preds = %21
  %25 = load i8, i8* %4, align 1, !dbg !101
  %26 = trunc i8 %25 to i1, !dbg !101
  br i1 %26, label %31, label %27, !dbg !102

27:                                               ; preds = %24
  %28 = call i32* @__errno_location() #6, !dbg !103
  %29 = load i32, i32* %28, align 4, !dbg !103
  %30 = icmp ne i32 %29, 9, !dbg !104
  br i1 %30, label %31, label %37, !dbg !105

31:                                               ; preds = %27, %24, %1
  %32 = load i8, i8* %6, align 1, !dbg !106
  %33 = trunc i8 %32 to i1, !dbg !106
  br i1 %33, label %36, label %34, !dbg !109

34:                                               ; preds = %31
  %35 = call i32* @__errno_location() #6, !dbg !110
  store i32 0, i32* %35, align 4, !dbg !111
  br label %36, !dbg !110

36:                                               ; preds = %34, %31
  store i32 -1, i32* %2, align 4, !dbg !112
  br label %38, !dbg !112

37:                                               ; preds = %27, %21
  store i32 0, i32* %2, align 4, !dbg !113
  br label %38, !dbg !113

38:                                               ; preds = %37, %36
  %39 = load i32, i32* %2, align 4, !dbg !114
  ret i32 %39, !dbg !114
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: nounwind
declare i64 @__fpending(%struct._IO_FILE* noundef) #2

; Function Attrs: nounwind
declare i32 @ferror(%struct._IO_FILE* noundef) #2

declare i32 @fclose(%struct._IO_FILE* noundef) #3

; Function Attrs: nounwind readnone willreturn
declare i32* @__errno_location() #4

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind readnone willreturn "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nounwind }
attributes #6 = { nounwind readnone willreturn }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5, !6, !7, !8}
!llvm.ident = !{!9}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "Debian clang version 14.0.6", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "lib/close-stream.c", directory: "/worker/hello-2.10", checksumkind: CSK_MD5, checksum: "8f8fbb85b7bb5c062722c0d134bcfe6b")
!2 = !{i32 7, !"Dwarf Version", i32 5}
!3 = !{i32 2, !"Debug Info Version", i32 3}
!4 = !{i32 1, !"wchar_size", i32 4}
!5 = !{i32 7, !"PIC Level", i32 2}
!6 = !{i32 7, !"PIE Level", i32 2}
!7 = !{i32 7, !"uwtable", i32 1}
!8 = !{i32 7, !"frame-pointer", i32 2}
!9 = !{!"Debian clang version 14.0.6"}
!10 = distinct !DISubprogram(name: "close_stream", scope: !1, file: !1, line: 56, type: !11, scopeLine: 57, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !76)
!11 = !DISubroutineType(types: !12)
!12 = !{!13, !14}
!13 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!14 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !15, size: 64)
!15 = !DIDerivedType(tag: DW_TAG_typedef, name: "FILE", file: !16, line: 7, baseType: !17)
!16 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types/FILE.h", directory: "", checksumkind: CSK_MD5, checksum: "571f9fb6223c42439075fdde11a0de5d")
!17 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "_IO_FILE", file: !18, line: 49, size: 1728, elements: !19)
!18 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types/struct_FILE.h", directory: "", checksumkind: CSK_MD5, checksum: "1bad07471b7974df4ecc1d1c2ca207e6")
!19 = !{!20, !21, !24, !25, !26, !27, !28, !29, !30, !31, !32, !33, !34, !37, !39, !40, !41, !45, !47, !49, !53, !56, !58, !61, !64, !65, !67, !71, !72}
!20 = !DIDerivedType(tag: DW_TAG_member, name: "_flags", scope: !17, file: !18, line: 51, baseType: !13, size: 32)
!21 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_read_ptr", scope: !17, file: !18, line: 54, baseType: !22, size: 64, offset: 64)
!22 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !23, size: 64)
!23 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!24 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_read_end", scope: !17, file: !18, line: 55, baseType: !22, size: 64, offset: 128)
!25 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_read_base", scope: !17, file: !18, line: 56, baseType: !22, size: 64, offset: 192)
!26 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_write_base", scope: !17, file: !18, line: 57, baseType: !22, size: 64, offset: 256)
!27 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_write_ptr", scope: !17, file: !18, line: 58, baseType: !22, size: 64, offset: 320)
!28 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_write_end", scope: !17, file: !18, line: 59, baseType: !22, size: 64, offset: 384)
!29 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_buf_base", scope: !17, file: !18, line: 60, baseType: !22, size: 64, offset: 448)
!30 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_buf_end", scope: !17, file: !18, line: 61, baseType: !22, size: 64, offset: 512)
!31 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_save_base", scope: !17, file: !18, line: 64, baseType: !22, size: 64, offset: 576)
!32 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_backup_base", scope: !17, file: !18, line: 65, baseType: !22, size: 64, offset: 640)
!33 = !DIDerivedType(tag: DW_TAG_member, name: "_IO_save_end", scope: !17, file: !18, line: 66, baseType: !22, size: 64, offset: 704)
!34 = !DIDerivedType(tag: DW_TAG_member, name: "_markers", scope: !17, file: !18, line: 68, baseType: !35, size: 64, offset: 768)
!35 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !36, size: 64)
!36 = !DICompositeType(tag: DW_TAG_structure_type, name: "_IO_marker", file: !18, line: 36, flags: DIFlagFwdDecl)
!37 = !DIDerivedType(tag: DW_TAG_member, name: "_chain", scope: !17, file: !18, line: 70, baseType: !38, size: 64, offset: 832)
!38 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !17, size: 64)
!39 = !DIDerivedType(tag: DW_TAG_member, name: "_fileno", scope: !17, file: !18, line: 72, baseType: !13, size: 32, offset: 896)
!40 = !DIDerivedType(tag: DW_TAG_member, name: "_flags2", scope: !17, file: !18, line: 73, baseType: !13, size: 32, offset: 928)
!41 = !DIDerivedType(tag: DW_TAG_member, name: "_old_offset", scope: !17, file: !18, line: 74, baseType: !42, size: 64, offset: 960)
!42 = !DIDerivedType(tag: DW_TAG_typedef, name: "__off_t", file: !43, line: 152, baseType: !44)
!43 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types.h", directory: "", checksumkind: CSK_MD5, checksum: "d108b5f93a74c50510d7d9bc0ab36df9")
!44 = !DIBasicType(name: "long", size: 64, encoding: DW_ATE_signed)
!45 = !DIDerivedType(tag: DW_TAG_member, name: "_cur_column", scope: !17, file: !18, line: 77, baseType: !46, size: 16, offset: 1024)
!46 = !DIBasicType(name: "unsigned short", size: 16, encoding: DW_ATE_unsigned)
!47 = !DIDerivedType(tag: DW_TAG_member, name: "_vtable_offset", scope: !17, file: !18, line: 78, baseType: !48, size: 8, offset: 1040)
!48 = !DIBasicType(name: "signed char", size: 8, encoding: DW_ATE_signed_char)
!49 = !DIDerivedType(tag: DW_TAG_member, name: "_shortbuf", scope: !17, file: !18, line: 79, baseType: !50, size: 8, offset: 1048)
!50 = !DICompositeType(tag: DW_TAG_array_type, baseType: !23, size: 8, elements: !51)
!51 = !{!52}
!52 = !DISubrange(count: 1)
!53 = !DIDerivedType(tag: DW_TAG_member, name: "_lock", scope: !17, file: !18, line: 81, baseType: !54, size: 64, offset: 1088)
!54 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !55, size: 64)
!55 = !DIDerivedType(tag: DW_TAG_typedef, name: "_IO_lock_t", file: !18, line: 43, baseType: null)
!56 = !DIDerivedType(tag: DW_TAG_member, name: "_offset", scope: !17, file: !18, line: 89, baseType: !57, size: 64, offset: 1152)
!57 = !DIDerivedType(tag: DW_TAG_typedef, name: "__off64_t", file: !43, line: 153, baseType: !44)
!58 = !DIDerivedType(tag: DW_TAG_member, name: "_codecvt", scope: !17, file: !18, line: 91, baseType: !59, size: 64, offset: 1216)
!59 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !60, size: 64)
!60 = !DICompositeType(tag: DW_TAG_structure_type, name: "_IO_codecvt", file: !18, line: 37, flags: DIFlagFwdDecl)
!61 = !DIDerivedType(tag: DW_TAG_member, name: "_wide_data", scope: !17, file: !18, line: 92, baseType: !62, size: 64, offset: 1280)
!62 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !63, size: 64)
!63 = !DICompositeType(tag: DW_TAG_structure_type, name: "_IO_wide_data", file: !18, line: 38, flags: DIFlagFwdDecl)
!64 = !DIDerivedType(tag: DW_TAG_member, name: "_freeres_list", scope: !17, file: !18, line: 93, baseType: !38, size: 64, offset: 1344)
!65 = !DIDerivedType(tag: DW_TAG_member, name: "_freeres_buf", scope: !17, file: !18, line: 94, baseType: !66, size: 64, offset: 1408)
!66 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!67 = !DIDerivedType(tag: DW_TAG_member, name: "__pad5", scope: !17, file: !18, line: 95, baseType: !68, size: 64, offset: 1472)
!68 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !69, line: 46, baseType: !70)
!69 = !DIFile(filename: "/usr/lib/llvm-14/lib/clang/14.0.6/include/stddef.h", directory: "", checksumkind: CSK_MD5, checksum: "2499dd2361b915724b073282bea3a7bc")
!70 = !DIBasicType(name: "unsigned long", size: 64, encoding: DW_ATE_unsigned)
!71 = !DIDerivedType(tag: DW_TAG_member, name: "_mode", scope: !17, file: !18, line: 96, baseType: !13, size: 32, offset: 1536)
!72 = !DIDerivedType(tag: DW_TAG_member, name: "_unused2", scope: !17, file: !18, line: 98, baseType: !73, size: 160, offset: 1568)
!73 = !DICompositeType(tag: DW_TAG_array_type, baseType: !23, size: 160, elements: !74)
!74 = !{!75}
!75 = !DISubrange(count: 20)
!76 = !{}
!77 = !DILocalVariable(name: "stream", arg: 1, scope: !10, file: !1, line: 56, type: !14)
!78 = !DILocation(line: 56, column: 21, scope: !10)
!79 = !DILocalVariable(name: "some_pending", scope: !10, file: !1, line: 58, type: !80)
!80 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !81)
!81 = !DIBasicType(name: "_Bool", size: 8, encoding: DW_ATE_boolean)
!82 = !DILocation(line: 58, column: 14, scope: !10)
!83 = !DILocation(line: 58, column: 42, scope: !10)
!84 = !DILocation(line: 58, column: 30, scope: !10)
!85 = !DILocation(line: 58, column: 50, scope: !10)
!86 = !DILocalVariable(name: "prev_fail", scope: !10, file: !1, line: 59, type: !80)
!87 = !DILocation(line: 59, column: 14, scope: !10)
!88 = !DILocation(line: 59, column: 35, scope: !10)
!89 = !DILocation(line: 59, column: 27, scope: !10)
!90 = !DILocation(line: 59, column: 43, scope: !10)
!91 = !DILocalVariable(name: "fclose_fail", scope: !10, file: !1, line: 60, type: !80)
!92 = !DILocation(line: 60, column: 14, scope: !10)
!93 = !DILocation(line: 60, column: 37, scope: !10)
!94 = !DILocation(line: 60, column: 29, scope: !10)
!95 = !DILocation(line: 60, column: 45, scope: !10)
!96 = !DILocation(line: 70, column: 7, scope: !97)
!97 = distinct !DILexicalBlock(scope: !10, file: !1, line: 70, column: 7)
!98 = !DILocation(line: 70, column: 17, scope: !97)
!99 = !DILocation(line: 70, column: 21, scope: !97)
!100 = !DILocation(line: 70, column: 33, scope: !97)
!101 = !DILocation(line: 70, column: 37, scope: !97)
!102 = !DILocation(line: 70, column: 50, scope: !97)
!103 = !DILocation(line: 70, column: 53, scope: !97)
!104 = !DILocation(line: 70, column: 59, scope: !97)
!105 = !DILocation(line: 70, column: 7, scope: !10)
!106 = !DILocation(line: 72, column: 13, scope: !107)
!107 = distinct !DILexicalBlock(scope: !108, file: !1, line: 72, column: 11)
!108 = distinct !DILexicalBlock(scope: !97, file: !1, line: 71, column: 5)
!109 = !DILocation(line: 72, column: 11, scope: !108)
!110 = !DILocation(line: 73, column: 9, scope: !107)
!111 = !DILocation(line: 73, column: 15, scope: !107)
!112 = !DILocation(line: 74, column: 7, scope: !108)
!113 = !DILocation(line: 77, column: 3, scope: !10)
!114 = !DILocation(line: 78, column: 1, scope: !10)

    """

    function_name = "close_stream"

    merged_ir = ir_linker(source_ir, modified_function_ir, function_name)
    print(merged_ir)