"""
Token definitions for the Password Policy Language
"""

# Reserved keywords
reserved = {
    'POLICY': 'POLICY',
    'MIN_LENGTH': 'MIN_LENGTH',
    'MAX_LENGTH': 'MAX_LENGTH',
    'REQUIRE': 'REQUIRE',
    'BLACKLIST': 'BLACKLIST',
    'FORBID': 'FORBID',
    'UPPERCASE': 'UPPERCASE',
    'LOWERCASE': 'LOWERCASE',
    'DIGITS': 'DIGITS',
    'SPECIAL': 'SPECIAL',
    'USERNAME': 'USERNAME',
    'REPETITION': 'REPETITION',
    'SEQUENTIAL': 'SEQUENTIAL',
}

# Token list
tokens = [
    'IDENTIFIER',
    'NUMBER',
    'STRING',
    'LBRACE',
    'RBRACE',
] + list(reserved.values())

# Token rules (as strings for documentation)
token_patterns = {
    'LBRACE': r'\{',
    'RBRACE': r'\}',
    'NUMBER': r'\d+',
    'STRING': r'"[^"]*"',
    'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',
    'COMMENT': r'\#.*',
    'WHITESPACE': r'[ \t]+',
    'NEWLINE': r'\n+',
}


class Token:
    """Represents a single token"""
    
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {self.line}, {self.column})"
    
    def __str__(self):
        return f"{self.type:15s} {self.value!r:20s} at {self.line}:{self.column}"
