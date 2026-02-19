"""
Abstract Syntax Tree (AST) node definitions for Password Policy Language
"""


class ASTNode:
    """Base class for all AST nodes"""
    
    def __init__(self, line=None, column=None):
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"{self.__class__.__name__}(...)"


class Program(ASTNode):
    """Root node containing a list of policies"""
    
    def __init__(self, policies, line=None, column=None):
        super().__init__(line, column)
        self.policies = policies
    
    def __repr__(self):
        return f"Program({len(self.policies)} policies)"


class Policy(ASTNode):
    """A single policy definition"""
    
    def __init__(self, name, rules, line=None, column=None):
        super().__init__(line, column)
        self.name = name
        self.rules = rules
    
    def __repr__(self):
        return f"Policy(name={self.name!r}, {len(self.rules)} rules)"


class Rule(ASTNode):
    """Base class for all rule types"""
    pass


class MinLengthRule(Rule):
    """MIN_LENGTH <number>"""
    
    def __init__(self, length, line=None, column=None):
        super().__init__(line, column)
        self.length = length
    
    def __repr__(self):
        return f"MinLengthRule(length={self.length})"


class MaxLengthRule(Rule):
    """MAX_LENGTH <number>"""
    
    def __init__(self, length, line=None, column=None):
        super().__init__(line, column)
        self.length = length
    
    def __repr__(self):
        return f"MaxLengthRule(length={self.length})"


class RequireRule(Rule):
    """REQUIRE <char_class> <number>"""
    
    def __init__(self, char_class, count, line=None, column=None):
        super().__init__(line, column)
        self.char_class = char_class
        self.count = count
    
    def __repr__(self):
        return f"RequireRule(char_class={self.char_class!r}, count={self.count})"


class BlacklistRule(Rule):
    """BLACKLIST <string>"""
    
    def __init__(self, filename, line=None, column=None):
        super().__init__(line, column)
        self.filename = filename
    
    def __repr__(self):
        return f"BlacklistRule(filename={self.filename!r})"


class ForbidRule(Rule):
    """FORBID <forbid_type>"""
    
    def __init__(self, forbid_type, line=None, column=None):
        super().__init__(line, column)
        self.forbid_type = forbid_type
    
    def __repr__(self):
        return f"ForbidRule(forbid_type={self.forbid_type!r})"


# Character class and forbid type enums
class CharClass:
    UPPERCASE = 'UPPERCASE'
    LOWERCASE = 'LOWERCASE'
    DIGITS = 'DIGITS'
    SPECIAL = 'SPECIAL'
    
    ALL = {UPPERCASE, LOWERCASE, DIGITS, SPECIAL}


class ForbidType:
    USERNAME = 'USERNAME'
    REPETITION = 'REPETITION'
    SEQUENTIAL = 'SEQUENTIAL'
    
    ALL = {USERNAME, REPETITION, SEQUENTIAL}
