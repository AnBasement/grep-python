from .pattern_parser import parse_pattern


def try_match(
    tokens: list[dict],
    input_line: str,
    has_end_anchor: bool,
    token_index: int,
    j: int,
    captures: dict[int, str],
) -> bool:
    """
    Matches a tokenized regex pattern against an input line.

    Processes single tokens one at a time and handles grouping, quantifiers
    and backreferences. Calls helper functions to test subpatterns and track
    captured groups. True is only returned if the full token sequence is a
    match and respects start/end anchors if specified.

    This function is the backbone of this regex engine. It models how it
    backtracks and evaluates nested patterns.

    Args:
        tokens (list[dict]): Parsed regex tokens to evaluate.
        input_line (str): The string to test against the pattern.
        has_end_anchor (bool): Whether the pattern has a line-end match.
        token_index (int): Current index in the token list.
        j (int): Current character position in the input string.
        captures (dict[int, str]): Active capture groups and their matched text.

    Returns:
        bool: True if the remaining tokens successfully match the input,
        else False.
    """
    if token_index == len(tokens):
        if has_end_anchor:
            return j == len(input_line)
        return True

    token = tokens[token_index]
    token_type = token["type"]
    quantifier = token.get("quantifier")

    if token_type == "group":
        saved_captures = captures.copy()
        group_start_position = j
        alternatives = token["alternatives"]

        if quantifier == "+":
            group_start_position = j
            matched_once = False

            for alt_tokens in alternatives:
                temporary_captures = saved_captures.copy()
                success, new_j = try_match_sequence(
                    alt_tokens, input_line, j, temporary_captures
                )
                if success:
                    test_captures = saved_captures.copy()
                    test_captures.update(temporary_captures)
                    group_number = token.get("number")
                    if group_number is not None:
                        test_captures[group_number] = input_line[
                            group_start_position:new_j
                        ]

                    matched_once = True
                    if try_match(
                        tokens,
                        input_line,
                        has_end_anchor,
                        token_index + 1,
                        new_j,
                        test_captures,
                    ):
                        captures.clear()
                        captures.update(test_captures)
                        return True

                    captures.clear()
                    captures.update(saved_captures)

            return matched_once and False

        elif quantifier == "?":
            group_start_position = j

            for alt_tokens in alternatives:
                temporary_captures = saved_captures.copy()
                success, new_j = try_match_sequence(
                    alt_tokens, input_line, j, temporary_captures
                )
                if success:
                    test_captures = saved_captures.copy()
                    test_captures.update(temporary_captures)
                    group_number = token.get("number")
                    if group_number is not None:
                        test_captures[group_number] = input_line[
                            group_start_position:new_j
                        ]

                    if try_match(
                        tokens,
                        input_line,
                        has_end_anchor,
                        token_index + 1,
                        new_j,
                        test_captures,
                    ):
                        captures.clear()
                        captures.update(test_captures)
                        return True

                    captures.clear()
                    captures.update(saved_captures)

            if try_match(
                tokens, input_line, has_end_anchor, token_index + 1, j, captures
            ):
                return True

            return False

        else:
            for alt_tokens in alternatives:
                max_possible_len = len(input_line) - j
                for max_len in range(max_possible_len, -1, -1):
                    temporary_captures = saved_captures.copy()

                    success, end_pos = try_match_sequence_with_limit(
                        alt_tokens, input_line, j, max_len, temporary_captures
                    )

                    if success:
                        test_captures = saved_captures.copy()
                        test_captures.update(temporary_captures)
                        group_number = token.get("number")
                        if group_number is not None:
                            test_captures[group_number] = input_line[
                                group_start_position:end_pos
                            ]

                        if try_match(
                            tokens,
                            input_line,
                            has_end_anchor,
                            token_index + 1,
                            end_pos,
                            test_captures,
                        ):
                            captures.clear()
                            captures.update(test_captures)
                            return True

            return False

    elif token_type == "backreference":
        ref_number = token["number"]

        if ref_number not in captures:
            return False

        captured_text = captures[ref_number]
        captured_len = len(captured_text)

        if j + captured_len > len(input_line):
            return False

        if input_line[j : j + captured_len] != captured_text:
            return False

        return try_match(
            tokens,
            input_line,
            has_end_anchor,
            token_index + 1,
            j + captured_len,
            captures,
        )

    elif quantifier == "+":
        max_count = count_greedy_matches(input_line, j, token)
        if max_count == 0:
            return False
        for count in range(max_count, 0, -1):
            if try_match(
                tokens, input_line, has_end_anchor, token_index + 1, j + count, captures
            ):
                return True

        return False

    elif quantifier == "?":
        single_match = (
            j < len(input_line)
            and character_matches_token(input_line[j], token)
            and try_match(
                tokens, input_line, has_end_anchor, token_index + 1, j + 1, captures
            )
        )
        no_match = try_match(
            tokens, input_line, has_end_anchor, token_index + 1, j, captures
        )
        return single_match or no_match

    else:
        if j >= len(input_line):
            return False
        c = input_line[j]
        if not character_matches_token(c, token):
            return False
        return try_match(
            tokens, input_line, has_end_anchor, token_index + 1, j + 1, captures
        )


