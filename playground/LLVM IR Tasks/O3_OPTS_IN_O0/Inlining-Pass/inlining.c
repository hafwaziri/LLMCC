#include <stdio.h>

int mul(int x, int y) {
    return x*y;
}

int main() {

    int a = 10;
    int b = 2;
    int c = mul(a,b);

    printf("c is: %d\n", c);

    return 0;
}