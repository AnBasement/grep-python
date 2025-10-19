from src.constants import (
    EXIT_MATCH_FOUND,
    EXIT_NO_MATCH,
    EXIT_ERROR,
    TOKEN_LITERAL,
    TOKEN_ESCAPE,
    TOKEN_CHAR_CLASS,
    TOKEN_WILDCARD,
    TOKEN_GROUP,
    TOKEN_BACKREFERENCE,
    QUANTIFIER_ONE_OR_MORE,
    QUANTIFIER_ZERO_OR_ONE,
)


def test_constants_values():
    assert EXIT_MATCH_FOUND == 0
    assert EXIT_NO_MATCH == 1
    assert EXIT_ERROR == 2

    assert TOKEN_LITERAL == "literal"
    assert TOKEN_ESCAPE == "escape"
    assert TOKEN_CHAR_CLASS == "char_class"
    assert TOKEN_WILDCARD == "wildcard"
    assert TOKEN_GROUP == "group"
    assert TOKEN_BACKREFERENCE == "backreference"

    assert QUANTIFIER_ONE_OR_MORE == "+"
    assert QUANTIFIER_ZERO_OR_ONE == "?"
