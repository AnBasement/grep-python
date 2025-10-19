# Architecture

Internal design and code structure of grep-python.

## Overview

grep-python uses a custom regex engine with recursive backtracking. The code is split into separate modules for parsing, matching, file operations, and CLI.

## Module Structure

```text
src/
├── __init__.py          # Package initialization
├── main.py              # Program entry point and orchestration
├── cli.py               # Command-line argument parsing
├── constants.py         # Error messages and exit codes
├── file_search.py       # File operations and search coordination
├── pattern_parser.py    # Regex pattern parsing
└── pattern_matcher.py   # Pattern matching engine
```

## Core Components

### 1. Pattern Parser (`pattern_parser.py`)

**Purpose**: Converts regex strings into tokens for matching.

**Key Functions**:

- `parse_pattern()` - Main entry point, returns tokens and anchor flags
- `find_matching_parentheses()` - Handles nested group parsing
- `split_alternatives()` - Processes alternation (`|`) within groups

**Token Types**:

```python
{
    "type": "literal",           # Regular characters
    "value": "a"
}

{
    "type": "escape",           # Escape sequences like \d, \w
    "value": "\\d"
}

{
    "type": "char_class",       # Character classes [abc], [^xyz]
    "value": "[aeiou]"
}

{
    "type": "wildcard"          # Dot (.) matches any character
}

{
    "type": "group",            # Parenthesized groups ()
    "alternatives": [...],       # For alternation (cat|dog)
    "number": 1                 # Group number for backreferences
}

{
    "type": "backreference",    # \1, \2, etc.
    "number": 1
}
```

**Quantifiers**: Added as `"quantifier": "+"` or `"quantifier": "?"` to tokens.

### 2. Pattern Matcher (`pattern_matcher.py`)

**Purpose**: Executes pattern matching using recursive backtracking algorithm.

**Key Functions**:

- `match_pattern()` - Main entry point with optional case-insensitive matching, returns boolean match result
- `try_match()` - Core recursive matching function
- `try_match_sequence()` - Matches token sequences (for groups)
- `character_matches_token()` - Individual character-to-token matching
- `count_greedy_matches()` - Implements greedy quantifier behavior

**Case-Insensitive Matching**:

When `ignore_case=True` is passed to `match_pattern()`, both the pattern and input text are converted to lowercase before matching. This enables case-insensitive searches with the `-i` flag.

**Algorithm Flow**:

1. Parse pattern into tokens
2. Apply case conversion if ignore_case is enabled
3. Calculate minimum match length for optimization
4. Try matching at each valid starting position
5. Use recursive backtracking for complex patterns
6. Handle quantifiers with greedy matching
7. Capture groups for backreferences

### 3. File Search (`file_search.py`)

**Purpose**: Coordinates file system operations and search execution.

**Key Functions**:

- `file_search()` - Searches single file line by line with optional line numbers, case-insensitivity, match inversion, and counting
- `multi_file_search()` - Handles multiple file operations with all output options
- `search_in_directories()` - Recursive directory traversal (when `-r` flag used)
- `get_all_files_in_directory()` - Recursively finds all files in a directory

**Output Options**:

- Line numbers (`print_line_number`) - Prefix matches with line number
- Case-insensitive (`ignore_case`) - Pass-through to pattern matcher
- Inverted match (`invert_match`) - Select non-matching lines
- Count only (`count_only`) - Print count instead of matches

**Error Handling**: Catches and reports file access errors gracefully.

### 4. Command Line Interface (`cli.py`)

**Purpose**: Parses and validates command-line arguments using argparse.

**Key Functions**:

- `parse_arguments()` - Returns argparse namespace object with parsed arguments
- `get_version()` - Retrieves version from package metadata

**Supported Arguments**:

