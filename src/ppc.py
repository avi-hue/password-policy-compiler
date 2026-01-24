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
        '--version',
        action='version',
        version='Password Policy Compiler v0.1.0 (Week 3)'
    )
    
    args = parser.parse_args()
    
    # Validate file extension
    if not args.policy_file.endswith('.pp'):
        print("Warning: Policy file should have .pp extension")
    
    # Read policy file
    if args.verbose:
        print(f"Reading policy file: {args.policy_file}")
    
    policy_content = read_policy_file(args.policy_file)
    
    # Lexical Analysis
    lexer = Lexer()
    lexer.build()
    
    if args.tokens:
        # Show detailed token output
        tokens = lexer.tokenize_and_print(policy_content)
    else:
        # Just tokenize
        tokens = lexer.tokenize(policy_content)
        print(f"Lexical analysis complete: {len(tokens)} tokens found")
        
        if lexer.errors:
            print(f"Errors: {len(lexer.errors)}")
            for error in lexer.errors:
                print(f"  {error}")
            return 1
        else:
            print("No lexical errors found.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
