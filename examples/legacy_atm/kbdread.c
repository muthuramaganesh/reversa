/* Unbuffered keyboard read used for PIN entry (masks echo). */
#include <stdio.h>
#include <termios.h>
#include <unistd.h>

int KBDREAD(char *out) {
    struct termios oldt, newt;
    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    for (int i = 0; i < 4; i++) {
        int c = getchar();
        if (c < '0' || c > '9') { i--; continue; }
        out[i] = (char)c;
        putchar('*');
    }
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    return 0;
}
