
def ir_injection(function_ir, injection_code):

    ir_lines = function_ir.splitlines()
    injection_lines = injection_code.splitlines()

    new_ir_lines = []

    for lines in ir_lines:
        new_ir_lines.append(lines)

        if lines.strip().startswith("define") and lines.strip().endswith("{"):
            for injection_line in injection_lines:
                new_ir_lines.append("  " + injection_line)

    return "\n".join(new_ir_lines)

if __name__ == "__main__":

    sample_ir = r"""
; ModuleID = '<stdin>'
source_filename = "module_compiler.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.cond_node = type { i32, %struct.cond_expr*, %struct.cond_av_list*, %struct.cond_av_list*, %struct.avrule*, %struct.avrule*, i32, [5 x i32], i32, %struct.cond_node*, i32 }
%struct.cond_expr = type { i32, i32, %struct.cond_expr* }
%struct.cond_av_list = type { %struct.avtab_node*, %struct.cond_av_list* }
%struct.avtab_node = type { %struct.avtab_key, %struct.avtab_datum, %struct.avtab_node*, i8*, i32 }
%struct.avtab_key = type { i16, i16, i16, i16 }
%struct.avtab_datum = type { i32, %struct.avtab_extended_perms* }
%struct.avtab_extended_perms = type { i8, i8, [8 x i32] }
%struct.avrule = type { i32, i32, %struct.type_set, %struct.type_set, %struct.class_perm_node*, %struct.av_extended_perms*, i64, i8*, i64, %struct.avrule* }
%struct.type_set = type { %struct.ebitmap, %struct.ebitmap, i32 }
%struct.ebitmap = type { %struct.ebitmap_node*, i32 }
%struct.ebitmap_node = type { i32, i64, %struct.ebitmap_node* }
%struct.class_perm_node = type { i32, i32, %struct.class_perm_node* }
%struct.av_extended_perms = type { i8, i8, [8 x i32] }

@.str.5 = external hidden unnamed_addr constant [18 x i8], align 1
@.str.15 = external hidden unnamed_addr constant [17 x i8], align 1
@__PRETTY_FUNCTION__.append_cond_list = external hidden unnamed_addr constant [37 x i8], align 1

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #0

; Function Attrs: noreturn nounwind
declare void @__assert_fail(i8* noundef, i8* noundef, i32 noundef, i8* noundef) #1

; Function Attrs: noinline nounwind optnone uwtable
declare dso_local %struct.cond_node* @get_current_cond_list(%struct.cond_node* noundef) #2

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @append_cond_list(%struct.cond_node* noundef %0) #2 !dbg !181 {
  %2 = alloca %struct.cond_node*, align 8
  %3 = alloca %struct.cond_node*, align 8
  %4 = alloca %struct.avrule*, align 8
  store %struct.cond_node* %0, %struct.cond_node** %2, align 8
  call void @llvm.dbg.declare(metadata %struct.cond_node** %2, metadata !286, metadata !DIExpression()), !dbg !287
  call void @llvm.dbg.declare(metadata %struct.cond_node** %3, metadata !288, metadata !DIExpression()), !dbg !289
  %5 = load %struct.cond_node*, %struct.cond_node** %2, align 8, !dbg !290
  %6 = call %struct.cond_node* @get_current_cond_list(%struct.cond_node* noundef %5), !dbg !291
  store %struct.cond_node* %6, %struct.cond_node** %3, align 8, !dbg !289
  call void @llvm.dbg.declare(metadata %struct.avrule** %4, metadata !292, metadata !DIExpression()), !dbg !293
  %7 = load %struct.cond_node*, %struct.cond_node** %3, align 8, !dbg !294
  %8 = icmp ne %struct.cond_node* %7, null, !dbg !294
  br i1 %8, label %9, label %10, !dbg !297

9:                                                ; preds = %1
  br label %11, !dbg !297

10:                                               ; preds = %1
  call void @__assert_fail(i8* noundef getelementptr inbounds ([17 x i8], [17 x i8]* @.str.15, i64 0, i64 0), i8* noundef getelementptr inbounds ([18 x i8], [18 x i8]* @.str.5, i64 0, i64 0), i32 noundef 1211, i8* noundef getelementptr inbounds ([37 x i8], [37 x i8]* @__PRETTY_FUNCTION__.append_cond_list, i64 0, i64 0)) #3, !dbg !294
  unreachable, !dbg !294

11:                                               ; preds = %9
  %12 = load %struct.cond_node*, %struct.cond_node** %3, align 8, !dbg !298
  %13 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %12, i32 0, i32 4, !dbg !300
  %14 = load %struct.avrule*, %struct.avrule** %13, align 8, !dbg !300
  %15 = icmp eq %struct.avrule* %14, null, !dbg !301
  br i1 %15, label %16, label %22, !dbg !302

16:                                               ; preds = %11
  %17 = load %struct.cond_node*, %struct.cond_node** %2, align 8, !dbg !303
  %18 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %17, i32 0, i32 4, !dbg !305
  %19 = load %struct.avrule*, %struct.avrule** %18, align 8, !dbg !305
  %20 = load %struct.cond_node*, %struct.cond_node** %3, align 8, !dbg !306
  %21 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %20, i32 0, i32 4, !dbg !307
  store %struct.avrule* %19, %struct.avrule** %21, align 8, !dbg !308
  br label %42, !dbg !309

22:                                               ; preds = %11
  %23 = load %struct.cond_node*, %struct.cond_node** %3, align 8, !dbg !310
  %24 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %23, i32 0, i32 4, !dbg !313
  %25 = load %struct.avrule*, %struct.avrule** %24, align 8, !dbg !313
  store %struct.avrule* %25, %struct.avrule** %4, align 8, !dbg !314
  br label %26, !dbg !315

26:                                               ; preds = %32, %22
  %27 = load %struct.avrule*, %struct.avrule** %4, align 8, !dbg !316
  %28 = getelementptr inbounds %struct.avrule, %struct.avrule* %27, i32 0, i32 9, !dbg !318
  %29 = load %struct.avrule*, %struct.avrule** %28, align 8, !dbg !318
  %30 = icmp ne %struct.avrule* %29, null, !dbg !319
  br i1 %30, label %31, label %36, !dbg !320

31:                                               ; preds = %26
  br label %32, !dbg !320

32:                                               ; preds = %31
  %33 = load %struct.avrule*, %struct.avrule** %4, align 8, !dbg !321
  %34 = getelementptr inbounds %struct.avrule, %struct.avrule* %33, i32 0, i32 9, !dbg !322
  %35 = load %struct.avrule*, %struct.avrule** %34, align 8, !dbg !322
  store %struct.avrule* %35, %struct.avrule** %4, align 8, !dbg !323
  br label %26, !dbg !324, !llvm.loop !325

36:                                               ; preds = %26
  %37 = load %struct.cond_node*, %struct.cond_node** %2, align 8, !dbg !328
  %38 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %37, i32 0, i32 4, !dbg !329
  %39 = load %struct.avrule*, %struct.avrule** %38, align 8, !dbg !329
  %40 = load %struct.avrule*, %struct.avrule** %4, align 8, !dbg !330
  %41 = getelementptr inbounds %struct.avrule, %struct.avrule* %40, i32 0, i32 9, !dbg !331
  store %struct.avrule* %39, %struct.avrule** %41, align 8, !dbg !332
  br label %42

42:                                               ; preds = %36, %16
  %43 = load %struct.cond_node*, %struct.cond_node** %3, align 8, !dbg !333
  %44 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %43, i32 0, i32 5, !dbg !335
  %45 = load %struct.avrule*, %struct.avrule** %44, align 8, !dbg !335
  %46 = icmp eq %struct.avrule* %45, null, !dbg !336
  br i1 %46, label %47, label %53, !dbg !337

47:                                               ; preds = %42
  %48 = load %struct.cond_node*, %struct.cond_node** %2, align 8, !dbg !338
  %49 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %48, i32 0, i32 5, !dbg !340
  %50 = load %struct.avrule*, %struct.avrule** %49, align 8, !dbg !340
  %51 = load %struct.cond_node*, %struct.cond_node** %3, align 8, !dbg !341
  %52 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %51, i32 0, i32 5, !dbg !342
  store %struct.avrule* %50, %struct.avrule** %52, align 8, !dbg !343
  br label %73, !dbg !344

53:                                               ; preds = %42
  %54 = load %struct.cond_node*, %struct.cond_node** %3, align 8, !dbg !345
  %55 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %54, i32 0, i32 5, !dbg !348
  %56 = load %struct.avrule*, %struct.avrule** %55, align 8, !dbg !348
  store %struct.avrule* %56, %struct.avrule** %4, align 8, !dbg !349
  br label %57, !dbg !350

57:                                               ; preds = %63, %53
  %58 = load %struct.avrule*, %struct.avrule** %4, align 8, !dbg !351
  %59 = getelementptr inbounds %struct.avrule, %struct.avrule* %58, i32 0, i32 9, !dbg !353
  %60 = load %struct.avrule*, %struct.avrule** %59, align 8, !dbg !353
  %61 = icmp ne %struct.avrule* %60, null, !dbg !354
  br i1 %61, label %62, label %67, !dbg !355

62:                                               ; preds = %57
  br label %63, !dbg !355

63:                                               ; preds = %62
  %64 = load %struct.avrule*, %struct.avrule** %4, align 8, !dbg !356
  %65 = getelementptr inbounds %struct.avrule, %struct.avrule* %64, i32 0, i32 9, !dbg !357
  %66 = load %struct.avrule*, %struct.avrule** %65, align 8, !dbg !357
  store %struct.avrule* %66, %struct.avrule** %4, align 8, !dbg !358
  br label %57, !dbg !359, !llvm.loop !360

67:                                               ; preds = %57
  %68 = load %struct.cond_node*, %struct.cond_node** %2, align 8, !dbg !362
  %69 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %68, i32 0, i32 5, !dbg !363
  %70 = load %struct.avrule*, %struct.avrule** %69, align 8, !dbg !363
  %71 = load %struct.avrule*, %struct.avrule** %4, align 8, !dbg !364
  %72 = getelementptr inbounds %struct.avrule, %struct.avrule* %71, i32 0, i32 9, !dbg !365
  store %struct.avrule* %70, %struct.avrule** %72, align 8, !dbg !366
  br label %73

73:                                               ; preds = %67, %47
  %74 = load %struct.cond_node*, %struct.cond_node** %2, align 8, !dbg !367
  %75 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %74, i32 0, i32 10, !dbg !368
  %76 = load i32, i32* %75, align 8, !dbg !368
  %77 = load %struct.cond_node*, %struct.cond_node** %3, align 8, !dbg !369
  %78 = getelementptr inbounds %struct.cond_node, %struct.cond_node* %77, i32 0, i32 10, !dbg !370
  %79 = load i32, i32* %78, align 8, !dbg !371
  %80 = or i32 %79, %76, !dbg !371
  store i32 %80, i32* %78, align 8, !dbg !371
  ret void, !dbg !372
}

"""

    nop_code = "%nop_temp = add i32 0, 0"

    result = ir_injection(sample_ir, nop_code)
    print(result)