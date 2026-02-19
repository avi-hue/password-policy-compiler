"""
Code Generator for Password Policy Language
Converts AST to Python validation code
"""

import re
from .ast_nodes import (
    Program, Policy, MinLengthRule, MaxLengthRule, RequireRule,
    BlacklistRule, ForbidRule, CharClass, ForbidType
)


class CodeGenerator:
    """Generates Python validation code from AST"""
    
    def __init__(self):
        self.generated_code = ""
        self.errors = []
    
    def generate(self, ast):
        """Generate Python code from AST"""
        if not isinstance(ast, Program):
            self.errors.append("Expected Program node")
            return ""
        
        self.generated_code = ""
        self._emit_header()
        
        for policy in ast.policies:
            self._generate_policy(policy)
        
        self._emit_main()
        return self.generated_code
    
    def _emit(self, code="", indent=0):
        """Emit code with indentation"""
        if code:
            self.generated_code += "    " * indent + code + "\n"
        else:
            self.generated_code += "\n"
    
    def _emit_header(self):
        """Emit file header"""
        self._emit('"""')
        self._emit('Auto-generated password validators from policy compiler')
        self._emit('"""')
        self._emit()
        self._emit('import re')
        self._emit('from typing import Tuple')
        self._emit()
    
    def _generate_policy(self, policy):
        """Generate validator class for a policy"""
        class_name = self._to_class_name(policy.name)
        
        self._emit()
        self._emit(f'class {class_name}:')
        self._emit('"""Password validator for {} policy"""'.format(policy.name), 1)
        self._emit()
        
        # Generate __init__
        self._emit('def __init__(self):', 1)
        self._emit('"""Initialize validator"""', 2)
        for rule in policy.rules:
            if isinstance(rule, BlacklistRule):
                self._emit(f'self.blacklist_file = "{rule.filename}"', 2)
        self._emit('pass', 2) if not any(isinstance(r, BlacklistRule) for r in policy.rules) else None
        
        self._emit()
        
        # Generate validate method
        self._emit('def validate(self, password: str) -> Tuple[bool, str]:', 1)
        self._emit('"""', 2)
        self._emit('Validate a password against this policy', 2)
        self._emit('Returns: (is_valid, error_message)', 2)
        self._emit('"""', 2)
        
        for rule in policy.rules:            
            if isinstance(rule, MinLengthRule):
                self._emit(f'# Minimum length: {rule.length}', 2)
                self._emit(f'if len(password) < {rule.length}:', 2)
                self._emit(f'return False, "Password must be at least {rule.length} characters"', 3)
            
            elif isinstance(rule, MaxLengthRule):
                self._emit(f'# Maximum length: {rule.length}', 2)
                self._emit(f'if len(password) > {rule.length}:', 2)
                self._emit(f'return False, "Password must not exceed {rule.length} characters"', 3)
            
            elif isinstance(rule, RequireRule):
                pattern = self._get_char_class_pattern(rule.char_class)
                self._emit(f'# Require {rule.count} {rule.char_class.lower()} character(s)', 2)
                self._emit(f'count = len(re.findall(r"{pattern}", password))', 2)
                self._emit(f'if count < {rule.count}:', 2)
                self._emit(f'return False, "Password must contain at least {rule.count} {rule.char_class.lower()} character(s)"', 3)
            
            elif isinstance(rule, ForbidRule):
                self._emit(f'# Forbid {rule.forbid_type.lower()}', 2)
                if rule.forbid_type == ForbidType.USERNAME:
                    self._emit('# Username check would be performed with context', 2)
                    self._emit('# For now, we skip this check', 2)
                elif rule.forbid_type == ForbidType.REPETITION:
                    self._emit('if self._has_repetition(password):', 2)
                    self._emit('return False, "Password contains repeated characters"', 3)
                elif rule.forbid_type == ForbidType.SEQUENTIAL:
                    self._emit('if self._has_sequential(password):', 2)
                    self._emit('return False, "Password contains sequential characters"', 3)
            
            elif isinstance(rule, BlacklistRule):
                self._emit(f'# Blacklist check: {rule.filename}', 2)
                self._emit('# Would check against blacklist file at runtime', 2)
        
        self._emit()
        self._emit('return True, "Password is valid"', 2)
        
        # Generate helper methods
        self._generate_helper_methods()
    
    def _generate_helper_methods(self):
        """Generate helper validation methods"""
        self._emit()
        self._emit('def _has_repetition(self, password: str) -> bool:', 1)
        self._emit('"""Check for character repetition (e.g., "aaa", "111")"""', 2)
        self._emit('for i in range(len(password) - 2):', 2)
        self._emit('if password[i] == password[i+1] == password[i+2]:', 3)
        self._emit('return True', 4)
        self._emit('return False', 2)
        
        self._emit()
        self._emit('def _has_sequential(self, password: str) -> bool:', 1)
        self._emit('"""Check for sequential characters (e.g., "abc", "123")"""', 2)
        self._emit('for i in range(len(password) - 2):', 2)
        self._emit('ord_vals = [ord(password[i]), ord(password[i+1]), ord(password[i+2])]', 3)
        self._emit('if ord_vals[1] == ord_vals[0] + 1 and ord_vals[2] == ord_vals[1] + 1:', 3)
        self._emit('return True', 4)
        self._emit('if ord_vals[1] == ord_vals[0] - 1 and ord_vals[2] == ord_vals[1] - 1:', 3)
        self._emit('return True', 4)
        self._emit('return False', 2)
    
    def _emit_main(self):
        """Emit main function for testing"""
        self._emit()
        self._emit('def main():')
        self._emit('"""Test validators"""', 1)
        self._emit('test_passwords = [', 1)
        self._emit('"Password123!"  # Should be valid', 2)
        self._emit('"pwd"           # Should be invalid (too short)', 2)
        self._emit('"abcabc"        # Should be invalid (no uppercase/digits)', 2)
        self._emit(']', 1)
        self._emit()
        self._emit('# Testing would go here', 1)
        self._emit()
        self._emit('if __name__ == "__main__":', 0)
        self._emit('main()', 1)
    
    def _to_class_name(self, name):
        """Convert policy name to Python class name"""
        # Remove spaces and convert to PascalCase
        words = name.replace('_', ' ').split()
        return ''.join(word.capitalize() for word in words) + 'Validator'
    
    def _get_char_class_pattern(self, char_class):
        """Get regex pattern for character class"""
        patterns = {
            CharClass.UPPERCASE: '[A-Z]',
            CharClass.LOWERCASE: '[a-z]',
            CharClass.DIGITS: '[0-9]',
            CharClass.SPECIAL: '[!@#$%^&*()_+\\-=\\[\\]{};:\'",.<>?/\\\\|`~]'
        }
        return patterns.get(char_class, '')