- `pattern` - Required positional argument for regex pattern
- `files` - Optional positional arguments for file paths
- `-E`, `--extended-regexp` - Extended regex mode (always enabled, for compatibility)
- `-r`, `-R`, `--recursive` - Search directories recursively
- `-n`, `--line-number` - Display line numbers with matches
- `-i`, `--ignore-case` - Case-insensitive matching
- `-v`, `--invert-match` - Select non-matching lines
- `-c`, `--count` - Print count of matching lines only
- `--version` - Show version and exit
- `--help` - Show help message and exit

**Features**:

- Automatic help and version display via argparse
- Argument validation (recursive requires files)
- Professional error messages with usage hints
- Returns namespace object with all flags as attributes
- Exits with appropriate error codes for invalid input

### 5. Main Program (`main.py`)

**Purpose**: Program orchestration and execution flow.

**Features**:

- Calls `parse_arguments()` to get CLI configuration as namespace object
- Handles stdin input when no files specified (supports all flags)
- Coordinates pattern matching and file searching
- Passes feature flags to search functions (line_number, ignore_case, invert_match, count_only)
- Manages exit codes based on search results

## Design Patterns

### 1. Token-Based Parsing

Rather than parsing regex patterns directly during matching, we first tokenize them into structured data. This separates parsing concerns from matching logic and enables optimization.

### 2. Recursive Backtracking

The matching engine uses recursive backtracking to handle complex patterns:

- Each recursive call represents one step in the matching process
- Backtracking occurs when a match path fails
- State (capture groups) is preserved and restored during backtracking

### 3. Greedy Quantifiers

For `+` quantifiers, we implement greedy matching:

- Count maximum possible matches first
- Try matching from maximum down to minimum required
- Backtrack if later parts of pattern fail

### 4. Anchor Optimization

Start (`^`) and end (`$`) anchors enable significant optimization:

- Start anchor: only try matching at position 0
- End anchor: only accept matches that consume entire remaining input
- Combined: only try exact-length matches

## Error Handling Strategy

### Consistent Error Reporting

- All error messages follow `{filename}: {description}` format
- Error messages use lowercase descriptions for consistency
- All errors output to stderr, not stdout
- Centralized error constants in `constants.py`

### Graceful Degradation

- File access errors don't crash the program
- Invalid patterns are reported clearly
- Missing arguments show usage information

## Performance Characteristics

### Time Complexity

- **Best case**: O(n) for simple literal patterns
- **Average case**: O(n*m) where n=input length, m=pattern complexity
- **Worst case**: O(2^n) for pathological patterns with excessive backtracking

### Space Complexity

- **Parsing**: O(m) where m=pattern length
- **Matching**: O(d) where d=maximum recursion depth
- **Capture groups**: O(g*c) where g=group count, c=capture length

### Optimization Features

- Minimum match length calculation reduces starting positions
- Anchor detection enables position optimization
- Early termination on first match (grep behavior)

## Testing Strategy

### Unit Tests

- Each module has comprehensive unit tests
- Pattern parsing tests cover edge cases
- Matching tests include both positive and negative cases
- File operations tested with mocked file system

### Integration Tests

- End-to-end CLI testing with `test_main_cli.py`
- Unit tests for argument parsing in `test_cli.py`
- Multi-file search scenarios
- Error condition handling

## Future Architecture Considerations

### Potential Improvements

1. **Compiled Patterns**: Cache parsed patterns for reuse
2. **Finite Automata**: Replace backtracking with NFA/DFA for better performance
3. **Streaming**: Process large files without loading entirely into memory
4. **Parallelization**: Multi-threaded file processing
5. **JIT Compilation**: Dynamic code generation for hot patterns

### Extension Points

- Additional token types for new regex features
- Pluggable matching strategies (NFA vs backtracking)
- Custom character class definitions
- Unicode support infrastructure

## Code Style and Conventions

- **Formatting**: Black (88-character line length)
- **Quality**: Pylint with project-specific configuration
- **Naming**: Snake_case for functions/variables, PascalCase for classes
- **Documentation**: Comprehensive docstrings for all public functions
- **Type Hints**: Gradually being added for better IDE support
