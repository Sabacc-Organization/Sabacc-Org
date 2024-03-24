#include <string.h>


int main(void) {

    char *s = " fly me to the moon  ";

    int counter = 0;

    int notSpaceSeen = 0;

    for (int i = strlen(s) - 1; i >= 0; i--) {

        char c = s[i];

        if (notSpaceSeen == 1) {
            if (c == ' ') {
                return counter;
            }

            counter++;
        }
        else if (c != ' ') {
            notSpaceSeen = 1;
        }
    }

    // c strip
    counter = 0;
    for (int i = 0; i < strlen(s); i++) {
        if (s[i] != ' ') {
            counter++;
        }
    }

    return counter;
}