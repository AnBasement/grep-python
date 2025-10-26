<!-- markdownlint-disable MD024 -->
# API Reference

Internal API documentation for grep-python. Use this if you want to understand or modify the code.

## Core Modules

### pattern_parser.py

Converts regex strings into token lists that the matcher can use.

#### Functions

##### `parse_pattern(pattern: str, group_number: Optional[list[int]] = None) -> tuple[list[dict], bool, bool]`

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

##### `split_alternatives(pattern: str) -> list[str]`

Splits pattern on pipe characters for alternation.

**Parameters:**

- `pattern`: Pattern string that might contain `|`

**Returns:**

- List of alternative pattern strings

### pattern_matcher.py

Does the actual pattern matching using recursive backtracking.

#### Functions

##### `match_pattern(input_line: str, pattern: str, ignore_case: bool = False) -> bool`

Main function for pattern matching with optional case-insensitivity.

**Parameters:**

- `input_line` (str): String to search in
- `pattern` (str): Regex pattern
- `ignore_case` (bool): Whether to ignore case distinctions (default: False)

**Returns:**

- `True` if pattern matches anywhere in input, `False` otherwise

**Behavior:**

- When `ignore_case=True`, converts both pattern and input to lowercase before matching
- Uses recursive backtracking algorithm for matching
- Supports anchors (`^`, `$`), groups, alternation, quantifiers, character classes

**Example:**

```python
from src.pattern_matcher import match_pattern

# Basic matching
result = match_pattern("hello world", "w\\w+")
# result: True

# Case-insensitive matching
result = match_pattern("Hello World", "hello", ignore_case=True)
# result: True
```

##### `try_match(tokens: List[Dict], input_line: str, has_end_anchor: bool, token_index: int, j: int, captures: Dict[int, str]) -> bool`

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

##### `character_matches_token(char: str, token: Dict) -> bool | None`

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

### search_file.py

Handles file operations and search across files with output formatting.

#### Functions

##### `search_file(filename: str, pattern: str, print_filename: bool = False, print_line_number: bool = False, ignore_case: bool = False, invert_match: bool = False, count_only: bool = False, after_context: int = 0, before_context: int = 0, patterns: Optional[list[str]] = None, quiet: bool = False, max_count: int = 0, files_with_matches: bool = False, files_without_match: bool = False) -> bool`

Searches a file for pattern matches with configurable output options.

**Parameters:**

- `filename` (str): Path to file to search
- `pattern` (str): Regex pattern (positional pattern, can be None if patterns list provided)
- `print_filename` (bool): Whether to print filename with matches (default: False)
- `print_line_number` (bool): Whether to print line numbers with matches (default: False)
- `ignore_case` (bool): Whether to ignore case in matching (default: False)
- `invert_match` (bool): Whether to invert match (select non-matching lines) (default: False)
- `count_only` (bool): Whether to print only count instead of matches (default: False)
- `after_context` (int): Number of lines to print after each match (default: 0)
- `before_context` (int): Number of lines to print before each match (default: 0)
- `patterns` (Optional[list[str]]): Additional patterns to match (default: None)
- `quiet` (bool): Whether to suppress all output and exit on first match (default: False)
- `max_count` (int): Maximum number of matches to find before stopping (0 = unlimited) (default: 0)
- `files_with_matches` (bool): Whether to print only filenames containing matches (default: False)
- `files_without_match` (bool): Whether to print only filenames without matches (default: False)

**Returns:**

- `True` if `max_count` reached (or if any matches found and `max_count` is 0)
- `False` if no matches found (or fewer matches than `max_count` when `max_count` > 0)

**Behavior:**

- **Multiple patterns**: If `patterns` list is provided, combines it with the positional `pattern` parameter
- **OR logic**: A line matches if it matches ANY of the patterns (from both sources)
- **Quiet mode**: When `quiet=True`, suppresses all output and exits immediately on first match (performance optimization)
- **Max count**: When `max_count` > 0, stops searching and returns `True` once limit is reached; returns `False` if fewer matches exist than the limit
- Line numbers start at 1 (not 0)
- Context lines are automatically deduplicated when regions overlap
- Each line is printed at most once, even if it appears in multiple context windows
- Before-context uses a circular buffer to store recent lines
- After-context uses a counter to track remaining context lines
- With `count_only`, prints format: `filename:count` or just `count`
- With `invert_match`, matches logic is inverted
- Output format with line numbers: `line_number:line_content`
- All flags passed through to `match_pattern()`
- When `files_with_matches=True`, prints only the filename if any match is found (early exit optimization). When `files_without_match=True`, prints only the filename if no matches are found. These flags are mutually exclusive.

**Error Handling:**

- Catches file access errors and prints to stderr
- Returns `False` for files that can't be read

**Example:**

