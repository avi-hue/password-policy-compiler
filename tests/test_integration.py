"""
Integration tests for the Password Policy Compiler (Week 6)
Tests the full pipeline: Lexer -> Parser -> Generator -> Validator
"""

import pytest
import sys
from pathlib import Path
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.generator import CodeGenerator
from compiler.validators import PasswordValidator, PolicyTest


@pytest.fixture
def full_pipeline():
    """Create lexer, parser, and generator"""
    lexer = Lexer()
    lexer.build()
    
    parser = Parser()
    parser.build()
    
    generator = CodeGenerator()
    
    return lexer, parser, generator


def test_full_pipeline_basic(full_pipeline):
    """Test complete pipeline with basic policy"""
    lexer, parser, generator = full_pipeline
    
    policy_code = '''
    POLICY BasicPassword {
        MIN_LENGTH 8
        REQUIRE UPPERCASE 1
        REQUIRE LOWERCASE 1
        REQUIRE DIGITS 1
    }
    '''
    
    # Lex
    tokens = lexer.tokenize(policy_code)
    assert len(tokens) > 0
    assert not any(t.type == 'ERROR' for t in tokens)
    
    # Parse
    ast = parser.parse(policy_code, lexer.lexer)
    assert ast is not None
    assert len(ast.policies) == 1
    
    # Generate
    code = generator.generate(ast)
    assert code is not None
    assert len(code) > 0
    
    # Validate generated code is syntactically correct
    try:
        compile(code, '<generated>', 'exec')
    except SyntaxError as e:
        pytest.fail(f"Generated code syntax error: {e}")


def test_full_pipeline_complex(full_pipeline):
    """Test complete pipeline with complex policy"""
    lexer, parser, generator = full_pipeline
    
    policy_code = '''
    POLICY EnterprisePassword {
        MIN_LENGTH 16
        MAX_LENGTH 128
        
        REQUIRE UPPERCASE 2
        REQUIRE LOWERCASE 2
        REQUIRE DIGITS 2
        REQUIRE SPECIAL 2
        
        BLACKLIST "passwords/common.txt"
        FORBID USERNAME
        FORBID REPETITION
        FORBID SEQUENTIAL
    }
    '''
    
    # Full pipeline
    tokens = lexer.tokenize(policy_code)
    assert len(tokens) > 0
    
    ast = parser.parse(policy_code, lexer.lexer)
    assert ast is not None
    assert len(ast.policies[0].rules) > 8
    
    code = generator.generate(ast)
    assert 'EnterprisePassword' in code or 'enterprise' in code.lower()
    assert '16' in code
    assert '128' in code


def test_full_pipeline_multiple_policies(full_pipeline):
    """Test pipeline with multiple policies"""
    lexer, parser, generator = full_pipeline
    
    policy_code = '''
    POLICY StrictPolicy {
        MIN_LENGTH 16
        REQUIRE UPPERCASE 2
        FORBID REPETITION
    }
    
    POLICY ModeratePolicy {
        MIN_LENGTH 12
        REQUIRE UPPERCASE 1
    }
    
    POLICY WeakPolicy {
        MIN_LENGTH 8
    }
    '''
    
    # Full pipeline
    tokens = lexer.tokenize(policy_code)
    ast = parser.parse(policy_code, lexer.lexer)
    assert len(ast.policies) == 3
    
    code = generator.generate(ast)
    assert len(code) > 0
    
    # Should generate validators for all policies
    for policy in ast.policies:
        policy_name_lower = policy.name.lower()
        assert policy_name_lower in code.lower()


def test_generated_code_execution(full_pipeline):
    """Test that generated code can actually execute"""
    lexer, parser, generator = full_pipeline
    
    policy_code = '''
    POLICY ExecutablePolicy {
        MIN_LENGTH 8
    }
    '''
    
    ast = parser.parse(policy_code, lexer.lexer)
    code = generator.generate(ast)
    
    # Try to execute the generated code
    namespace = {}
    try:
        exec(code, namespace)
        # Check that the validator class was created
        assert any('validator' in name.lower() for name in namespace.keys())
    except Exception as e:
        pytest.fail(f"Generated code failed to execute: {e}")


def test_validator_with_test_harness(full_pipeline):
    """Test validator with PolicyTest harness"""
    
    # Create a simple test validator
    class SimpleValidator(PasswordValidator):
        def validate(self, password: str, username: str = None):
            is_valid, msg = self.check_length(password, min_length=8)
            if not is_valid:
                return is_valid, msg
            
            is_valid, msg = self.check_character_class(password, 'uppercase', 1)
            if not is_valid:
                return is_valid, msg
            
            return True, "Valid"
    
    validator = SimpleValidator()
    tester = PolicyTest(validator)
    
    # Run tests
    test_cases = [
        {'password': 'ValidPass', 'should_pass': True},
        {'password': 'short', 'should_pass': False},
        {'password': 'nouppercase', 'should_pass': False},
    ]
    
    passed, total = tester.run_tests(test_cases)
    assert total == 3
    assert passed >= 2  # At least 2 tests should pass


def test_end_to_end_no_errors(full_pipeline):
    """Test that full pipeline completes without errors"""
    lexer, parser, generator = full_pipeline
    
    policies = [
        'POLICY Test1 { MIN_LENGTH 8 }',
        'POLICY Test2 { MAX_LENGTH 128 REQUIRE UPPERCASE 1 }',
        'POLICY Test3 { FORBID REPETITION FORBID SEQUENTIAL }',
    ]
    
    for policy_code in policies:
        tokens = lexer.tokenize(policy_code)
        assert len(lexer.errors) == 0
        
        ast = parser.parse(policy_code, lexer.lexer)
        assert ast is not None
        assert len(parser.errors) == 0
        
        code = generator.generate(ast)
        assert code is not None
        assert len(generator.errors) == 0


def test_pipeline_with_file_io(full_pipeline):
    """Test pipeline with file I/O"""
    lexer, parser, generator = full_pipeline
    
    policy_code = '''
    POLICY FilePolicy {
        MIN_LENGTH 10
        REQUIRE LOWERCASE 1
    }
    '''
    
    # Generate code
    ast = parser.parse(policy_code, lexer.lexer)
    code = generator.generate(ast)
    
    # Try to write to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Verify file was written
        assert os.path.exists(temp_file)
        
        # Read and verify content
        with open(temp_file, 'r') as f:
            content = f.read()
        
        assert len(content) > 0
        assert 'FilePolicy' in content or 'filepolicy' in content.lower()
        
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_error_recovery(full_pipeline):
    """Test that pipeline handles errors gracefully"""
    lexer, parser, generator = full_pipeline
    
    # Invalid policy (missing rules)
    policy_code = 'POLICY InvalidPolicy { }'
    
    tokens = lexer.tokenize(policy_code)
    ast = parser.parse(policy_code, lexer.lexer)
    
    # Should still generate code, even with empty rules
    if ast:
        code = generator.generate(ast)
        assert code is not None


def test_performance_many_policies(full_pipeline):
    """Test performance with many policies"""
    lexer, parser, generator = full_pipeline
    
    # Generate many policies
    policies = '\n'.join([
        f'POLICY Policy{i} {{ MIN_LENGTH {8+i} }}'
        for i in range(20)
    ])
    
    # Should handle without issues
    tokens = lexer.tokenize(policies)
    assert len(tokens) > 0
    
    ast = parser.parse(policies, lexer.lexer)
    assert ast is not None
    assert len(ast.policies) == 20
    
    code = generator.generate(ast)
    assert code is not None
    assert len(code) > 1000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
