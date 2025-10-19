from src.pattern_parser import parse_pattern


class TestPatternParser:
    def test_detects_start_and_end_anchors(self):
        tokens, has_start, has_end = parse_pattern("^abc$")
        assert has_start is True
        assert has_end is True
        assert [t["type"] for t in tokens] == ["literal", "literal", "literal"]
        assert [t.get("value") for t in tokens] == ["a", "b", "c"]

    def test_parses_escape_sequences(self):
        pattern = "\\d\\w\\+"
        tokens, _, _ = parse_pattern(pattern)
        assert [t["type"] for t in tokens] == ["escape", "escape", "escape"]
        assert [t["value"] for t in tokens] == ["\\d", "\\w", "\\+"]

    def test_parses_character_classes(self):
        tokens, _, _ = parse_pattern("[abc][^xyz]")
        assert [t["type"] for t in tokens] == ["char_class", "char_class"]
        assert tokens[0]["value"] == "[abc]"
        assert tokens[1]["value"] == "[^xyz]"

    def test_parses_groups_and_alternation_with_numbering(self):
        pattern = "(ab|cd)(e(f|g))"
        tokens, _, _ = parse_pattern(pattern)
        assert len(tokens) == 2
        assert tokens[0]["type"] == "group"
        assert tokens[1]["type"] == "group"
        assert tokens[0]["number"] == 1
        assert tokens[1]["number"] == 2
        inner_alts = tokens[1]["alternatives"][0]
        assert (inner_alts[0]["type"] == "literal" and
                inner_alts[0]["value"] == "e")
        assert inner_alts[1]["type"] == "group"
        assert inner_alts[1]["number"] == 3
        alts0 = tokens[0]["alternatives"]
        assert len(alts0) == 2
        alt0_vals = [tok["value"] for tok in alts0[0]]
        alt1_vals = [tok["value"] for tok in alts0[1]]
        assert alt0_vals == ["a", "b"]
        assert alt1_vals == ["c", "d"]

    def test_applies_quantifiers_to_previous_token(self):
        tokens, _, _ = parse_pattern("a+b?")
        assert len(tokens) == 2
        assert tokens[0]["type"] == "literal" and tokens[0]["value"] == "a"
        assert tokens[0].get("quantifier") == "+"
        assert tokens[1]["type"] == "literal" and tokens[1]["value"] == "b"
        assert tokens[1].get("quantifier") == "?"

    def test_parses_backreference_tokens(self):
        tokens, _, _ = parse_pattern("(ab)\\1")
        # Expect a group token followed by a backreference token
        assert tokens[0]["type"] == "group"
        assert tokens[0]["number"] == 1
        assert tokens[1]["type"] == "backreference"
        assert tokens[1]["number"] == 1
