import zipfile

# Define the files to put inside the ZIP
files = {
    "secure_math.c": """
#include <stdio.h>
int add(int a, int b) {
    return a + b;
}
""",
    "vulnerable_buffer.c": """
#include <stdio.h>
#include <string.h>
void process_input(char *user_input) {
    char buffer[10];
    // VULNERABLE: strcpy does not check bounds
    strcpy(buffer, user_input);
    printf("Input processed: %s\\n", buffer);
}
""",
    "auth_system.cpp": """
#include <iostream>
#include <string>
bool login(std::string password) {
    // VULNERABLE: Hardcoded credentials
    if (password == "admin123") {
        return true;
    }
    return false;
}
""",
    "notes.txt": "This file should be totally ignored by the scanner since it is not C or C++."
}

# Create the ZIP file
with zipfile.ZipFile('test_repository.zip', 'w') as zf:
    for filename, content in files.items():
        zf.writestr(filename, content.strip())

print("✅ test_repository.zip created successfully on your desktop!")