```python
# Basic search
found = search_file("data.txt", "error")

# With line numbers
found = search_file("log.txt", "error", print_line_number=True)

# Multiple patterns
found = search_file("log.txt", "error", patterns=["warning", "exception"])

# Quiet mode (no output, early exit)
found = search_file("file.txt", "pattern", quiet=True)

# Case-insensitive with count
found = search_file("file.txt", "TODO", ignore_case=True, count_only=True)

# Inverted match
found = search_file("config.txt", "^#", invert_match=True)
```

##### `search_multiple_files(filenames: List[str], pattern: str, print_line_number: bool = False, ignore_case: bool = False, invert_match: bool = False, count_only: bool = False, after_context: int = 0, before_context: int = 0, patterns: Optional[list[str]] = None, quiet: bool = False, max_count: int = 0, files_with_matches: bool = False, files_without_match: bool = False) -> bool`

Searches multiple files for pattern matches.

**Parameters:**

- `filenames` (list[str]): List of file paths
- `pattern` (str): Regex pattern (positional pattern, can be None if patterns list provided)
- `print_line_number` (bool): Whether to print line numbers (default: False)
- `ignore_case` (bool): Whether to ignore case (default: False)
- `invert_match` (bool): Whether to invert match (default: False)
- `count_only` (bool): Whether to print only counts (default: False)
- `after_context` (int): Number of lines to print after each match (default: 0)
- `before_context` (int): Number of lines to print before each match (default: 0)
- `patterns` (Optional[list[str]]): Additional patterns to match (default: None)
- `quiet` (bool): Whether to suppress all output and exit on first match (default: False)
- `max_count` (int): Maximum number of matches to find before stopping (0 = unlimited) (default: 0)
- `files_with_matches` (bool): Whether to print only filenames containing matches (default: False)
- `files_without_match` (bool): Whether to print only filenames without matches (default: False)

**Returns:**

- `True` if any matches found in any file (or if `max_count` reached)

**Behavior:**

- Always prints filenames when searching multiple files
- **Multiple patterns**: Passes `patterns` parameter to `search_file()` for each file
- **OR logic**: Lines match if they match ANY pattern from either source
- **Quiet mode**: Passes `quiet` parameter through to enable early exit across files
- Continues searching remaining files after errors
- Passes all flags to `search_file()`, including context parameters

##### `search_directory_recursively(directory: str, pattern: str, print_line_number: bool = False, ignore_case: bool = False, invert_match: bool = False, count_only: bool = False, after_context: int = 0, before_context: int = 0, patterns: Optional[list[str]] = None, quiet: bool = False, max_count: int = 0, files_with_matches: bool = False, files_without_match: bool = False) -> bool`

Recursively searches directories for pattern matches.

**Parameters:**

- `directory` (str): Directory path to search
- `pattern` (str): Regex pattern (positional pattern, can be None if patterns list provided)
- `print_line_number` (bool): Whether to print line numbers (default: False)
- `ignore_case` (bool): Whether to ignore case (default: False)
- `invert_match` (bool): Whether to invert match (default: False)
- `count_only` (bool): Whether to print only counts (default: False)
- `after_context` (int): Number of lines to print after each match (default: 0)
- `before_context` (int): Number of lines to print before each match (default: 0)
- `patterns` (Optional[list[str]]): Additional patterns to match (default: None)
- `quiet` (bool): Whether to suppress all output and exit on first match (default: False)
- `max_count` (int): Maximum number of matches to find before stopping (0 = unlimited) (default: 0)
- `files_with_matches` (bool): Whether to print only filenames containing matches (default: False)
- `files_without_match` (bool): Whether to print only filenames without matches (default: False)

**Returns:**

- `True` if any matches found in any file (or if `max_count` reached)

**Behavior:**

- Recursively finds all files in directories
- **Multiple patterns**: Passes `patterns` parameter through to file search functions
- **OR logic**: Lines match if they match ANY pattern from either source
- **Quiet mode**: Passes `quiet` parameter through to enable early exit
- Searches each file with `search_file()`
- Passes all flags through, including context parameters

##### `get_files_recursively(directory: str) -> List[str]`

Recursively finds all files in a directory.

**Parameters:**

- `directory` (str): Directory path to search

**Returns:**

- List of file paths (strings)

**Behavior:**

- Uses `os.walk()` for recursive traversal
- Returns only files, not directories
- Absolute paths for all files

### cli.py

Command-line argument parsing using argparse.

#### Functions

##### `get_version() -> str`

Retrieves the version string from `src/__init__.py`.

**Returns:**

- `str`: Version string (e.g., "0.2.3")

**Implementation:**

Uses `importlib.metadata.version('grep-python')` to dynamically retrieve version.

##### `parse_arguments() -> argparse.Namespace`

Parses and validates command-line arguments using argparse.

**Returns:**

