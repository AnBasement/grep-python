def parse_pattern(pattern, group_number=None):
    """
    Parses the input pattern into tokens and detects start and
    end anchors.

    Does this by scanning the pattern string and extracting
    escaped characters, character classes and quantifiers
    that are then placed in a token list.
    Also detects start of string anchor (^) and end of string
    anchor ($).

    Tokenizing the pattern simplifies the following matching logic
    and separates handling of anchors from the main matching algorithm.
    """
    if group_number is None:
        group_number = [0]

    i = 0
    tokens = []

    has_start_anchor = pattern.startswith("^")
    has_end_anchor = pattern.endswith("$")

    if has_start_anchor:
        pattern = pattern[1:]
    if has_end_anchor:
        pattern = pattern[:-1]

    while i < len(pattern):
        char = pattern[i]

        if char == "\\" and i + 1 < len(pattern):

            if pattern[i+1].isdigit():
                digit_start = i + 1
                digit_end = digit_start

                while (
                    digit_end < len(pattern)
                    and pattern[digit_end].isdigit()
                ):
                    digit_end += 1

                number_str = pattern[digit_start:digit_end]
                backref_number = int(number_str)

                tokens.append({
                    "type": "backreference",
                    "number": backref_number
                })
                i = digit_end

            else:
                tokens.append({
                    "type": "escape",
                    "value": pattern[i:i+2]
                })
                i += 2

        elif char == "[":
            end_index = pattern.find("]", i)
            tokens.append({
                "type": "char_class",
                "value": pattern[i:end_index+1]
            })
            i = end_index + 1

        elif char == ".":
            tokens.append({"type": "wildcard"})
            i += 1

        elif char == "(":
            group_number[0] += 1
            current_group_number = group_number[0]

            end_index = find_matching_parentheses(pattern, i)
            group_content = pattern[i+1:end_index]
            alt_patterns = split_alternatives(group_content)

            alternatives = []
            for alt_pattern in alt_patterns:
                alt_tokens, _, _ = parse_pattern(alt_pattern, group_number)
                alternatives.append(alt_tokens)

            tokens.append({
                "type": "group",
                "alternatives": alternatives,
                "number": current_group_number
            })

            i = end_index + 1
        else:
            tokens.append({
                "type": "literal",
                "value": char
            })
            i += 1

        if i < len(pattern) and pattern[i] in ("+", "?"):
            tokens[-1]["quantifier"] = pattern[i]
            i += 1

    return tokens, has_start_anchor, has_end_anchor


def find_matching_parentheses(pattern, start_index):
    """
    Finds the index of the closing parentheses matching a given
    opening parenthesis in the pattern string.
    """
    depth = 1
    i = start_index + 1

    while i < len(pattern):
        if pattern[i] == "(":
            depth += 1
        elif pattern[i] == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1


def split_alternatives(pattern):
    """
    Divides the input pattern into separate branches based on
    the alternation operator (|) on the top level.

    In case of a pattern like stricter|(gun|laws), this will split
    it into ["stricter", "(gun|laws)"] instead of
    ["stricter", "(gun", "laws)"] as the inner | belongs in the
    nested group.
    """
    alternatives = []
    current_alternative = ""
    depth = 0

    for char in pattern:
        if char == "(":
            depth += 1
            current_alternative += char
        elif char == ")":
            depth -= 1
            current_alternative += char
        elif char == "|" and depth == 0:
            alternatives.append(current_alternative)
            current_alternative = ""
        else:
            current_alternative += char

    alternatives.append(current_alternative)
    return alternatives
