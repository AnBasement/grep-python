"""
Constants used throughout the grep implementation.
"""

# Exit codes
EXIT_MATCH_FOUND = 0
EXIT_NO_MATCH = 1
EXIT_ERROR = 2

# Pattern token types
TOKEN_LITERAL = "literal"
TOKEN_ESCAPE = "escape"
TOKEN_CHAR_CLASS = "char_class"
TOKEN_WILDCARD = "wildcard"
TOKEN_GROUP = "group"
TOKEN_BACKREFERENCE = "backreference"

# Quantifiers
QUANTIFIER_ONE_OR_MORE = "+"
QUANTIFIER_ZERO_OR_ONE = "?"