- `argparse.Namespace`: Object with parsed arguments as attributes
  - `pattern` (str): Regex pattern to search for
  - `files` (list[str]): Files or directories to search
  - `recursive` (bool): Enable recursive directory search
  - `line_number` (bool): Print line numbers with matches
  - `ignore_case` (bool): Ignore case distinctions
  - `invert_match` (bool): Select non-matching lines
  - `count_only` (bool): Print count of matches instead of lines
  - `after_context` (int): Number of lines to print after matches
  - `before_context` (int): Number of lines to print before matches
  - `context` (int): Number of lines to print before and after matches
  - `files_with_matches` (bool): Print only filenames with matches
  - `files_without_match` (bool): Print only filenames without matches

**Available Arguments:**

- `pattern`: Positional argument for regex pattern (optional if `-e` or `-f` is used)
- `files`: Optional positional arguments for file paths (reads stdin if none)
- `-E`, `--extended-regexp`: Extended regex mode (always enabled, for compatibility)
- `-e PATTERNS`, `--regexp PATTERNS`: Specify pattern(s) (can be used multiple times)
- `-f FILE`, `--file FILE`: Read patterns from file (one per line, empty lines ignored)
- `-r`, `-R`, `--recursive`: Search directories recursively
- `-n`, `--line-number`: Display line numbers with output
- `-i`, `--ignore-case`: Case-insensitive matching
- `-v`, `--invert-match`: Select lines that do NOT match
- `-c`, `--count`: Print only count of matching lines
- `-A NUM`, `--after-context NUM`: Print NUM lines after each match
- `-B NUM`, `--before-context NUM`: Print NUM lines before each match
- `-C NUM`, `--context NUM`: Print NUM lines before and after each match
- `-q`, `--quiet`, `--silent`: Suppress all output, exit immediately on first match
- `-m NUM`, `--max-count NUM`: Stop searching after NUM matches (0 = unlimited)
- `-l`, `--files-with-matches`: Print only names of files containing matches
- `-L`, `--files-without-match`: Print only names of files without matches
- `--version`: Show version and exit
- `--help`: Show help message and exit

**Pattern Sources:**

- Patterns can be specified via positional argument, `-e` flag(s), or `-f` file
- Multiple `-e` flags can be used to specify multiple patterns
- Pattern file (`-f`) contains one pattern per line (UTF-8 encoding)
- All sources are combined: a line matches if it matches ANY pattern (OR logic)
- At least one pattern must be provided from any source

**Context Behavior:**

- When `-C` is specified, it sets both `before_context` and `after_context`
- Context lines are deduplicated when regions overlap
- Context is not applied to stdin input (streaming limitation)

**Quiet Mode:**

- Suppresses all normal output (match lines, filenames, counts, etc.)
- Returns immediately after first match (early exit optimization)
- Exit code indicates match status: 0 if match found, 1 if not, 2 on error
- Useful in shell scripts for checking if pattern exists without processing output

**Max Count Mode:**

- When `-m NUM` is specified with `NUM > 0`, stops after finding NUM matches
- Returns 0 (match found) if limit is reached
- Returns 1 (no match) if fewer matches exist than the limit
- Useful for finding first N occurrences or sampling large files
- Combines with other options: `-m 3 -n` prints first 3 matches with line numbers

**Files-Only Modes:**

- When `-l` is specified, prints only filenames that contain at least one match
- When `-L` is specified, prints only filenames that contain no matches
- These flags are mutually exclusive and cannot be used together
- `-l` uses early exit optimization (stops reading file after first match)
- Output shows only filenames, one per line, without line content or numbers
- Useful for finding files that need processing or validation

**Exit Codes:**

- `EXIT_MATCH_FOUND (0)`: Pattern matched (normal operation or quiet/max-count mode)
- `EXIT_NO_MATCH (1)`: No matches found (or fewer than max-count)
- `EXIT_ERROR (2)`: Invalid arguments or validation failure

**Validation:**

- Recursive mode requires at least one file path
- At least one pattern must be provided (via positional, `-e`, or `-f`)
- Pattern file (`-f`) must exist and be readable

**Error Handling:**

- Argparse automatically handles invalid arguments
- Custom validation for recursive mode without files
- Custom validation for missing patterns
- File reading errors for pattern files
- Professional error messages with usage hints

**Example:**

```python
from src.cli import parse_arguments

# Call from within main()
args = parse_arguments()

# Access arguments as attributes
pattern = args.pattern  # Positional pattern (may be None)
pattern_list = args.pattern_list  # Combined patterns from all sources
files = args.files
recursive = args.recursive
line_number = args.line_number
ignore_case = args.ignore_case
invert_match = args.invert_match
count_only = args.count_only

# Use in logic
if not files:
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
2. Handles stdin input if no files specified (with all flag support)
3. Delegates to appropriate search function (recursive/single/multi-file)
4. Passes flags to search functions for feature enablement
5. Exits with appropriate code based on results

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
def test_search_file_with_temp_file():
    """Test file search with temporary test data."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        f.flush()
        result = search_file(f.name, "test")
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
