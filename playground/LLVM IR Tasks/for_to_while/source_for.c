#include <stdio.h>

int main() {
    int x = 1;
    
    for (int i = 0; i < 10; i++) {
        x = x + x;
    }
    
    printf("x is: %d\n", x);
    
    return 0;
}