def try_match_sequence_with_limit(
    tokens: list[dict],
    input_line: str,
    start_j: int,
    max_len: int,
    captures: dict[int, str],
) -> tuple[bool, int]:
    """
    Works similar to `try_match_sequence()`, but has a hard limit (`max_len`)
    that prevents over-matching. Matches a sequence of regex tokens against a
    substring of the input and stops when max_len is reached. Utilizes recursive
    descent for evaluation of groups, backreferences and quantifiers.

    Args:
        tokens (list[dict]): Parsed regex tokens to evaluate.
        input_line (str): The string to test against the pattern.
        start_j (int): The starting index for matching.
        max_len (int): The maximum allowed span to match within.
        captures (dict[int, str]): Active capture groups and their matched text.

    Returns:
        A tuple `(success, new_index)` where:
            - `success`: True if token sequence matched within limits.
            - `new_index`: Position in `input_line` after match.
    """
    j = start_j
    first_captures = captures.copy()

    for token in tokens:
        if j > start_j + max_len:
            captures.clear()
            captures.update(first_captures)
            return (False, start_j)

        token_type = token["type"]
        quantifier = token.get("quantifier")

        if token_type == "group":
            saved_captures = captures.copy()
            group_start_position = j
            alternatives = token["alternatives"]

            remaining_len = max_len - (j - start_j)

            if quantifier == "+":
                matched = False
                for alt_tokens in alternatives:
                    temporary_captures = saved_captures.copy()
                    success, new_j = try_match_sequence_with_limit(
                        alt_tokens, input_line, j, remaining_len, temporary_captures
                    )
                    if success:
                        captures.update(temporary_captures)
                        group_number = token.get("number")
                        if group_number is not None:
                            captures[group_number] = input_line[
                                group_start_position:new_j
                            ]
                        j = new_j
                        matched = True
                        break
                if not matched:
                    captures.clear()
                    captures.update(first_captures)
                    return (False, start_j)

            elif quantifier == "?":
                for alt_tokens in alternatives:
                    temporary_captures = saved_captures.copy()
                    success, new_j = try_match_sequence_with_limit(
                        alt_tokens, input_line, j, remaining_len, temporary_captures
                    )
                    if success:
                        captures.update(temporary_captures)
                        group_number = token.get("number")
                        if group_number is not None:
                            captures[group_number] = input_line[
                                group_start_position:new_j
                            ]
                        j = new_j
                        break

            else:
                matched = False
                for alt_tokens in alternatives:
                    temporary_captures = saved_captures.copy()
                    success, new_j = try_match_sequence_with_limit(
                        alt_tokens, input_line, j, remaining_len, temporary_captures
                    )
                    if success:
                        captures.update(temporary_captures)
                        group_number = token.get("number")
                        if group_number is not None:
                            captures[group_number] = input_line[
                                group_start_position:new_j
                            ]
                        j = new_j
                        matched = True
                        break
                if not matched:
                    captures.clear()
                    captures.update(first_captures)
                    return (False, start_j)

        elif quantifier == "+":
            remaining_len = max_len - (j - start_j)
            max_count = count_greedy_matches(input_line, j, token)
            max_count = min(max_count, remaining_len)
            if max_count == 0:
                return (False, start_j)
            j += max_count

        elif quantifier == "?":
            if j < len(input_line) and character_matches_token(input_line[j], token):
                j += 1

        elif token_type == "backreference":
            ref_number = token["number"]
            if ref_number not in captures:
                return (False, start_j)
            captured_text = captures[ref_number]
            captured_len = len(captured_text)
            if j + captured_len > len(input_line):
                return (False, start_j)
            if input_line[j : j + captured_len] != captured_text:
                return (False, start_j)
            j += captured_len

        else:
            if j >= len(input_line):
                return (False, start_j)
            if not character_matches_token(input_line[j], token):
                return (False, start_j)
            j += 1

    return (True, j)


