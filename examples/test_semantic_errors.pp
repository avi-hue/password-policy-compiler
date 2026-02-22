# Test policy - valid syntax but semantic errors

POLICY BadPolicy {
    MIN_LENGTH 20
    MAX_LENGTH 10
    REQUIRE UPPERCASE 5
}
