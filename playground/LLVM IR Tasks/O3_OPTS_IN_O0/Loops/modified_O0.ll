; ModuleID = 'source.c'
source_filename = "source.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [9 x i8] c"Sum: %d\0A\00", align 1

; ; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
; define i32 @sum_array_helper(i32 noundef %0, i32 noundef %1) #0 {
;   %3 = alloca i32, align 4
;   %4 = alloca i32, align 4
;   %5 = alloca i32, align 4
;   store i32 %0, ptr %3, align 4
;   store i32 %1, ptr %4, align 4
;   %6 = load i32, ptr %3, align 4
;   %7 = mul nsw i32 %6, 2
;   %8 = load i32, ptr %4, align 4
;   %9 = add nsw i32 %7, %8
;   store i32 %9, ptr %5, align 4
;   %10 = load i32, ptr %5, align 4
;   ret i32 %10
; }

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define i32 @sum_array(ptr noundef %arr, i32 noundef %n) #0 {
  %n_mod_4 = and i32 %n, 3
  %n_div_4 = lshr i32 %n, 2
  br label %sum_loop_condition

sum_loop_condition:                                                ; preds = %sum_counter_update
  %sum = phi i32 [0, %0], [%sum_updated_3, %sum_loop_body]
  %j = phi i32 [0, %0], [%j_next, %sum_loop_body]
  %curr_ptr = phi ptr [%arr, %0], [%next_ptr_3, %sum_loop_body]
  %cmp = icmp slt i32 %j, %n_div_4
  br i1 %cmp, label %sum_loop_body, label %sum_loop_exit

sum_loop_body:                                               ; preds = %sum_loop_condition
  %arr_j = load i32, ptr %curr_ptr, align 4
  %index_j = mul nsw i32 %j, 4
  %mul_result = shl nsw i32 %arr_j, 1
  %add_result = add nsw i32 %mul_result, %index_j
  %sum_updated = add nsw i32 %sum, %add_result

  %next_ptr = getelementptr inbounds i32, ptr %curr_ptr, i64 1
  %arr_j_1 = load i32, ptr %next_ptr, align 4
  %index_j_1 = add nsw i32 %index_j, 1
  %mul_result_1 = shl nsw i32 %arr_j_1, 1
  %add_result_1 = add nsw i32 %mul_result_1, %index_j_1
  %sum_updated_1 = add nsw i32 %sum_updated, %add_result_1

  %next_ptr_1 = getelementptr inbounds i32, ptr %next_ptr, i64 1
  %arr_j_2 = load i32, ptr %next_ptr_1, align 4
  %index_j_2 = add nsw i32 %index_j, 2
  %mul_result_2 = shl nsw i32 %arr_j_2, 1
  %add_result_2 = add nsw i32 %mul_result_2, %index_j_2
  %sum_updated_2 = add nsw i32 %sum_updated_1, %add_result_2

  %next_ptr_2 = getelementptr inbounds i32, ptr %next_ptr_1, i64 1
  %arr_j_3 = load i32, ptr %next_ptr_2, align 4
  %index_j_3 = add nsw i32 %index_j, 3
  %mul_result_3 = shl nsw i32 %arr_j_3, 1
  %add_result_3 = add nsw i32 %mul_result_3, %index_j_3
  %sum_updated_3 = add nsw i32 %sum_updated_2, %add_result_3

  %j_next = add nsw i32 %j, 1
  %next_ptr_3 = getelementptr inbounds i32, ptr %next_ptr_2, i64 1
  br label %sum_loop_condition


sum_loop_exit:                                               ; preds = %sum_loop_condition
  %remainder_cmp = icmp eq i32 %n_mod_4, 0
  br i1 %remainder_cmp, label %final_return, label %remainder_loop_condition