def try_match_sequence(
    tokens: list[dict], input_line: str, start_j: int, captures: dict[int, str]
) -> tuple[bool, int]:
    """
    Matches a sequence of regex tokens against an input line
    starting from a given index (`start_j`). Similar to `try_match()`,
    but tracks how far the match extends and keeps captured groups for later
    reference.

    Iterates through tokens recursively and evaluates grousp, quantifiers and
    backreferences in sequence. Upon a failed match it restores previous capture
    states to ensure backtracking.

    Args:
        tokens (list[dict]): Parsed regex tokens to evaluate.
        input_line (str): The string to test against the pattern.
        start_j (int): The starting index for matching.
        captures (dict[int, str]): Active capture groups and their matched text.

    Returns:
        A tuple `(success, new_index)` where:
            - `success`: True if token sequence matched within limits.
            - `new_index`: Position in `input_line` after match.
    """
    j = start_j
    first_captures = captures.copy()

    for token in tokens:
        token_type = token["type"]
        quantifier = token.get("quantifier")

        if token_type == "group":
            saved_captures = captures.copy()
            group_start_position = j
            alternatives = token["alternatives"]

            if quantifier == "+":
                matched = False
                for alt_tokens in alternatives:
                    temporary_captures = saved_captures.copy()
                    success, new_j = try_match_sequence(
                        alt_tokens, input_line, j, temporary_captures
                    )
                    if success:
                        captures.update(temporary_captures)

                        group_number = token.get("number")
                        if group_number is not None:
                            captures[group_number] = input_line[
                                group_start_position:new_j
                            ]

                        j = new_j
                        matched = True
                        break
                if not matched:
                    captures.clear()
                    captures.update(first_captures)
                    return (False, start_j)

            elif quantifier == "?":
                for alt_tokens in alternatives:
                    temporary_captures = saved_captures.copy()
                    success, new_j = try_match_sequence(
                        alt_tokens, input_line, j, temporary_captures
                    )
                    if success:
                        captures.update(temporary_captures)

                        group_number = token.get("number")
                        if group_number is not None:
                            captures[group_number] = input_line[
                                group_start_position:new_j
                            ]
                        j = new_j
                        break

            else:
                matched = False
                for alt_tokens in alternatives:
                    temporary_captures = saved_captures.copy()
                    success, new_j = try_match_sequence(
                        alt_tokens, input_line, j, temporary_captures
                    )
                    if success:
                        captures.update(temporary_captures)

                        group_number = token.get("number")
                        if group_number is not None:
                            captures[group_number] = input_line[
                                group_start_position:new_j
                            ]
                        j = new_j
                        matched = True
                        break
                if not matched:
                    captures.clear()
                    captures.update(first_captures)
                    return (False, start_j)

        elif quantifier == "+":
            max_count = count_greedy_matches(input_line, j, token)
            if max_count == 0:
                return (False, start_j)
            j += max_count

        elif quantifier == "?":
            if j < len(input_line) and character_matches_token(input_line[j], token):
                j += 1

        elif token_type == "backreference":
            ref_number = token["number"]

            if ref_number not in captures:
                return (False, start_j)

            captured_text = captures[ref_number]
            captured_len = len(captured_text)

            if j + captured_len > len(input_line):
                return (False, start_j)

            if input_line[j : j + captured_len] != captured_text:
                return (False, start_j)

            j += captured_len

        else:
            if j >= len(input_line):
                return (False, start_j)
            if not character_matches_token(input_line[j], token):
                return (False, start_j)
            j += 1

    return (True, j)


