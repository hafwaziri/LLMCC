#include <stdio.h>

#define SIZE 1000

int sum_array_helper(int arr_j,int j) {
    int z = arr_j * 2 + j;
    return z;
}

int sum_array(int *arr, int n) {
    int sum = 0;
    for (int j = 0; j < n; ++j) {
        sum += sum_array_helper(arr[j], j);
    }
    return sum;
    printf("This is deadcode\n");
}

int main() {
    int data[SIZE];
    for (int i = 0; i < SIZE; ++i) {
        data[i] = i;
    }

    int result = sum_array(data, SIZE);
    printf("Sum: %d\n", result);
    return 0;
}
