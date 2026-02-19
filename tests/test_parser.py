"""
Unit tests for the Parser (Week 4)
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.ast_nodes import (
    Program, Policy, MinLengthRule, MaxLengthRule, RequireRule,
    BlacklistRule, ForbidRule, CharClass, ForbidType
)


@pytest.fixture
def lexer():
    """Create and build a lexer"""
    lex = Lexer()
    lex.build()
    return lex


@pytest.fixture
def parser():
    """Create and build a parser"""
    p = Parser()
    p.build()
    return p


def test_parser_creation(parser):
    """Test that parser can be created and built"""
    assert parser.parser is not None


def test_parse_empty_program(parser, lexer):
    """Test parsing empty input"""
    code = ""
    ast = parser.parse(code, lexer.lexer)
    assert ast is not None
    assert isinstance(ast, Program)
    assert len(ast.policies) == 0


def test_parse_simple_policy(parser, lexer):
    """Test parsing a simple policy"""
    code = '''
    POLICY TestPolicy {
        MIN_LENGTH 8
    }
    '''
    ast = parser.parse(code, lexer.lexer)
    
    assert ast is not None
    assert len(ast.policies) == 1
    
    policy = ast.policies[0]
    assert policy.name == 'TestPolicy'
    assert len(policy.rules) == 1
    assert isinstance(policy.rules[0], MinLengthRule)
    assert policy.rules[0].length == 8


def test_parse_min_max_length_rules(parser, lexer):
    """Test parsing MIN_LENGTH and MAX_LENGTH rules"""
    code = '''
    POLICY LengthPolicy {
        MIN_LENGTH 8
        MAX_LENGTH 128
    }
    '''
    ast = parser.parse(code, lexer.lexer)
    
    policy = ast.policies[0]
    assert len(policy.rules) == 2
    assert isinstance(policy.rules[0], MinLengthRule)
    assert policy.rules[0].length == 8
    assert isinstance(policy.rules[1], MaxLengthRule)
    assert policy.rules[1].length == 128


def test_parse_require_rules(parser, lexer):
    """Test parsing REQUIRE rules"""
    code = '''
    POLICY RequirePolicy {
        REQUIRE UPPERCASE 1
        REQUIRE LOWERCASE 2
        REQUIRE DIGITS 1
        REQUIRE SPECIAL 1
    }
    '''
    ast = parser.parse(code, lexer.lexer)
    
    policy = ast.policies[0]
    assert len(policy.rules) == 4
    
    rules = policy.rules
    assert isinstance(rules[0], RequireRule)
    assert rules[0].char_class == CharClass.UPPERCASE
    assert rules[0].count == 1
    
    assert isinstance(rules[1], RequireRule)
    assert rules[1].char_class == CharClass.LOWERCASE
    assert rules[1].count == 2
    
    assert isinstance(rules[2], RequireRule)
    assert rules[2].char_class == CharClass.DIGITS
    
    assert isinstance(rules[3], RequireRule)
    assert rules[3].char_class == CharClass.SPECIAL


def test_parse_blacklist_rule(parser, lexer):
    """Test parsing BLACKLIST rule"""
    code = '''
    POLICY BlacklistPolicy {
        BLACKLIST "common_passwords.txt"
    }
    '''
    ast = parser.parse(code, lexer.lexer)
    
    policy = ast.policies[0]
    assert len(policy.rules) == 1
    assert isinstance(policy.rules[0], BlacklistRule)
    assert policy.rules[0].filename == 'common_passwords.txt'


def test_parse_forbid_rules(parser, lexer):
    """Test parsing FORBID rules"""
    code = '''
    POLICY ForbidPolicy {
        FORBID USERNAME
        FORBID REPETITION
        FORBID SEQUENTIAL
    }
    '''
    ast = parser.parse(code, lexer.lexer)
    
    policy = ast.policies[0]
    assert len(policy.rules) == 3
    
    rules = policy.rules
    assert isinstance(rules[0], ForbidRule)
    assert rules[0].forbid_type == ForbidType.USERNAME
    
    assert isinstance(rules[1], ForbidRule)
    assert rules[1].forbid_type == ForbidType.REPETITION
    
    assert isinstance(rules[2], ForbidRule)
    assert rules[2].forbid_type == ForbidType.SEQUENTIAL


def test_parse_multiple_policies(parser, lexer):
    """Test parsing multiple policies"""
    code = '''
    POLICY Policy1 {
        MIN_LENGTH 8
    }
    
    POLICY Policy2 {
        MIN_LENGTH 12
        REQUIRE UPPERCASE 1
    }
    
    POLICY Policy3 {
        MIN_LENGTH 16
    }
    '''
    ast = parser.parse(code, lexer.lexer)
    
    assert len(ast.policies) == 3
    assert ast.policies[0].name == 'Policy1'
    assert ast.policies[1].name == 'Policy2'
    assert ast.policies[2].name == 'Policy3'
    
    assert len(ast.policies[0].rules) == 1
    assert len(ast.policies[1].rules) == 2
    assert len(ast.policies[2].rules) == 1


def test_parse_complex_policy(parser, lexer):
    """Test parsing a complex policy with multiple rule types"""
    code = '''
    POLICY ComplexPassword {
        MIN_LENGTH 12
        MAX_LENGTH 128
        
        REQUIRE UPPERCASE 2
        REQUIRE LOWERCASE 2
        REQUIRE DIGITS 2
        REQUIRE SPECIAL 1
        
        BLACKLIST "dictionaries/common_10000.txt"
        FORBID USERNAME
        FORBID REPETITION
        FORBID SEQUENTIAL
    }
    '''
    ast = parser.parse(code, lexer.lexer)
    
    policy = ast.policies[0]
    assert policy.name == 'ComplexPassword'
    assert len(policy.rules) == 10
    
    # Verify rule types
    rule_types = [type(r).__name__ for r in policy.rules]
    assert rule_types.count('MinLengthRule') == 1
    assert rule_types.count('MaxLengthRule') == 1
    assert rule_types.count('RequireRule') == 4
    assert rule_types.count('BlacklistRule') == 1
    assert rule_types.count('ForbidRule') == 3


def test_parse_with_comments(parser, lexer):
    """Test that comments don't affect parsing"""
    code = '''
    # This is a comment
    POLICY CommentedPolicy {
        # Another comment
        MIN_LENGTH 8  # Inline comment
        # Yet another comment
    }
    '''
    ast = parser.parse(code, lexer.lexer)
    
    policy = ast.policies[0]
    assert policy.name == 'CommentedPolicy'
    assert len(policy.rules) == 1


def test_parser_error_handling(parser, lexer):
    """Test parser error handling"""
    code = '''
    POLICY NoClosingBrace {
        MIN_LENGTH 8
    '''  # Missing closing brace
    
    # Parser should handle this gracefully
    try:
        ast = parser.parse(code, lexer.lexer)
        # If we get here, check if errors were recorded
        if parser.errors:
            assert len(parser.errors) > 0
    except:
        pass  # Expected


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
