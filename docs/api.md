<!-- markdownlint-disable MD024 -->
# API Reference

Internal API documentation for grep-python. Use this if you want to understand or modify the code.

## Core Modules

### pattern_parser.py

Converts regex strings into token lists that the matcher can use.

#### Functions

##### `parse_pattern(pattern: str) -> Tuple[List[Dict], bool, bool]`

Main function for parsing patterns.

**Parameters:**

- `pattern`: Regex string to parse

**Returns:**

- Tuple with:
  - `tokens`: List of token dictionaries
  - `has_start_anchor`: True if pattern starts with `^`
  - `has_end_anchor`: True if pattern ends with `$`

**Example:**

```python
from src.pattern_parser import parse_pattern

tokens, start_anchor, end_anchor = parse_pattern("^hello\\d+$")
# tokens: [{'type': 'literal', 'value': 'h'}, ...]
# start_anchor: True
# end_anchor: True
```

##### `find_matching_parentheses(pattern: str, start_index: int) -> int`

Finds the closing parenthesis for a group.

**Parameters:**

- `pattern`: The regex pattern string
- `start_index`: Index of opening parenthesis

**Returns:**

- Index of matching closing parenthesis

**Raises:**

- `ValueError`: If no matching parenthesis found

##### `split_alternatives(pattern: str) -> List[str]`

Splits pattern on pipe characters for alternation.

**Parameters:**

- `pattern`: Pattern string that might contain `|`

**Returns:**

- List of alternative pattern strings

### pattern_matcher.py

Does the actual pattern matching using recursive backtracking.

#### Functions

##### `match_pattern(input_line: str, pattern: str) -> bool`

Main function for pattern matching.

**Parameters:**

- `input_line`: String to search in
- `pattern`: Regex pattern

**Returns:**

- `True` if pattern matches anywhere in input, `False` otherwise

**Example:**

```python
from src.pattern_matcher import match_pattern

result = match_pattern("hello world", "w\\w+")
# result: True
```

##### `try_match(tokens, input_line, has_end_anchor, token_index, j, captures) -> bool`

Internal recursive matching function.

**Parameters:**

- `tokens`: Parsed token list
- `input_line`: Input string
- `has_end_anchor`: Whether pattern has end anchor
- `token_index`: Current token position
- `j`: Current input position
- `captures`: Dictionary of captured groups

**Returns:**

- `True` if remaining pattern matches from current position

##### `character_matches_token(char: str, token: Dict) -> bool`

Tests if a character matches a token.

**Parameters:**

- `char`: Single character to test
- `token`: Token dictionary

**Returns:**

- `True` if character matches token

**Token Types:**

- `literal`: Exact character match
- `escape`: Escape sequences (`\\d`, `\\w`)
- `char_class`: Character classes (`[abc]`, `[^xyz]`)
- `wildcard`: Dot (`.`) matches any character

##### `calculate_min_match_length(tokens: List[Dict]) -> int`

Calculates minimum characters needed for pattern to match.

**Parameters:**

- `tokens`: List of parsed tokens

**Returns:**

- Minimum number of characters needed

**Used for:** Optimization to reduce starting positions.

##### `count_greedy_matches(input_line: str, j: int, token: Dict) -> int`

Counts max consecutive matches for greedy quantifiers.

**Parameters:**

- `input_line`: Input string
- `j`: Starting position
- `token`: Token to match

**Returns:**

- Maximum number of consecutive matches

### file_search.py

Handles file operations and search across files.

#### Functions

##### `file_search(filename: str, pattern: str, print_filename: bool = False) -> bool`

Searches a file for pattern matches.

**Parameters:**

- `filename`: Path to file to search
- `pattern`: Regex pattern
- `print_filename`: Whether to print filename with matches

**Returns:**

- `True` if any matches found in file

**Error Handling:**

- Catches file access errors and prints to stderr
- Returns `False` for files that can't be read

##### `multiple_file_search(filenames: List[str], pattern: str) -> bool`

Searches multiple files for pattern matches.

**Parameters:**

- `filenames`: List of file paths
- `pattern`: Regex pattern

**Returns:**

- `True` if any matches found in any file

**Behavior:**

- Always prints filenames when searching multiple files
- Continues searching remaining files after errors

### cli.py

Command-line argument parsing.

#### Functions

##### `parse_arguments() -> tuple[bool, str, list[str]]`

Parses and validates command-line arguments.

**Returns:**

- `tuple`: `(recursive: bool, pattern: str, search_paths: list[str])`

**Exit Codes:**

- `EXIT_ERROR (2)`: Invalid arguments or missing required flags

**Validation:**

- Ensures `-E` flag is present
- Validates `-r` flag is followed by `-E`
- Checks for required pattern argument
- Returns empty list for search_paths when reading from stdin

**Error Handling:**

- Prints usage message for insufficient arguments
- Shows specific error for missing `-E` flag
- Exits immediately on validation failure

**Example:**

```python
from src.cli import parse_arguments

# Call from within main()
recursive, pattern, search_paths = parse_arguments()

if not search_paths:
    # Read from stdin
    ...
elif recursive:
    # Recursive directory search
    ...
else:
    # File search
    ...
```

### main.py

Program entry point and execution orchestration.

#### Functions

##### `main() -> None`

Main entry point - orchestrates pattern matching and file searching.

**Workflow:**

1. Calls `parse_arguments()` to get CLI configuration
2. Handles stdin input if no files specified
3. Delegates to appropriate search function (recursive/single/multi-file)
4. Exits with appropriate code based on results

**Exit Codes:**