def match_pattern(input_line: str, pattern: str, ignore_case: bool = False) -> bool:
    """
    The main function for pattern matching. Determines if an input string (`input_line`)
    matches a given regex pattern.

    Pattern is parsed into tokens and evaluated against the input at every possible
    starting position while respecting anchors. Calls `try_match()` for the actual
    matching. Can optionally ignore case.

    Args:
        input_line (str): The string to test against the pattern.
        pattern (str): The regex pattern to match against.
        ignore_case (bool, optional): If True, ignores case. Defaults to False.

    Returns:
        bool: True if pattern matches anywhere in the input line; else False.
    """
    if ignore_case:
        input_line = input_line.lower()
        pattern = pattern.lower()

    tokens, has_start_anchor, has_end_anchor = parse_pattern(pattern)
    min_length = calculate_min_match_length(tokens)
    start_indices = calculate_start_indices(
        len(input_line), min_length, has_start_anchor
    )

    for start_index in start_indices:
        captures = {}
        if try_match(tokens, input_line, has_end_anchor, 0, start_index, captures):
            return True

    return False


def character_matches_token(char: str, token: dict) -> bool | None:
    """
    Checks if a single character matches a regex token.

    Handles literals, escaped sequences (e.g., `\\d`, `\\w`), character classes
    (incl. negated) and wildcards. Gathers all character-level matching logic
    for the engine.

    Args:
        char (str): The character from the input string.
        token (dict): A parsed token dictionary specifying the type of match
            (literal, escape, char_class, wildcard) and associated value.

    Returns:
        bool | None: True if the character matches the token, False if it
        doesn't match, or None if token type is unrecognized.
    """
    token_type = token["type"]

    if token_type == "literal":
        return char == token["value"]
    elif token_type == "escape":
        value = token["value"]
        if value == "\\d":
            return char.isdigit()
        elif value == "\\w":
            return char.isalnum() or char == "_"

        else:
            return char == value[1]

    elif token_type == "char_class":
        value = token["value"]
        if value.startswith("[^"):
            return char not in value[2:-1]
        else:
            return char in value[1:-1]

    elif token_type == "wildcard":
        return True
    return None


def calculate_min_match_length(tokens: list[dict]) -> int:
    """
    Count minimum number of characters required to match a sequence of tokens.

    Recursively evaluates the tokens and accounts for quantifiers ('+', '?') and
    grouped alternatives. The minimum length is utilized to determine valid starting
    positions when scanning input, thereby skipping positions where a match is
    impossible.

    Args:
        tokens (list[dict]): A list of parsed regex tokens representing the pattern.

    Returns:
        int: The minimum number of characters required to match the token sequence.
    """
    length = 0
    for token in tokens:
        token_type = token["type"]
        quantifier = token.get("quantifier")

        if token_type == "group":
            alternatives = token["alternatives"]
            min_alt_lengths = [calculate_min_match_length(alt) for alt in alternatives]
            group_min = min(min_alt_lengths)

            if quantifier == "?":
                length += 0
            elif quantifier == "+":
                length += group_min
            else:
                length += group_min

        else:
            if quantifier == "?":
                length += 0
            elif quantifier == "+":
                length += 1
            else:
                length += 1

    return length


def calculate_start_indices(
    input_length: int, min_length: int, has_start_anchor: bool
) -> list | range:
    """
    Calculates valid starting positions for pattern matching in a string.

    Considers the pattern’s minimum match length and any anchors to avoid
    unnecessary attempts. Matching begins at index 0 if the pattern has a
    start-of-line anchor (`^`), otherwise, returns all indices where the
    pattern could fit.

    Args:
        input_length (int): Length of the input string to match against.
        min_length (int): Minimum number of characters required for a match.
        has_start_anchor (bool): Whether the pattern starts with '^'.

    Returns:
        list[int] | range: Valid starting indices for attempting a match.
    """
    if has_start_anchor:
        return [0]
    else:
        return range(input_length - min_length + 1)


def count_greedy_matches(input_line: str, j: int, token: dict) -> int:
    """
    Counts maximum number of consecutive matches for a token from a given position.

    Iterates through the input string starting at index `j` and increments a
    counter for characters that match the given token. Used for the greedy
    behavior of the '+' quantifier in the pattern matching.

    Args:
        input_line (str): The string to test against the pattern.
        j (int): Current character position in the input string.
        token (dict): A parsed token dictionary specifying the type of match.

    Returns:
        int: The number of consecutive characters matching the token.
    """
    max_count = 0
    temp_j = j

    while temp_j < len(input_line):
        c = input_line[temp_j]
        if not character_matches_token(c, token):
            break
        max_count += 1
        temp_j += 1

    return max_count
