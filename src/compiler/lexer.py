"""
Lexical Analyzer (Lexer) for Password Policy Language
Tokenizes input source code using PLY
"""

import ply.lex as lex
from tokens import tokens, reserved


class Lexer:
    """Lexer for Password Policy Language"""
    
    # Token list (required by PLY)
    tokens = tokens
    
    # Regular expression rules for simple tokens
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    
    # Ignored characters (spaces and tabs)
    t_ignore = ' \t'
    
    # Reserved words (handled in t_IDENTIFIER)
    reserved = reserved
    
    def __init__(self):
        self.lexer = None
        self.errors = []
    
    def t_COMMENT(self, t):
        r'\#.*'
        # Comments are ignored, no return value
        pass
    
    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t
    
    def t_STRING(self, t):
        r'"[^"]*"'
        # Remove quotes from string value
        t.value = t.value[1:-1]
        return t
    
    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        # Check if it's a reserved word
        t.type = self.reserved.get(t.value, 'IDENTIFIER')
        return t
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    def t_error(self, t):
        """Error handling for illegal characters"""
        error_msg = f"Illegal character '{t.value[0]}' at line {t.lineno}, column {self.find_column(t)}"
        self.errors.append(error_msg)
        print(f"Lexer Error: {error_msg}")
        t.lexer.skip(1)
    
    def find_column(self, token):
        """Find column number of token"""
        line_start = self.lexer.lexdata.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1
    
    def build(self, **kwargs):
        """Build the lexer"""
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer
    
    def tokenize(self, data):
        """Tokenize input data and return list of tokens"""
        self.errors = []
        self.lexer.input(data)
        
        tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            
            # Add column information
            tok.column = self.find_column(tok)
            tokens.append(tok)
        
        return tokens
    
    def tokenize_and_print(self, data):
        """Tokenize and print tokens for debugging"""
        tokens = self.tokenize(data)
        
        print("=" * 80)
        print("LEXICAL ANALYSIS RESULTS")
        print("=" * 80)
        print(f"{'TYPE':<15} {'VALUE':<25} {'LINE':<8} {'COLUMN':<8}")
        print("-" * 80)
        
        for tok in tokens:
            value_str = str(tok.value)
            if len(value_str) > 23:
                value_str = value_str[:20] + "..."
            print(f"{tok.type:<15} {value_str:<25} {tok.lineno:<8} {tok.column:<8}")
        
        print("-" * 80)
        print(f"Total tokens: {len(tokens)}")
        
        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\nNo lexical errors found.")
        
        print("=" * 80)
        
        return tokens


def test_lexer():
    """Test the lexer with sample input"""
    
    sample_code = '''
    # Strong password policy
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
    
    # Weak policy for testing
    POLICY WeakPassword {
        MIN_LENGTH 6
        REQUIRE LOWERCASE 1
    }
    '''
    
    print("\nInput Source Code:")
    print("=" * 80)
    print(sample_code)
    print("=" * 80)
    
    # Create and build lexer
    lexer = Lexer()
    lexer.build()
    
    # Tokenize and display results
    tokens = lexer.tokenize_and_print(sample_code)
    
    return tokens


if __name__ == '__main__':
    test_lexer()
