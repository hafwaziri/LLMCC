; ModuleID = 'source.c'
source_filename = "source.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@__const.main.source = private unnamed_addr constant [62 x i8] c"A long string that has the potential to cause buffer overflow\00", align 16
@.str = private unnamed_addr constant [12 x i8] c"Source: %s\0A\00", align 1
@.str.1 = private unnamed_addr constant [17 x i8] c"Destination: %s\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca [62 x i8], align 16
  %3 = alloca [10 x i8], align 1
  store i32 0, ptr %1, align 4
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %2, ptr align 16 @__const.main.source, i64 62, i1 false)
  %4 = getelementptr inbounds [62 x i8], ptr %2, i64 0, i64 0
  %5 = call i32 (ptr, ...) @printf(ptr noundef @.str, ptr noundef %4)
  %6 = getelementptr inbounds [10 x i8], ptr %3, i64 0, i64 0
  %7 = getelementptr inbounds [62 x i8], ptr %2, i64 0, i64 0
  %8 = call ptr @strncpy(ptr noundef %6, ptr noundef %7, i64 noundef 9) #4
  %9 = getelementptr inbounds [10 x i8], ptr %3, i64 0, i64 9
  store i8 0, ptr %9, align 1
  %10 = getelementptr inbounds [10 x i8], ptr %3, i64 0, i64 0
  %11 = call i32 (ptr, ...) @printf(ptr noundef @.str.1, ptr noundef %10)
  ret i32 0
}

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #1

declare i32 @printf(ptr noundef, ...) #2

; Function Attrs: nounwind
declare ptr @strncpy(ptr noundef, ptr noundef, i64 noundef) #3

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 19.1.1 (1ubuntu1)"}
