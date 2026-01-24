"""
Token Recognition Demo
Demonstrates how tokens are identified from source code
"""

from tokens import tokens, reserved, Token


def demonstrate_tokens():
    """Show examples of each token type"""
    
    sample_policy = '''
    POLICY StrongPassword {
        MIN_LENGTH 12
        MAX_LENGTH 64
        REQUIRE UPPERCASE 2
        REQUIRE LOWERCASE 2
        REQUIRE DIGITS 2
        REQUIRE SPECIAL 1
        BLACKLIST "common_passwords.txt"
        FORBID USERNAME
    }
    '''
    
    print("=" * 70)
    print("TOKEN RECOGNITION DEMONSTRATION")
    print("=" * 70)
    print("\nSample Policy:")
    print("-" * 70)
    print(sample_policy)
    print("-" * 70)
    
    print("\nIdentified Tokens:")
    print("-" * 70)
    
    # Manual token identification for demo
    demo_tokens = [
        Token('POLICY', 'POLICY', 2, 5),
        Token('IDENTIFIER', 'StrongPassword', 2, 12),
        Token('LBRACE', '{', 2, 27),
        Token('MIN_LENGTH', 'MIN_LENGTH', 3, 9),
        Token('NUMBER', '12', 3, 20),
        Token('MAX_LENGTH', 'MAX_LENGTH', 4, 9),
        Token('NUMBER', '64', 4, 20),
        Token('REQUIRE', 'REQUIRE', 5, 9),
        Token('UPPERCASE', 'UPPERCASE', 5, 17),
        Token('NUMBER', '2', 5, 27),
        Token('REQUIRE', 'REQUIRE', 6, 9),
        Token('LOWERCASE', 'LOWERCASE', 6, 17),
        Token('NUMBER', '2', 6, 27),
        Token('REQUIRE', 'REQUIRE', 7, 9),
        Token('DIGITS', 'DIGITS', 7, 17),
        Token('NUMBER', '2', 7, 24),
        Token('REQUIRE', 'REQUIRE', 8, 9),
        Token('SPECIAL', 'SPECIAL', 8, 17),
        Token('NUMBER', '1', 8, 25),
        Token('BLACKLIST', 'BLACKLIST', 9, 9),
        Token('STRING', '"common_passwords.txt"', 9, 19),
        Token('FORBID', 'FORBID', 10, 9),
        Token('USERNAME', 'USERNAME', 10, 16),
        Token('RBRACE', '}', 11, 5),
    ]
    
    for token in demo_tokens:
        print(token)
    
    print("-" * 70)
    print(f"\nTotal tokens: {len(demo_tokens)}")
    print(f"Reserved keywords used: {len([t for t in demo_tokens if t.type in reserved])}")
    print(f"Identifiers: {len([t for t in demo_tokens if t.type == 'IDENTIFIER'])}")
    print(f"Numbers: {len([t for t in demo_tokens if t.type == 'NUMBER'])}")
    
    print("\n" + "=" * 70)
    print("SUPPORTED TOKEN TYPES:")
    print("=" * 70)
    for token in tokens:
        print(f"  - {token}")


if __name__ == '__main__':
    demonstrate_tokens()