- `0`: Pattern found in at least one file
- `1`: Pattern not found
- `2`: Error occurred

**Error Handling:**

- Catches exceptions during pattern matching
- Reports search failures with context
- Ensures proper cleanup and exit

### constants.py

Defines application constants and error messages.

#### Constants

##### Exit Codes

```python
EXIT_SUCCESS = 0  # Pattern found
EXIT_ERROR = 1    # Pattern not found or error
```

##### Error Messages

```python
ERROR_USAGE = "usage: {program} -E <pattern> [file ...]"
ERROR_EXPECTED_E_AFTER_R = "expected 'e' after 'r'"
ERROR_EXPECTED_E = "expected 'e' option"
ERROR_INVALID_PATTERN = "{filename}: invalid pattern"
ERROR_SEARCH_FAILED = "{filename}: search failed"
```

## Token Format Reference

### Token Structure

All tokens are dictionaries with at least a `type` field:

```python
{
    "type": "token_type",
    # ... additional fields based on type
    "quantifier": "+" | "?"  # Optional quantifier
}
```

### Token Types

#### Literal Token

```python
{
    "type": "literal",
    "value": "a"  # Single character
}
```

#### Escape Token

```python
{
    "type": "escape",
    "value": "\\d"  # Full escape sequence
}
```

Supported escapes:

- `\\d`: Digits (`[0-9]`)
- `\\w`: Word characters (`[a-zA-Z0-9_]`)
- `\\.`: Literal dot
- `\\\\`: Literal backslash

#### Character Class Token

```python
{
    "type": "char_class",
    "value": "[abc]"  # Full character class including brackets
}
```

#### Wildcard Token

```python
{
    "type": "wildcard"
}
```

#### Group Token

```python
{
    "type": "group",
    "alternatives": [
        [token1, token2, ...],  # First alternative
        [token3, token4, ...],  # Second alternative
    ],
    "number": 1  # Group number for backreferences
}
```

#### Backreference Token

```python
{
    "type": "backreference",
    "number": 1  # References group number
}
```

## Error Handling

### Exception Types

The codebase uses standard Python exceptions:

- `ValueError`: Malformed patterns, unmatched parentheses
- `IndexError`: Internal array access errors (should not reach user)
- `FileNotFoundError`: File access issues
- `PermissionError`: File permission issues

### Error Reporting

All user-facing errors follow this format:

```text
{filename}: {lowercase description}
```

Examples:

- `file.txt: no such file or directory`
- `input.txt: permission denied`
- `stdin: invalid pattern`

### Error Constants

Use constants from `constants.py` for consistent messaging:

```python
from src.constants import ERROR_INVALID_PATTERN, ERROR_SEARCH_FAILED

# Format with filename
error_msg = ERROR_INVALID_PATTERN.format(filename="test.txt")
print(error_msg, file=sys.stderr)
```

## Performance Considerations

### Time Complexity

- **Simple patterns**: O(n) where n = input length
- **Complex patterns**: O(n × m) where m = pattern complexity
- **Pathological cases**: O(2^n) with excessive backtracking

### Optimization Strategies

1. **Anchor Detection**: Use start/end anchors to limit search positions
2. **Minimum Length**: Calculate minimum match length to reduce starting positions
3. **Early Termination**: Stop on first match (grep behavior)
4. **Greedy Matching**: Use greedy quantifiers to reduce backtracking

### Memory Usage

- **Token Storage**: O(pattern_length)
- **Recursion Stack**: O(max_recursion_depth)
- **Capture Groups**: O(group_count × capture_length)

## Extension Points

### Adding New Token Types

1. **Parser**: Add recognition logic in `parse_pattern()`
2. **Matcher**: Add handling in `character_matches_token()` and `try_match()`
3. **Tests**: Add comprehensive test coverage

Example structure for new token type:

```python
# In parser
if char == 'X':  # New syntax
    tokens.append({
        "type": "new_type",
        "value": some_value
    })

# In matcher
elif token_type == "new_type":
    # Implement matching logic
    return match_result
```

### Adding New Quantifiers

Extend quantifier handling in `try_match()`:

```python
elif quantifier == "*":  # New quantifier
    # Implement zero-or-more logic
    pass
```

### Performance Optimizations

Potential areas for optimization:

- Replace recursion with iterative approach
- Implement NFA/DFA compilation
- Add pattern caching for repeated searches
- Optimize character class matching

## Testing API

### Test Utilities

Common test patterns used throughout the test suite:

```python
# Pattern testing
def test_pattern_cases(pattern, test_cases):
    """Test pattern against multiple input cases."""
    for input_str, expected in test_cases:
        result = match_pattern(input_str, pattern)
        assert result == expected

# File testing with temporary files
def test_file_search_with_temp_file():
    """Test file search with temporary test data."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        f.flush()
        result = file_search(f.name, "test")
        assert result is True
```

### Integration Testing

Test CLI behavior:

```python
import subprocess

def test_cli_integration():
    """Test complete CLI workflow."""
    result = subprocess.run([
        "python", "-m", "src.main", 
        "-E", "pattern", "file.txt"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    # Verify output format
```

### Unit Testing CLI

Test argument parsing directly:

```python
import sys
from src.cli import parse_arguments

def test_parse_arguments(monkeypatch):
    """Test argument parsing logic."""
    monkeypatch.setattr(sys, "argv", ["pygrep", "-E", "test", "file.txt"])
    recursive, pattern, search_paths = parse_arguments()
    
    assert recursive is False
    assert pattern == "test"
    assert search_paths == ["file.txt"]
```

This API reference provides the foundation for understanding and extending grep-python's functionality.
