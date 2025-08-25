#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

void print_hello() {
    printf("Hello, World!\n");
}

double multiply(double x, double y) {
    return x * y;
}

char get_initial() {
    return 'A';
}

int main() {
    print_hello();
    int sum = add(2, 3);
    double product = multiply(2.0, 4.5);
    char initial = get_initial();
    printf("Sum: %d, Product: %f, Initial: %c\n", sum, product, initial);
    return 0;
}