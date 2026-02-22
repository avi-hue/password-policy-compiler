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
from compiler.semantic_analyzer import SemanticAnalyzer
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
  ppc policy.pp --semantic         # Perform semantic analysis
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
        '--semantic',
        action='store_true',
        help='Display semantic analysis results'
    )
    
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate Python validator code'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Password Policy Compiler v0.5.0 (Weeks 1-7 complete)'
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
        print(f"\n[ERROR] Lexical Errors: {len(lexer.errors)}")
        for error in lexer.errors:
            print(f"  {error}")
        return 1
    
    if not (args.ast or args.semantic or args.generate):
        print(f"[OK] Lexical analysis complete: {len(tokens)} tokens found")
        print("[OK] No lexical errors found.")
        return 0
    
    # STEP 2: Parsing
    if args.verbose:
        print("\nParsing policy...")
    
    parser_obj = Parser()
    parser_obj.build()
    ast = parser_obj.parse(policy_content, lexer.lexer)
    
    if parser_obj.errors:
        print(f"\n[ERROR] Parsing Errors: {len(parser_obj.errors)}")
        for error in parser_obj.errors:
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
    
    # STEP 2.5: Semantic Analysis
    if args.semantic or args.verbose:
        print("\nPerforming semantic analysis...")
    
    semantic_analyzer = SemanticAnalyzer()
    is_valid, semantic_errors = semantic_analyzer.analyze(ast)
    
    if args.semantic or args.verbose:
        semantic_analyzer.print_report()
    
    if semantic_errors:
        print(f"\n[ERROR] Semantic Errors: {len(semantic_errors)}")
        for error in semantic_errors:
            print(f"  {error}")
    
    if semantic_analyzer.warnings:
        print(f"\n[WARNING] Semantic Warnings: {len(semantic_analyzer.warnings)}")
        for warning in semantic_analyzer.warnings:
            print(f"  • {warning}")
    
    if not args.generate:
        print(f"\n[OK] Analysis complete: {len(ast.policies)} policy/policies parsed")
        if not parser_obj.errors:
            print("[OK] No parsing errors found.")
        return 0 if is_valid else 1
    
    # STEP 3: Code Generation (only if semantic analysis passed or verbose)
    if semantic_errors and not args.verbose:
        print("\n[ERROR] Semantic errors must be fixed before code generation.")
        return 1
    
    if args.verbose:
        print("\nGenerating Python validator code...")
    
    generator = CodeGenerator()
    generated_code = generator.generate(ast)
    
    if generator.errors:
        print(f"\n[ERROR] Generation Errors: {len(generator.errors)}")
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
            print(f"\n[OK] Generated code saved to: {args.output}")
        except Exception as e:
            print(f"\n[ERROR] Error writing to file: {e}")
            return 1
    else:
        # Auto-generate output filename
        input_path = Path(args.policy_file)
        output_path = Path('output') / f"{input_path.stem}_validator.py"
        output_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(output_path, 'w') as f:
                f.write(generated_code)
            print(f"\n[OK] Generated code saved to: {output_path}")
        except Exception as e:
            print(f"\n[ERROR] Error writing to file: {e}")
            return 1
    
    print("\n[OK] Compilation complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
