import sys


def find_matching_parantheses(pattern, start_index):
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

            end_index = find_matching_parantheses(pattern, i)
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


def character_matches_token(char, token):
    """
    Checks if a character matches a token. Handles literal characters,
    escaped tokens like \\d and \\w, character classes like [abc] and
    [^xyz], negated classes and wildcards

    This collects all character-to-token logic in one place.
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


def calculate_min_match_length(tokens):
    """
    Counts every token and treat quantifiers (like +) as requiring the
    correct amount of matches to determine the valid starting indices for
    matching.
    """
    length = 0
    for token in tokens:
        token_type = token["type"]
        quantifier = token.get("quantifier")

        if token_type == "group":
            alternatives = token["alternatives"]
            min_alt_lengths = [
                calculate_min_match_length(alt)
                for alt in alternatives
            ]
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
        input_length,
        min_length,
        has_start_anchor,
        has_end_anchor
        ):
    """
    Calculates potential starting index for pattern matching.

    Uses the anchors and minimum match length to determine valid
    starting positions in the input string.

    Ensures that matching starts at positions requested by anchors and
    permitted by pattern length.
    """
    if has_start_anchor:
        return [0]
    elif has_end_anchor:
        return [input_length - min_length]
    else:
        return range(input_length - min_length + 1)


def count_greedy_matches(input_line, j, token):
    """
    Iterates from position j and counts the max number of consecutive
    matches for a token. Used in the logic for pattern matching for
    the greedy quantifier ('+').
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


def try_match(tokens, input_line, has_end_anchor, token_index, j, captures):
    """
    Goes back and attempts to match a token sequence to the input line.

    Checks for quantifiers and matches on every token.
    count_greedy_matches for '+' quantifiers, and character_matches for
    the rest.
    """
    if token_index == len(tokens):
        if has_end_anchor:
            return j == len(input_line)
        return True

    token = tokens[token_index]
    token_type = token["type"]
    quantifier = token.get("quantifier")

    if token_type == "group":
        group_start_position = j
        alternatives = token["alternatives"]

        if quantifier == "+":
            group_start_position = j
            matched_once = False

            for alt_tokens in alternatives:
                success, new_j = try_match_sequence(
                    alt_tokens,
                    input_line,
                    j,
                    captures
                )
                if success:
                    group_number = token.get("number")
                    if group_number is not None:
                        captures[group_number] = (
                            input_line[group_start_position:new_j]
                        )

                    matched_once = True
                    if try_match(
                        tokens,
                        input_line,
                        has_end_anchor,
                        token_index + 1,
                        new_j,
                        captures
                    ):
                        return True

            return matched_once and False

        elif quantifier == "?":
            group_start_position = j

            for alt_tokens in alternatives:
                success, new_j = try_match_sequence(
                    alt_tokens,
                    input_line,
                    j,
                    captures
                )
                if success:
                    group_number = token.get("number")
                    if group_number is not None:
                        captures[group_number] = (
                            input_line[group_start_position:new_j]
                        )

                    if try_match(
                        tokens,
                        input_line,
                        has_end_anchor,
                        token_index + 1,
                        new_j,
                        captures
                    ):
                        return True

            if try_match(
                tokens,
                input_line,
                has_end_anchor,
                token_index + 1,
                j,
                captures
            ):
                return True

            return False

        else:
            for alt_tokens in alternatives:
                success, new_j = try_match_sequence(
                    alt_tokens,
                    input_line,
                    j,
                    captures
                )
                if success:
                    group_number = token.get("number")
                    if group_number is not None:
                        captures[group_number] = (
                            input_line[group_start_position:new_j]
                        )

                    if try_match(
                        tokens,
                        input_line,
                        has_end_anchor,
                        token_index + 1,
                        new_j,
                        captures
                    ):
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

        if input_line[j:j+captured_len] != captured_text:
            return False

        return try_match(
            tokens,
            input_line,
            has_end_anchor,
            token_index + 1,
            j + captured_len,
            captures
        )

    elif quantifier == "+":
        max_count = count_greedy_matches(input_line, j, token)
        if max_count == 0:
            return False
        for count in range(max_count, 0, -1):
            if try_match(
                tokens,
                input_line,
                has_end_anchor,
                token_index + 1,
                j + count,
                captures
            ):
                return True

        return False

    elif quantifier == "?":
        single_match = (
            j < len(input_line)
            and character_matches_token(input_line[j], token)
            and try_match(
                tokens,
                input_line,
                has_end_anchor,
                token_index + 1,
                j + 1,
                captures
            )
        )
        no_match = try_match(
            tokens,
            input_line,
            has_end_anchor,
            token_index + 1,
            j,
            captures
        )
        return single_match or no_match

    else:
        if j >= len(input_line):
            return False
        c = input_line[j]
        if not character_matches_token(c, token):
            return False
        return try_match(
            tokens,
            input_line,
            has_end_anchor,
            token_index + 1,
            j + 1,
            captures
        )


