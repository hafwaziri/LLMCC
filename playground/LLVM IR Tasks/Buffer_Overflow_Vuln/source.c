#include <stdio.h>
#include <string.h>


int main() {

	char source[] = "A long string that has the potential to cause buffer overflow";
	char dest[10];

	printf("Source: %s\n", source);

	strncpy(dest, source, sizeof(dest) - 1);
	dest[sizeof(dest) - 1] = '\0';

	printf("Destination: %s\n", dest);

	return 0;
}