remainder_loop_condition:
  %curr_sum = phi i32 [%sum, %sum_loop_exit], [%sum_updated_remainder, %remainder_loop_body]
  %curr_i = phi i32 [%n_div_4, %sum_loop_exit], [%next_i, %remainder_loop_body]
  %curr_ptr_rem = phi ptr [%curr_ptr, %sum_loop_exit], [%next_ptr_remainder, %remainder_loop_body]
  %i_remainder = mul i32 %n_div_4, 4
  %cmp_remainder = icmp slt i32 %curr_i, %n
  br i1 %cmp_remainder, label %remainder_loop_body, label %final_return

remainder_loop_body:                                        
  %arr_val = load i32, ptr %curr_ptr_rem, align 4
  %mul_remainder = shl nsw i32 %arr_val, 1
  %add_remainder = add nsw i32 %mul_remainder, %curr_i
  %sum_updated_remainder = add nsw i32 %curr_sum, %add_remainder
  %next_i = add nsw i32 %curr_i, 1
  %next_ptr_remainder = getelementptr inbounds i32, ptr %curr_ptr_rem, i64 1
  br label %remainder_loop_condition

final_return:                                              
  %final_sum = phi i32 [%sum, %sum_loop_exit], [%curr_sum, %remainder_loop_condition]
  ret i32 %final_sum

}


; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define i32 @main() #0 {
  %arr = alloca [1000 x i32], align 4
  br label %main_loop_condition

main_loop_condition:                                                ; preds = %i_counter_update, %arr
  %i = phi i32 [0, %0], [%i_next, %loop_body]
  %cmp = icmp slt i32 %i, 996
  br i1 %cmp, label %loop_body, label %loop_exit

loop_body:                                                ; preds = %main_loop_condition
  %i_i64 = sext i32 %i to i64
  %arr_index = getelementptr inbounds [1000 x i32], ptr %arr, i64 0, i64 %i_i64
  store i32 %i, ptr %arr_index, align 4

  %i_plus_1 = add nsw i32 %i, 1
  %i_plus_1_i64 = sext i32 %i_plus_1 to i64
  %arr_index_plus_1 = getelementptr inbounds [1000 x i32], ptr %arr, i64 0, i64 %i_plus_1_i64
  store i32 %i_plus_1, ptr %arr_index_plus_1, align 4

  %i_plus_2 = add nsw i32 %i, 2
  %i_plus_2_i64 = sext i32 %i_plus_2 to i64
  %arr_index_plus_2 = getelementptr inbounds [1000 x i32], ptr %arr, i64 0, i64 %i_plus_2_i64
  store i32 %i_plus_2, ptr %arr_index_plus_2, align 4

  %i_plus_3 = add nsw i32 %i, 3
  %i_plus_3_i64 = sext i32 %i_plus_3 to i64
  %arr_index_plus_3 = getelementptr inbounds [1000 x i32], ptr %arr, i64 0, i64 %i_plus_3_i64
  store i32 %i_plus_3, ptr %arr_index_plus_3, align 4

  %i_next = add nsw i32 %i, 4
  br label %main_loop_condition

loop_exit:                                               ; preds = %main_loop_condition
  
  %arr_index_996 = getelementptr inbounds [1000 x i32], ptr %arr, i64 0, i64 996
  store i32 996, ptr %arr_index_996, align 4
  
  %arr_index_997 = getelementptr inbounds [1000 x i32], ptr %arr, i64 0, i64 997
  store i32 997, ptr %arr_index_997, align 4
  
  %arr_index_998 = getelementptr inbounds [1000 x i32], ptr %arr, i64 0, i64 998
  store i32 998, ptr %arr_index_998, align 4
  
  %arr_index_999 = getelementptr inbounds [1000 x i32], ptr %arr, i64 0, i64 999
  store i32 999, ptr %arr_index_999, align 4

  %sum_call = call i32 @sum_array(ptr noundef %arr, i32 noundef 1000)
  %20 = call i32 (ptr, ...) @printf(ptr noundef @.str, i32 noundef %sum_call)
  ret i32 0
}

declare i32 @printf(ptr noundef, ...) #1

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 19.1.1 (1ubuntu1)"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
!8 = distinct !{!8, !7}
