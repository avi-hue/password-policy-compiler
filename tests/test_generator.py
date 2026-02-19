"""
Unit tests for the Code Generator (Week 5)
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.generator import CodeGenerator
from compiler.ast_nodes import Program, Policy, MinLengthRule, MaxLengthRule


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


@pytest.fixture
def generator():
    """Create a code generator"""
    return CodeGenerator()


def test_generator_creation(generator):
    """Test that generator can be created"""
    assert generator is not None
    assert generator.generated_code == ""


def test_generate_from_empty_program(generator):
    """Test generating from empty program"""
    ast = Program([])
    code = generator.generate(ast)
    
    assert code is not None
    assert "import re" in code
    assert "import" in code


def test_generate_simple_policy(generator, parser, lexer):
    """Test generating code from a simple policy"""
    code_input = '''
    POLICY TestPolicy {
        MIN_LENGTH 8
    }
    '''
    
    ast = parser.parse(code_input, lexer.lexer)
    code = generator.generate(ast)
    
    # Check generated code contains expected elements
    assert 'TestpolicyValidator' in code or 'TestPolicy' in code.lower()
    assert 'def validate' in code
    assert 'MIN_LENGTH' in code or '8' in code
    assert 'import re' in code


def test_generate_class_name_conversion(generator):
    """Test class name conversion"""
    assert 'TestvalidatorValidator' in generator._to_class_name('Test').lower() or \
           'testvalidator' in generator._to_class_name('Test').lower()


def test_generate_char_class_patterns(generator):
    """Test character class pattern generation"""
    from compiler.ast_nodes import CharClass
    
    uppercase_pattern = generator._get_char_class_pattern(CharClass.UPPERCASE)
    assert '[A-Z]' in uppercase_pattern or 'A-Z' in uppercase_pattern
    
    lowercase_pattern = generator._get_char_class_pattern(CharClass.LOWERCASE)
    assert '[a-z]' in lowercase_pattern or 'a-z' in lowercase_pattern
    
    digits_pattern = generator._get_char_class_pattern(CharClass.DIGITS)
    assert '[0-9]' in digits_pattern or '0-9' in digits_pattern
    
    special_pattern = generator._get_char_class_pattern(CharClass.SPECIAL)
    assert len(special_pattern) > 0


def test_generate_with_require_rules(generator, parser, lexer):
    """Test generating code with REQUIRE rules"""
    code_input = '''
    POLICY RequirePolicy {
        REQUIRE UPPERCASE 1
        REQUIRE LOWERCASE 1
        REQUIRE DIGITS 1
        REQUIRE SPECIAL 1
    }
    '''
    
    ast = parser.parse(code_input, lexer.lexer)
    code = generator.generate(ast)
    
    # Check generated code contains character class checks
    assert 'uppercase' in code.lower() or 'UPPERCASE' in code
    assert 'lowercase' in code.lower() or 'LOWERCASE' in code
    assert 'def validate' in code


def test_generate_with_length_constraints(generator, parser, lexer):
    """Test generating code with length constraints"""
    code_input = '''
    POLICY LengthPolicy {
        MIN_LENGTH 8
        MAX_LENGTH 128
    }
    '''
    
    ast = parser.parse(code_input, lexer.lexer)
    code = generator.generate(ast)
    
    # Check for length validation code
    assert 'len(password)' in code
    assert '8' in code
    assert '128' in code


def test_generate_with_forbid_rules(generator, parser, lexer):
    """Test generating code with FORBID rules"""
    code_input = '''
    POLICY ForbidPolicy {
        FORBID REPETITION
        FORBID SEQUENTIAL
    }
    '''
    
    ast = parser.parse(code_input, lexer.lexer)
    code = generator.generate(ast)
    
    # Check for forbid rule implementations
    assert 'repetition' in code.lower() or 'REPETITION' in code
    assert 'sequential' in code.lower() or 'SEQUENTIAL' in code


def test_generate_valid_python(generator, parser, lexer):
    """Test that generated code is valid Python"""
    code_input = '''
    POLICY TestPolicy {
        MIN_LENGTH 8
    }
    '''
    
    ast = parser.parse(code_input, lexer.lexer)
    code = generator.generate(ast)
    
    # Try to compile the generated code
    try:
        compile(code, '<generated>', 'exec')
    except SyntaxError as e:
        pytest.fail(f"Generated code has syntax error: {e}")


def test_generate_multiline_output(generator, parser, lexer):
    """Test that generated code is properly formatted"""
    code_input = '''
    POLICY FormattedPolicy {
        MIN_LENGTH 8
        MAX_LENGTH 128
        REQUIRE UPPERCASE 1
    }
    '''
    
    ast = parser.parse(code_input, lexer.lexer)
    code = generator.generate(ast)
    
    lines = code.split('\n')
    assert len(lines) > 10  # Should have substantial output
    assert all(isinstance(line, str) for line in lines)


def test_generate_contains_helper_methods(generator, parser, lexer):
    """Test that generated code includes helper methods"""
    code_input = '''
    POLICY HelperPolicy {
        FORBID REPETITION
        FORBID SEQUENTIAL
    }
    '''
    
    ast = parser.parse(code_input, lexer.lexer)
    code = generator.generate(ast)
    
    # Check for helper methods
    assert '_has_repetition' in code or 'repetition' in code.lower()
    assert '_has_sequential' in code or 'sequential' in code.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
