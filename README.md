# grep-python

![Coverage](.github/coverage/coverage.svg) ![Python3.12](https://img.shields.io/badge/python-3.12%2B-blue)

A grep implementation built in Python with a custom regex engine using recursive backtracking. This started out as a [Codecrafters.io](https://app.codecrafters.io/courses/grep/overview) challenge, but has since been expanded upon with better functionality. This project has been developed as a personal learning exercise to understand how text search tools and regex engines work from the ground up.

The main goal is to make a developer-friendly search tool for code. Read more about planned features in the [Planned Development](#planned-development) section.

## Features

grep-python achieves essential grep parity with the following capabilities:

### Pattern Matching

- Custom regex engine with recursive backtracking
- Literals, groups `()`, alternation `|`, quantifiers `+` and `?`
- Character classes `[]`, wildcards `.`, anchors `^` and `$`
- Backreferences `\1`, `\2` for captured groups
- Escape sequences `\d`, `\w` for common patterns

### Search Capabilities

- Multiple pattern matching with `-e` flag or pattern files (`-f`)
- Recursive directory search (`-r`)
- Multiple file support with automatic filename prefixing
- Standard input support for pipeline integration

### Output Control

- Line numbers (`-n`)
- Context lines: before (`-B`), after (`-A`), or both (`-C`)
- Count only mode (`-c`)
- Quiet mode for scripting (`-q`)
- Files-only output: list matching (`-l`) or non-matching (`-L`) files
- Max count: limit results to first N matches (`-m`)

### Matching Options

- Case-insensitive search (`-i`)
- Inverted matching (`-v`)

## Installation

### Prerequisites

- Python 3.12 or higher
- Git

### From Source

```bash
# Clone the repository
git clone https://github.com/anbasement/grep-python.git
cd grep-python

# Make the shell wrapper executable
chmod +x pygrep.sh

# Run directly
./pygrep.sh --version
```

## Quick Start

### Basic Searching

```bash
# Search for a pattern in a file
./pygrep.sh "error" log.txt

# Search multiple files
./pygrep.sh "TODO" src/*.py

# Search from stdin
cat file.txt | ./pygrep.sh "pattern"
```

### Common Usage Patterns

```bash
# Find files with errors (useful for CI/CD)
./pygrep.sh -l "error" logs/*.txt

# Show context around matches
./pygrep.sh -C 3 "FIXME" src/main.py

# Case-insensitive search with line numbers
./pygrep.sh -i -n "warning" system.log

# Count occurrences across files
./pygrep.sh -c "import" src/**/*.py

# Search for multiple patterns
./pygrep.sh -e "error" -e "warning" -e "critical" app.log

# Exclude comments from source files
./pygrep.sh -v "^#" config.py
```

### Scripting Examples

```bash
# Check if file contains errors (exit code 0 if found)
if ./pygrep.sh -q "ERROR" log.txt; then
    echo "Errors detected!"
fi

# Find and process files with TODOs
for file in $(./pygrep.sh -l "TODO" src/*.py); do
    echo "Processing: $file"
done

# Limit output to first 5 matches
./pygrep.sh -m 5 "pattern" large_file.txt
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Pattern Syntax](docs/pattern_syntax.md)** - Complete regex syntax reference with examples
- **[Usage Examples](docs/examples.md)** - Real-world usage patterns and combinations
- **[Architecture Guide](docs/architecture.md)** - Internal design and implementation details
- **[API Reference](docs/api.md)** - Developer documentation for code understanding
- **[Performance Tips](docs/performance.md)** - Optimization strategies and benchmarks
- **[Contributing Guide](docs/contributing.md)** - Development workflow and standards

## Development

### Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage report
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest tests/test_pattern_matcher.py
```

### Code Quality

This project uses Black for formatting and Pylint for code quality:

```bash
# Format code (run first)
black src/ tests/

# Check code quality
pylint src/

# Combined workflow
black src/ tests/ && pylint src/
```

Configuration for both tools is in `pyproject.toml`.

### Version Management

This project uses [bump-my-version](https://github.com/callowayproject/bump-my-version):

```bash
# Show current version
bump-my-version show-bump

# Bump version (patch, minor, or major)
bump-my-version bump patch  # 0.3.16 -> 0.3.17
bump-my-version bump minor  # 0.3.16 -> 0.4.0
bump-my-version bump major  # 0.3.16 -> 1.0.0
```

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Project Structure

```text
grep-python/
├── src/                    # Source code
│   ├── main.py            # Program entry point
│   ├── cli.py             # Argument parsing
│   ├── file_search.py     # File operations and search coordination
│   ├── pattern_parser.py  # Regex pattern tokenization
│   ├── pattern_matcher.py # Pattern matching engine
│   └── constants.py       # Error messages and exit codes
├── tests/                 # Test suite
├── docs/                  # Documentation
├── pygrep.sh             # Shell wrapper script
└── pyproject.toml        # Project configuration
```

## Test Coverage

Current coverage: ~75%

The pattern matching engine uses recursive backtracking, which makes 100% coverage impractical without artificial test cases. Coverage focuses on:

- All user-facing features and CLI flags
- Common regex patterns and edge cases  
- Error handling and validation paths

## Exit Codes

- `0`: Pattern matched in at least one file
- `1`: No matches found
- `2`: Invalid arguments or error occurred

## Limitations

This is a learning project, not a production grep replacement:

- Supports a subset of full regex syntax (no `*`, lookahead, or other advanced features)
- Performance may not match GNU grep for very large files or complex patterns
- Backreferences limited to 9 groups
- Context lines not supported for stdin input

See the [Performance Guide](docs/performance.md) for optimization tips and benchmarks.

## Planned Development

The immediate plans for pygrep is to make it a developer-friendly tool:

- **Language-Aware Search**  
  Add support for searching within specific code elements (functions, comments, strings) using language detection and syntax parsing.

  Example:

  ```bash
  ./pygrep.sh --lang python --scope functions "def.*user"
  ```

- **Interactive Mode**  
  Build a live, terminal-based UI for searching and navigating results with arrow keys, previews, and editor integration.  
  Example:

  ```bash
  ./pygrep.sh -I "pattern" src/
  ```

- **Flexible Output Formatting**  
  Support output as JSON, Markdown tables, or syntax-highlighted text for easier integration with scripts and documentation.  
  Example:

  ```bash
  ./pygrep.sh --json "error" log.txt
  ```

- **Git Integration**  
  Enable searching only in tracked, modified, or branch-specific files, and display git blame info for matches.  
  Example:

  ```bash
  ./pygrep.sh --git "pattern" .
  ```

- **Search History & Bookmarks**  
  Save and reuse complex search queries, and view recent searches for faster workflows.

The end goal is to make a developer-friendly search tool with code understanding that can be integrated with modern workflows.

If you have suggestions or want to contribute, check out [docs/contributing.md](docs/contributing.md).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Codecrafters.io](https://codecrafters.io) for the initial challenge structure
- GNU grep for setting the standard for text search tools
- [CodeRabbit](https://coderabbit.ai) for AI-powered PR reviews
- [Claude](https://claude.ai) (Anthropic) for development assistance and documentation guidance
