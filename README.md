# grep-python

![Coverage](./coverage.svg)
A grep tool written in Python while following the [Codecrafters.io guide](https://app.codecrafters.io/courses/grep/overview) before being expanded upon with added functionality.

## Features

- **Custom regex engine**: Supports literals, groups `()`, alternation `|`, quantifiers `+` and `?`, character classes `[]`, start `^` and end `$` anchors, and backreferences (`\1`, `\2`, etc.).
- **Recursive search**: Search directories recursively with `-r` flag.
- **Multiple file support**: Search one or more files at once.
- **Standard input support**: Reads from stdin if no files are specified.
- **Line numbers**: Display line numbers with `-n` flag.
- **Case-insensitive**: Ignore case distinctions with `-i` flag.
- **Inverted match**: Select non-matching lines with `-v` flag.
- **Count matches**: Print count of matching lines with `-c` flag.

## Installation

### From Source

```bash
git clone https://github.com/anbasement/grep-python.git
cd grep-python
chmod +x pygrep.sh
```

## Quick Start

```bash
# Search for pattern in a file
./pygrep.sh -E "pattern" file.txt

# Search multiple files
./pygrep.sh -E "pattern" file1.txt file2.txt

# Search from stdin
echo "hello world" | ./pygrep.sh -E "hello"

# Recursive search
./pygrep.sh -r -E "pattern" directory/

# Show line numbers
./pygrep.sh -n -E "error" log.txt

# Case-insensitive search
./pygrep.sh -i -E "error" log.txt

# Show non-matching lines
./pygrep.sh -v -E "^#" config.txt

# Count matches
./pygrep.sh -c -E "TODO" src/*.py
```

## Documentation

Comprehensive documentation is available in the `/docs` folder:

- **[Pattern Syntax](docs/pattern_syntax.md)** - Complete regex syntax reference
- **[Examples](docs/examples.md)** - Real-world usage examples
- **[Architecture](docs/architecture.md)** - Internal design and code structure
- **[API Reference](docs/api.md)** - Developer API documentation
- **[Performance Guide](docs/performance.md)** - Optimization tips and benchmarking
- **[Contributing](docs/contributing.md)** - Development guidelines

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

### Code Style

This project uses Black for code formatting and Pylint for code quality checks.

```bash
# Format code with Black (run first)
black src/ tests/

# Check code quality with Pylint
pylint src/

# Format and lint everything
black src/ tests/ && pylint src/
```

**Workflow**: Always run Black first to format, then Pylint to check quality. Black and Pylint are configured to work together via `pyproject.toml`.

### Version Management

This project uses [bump-my-version](https://github.com/callowayproject/bump-my-version) for version management.

```bash
# Show current version and bump options
bump-my-version show-bump

# Bump patch version (0.1.0 -> 0.1.1)
bump-my-version bump patch

# Bump minor version (0.1.0 -> 0.2.0) 
bump-my-version bump minor

# Bump major version (0.1.0 -> 1.0.0)
bump-my-version bump major
```

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Test Coverage

Current coverage: ~80%

The pattern matching engine uses recursive backtracking, which makes 100%
coverage impractical without artificial test cases. As a result, `pattern_matcher.py`
has low coverage hovering around 55%. Coverage focuses on:

- All user-facing features and CLI flags
- Common regex patterns and edge cases
- Error handling paths

## Exit Codes

- `0`: At least one match found.
- `1`: No matches found.

## Limitations

- Only a subset of full regular expression syntax is supported.
- Performance may not match native `grep` for large files or complex patterns.
- Backreferences are currently limited to 9 groups.

See the [Performance Guide](docs/performance.md) for optimization tips.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built as a learning project to understand:

- Regular expression engines
- Recursive backtracking algorithms
- File system operations
- Command-line tool design

## Resources

- [GNU grep documentation](https://www.gnu.org/software/grep/manual/)
- [Regular expression theory](https://en.wikipedia.org/wiki/Regular_expression)
- [Extended Regular Expressions (ERE)](https://en.wikipedia.org/wiki/Regular_expression#POSIX_extended)
