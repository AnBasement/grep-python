from src.pattern_matcher import (
    match_pattern,
    character_matches_token,
    calculate_min_match_length,
    calculate_start_indices,
    count_greedy_matches,
)
from src.pattern_parser import parse_pattern


class TestMatchPattern:
    def test_simple_literal_match(self):
        assert match_pattern("hello world", "world") is True
        assert match_pattern("hello world", "mars") is False

    def test_start_and_end_anchors(self):
        assert match_pattern("abc", "^abc$") is True
        assert match_pattern("xabc", "^abc$") is False
        assert match_pattern("abcx", "^abc$") is False
        assert match_pattern("abc", "^ab") is True
        assert match_pattern("xabc", "^ab") is False

    def test_escape_classes(self):
        assert match_pattern("a1_", r"\w\d_+") is True
        assert match_pattern("a1-", r"\w\d_+") is False
        assert match_pattern("9", r"\d") is True

    def test_character_class_and_negation(self):
        assert match_pattern("bat", "[bcr]a[rt]") is True
        assert match_pattern("baq", "[bcr]a[rt]") is False
        assert match_pattern("a", "[^xyz]") is True
        assert match_pattern("x", "[^xyz]") is False

    def test_groups_and_alternation(self):
        assert match_pattern("cat", "(dog|cat)") is True
        assert match_pattern("doge", "(dog|cat)$") is False
        assert match_pattern("fog", "(dog|cat)") is False

    def test_quantifiers_plus_and_optional(self):
        assert match_pattern("aaaab", "a+b") is True
        assert match_pattern("b", "a?b") is True
        assert match_pattern("ab", "a?b") is True
        assert match_pattern("aaab", "a?b") is True

    def test_backreference(self):
        assert match_pattern("abab", "(ab)\\1") is True
        assert match_pattern("aba", "(ab)\\1") is False


class TestHelperFunctions:
    def test_character_matches_token(self):
        assert character_matches_token("a", {"type": "literal", "value": "a"})
        assert not character_matches_token("b", {"type": "literal", "value": "a"})
        assert character_matches_token("5", {"type": "escape", "value": "\\d"})
        assert character_matches_token("_", {"type": "escape", "value": "\\w"})
        assert not character_matches_token("-", {"type": "escape", "value": "\\w"})
        assert character_matches_token("a", {"type": "char_class", "value": "[abc]"})
        assert not character_matches_token(
            "d", {"type": "char_class", "value": "[abc]"}
        )
        assert character_matches_token("d", {"type": "char_class", "value": "[^abc]"})
        assert character_matches_token("x", {"type": "wildcard"})

    def test_min_match_length(self):
        tokens, _, _ = parse_pattern("a(b|cd)?e+")
        assert calculate_min_match_length(tokens) == 2

    def test_start_indices_with_and_without_anchor(self):
        tokens, start, end = parse_pattern("^abc")
        min_len = calculate_min_match_length(tokens)
        indices = list(calculate_start_indices(5, min_len, start, end))
        assert indices == [0]

        tokens, start, end = parse_pattern("abc")
        min_len = calculate_min_match_length(tokens)
        indices = list(calculate_start_indices(5, min_len, start, end))
        assert indices == list(range(5 - min_len + 1))

    def test_count_greedy_matches(self):
        tokens, _, _ = parse_pattern("a")
        token = tokens[0]
        assert count_greedy_matches("aaab", 0, token) == 3
        assert count_greedy_matches("baaa", 0, token) == 0
