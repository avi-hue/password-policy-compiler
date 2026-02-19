# Enterprise-grade password policy

POLICY EnterprisePassword {
    MIN_LENGTH 16
    MAX_LENGTH 128
    
    REQUIRE UPPERCASE 2
    REQUIRE LOWERCASE 2
    REQUIRE DIGITS 2
    REQUIRE SPECIAL 2
    
    BLACKLIST "dictionaries/common_10000.txt"
    FORBID USERNAME
    FORBID REPETITION
    FORBID SEQUENTIAL
}
