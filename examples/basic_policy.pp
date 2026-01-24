# Basic Password Policy
# This is a comment

POLICY UserPasswordPolicy {
    MIN_LENGTH 8
    MAX_LENGTH 128
    
    REQUIRE UPPERCASE 1
    REQUIRE LOWERCASE 1
    REQUIRE DIGITS 1
    REQUIRE SPECIAL 1
    
    BLACKLIST "common_passwords.txt"
    FORBID USERNAME
}