def try_match_sequence(tokens, input_line, start_j, captures):
    """
    Matches a sequence of tokens against the input line at
    position start_j. Similar to the try_match() function, but
    returns the specific ending position instead of a boolean.

    Used for matching groups to find the position we end up
    at after a match.

    For instance, with input_line "catdog" and "cat" as tokens
    and start_j as 0 we return "True, j=3" as three characters
    were matched.
    """
    j = start_j

    for token in tokens:
        token_type = token["type"]
        quantifier = token.get("quantifier")

        if token_type == "group":
            group_start_position = j
            alternatives = token["alternatives"]

            if quantifier == "+":
                matched = False
                for alt_tokens in alternatives:
                    success, new_j = try_match_sequence(
                        alt_tokens,
                        input_line,
                        j,
                        captures
                    )
                    if success:
                        group_number = token.get("number")
                        if group_number is not None:
                            captures[group_number] = (
                                input_line[group_start_position:new_j]
                            )

                        j = new_j
                        matched = True
                        break
                if not matched:
                    return (False, start_j)

            elif quantifier == "?":
                for alt_tokens in alternatives:
                    success, new_j = try_match_sequence(
                        alt_tokens,
                        input_line,
                        j,
                        captures
                    )
                    if success:
                        group_number = token.get("number")
                        if group_number is not None:
                            captures[group_number] = (
                                input_line[group_start_position:new_j]
                            )
                        j = new_j
                        break

            else:
                matched = False
                for alt_tokens in alternatives:
                    success, new_j = try_match_sequence(
                        alt_tokens,
                        input_line,
                        j,
                        captures
                    )
                    if success:
                        group_number = token.get("number")
                        if group_number is not None:
                            captures[group_number] = (
                                input_line[group_start_position:new_j]
                            )
                        j = new_j
                        matched = True
                        break
                if not matched:
                    return (False, start_j)

        elif quantifier == "+":
            max_count = count_greedy_matches(input_line, j, token)
            if max_count == 0:
                return (False, start_j)
            j += max_count

        elif quantifier == "?":
            if j < len(input_line) and character_matches_token(
                input_line[j],
                token
            ):
                j += 1

        else:
            if j >= len(input_line):
                return (False, start_j)
            if not character_matches_token(input_line[j], token):
                return (False, start_j)
            j += 1

    return (True, j)


def match_pattern(input_line, pattern):
    """
    Main function for pattern matching.

    Parses the pattern and calculates minimum match length and indices.
    Calls try_match for each start index.
    """
    tokens, has_start_anchor, has_end_anchor = parse_pattern(pattern)
    min_length = calculate_min_match_length(tokens)
    start_indices = calculate_start_indices(
        len(input_line),
        min_length,
        has_start_anchor,
        has_end_anchor
    )

    for start_index in start_indices:
        captures = {}
        if try_match(
            tokens,
            input_line,
            has_end_anchor,
            0,
            start_index,
            captures
        ):
            return True

    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python app.py PATTERN [FILE]")
        sys.exit(1)

    pattern = sys.argv[1]

    if len(sys.argv) > 2:
        filename = sys.argv[2]
        with open(filename, "r") as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()

    for line in lines:
        line = line.rstrip("\n")
        if match_pattern(line, pattern):
            print(line)


if __name__ == "__main__":
    main()
