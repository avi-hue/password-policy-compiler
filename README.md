# Password Policy Compiler

A domain-specific compiler that translates password policy definitions into validation code.

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
# Lexical analysis only
python src/ppc.py examples/basic_policy.pp

# Show detailed tokens
python src/ppc.py examples/basic_policy.pp --tokens

# Parse and show AST
python src/ppc.py examples/basic_policy.pp --ast

# Full compilation with code generation
python src/ppc.py examples/basic_policy.pp --generate

# Save generated code to specific file
python src/ppc.py examples/basic_policy.pp --generate -o my_validator.py
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_lexer.py -v
pytest tests/test_parser.py -v
pytest tests/test_generator.py -v
pytest tests/test_integration.py -v

# Run with coverage
pytest tests/ -v --cov=src/compiler
```

## Compiler Pipeline

The compiler works through six stages:

1. **Lexical Analysis** (Week 3)
   - Tokenizes the input `.pp` policy file
   - Recognizes keywords, identifiers, numbers, strings
   - Handles comments and whitespace

2. **Parsing** (Week 4)
   - Builds Abstract Syntax Tree (AST) from tokens
   - Validates grammar and structure
   - Reports syntax errors

3. **Code Generation** (Week 5)
   - Converts AST to Python validator classes
   - Generates validation methods
   - Outputs executable Python code

4. **Runtime Validation** (Week 6)
   - Runtime validation of passwords
   - Test harness for validators
   - Performance monitoring

## Project Structure

```
password-policy-compiler/
├── src/
│   ├── ppc.py                     # Main CLI
│   └── compiler/
│       ├── tokens.py              # Token definitions
│       ├── token_demo.py          # Token demo
│       ├── lexer.py               # Lexical analyzer
│       ├── ast_nodes.py           # AST node classes
│       ├── parser.py              # Parser (tokens → AST)
│       ├── generator.py           # Code generator (AST → Python)
│       └── validators.py          # Runtime validators
├── tests/
│       ├── test_lexer.py          # Lexer tests (9 tests)
│       ├── test_parser.py         # Parser tests (10 tests)
│       ├── test_generator.py      # Generator tests (12 tests)
│       └── test_integration.py    # Integration tests (8 tests)
├── examples/
│       ├── basic_policy.pp        # Basic example
│       ├── weak_policy.pp         # Weak policy
│       └── strong_policy.pp       # Strong policy
├── docs/
│       └── grammar.txt            # DSL grammar
└── output/
       └── (auto-generated validators)
```

## Project Status

- ✅ **Week 1**: Project Setup & Basic CLI
- ✅ **Week 2**: DSL Grammar & Tokens
- ✅ **Week 3**: Lexer Implementation (Tokenization)
- ✅ **Week 4**: Parser Implementation (AST Building)
- ✅ **Week 5**: Code Generation (Validator Creation)
- ✅ **Week 6**: Testing & Validation (Runtime Testing)

## Example

### Input Policy File (examples/strong_policy.pp)
```
POLICY EnterprisePassword {
    MIN_LENGTH 16
    MAX_LENGTH 128
    
    REQUIRE UPPERCASE 2
    REQUIRE LOWERCASE 2
    REQUIRE DIGITS 2
    REQUIRE SPECIAL 2
    
    BLACKLIST "dictionaries/common_10000.txt"
    FORBID USERNAME
    FORBID REPETITION
    FORBID SEQUENTIAL
}
```

### Generate Validator
```bash
python src/ppc.py examples/strong_policy.pp --generate -o output/enterprise_validator.py
```

### Generated Validator Code
```python
class EnterprisepasswordValidator:
    """Password validator for EnterprisePassword policy"""
    
    def validate(self, password: str) -> Tuple[bool, str]:
        # Minimum length: 16
        if len(password) < 16:
            return False, "Password must be at least 16 characters"
        
        # Maximum length: 128
        if len(password) > 128:
            return False, "Password must not exceed 128 characters"
        
        # Require UPPERCASE characters
        count = len(re.findall(r"[A-Z]", password))
        if count < 2:
            return False, "Password must contain at least 2 uppercase character(s)"
        
        # ... more validation checks ...
        
        return True, "Password is valid"
    
    def _has_repetition(self, password: str) -> bool:
        """Check for character repetition"""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
    
    def _has_sequential(self, password: str) -> bool:
        """Check for sequential characters"""
        for i in range(len(password) - 2):
            # implementation...
        return False
```

## Testing

The project includes comprehensive test coverage:

- **Lexer Tests**: Token recognition, error handling
- **Parser Tests**: Grammar validation, AST construction
- **Generator Tests**: Code generation, syntax validation
- **Integration Tests**: End-to-end pipeline testing

Total: **39 unit tests** across 4 test modules

Run the complete test suite:
```bash
pytest tests/ -v --tb=short
```
