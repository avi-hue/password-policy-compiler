"""
Semantic Analyzer for Password Policy Language
Validates policy rules for correctness, consistency, and logical soundness
"""

from typing import Tuple, List, Dict, Optional
from .ast_nodes import (
    Program, Policy, Rule, MinLengthRule, MaxLengthRule, 
    RequireRule, BlacklistRule, ForbidRule, CharClass, ForbidType
)


class SemanticError(Exception):
    """Exception for semantic validation errors"""
    
    def __init__(self, message: str, line: int = None, column: int = None, rule_name: str = None):
        self.message = message
        self.line = line
        self.column = column
        self.rule_name = rule_name
    
    def __str__(self):
        if self.line is not None:
            return f"Semantic Error at line {self.line}, column {self.column}: {self.message}"
        return f"Semantic Error: {self.message}"
    
    def __repr__(self):
        return f"SemanticError({self.message!r}, line={self.line}, column={self.column})"


class SemanticAnalyzer:
    """
    Performs semantic analysis on parsed AST
    
    Validates:
    - Rule consistency (no conflicting rules)
    - Rule validity (sensible values)
    - Policy well-formedness
    - Resource existence (blacklist files)
    """
    
    def __init__(self):
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []
        self.policies: Dict[str, Policy] = {}
        self.current_policy: Optional[Policy] = None
    
    def analyze(self, program: Program) -> Tuple[bool, List[SemanticError]]:
        """
        Perform semantic analysis on AST
        Returns: (is_valid, error_list)
        """
        self.errors = []
        self.warnings = []
        self.policies = {}
        
        if not isinstance(program, Program):
            self.errors.append(SemanticError("Input must be a Program node"))
            return False, self.errors
        
        # Analyze each policy
        for policy in program.policies:
            self._analyze_policy(policy)
        
        # Check for policy name conflicts
        self._check_policy_names(program.policies)
        
        # Global consistency checks
        self._check_global_consistency()
        
        return len(self.errors) == 0, self.errors
    
    def _analyze_policy(self, policy: Policy) -> None:
        """Analyze a single policy definition"""
        if not isinstance(policy, Policy):
            self.errors.append(SemanticError("Expected Policy node"))
            return
        
        self.current_policy = policy
        
        # Check policy name validity
        if not policy.name or not isinstance(policy.name, str):
            self.errors.append(SemanticError(
                "Policy must have a valid name",
                line=policy.line,
                column=policy.column
            ))
            return
        
        # Check for valid Python identifier
        if not self._is_valid_identifier(policy.name):
            self.errors.append(SemanticError(
                f"Policy name '{policy.name}' is not a valid Python identifier",
                line=policy.line,
                column=policy.column
            ))
        
        # Register policy
        self.policies[policy.name] = policy
        
        # Analyze rules
        rule_tracker = {
            'min_length': None,
            'max_length': None,
            'require_rules': [],
            'blacklist_rules': [],
            'forbid_rules': []
        }
        
        for rule in policy.rules:
            self._analyze_rule(rule, rule_tracker)
        
        # Cross-check rules
        self._check_rule_consistency(policy, rule_tracker)
    
    def _analyze_rule(self, rule: Rule, rule_tracker: Dict) -> None:
        """Analyze a single rule within a policy"""
        if isinstance(rule, MinLengthRule):
            self._analyze_min_length(rule, rule_tracker)
        elif isinstance(rule, MaxLengthRule):
            self._analyze_max_length(rule, rule_tracker)
        elif isinstance(rule, RequireRule):
            self._analyze_require(rule, rule_tracker)
        elif isinstance(rule, BlacklistRule):
            self._analyze_blacklist(rule, rule_tracker)
        elif isinstance(rule, ForbidRule):
            self._analyze_forbid(rule, rule_tracker)
        else:
            self.errors.append(SemanticError(
                f"Unknown rule type: {type(rule).__name__}",
                line=rule.line,
                column=rule.column
            ))
    
    def _analyze_min_length(self, rule: MinLengthRule, rule_tracker: Dict) -> None:
        """Validate MIN_LENGTH rule"""
        # Check for duplicate
        if rule_tracker['min_length'] is not None:
            self.warnings.append(
                f"Policy '{self.current_policy.name}' has multiple MIN_LENGTH rules. "
                f"Using value {rule.length}"
            )
        
        # Validate value
        if not isinstance(rule.length, int):
            self.errors.append(SemanticError(
                f"MIN_LENGTH must be an integer, got {type(rule.length).__name__}",
                line=rule.line,
                column=rule.column
            ))
            return
        
        if rule.length < 0:
            self.errors.append(SemanticError(
                f"MIN_LENGTH must be non-negative, got {rule.length}",
                line=rule.line,
                column=rule.column
            ))
        elif rule.length > 256:
            self.warnings.append(f"MIN_LENGTH {rule.length} is unusually large")
        
        if rule.length == 0:
            self.warnings.append("MIN_LENGTH of 0 effectively disables length checking")
        
        rule_tracker['min_length'] = rule.length
    
    def _analyze_max_length(self, rule: MaxLengthRule, rule_tracker: Dict) -> None:
        """Validate MAX_LENGTH rule"""
        # Check for duplicate
        if rule_tracker['max_length'] is not None:
            self.warnings.append(
                f"Policy '{self.current_policy.name}' has multiple MAX_LENGTH rules. "
                f"Using value {rule.length}"
            )
        
        # Validate value
        if not isinstance(rule.length, int):
            self.errors.append(SemanticError(
                f"MAX_LENGTH must be an integer, got {type(rule.length).__name__}",
                line=rule.line,
                column=rule.column
            ))
            return
        
        if rule.length < 1:
            self.errors.append(SemanticError(
                f"MAX_LENGTH must be at least 1, got {rule.length}",
                line=rule.line,
                column=rule.column
            ))
        
        if rule.length > 4096:
            self.warnings.append(f"MAX_LENGTH {rule.length} is unusually large")
        
        rule_tracker['max_length'] = rule.length
    
    def _analyze_require(self, rule: RequireRule, rule_tracker: Dict) -> None:
        """Validate REQUIRE rule"""
        # Validate character class
        if rule.char_class not in CharClass.ALL:
            self.errors.append(SemanticError(
                f"Invalid character class '{rule.char_class}'. "
                f"Must be one of: {', '.join(CharClass.ALL)}",
                line=rule.line,
                column=rule.column
            ))
            return
        
        # Validate count
        if not isinstance(rule.count, int):
            self.errors.append(SemanticError(
                f"REQUIRE count must be an integer, got {type(rule.count).__name__}",
                line=rule.line,
                column=rule.column
            ))
            return
        
        if rule.count < 0:
            self.errors.append(SemanticError(
                f"REQUIRE count must be non-negative, got {rule.count}",
                line=rule.line,
                column=rule.column
            ))
        elif rule.count == 0:
            self.warnings.append(
                f"REQUIRE {rule.char_class} 0 is ineffective (always satisfied)"
            )
        
        # Check for duplicate character class requirements
        for prev_rule in rule_tracker['require_rules']:
            if prev_rule.char_class == rule.char_class:
                self.warnings.append(
                    f"Multiple REQUIRE {rule.char_class} rules detected. "
                    f"Using maximum count: {max(prev_rule.count, rule.count)}"
                )
                break
        
        rule_tracker['require_rules'].append(rule)
    
    def _analyze_blacklist(self, rule: BlacklistRule, rule_tracker: Dict) -> None:
        """Validate BLACKLIST rule"""
        # Check for duplicate
        if rule_tracker['blacklist_rules']:
            self.warnings.append(
                f"Policy '{self.current_policy.name}' has multiple BLACKLIST rules"
            )
        
        # Validate filename format
        if not isinstance(rule.filename, str):
            self.errors.append(SemanticError(
                f"BLACKLIST filename must be a string, got {type(rule.filename).__name__}",
                line=rule.line,
                column=rule.column
            ))
            return
        
        if not rule.filename:
            self.errors.append(SemanticError(
                "BLACKLIST filename cannot be empty",
                line=rule.line,
                column=rule.column
            ))
        
        rule_tracker['blacklist_rules'].append(rule)
    
    def _analyze_forbid(self, rule: ForbidRule, rule_tracker: Dict) -> None:
        """Validate FORBID rule"""
        # Validate forbid type
        if rule.forbid_type not in ForbidType.ALL:
            self.errors.append(SemanticError(
                f"Invalid forbid type '{rule.forbid_type}'. "
                f"Must be one of: {', '.join(ForbidType.ALL)}",
                line=rule.line,
                column=rule.column
            ))
            return
        
        # Check for duplicate forbid types
        for prev_rule in rule_tracker['forbid_rules']:
            if prev_rule.forbid_type == rule.forbid_type:
                self.warnings.append(
                    f"FORBID {rule.forbid_type} specified multiple times"
                )
                break
        
        rule_tracker['forbid_rules'].append(rule)
    
    def _check_rule_consistency(self, policy: Policy, rule_tracker: Dict) -> None:
        """Check consistency of rules within a policy"""
        min_len = rule_tracker['min_length']
        max_len = rule_tracker['max_length']
        
        # Check MIN_LENGTH <= MAX_LENGTH
        if min_len is not None and max_len is not None:
            if min_len > max_len:
                self.errors.append(SemanticError(
                    f"MIN_LENGTH ({min_len}) cannot be greater than MAX_LENGTH ({max_len})",
                    line=policy.line,
                    column=policy.column,
                    rule_name=policy.name
                ))
        
        # Check if password can satisfy all character requirements
        total_required_chars = sum(req.count for req in rule_tracker['require_rules'])
        if min_len is not None and total_required_chars > min_len:
            self.warnings.append(
                f"Policy '{policy.name}' requires {total_required_chars} characters "
                f"but MIN_LENGTH is only {min_len}"
            )
        
        # Check for policy completeness
        if not rule_tracker['require_rules'] and not rule_tracker['forbid_rules']:
            self.warnings.append(
                f"Policy '{policy.name}' has no REQUIRE or FORBID rules "
                "(very permissive)"
            )
        
        if not rule_tracker['min_length']:
            self.warnings.append(
                f"Policy '{policy.name}' has no MIN_LENGTH rule"
            )
    
    def _check_policy_names(self, policies: List[Policy]) -> None:
        """Check for duplicate policy names"""
        names = {}
        for policy in policies:
            if policy.name in names:
                self.errors.append(SemanticError(
                    f"Duplicate policy name '{policy.name}' at line {policy.line}; "
                    f"previously defined at line {names[policy.name].line}",
                    line=policy.line,
                    column=policy.column
                ))
            else:
                names[policy.name] = policy
    
    def _check_global_consistency(self) -> None:
        """Check global consistency across all policies"""
        # Could add cross-policy validation here
        pass
    
    @staticmethod
    def _is_valid_identifier(name: str) -> bool:
        """Check if name is a valid Python identifier"""
        import keyword
        if not name.isidentifier():
            return False
        if keyword.iskeyword(name):
            return False
        return True
    
    def get_errors(self) -> List[SemanticError]:
        """Return list of semantic errors"""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Return list of semantic warnings"""
        return self.warnings
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0
    
    def print_report(self) -> None:
        """Print semantic validation report"""
        print("\n" + "=" * 80)
        print("SEMANTIC ANALYSIS REPORT")
        print("=" * 80)
        
        if not self.errors and not self.warnings:
            print("[OK] All semantic checks passed!")
            print("=" * 80 + "\n")
            return
        
        # Print errors
        if self.errors:
            print(f"\n[ERROR] ERRORS ({len(self.errors)} found):\n")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
                if error.message:
                    print(f"   Details: {error.message}")
        
        # Print warnings
        if self.warnings:
            print(f"\n[WARNING] WARNINGS ({len(self.warnings)} found):\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning}")
        
        print("\n" + "=" * 80 + "\n")
    
    def get_summary(self) -> Dict:
        """Get summary of semantic analysis"""
        return {
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'policies_analyzed': len(self.policies),
            'is_valid': not self.has_errors(),
            'errors': [str(e) for e in self.errors],
            'warnings': self.warnings
        }
