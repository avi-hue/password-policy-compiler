# Password Policy Compiler

A domain-specific compiler that translates password policy definitions into validation code.

# Installation
```bash
pip install -r requirements.txt
```

# Usage
```bash
# Compile a policy file
python src/ppc.py examples/basic_policy.pp

# Show token output
python src/ppc.py examples/basic_policy.pp --tokens

# Run tests
pytest tests/ -v
```