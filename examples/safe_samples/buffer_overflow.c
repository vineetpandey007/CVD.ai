#include <string.h>

void copy_name(char *user) {
    char buf[32];
    strncpy(buf, user, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';
}
