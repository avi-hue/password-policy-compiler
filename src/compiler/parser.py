"""
Parser for Password Policy Language using PLY
Converts tokens into an Abstract Syntax Tree (AST)
"""

import ply.yacc as yacc
from .tokens import tokens
from .ast_nodes import (
    Program, Policy, MinLengthRule, MaxLengthRule, RequireRule,
    BlacklistRule, ForbidRule, CharClass, ForbidType
)


class Parser:
    """Parser for Password Policy Language"""
    
    # Token list (required by PLY)
    tokens = tokens
    
    # Precedence (if needed)
    precedence = ()
    
    def __init__(self):
        self.parser = None
        self.errors = []
        self.current_lexer = None
    
    # Grammar rules
    
    def p_program(self, p):
        """program : policy_list"""
        p[0] = Program(p[1])
    
    def p_program_empty(self, p):
        """program : empty"""
        p[0] = Program([])
    
    def p_policy_list(self, p):
        """policy_list : policy"""
        p[0] = [p[1]]
    
    def p_policy_list_multiple(self, p):
        """policy_list : policy_list policy"""
        p[0] = p[1] + [p[2]]
    
    def p_policy(self, p):
        """policy : POLICY IDENTIFIER LBRACE rule_list RBRACE"""
        p[0] = Policy(p[2], p[4], line=p.lineno(1))
    
    def p_rule_list(self, p):
        """rule_list : rule"""
        p[0] = [p[1]]
    
    def p_rule_list_multiple(self, p):
        """rule_list : rule_list rule"""
        p[0] = p[1] + [p[2]]
    
    def p_rule_list_empty(self, p):
        """rule_list : empty"""
        p[0] = []
    
    def p_rule_min_length(self, p):
        """rule : MIN_LENGTH NUMBER"""
        p[0] = MinLengthRule(p[2], line=p.lineno(1))
    
    def p_rule_max_length(self, p):
        """rule : MAX_LENGTH NUMBER"""
        p[0] = MaxLengthRule(p[2], line=p.lineno(1))
    
    def p_rule_require(self, p):
        """rule : REQUIRE char_class NUMBER"""
        p[0] = RequireRule(p[2], p[3], line=p.lineno(1))
    
    def p_rule_blacklist(self, p):
        """rule : BLACKLIST STRING"""
        p[0] = BlacklistRule(p[2], line=p.lineno(1))
    
    def p_rule_forbid(self, p):
        """rule : FORBID forbid_type"""
        p[0] = ForbidRule(p[2], line=p.lineno(1))
    
    def p_char_class_uppercase(self, p):
        """char_class : UPPERCASE"""
        p[0] = CharClass.UPPERCASE
    
    def p_char_class_lowercase(self, p):
        """char_class : LOWERCASE"""
        p[0] = CharClass.LOWERCASE
    
    def p_char_class_digits(self, p):
        """char_class : DIGITS"""
        p[0] = CharClass.DIGITS
    
    def p_char_class_special(self, p):
        """char_class : SPECIAL"""
        p[0] = CharClass.SPECIAL
    
    def p_forbid_type_username(self, p):
        """forbid_type : USERNAME"""
        p[0] = ForbidType.USERNAME
    
    def p_forbid_type_repetition(self, p):
        """forbid_type : REPETITION"""
        p[0] = ForbidType.REPETITION
    
    def p_forbid_type_sequential(self, p):
        """forbid_type : SEQUENTIAL"""
        p[0] = ForbidType.SEQUENTIAL
    
    def p_empty(self, p):
        """empty :"""
        p[0] = None
    
    def p_error(self, p):
        """Error handling"""
        if p:
            error_msg = f"Syntax error at '{p.value}' (line {p.lineno}, token {p.type})"
            self.errors.append(error_msg)
            print(f"Parser Error: {error_msg}")
        else:
            error_msg = "Syntax error at EOF"
            self.errors.append(error_msg)
            print(f"Parser Error: {error_msg}")
    
    def build(self, **kwargs):
        """Build the parser"""
        self.parser = yacc.yacc(module=self, write_tables=False, **kwargs)
        return self.parser
    
    def parse(self, data, lexer):
        """Parse input data and return AST"""
        self.errors = []
        self.current_lexer = lexer
        ast = self.parser.parse(data, lexer=lexer)
        return ast


def test_parser():
    """Test the parser with sample input"""
    from .lexer import Lexer
    
    sample_code = '''
    # Corporate password policy
    POLICY CorporatePassword {
        MIN_LENGTH 12
        MAX_LENGTH 128
        
        REQUIRE UPPERCASE 2
        REQUIRE LOWERCASE 2
        REQUIRE DIGITS 2
        REQUIRE SPECIAL 1
        
        BLACKLIST "passwords/common.txt"
        FORBID USERNAME
        FORBID REPETITION
    }
    
    POLICY WeakPassword {
        MIN_LENGTH 6
        REQUIRE LOWERCASE 1
    }
    '''
    
    print("=" * 80)
    print("PARSER TEST")
    print("=" * 80)
    print("\nInput Source Code:")
    print("-" * 80)
    print(sample_code)
    print("-" * 80)
    
    # Create lexer and parser
    lexer = Lexer()
    lexer.build()
    
    parser = Parser()
    parser.build()
    
    # Parse
    ast = parser.parse(sample_code, lexer.lexer)
    
    print("\nParsed AST:")
    print("-" * 80)
    if ast:
        print(ast)
        for i, policy in enumerate(ast.policies):
            print(f"\n  Policy {i+1}: {policy.name}")
            for j, rule in enumerate(policy.rules):
                print(f"    {j+1}. {rule}")
    
    if parser.errors:
        print("\nParser Errors:")
        for error in parser.errors:
            print(f"  - {error}")
    else:
        print("\nNo parsing errors.")
    
    print("\n" + "=" * 80)
    
    return ast


if __name__ == '__main__':
    test_parser()
