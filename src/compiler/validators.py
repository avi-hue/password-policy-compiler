"""
Validator Runtime Utilities for Password Policy Language
Provides utilities for testing and running generated validators
"""

import re
import string
from typing import Tuple, List, Dict


class PasswordValidator:
    """Base class for password validators"""
    
    def __init__(self):
        self.rules = {}
    
    def validate(self, password: str, username: str = None) -> Tuple[bool, str]:
        """
        Validate a password
        Returns: (is_valid, error_message)
        """
        raise NotImplementedError()
    
    def add_rule(self, rule_name: str, rule_value):
        """Add a rule to the validator"""
        self.rules[rule_name] = rule_value
    
    def check_length(self, password: str, min_length: int = None, max_length: int = None) -> Tuple[bool, str]:
        """Check password length constraints"""
        if min_length and len(password) < min_length:
            return False, f"Password must be at least {min_length} characters"
        if max_length and len(password) > max_length:
            return False, f"Password must not exceed {max_length} characters"
        return True, ""
    
    def check_character_class(self, password: str, char_class: str, count: int) -> Tuple[bool, str]:
        """Check for required character class"""
        pattern = self._get_pattern(char_class)
        matches = len(re.findall(pattern, password))
        if matches < count:
            return False, f"Password must contain at least {count} {char_class.lower()} character(s)"
        return True, ""
    
    def check_no_repetition(self, password: str) -> Tuple[bool, str]:
        """Check for character repetition (3+ consecutive identical chars)"""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return False, f"Password contains repeated character '{password[i]}' at position {i}"
        return True, ""
    
    def check_no_sequential(self, password: str) -> Tuple[bool, str]:
        """Check for sequential characters (abc, 123, etc.)"""
        for i in range(len(password) - 2):
            ord_vals = [ord(password[i]), ord(password[i+1]), ord(password[i+2])]
            # Forward sequence
            if ord_vals[1] == ord_vals[0] + 1 and ord_vals[2] == ord_vals[1] + 1:
                return False, f"Password contains sequential characters at position {i}"
            # Backward sequence
            if ord_vals[1] == ord_vals[0] - 1 and ord_vals[2] == ord_vals[1] - 1:
                return False, f"Password contains sequential characters at position {i}"
        return True, ""
    
    def check_not_username(self, password: str, username: str) -> Tuple[bool, str]:
        """Check that password doesn't contain username"""
        if not username:
            return True, ""
        
        username_lower = username.lower()
        password_lower = password.lower()
        
        if username_lower in password_lower:
            return False, "Password must not contain username"
        
        return True, ""
    
    def check_blacklist(self, password: str, blacklist: List[str]) -> Tuple[bool, str]:
        """Check against blacklist of common passwords"""
        if password.lower() in [p.lower() for p in blacklist]:
            return False, "Password is in the blacklist of common passwords"
        return True, ""
    
    @staticmethod
    def _get_pattern(char_class: str) -> str:
        """Get regex pattern for character class"""
        patterns = {
            'uppercase': '[A-Z]',
            'lowercase': '[a-z]',
            'digits': '[0-9]',
            'special': '[!@#$%^&*()_+\\-=\\[\\]{};:\'",.<>?/\\\\|`~]'
        }
        return patterns.get(char_class.lower(), '')


class PolicyTest:
    """Test harness for password policies"""
    
    def __init__(self, validator):
        self.validator = validator
        self.test_results = []
    
    def test_password(self, password: str, should_pass: bool = True, username: str = None) -> Dict:
        """Test a single password"""
        is_valid, message = self.validator.validate(password, username)
        
        result = {
            'password': password,
            'expected': should_pass,
            'actual': is_valid,
            'message': message,
            'passed': is_valid == should_pass
        }
        
        self.test_results.append(result)
        return result
    
    def run_tests(self, test_cases: List[Dict]) -> Tuple[int, int]:
        """
        Run multiple test cases
        test_cases format: [{'password': 'pass', 'should_pass': True}, ...]
        Returns: (passed_count, total_count)
        """
        passed = 0
        for test_case in test_cases:
            result = self.test_password(
                test_case['password'],
                test_case.get('should_pass', True),
                test_case.get('username')
            )
            if result['passed']:
                passed += 1
        
        return passed, len(test_cases)
    
    def print_results(self):
        """Print test results"""
        if not self.test_results:
            print("No test results")
            return
        
        print("=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        print(f"{'Password':<20} {'Expected':<10} {'Actual':<10} {'Status':<8} {'Message':<25}")
        print("-" * 80)
        
        passed = 0
        for result in self.test_results:
            status = "PASS" if result['passed'] else "FAIL"
            pwd = result['password'][:18] + ".." if len(result['password']) > 20 else result['password']
            msg = result['message'][:23] + ".." if len(result['message']) > 25 else result['message']
            
            print(f"{pwd:<20} {str(result['expected']):<10} {str(result['actual']):<10} {status:<8} {msg:<25}")
            if result['passed']:
                passed += 1
        
        print("-" * 80)
        print(f"Total: {passed}/{len(self.test_results)} passed")
        print("=" * 80)
    
    def get_summary(self) -> Dict:
        """Get summary of test results"""
        if not self.test_results:
            return {'total': 0, 'passed': 0, 'failed': 0, 'pass_rate': 0.0}
        
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        
        return {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': (passed / total * 100) if total > 0 else 0.0
        }


# Default common passwords blacklist (subset)
DEFAULT_BLACKLIST = [
    'password', '123456', 'qwerty', 'abc123',
    'password123', 'admin', 'letmein', 'welcome',
    'monkey', 'dragon', 'master', 'sunshine'
]


def test_validators():
    """Test the validator utilities"""
    
    print("=" * 80)
    print("VALIDATOR UTILITIES TEST")
    print("=" * 80)
    
    # Create a simple test validator
    class TestValidator(PasswordValidator):
        def validate(self, password: str, username: str = None) -> Tuple[bool, str]:
            # Check length
            is_valid, msg = self.check_length(password, min_length=8, max_length=128)
            if not is_valid:
                return is_valid, msg
            
            # Check character classes
            for char_class, count in [('uppercase', 1), ('lowercase', 1), ('digits', 1), ('special', 1)]:
                is_valid, msg = self.check_character_class(password, char_class, count)
                if not is_valid:
                    return is_valid, msg
            
            # Check no repetition
            is_valid, msg = self.check_no_repetition(password)
            if not is_valid:
                return is_valid, msg
            
            # Check no sequential
            is_valid, msg = self.check_no_sequential(password)
            if not is_valid:
                return is_valid, msg
            
            return True, "Password is valid"
    
    validator = TestValidator()
    tester = PolicyTest(validator)
    
    # Define test cases
    test_cases = [
        {'password': 'ValidPass123!', 'should_pass': True},
        {'password': 'short', 'should_pass': False},
        {'password': 'NoDigitsOrSpecial', 'should_pass': False},
        {'password': 'NoUpperCase123!', 'should_pass': False},
        {'password': 'NOLOWERCASE123!', 'should_pass': False},
        {'password': 'NoSpecial123ABC', 'should_pass': False},
        {'password': 'Has333Repetition!', 'should_pass': False},
        {'password': 'HasAbc123!', 'should_pass': False},
    ]
    
    print("\nTesting password validator...")
    tester.run_tests(test_cases)
    tester.print_results()
    
    summary = tester.get_summary()
    print(f"\nSummary: {summary['passed']}/{summary['total']} tests passed ({summary['pass_rate']:.1f}%)")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    test_validators()