def generate_from_policy(ast, output_file=None):
    """Generate code from AST and optionally save to file"""
    generator = CodeGenerator()
    code = generator.generate(ast)
    
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(code)
            return code, None
        except Exception as e:
            return code, str(e)
    
    return code, None


def test_generator():
    """Test the generator with sample AST"""
    from .parser import Parser
    from .lexer import Lexer
    
    sample_code = '''
    POLICY SimplePassword {
        MIN_LENGTH 8
        MAX_LENGTH 128
        
        REQUIRE UPPERCASE 1
        REQUIRE LOWERCASE 1
        REQUIRE DIGITS 1
        REQUIRE SPECIAL 1
        
        FORBID REPETITION
        FORBID SEQUENTIAL
    }
    '''
    
    print("=" * 80)
    print("CODE GENERATOR TEST")
    print("=" * 80)
    
    # Lex and parse
    lexer = Lexer()
    lexer.build()
    
    parser = Parser()
    parser.build()
    
    ast = parser.parse(sample_code, lexer.lexer)
    
    # Generate code
    generator = CodeGenerator()
    code = generator.generate(ast)
    
    print("\nGenerated Python Code:")
    print("-" * 80)
    print(code)
    print("-" * 80)
    print("\n" + "=" * 80)
    
    return code


if __name__ == '__main__':
    test_generator()
