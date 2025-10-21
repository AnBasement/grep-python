from typing import Optional


def parse_pattern(
    pattern: str, group_number: Optional[list[int]] = None
) -> tuple[list[dict], bool, bool]:
    """
    Converts a pattern string into a list of tokens.

    Scans each character of the pattern to identify literals, escaped
    sequences (e.g., `\\d`, `\\w`), character classes, wildcards, groups with
    alternatives and backreferences. Detects anchors for start-of-line (^) and
    end-of-line ($) separately.

    Args:
        pattern (str): The pattern to tokenize.
        group_number (Optional[list[int]]): A list used to assign unique numbers
            to capturing groups during recursion. Defaults to None.

    Returns:
        tuple[list[dict], bool, bool]:
            - A list of token dictionaries representing the parsed pattern.
            - A boolean indicating if pattern has a start-of-line anchor (^).
            - A boolean indicating if pattern has an end-of-line anchor ($).
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

            if pattern[i + 1].isdigit():
                digit_start = i + 1
                digit_end = digit_start

                while digit_end < len(pattern) and pattern[digit_end].isdigit():
                    digit_end += 1

                number_str = pattern[digit_start:digit_end]
                backref_number = int(number_str)

                tokens.append({"type": "backreference", "number": backref_number})
                i = digit_end

            else:
                tokens.append({"type": "escape", "value": pattern[i : i + 2]})
                i += 2

        elif char == "[":
            end_index = pattern.find("]", i)
            tokens.append({"type": "char_class", "value": pattern[i : end_index + 1]})
            i = end_index + 1

        elif char == ".":
            tokens.append({"type": "wildcard"})
            i += 1

        elif char == "(":
            group_number[0] += 1
            current_group_number = group_number[0]

            end_index = find_matching_parentheses(pattern, i)
            group_content = pattern[i + 1 : end_index]
            alt_patterns = split_alternatives(group_content)

            alternatives = []
            for alt_pattern in alt_patterns:
                alt_tokens, _, _ = parse_pattern(alt_pattern, group_number)
                alternatives.append(alt_tokens)

            tokens.append(
                {
                    "type": "group",
                    "alternatives": alternatives,
                    "number": current_group_number,
                }
            )

            i = end_index + 1
        else:
            tokens.append({"type": "literal", "value": char})
            i += 1

        if i < len(pattern) and pattern[i] in ("+", "?"):
            tokens[-1]["quantifier"] = pattern[i]
            i += 1

    return tokens, has_start_anchor, has_end_anchor


def find_matching_parentheses(pattern: str, start_index: int) -> int:
    """
    Finds the index of a closing parenthesis to match an opening parenthesis.

    Scans the pattern starting after `start_index` and tracks nested parentheses
    with a depth counter, which ensures correct matching with nested groups.
    An error is raised if no closing parenthesis is found.

    Args:
        pattern (str): The pattern containing parentheses.
        start_index (int): The index of the opening parenthesis to match against.

    Returns:
        int: The index of the corresponding closing parenthesis in the pattern.
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

    raise ValueError(f"Unmatched opening parenthesis at position {start_index}")


def split_alternatives(pattern: str) -> list[str]:
    """
    Splits a pattern into alternatives using the `|` operator.

    Searches through the pattern and keeps track of nested parentheses depth
    to make sure that only the top-level `|` characters are used for splitting.
    This is done to prevent splitting inside grouped subpatterns.

    Args:
        pattern (str): The pattern to split at top-level alternations.

    Returns:
        list[str]: A list of strings representing the separate alternatives.
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
