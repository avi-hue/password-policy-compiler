#!/usr/bin/env python3
"""
Password Policy Compiler (ppc)
Main CLI entry point for the compiler
"""

import argparse
import sys
from pathlib import Path

# Import compiler modules
sys.path.insert(0, str(Path(__file__).parent))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.generator import CodeGenerator


def read_policy_file(filepath):
    """Read and return contents of a policy file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"Error: Policy file '{filepath}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the compiler"""
    parser = argparse.ArgumentParser(
        description='Password Policy Compiler - Compile .pp files to validation code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  ppc policy.pp                    # Compile policy file
  ppc policy.pp -o validator.py    # Specify output file
  ppc policy.pp --tokens           # Show token output
  ppc policy.pp --ast              # Show parsed AST
  ppc policy.pp --generate         # Generate Python validator code
  ppc --version                    # Show version
        '''
    )
    
    parser.add_argument(
        'policy_file',
        type=str,
        help='Path to the .pp policy file'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file for generated code (default: auto-generated)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--tokens',
        action='store_true',
        help='Display token output from lexer'
    )
    
    parser.add_argument(
        '--ast',
        action='store_true',
        help='Display parsed AST'
    )
    
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate Python validator code'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Password Policy Compiler v0.4.0 (Weeks 1-4 complete)'
    )
    
    args = parser.parse_args()
    
    # Validate file extension
    if not args.policy_file.endswith('.pp'):
        print("Warning: Policy file should have .pp extension")
    
    # Read policy file
    if args.verbose:
        print(f"Reading policy file: {args.policy_file}")
    
    policy_content = read_policy_file(args.policy_file)
    
    # STEP 1: Lexical Analysis
    lexer = Lexer()
    lexer.build()
    
    if args.tokens or args.verbose:
        tokens = lexer.tokenize_and_print(policy_content)
    else:
        tokens = lexer.tokenize(policy_content)
    
    if lexer.errors:
        print(f"\n❌ Lexical Errors: {len(lexer.errors)}")
        for error in lexer.errors:
            print(f"  {error}")
        return 1
    
    if not (args.ast or args.generate):
        print(f"✓ Lexical analysis complete: {len(tokens)} tokens found")
        print("✓ No lexical errors found.")
        return 0
    
    # STEP 2: Parsing
    if args.verbose:
        print("\nParsing policy...")
    
    parser = Parser()
    parser.build()
    ast = parser.parse(policy_content, lexer.lexer)
    
    if parser.errors:
        print(f"\n❌ Parsing Errors: {len(parser.errors)}")
        for error in parser.errors:
            print(f"  {error}")
        return 1
    
    if args.ast or args.verbose:
        print("\n" + "=" * 80)
        print("PARSED AST")
        print("=" * 80)
        if ast:
            print(f"Program with {len(ast.policies)} policy/policies:")
            for i, policy in enumerate(ast.policies):
                print(f"\n  {i+1}. {policy.name} ({len(policy.rules)} rules)")
                for j, rule in enumerate(policy.rules):
                    print(f"     {j+1}. {rule}")
        print("=" * 80)
    
    if not args.generate:
        print(f"\n✓ Parsing complete: {len(ast.policies)} policy/policies parsed")
        if not parser.errors:
            print("✓ No parsing errors found.")
        return 0
    
    # STEP 3: Code Generation
    if args.verbose:
        print("\nGenerating Python validator code...")
    
    generator = CodeGenerator()
    generated_code = generator.generate(ast)
    
    if generator.errors:
        print(f"\n❌ Generation Errors: {len(generator.errors)}")
        for error in generator.errors:
            print(f"  {error}")
        return 1
    
    # Output generated code
    print("\n" + "=" * 80)
    print("GENERATED PYTHON CODE")
    print("=" * 80)
    print(generated_code)
    print("=" * 80)
    
    # Save to file if specified
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(generated_code)
            print(f"\n✓ Generated code saved to: {args.output}")
        except Exception as e:
            print(f"\n❌ Error writing to file: {e}")
            return 1
    else:
        # Auto-generate output filename
        input_path = Path(args.policy_file)
        output_path = Path('output') / f"{input_path.stem}_validator.py"
        output_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(output_path, 'w') as f:
                f.write(generated_code)
            print(f"\n✓ Generated code saved to: {output_path}")
        except Exception as e:
            print(f"\n❌ Error writing to file: {e}")
            return 1
    
    print("\n✓ Compilation complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
