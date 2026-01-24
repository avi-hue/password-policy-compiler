"""
Unit tests for the Lexer
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from compiler.lexer import Lexer


def test_lexer_creation():
    """Test that lexer can be created and built"""
    lexer = Lexer()
    lexer.build()
    assert lexer.lexer is not None


def test_keywords():
    """Test recognition of reserved keywords"""
    lexer = Lexer()
    lexer.build()
    
    keywords = ['POLICY', 'MIN_LENGTH', 'MAX_LENGTH', 'REQUIRE', 
                'BLACKLIST', 'FORBID', 'UPPERCASE', 'LOWERCASE', 
                'DIGITS', 'SPECIAL', 'USERNAME']
    
    for keyword in keywords:
        tokens = lexer.tokenize(keyword)
        assert len(tokens) == 1
        assert tokens[0].type == keyword


def test_numbers():
    """Test number token recognition"""
    lexer = Lexer()
    lexer.build()
    
    tokens = lexer.tokenize('8 12 128 999')
    assert len(tokens) == 4
    assert all(t.type == 'NUMBER' for t in tokens)
    assert [t.value for t in tokens] == [8, 12, 128, 999]


def test_strings():
    """Test string token recognition"""
    lexer = Lexer()
    lexer.build()
    
    tokens = lexer.tokenize('"test.txt" "another_file.txt"')
    assert len(tokens) == 2
    assert all(t.type == 'STRING' for t in tokens)
    assert tokens[0].value == 'test.txt'
    assert tokens[1].value == 'another_file.txt'


def test_identifiers():
    """Test identifier recognition"""
    lexer = Lexer()
    lexer.build()
    
    tokens = lexer.tokenize('MyPolicy user_password test123')
    assert len(tokens) == 3
    assert all(t.type == 'IDENTIFIER' for t in tokens)


def test_braces():
    """Test brace recognition"""
    lexer = Lexer()
    lexer.build()
    
    tokens = lexer.tokenize('{ }')
    assert len(tokens) == 2
    assert tokens[0].type == 'LBRACE'
    assert tokens[1].type == 'RBRACE'


def test_comments():
    """Test that comments are ignored"""
    lexer = Lexer()
    lexer.build()
    
    code = '''
    # This is a comment
    POLICY Test {
        # Another comment
        MIN_LENGTH 8
    }
    '''
    
    tokens = lexer.tokenize(code)
    # Should not include comment tokens
    assert all(t.type != 'COMMENT' for t in tokens)


def test_complete_policy():
    """Test tokenization of complete policy"""
    lexer = Lexer()
    lexer.build()
    
    policy = '''
    POLICY StrongPassword {
        MIN_LENGTH 12
        REQUIRE UPPERCASE 1
        FORBID USERNAME
    }
    '''
    
    tokens = lexer.tokenize(policy)
    
    expected_types = [
        'POLICY', 'IDENTIFIER', 'LBRACE',
        'MIN_LENGTH', 'NUMBER',
        'REQUIRE', 'UPPERCASE', 'NUMBER',
        'FORBID', 'USERNAME',
        'RBRACE'
    ]
    
    actual_types = [t.type for t in tokens]
    assert actual_types == expected_types


def test_line_numbers():
    """Test that line numbers are tracked correctly"""
    lexer = Lexer()
    lexer.build()
    
    code = '''POLICY Test {
    MIN_LENGTH 8
}'''
    
    tokens = lexer.tokenize(code)
    assert tokens[0].lineno == 1  # POLICY
    assert tokens[3].lineno == 2  # MIN_LENGTH
    assert tokens[5].lineno == 3  # }


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
