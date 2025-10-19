# grep-python

A grep tool written in Python while following the [Codecrafters.io guide](https://app.codecrafters.io/courses/grep/overview) before being expanded upon with added functionality.

## Features

- **Custom regex engine**: Supports literals, groups `()`, alternation `|`, quantifiers `+` and `?`, character classes `[]`, start `^` and end `$` anchors, and backreferences (`\1`, `\2`, etc.).
- **Recursive search**: Optionally search directories recursively.
- **Multiple file support**: Search one or more files at once.
- **Standard input support**: Reads from stdin if no files are specified.

## Installation

### From Source

```bash
git clone https://github.com/anbasement/grep-python.git
cd grep-python
chmod +x your_program.sh
```

## Usage

### Basic Search

```bash
# Search for pattern in a file
./your_program.sh -E "pattern" file.txt

# Search multiple files
./your_program.sh -E "pattern" file1.txt file2.txt

# Search from stdin
echo "hello world" | ./your_program.sh -E "hello"
```

### Recursive Search

```bash
# Search all files in a directory recursively
./your_program.sh -r -E "pattern" directory/
```

### Pattern Examples

```bash
# Anchors
./your_program.sh -E "^start" file.txt    # Lines starting with "start"
./your_program.sh -E "end$" file.txt      # Lines ending with "end"

# Character classes
./your_program.sh -E "[aeiou]" file.txt   # Lines with vowels
./your_program.sh -E "[^0-9]" file.txt    # Lines with non-digits

# Quantifiers
./your_program.sh -E "a+" file.txt        # One or more 'a'
./your_program.sh -E "a?" file.txt        # Zero or one 'a'

# Wildcards
./your_program.sh -E "c.t" file.txt       # cat, cot, cut, etc.

# Escape sequences
./your_program.sh -E "\d+" file.txt       # One or more digits
./your_program.sh -E "\w+" file.txt       # One or more word characters

# Groups and alternation
./your_program.sh -E "(cat|dog)" file.txt # cat or dog

# Backreferences
./your_program.sh -E "(cat) and \1" file.txt  # "cat and cat"
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_pattern_matcher.py

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

## Exit Codes

- `0`: At least one match found.
- `1`: No matches found.

## Limitations

- Only a subset of full regular expression syntax is supported.
- Performance may not match native `grep` for large files or complex patterns.
- Backreferences are currently limited to 9 groups.

## TODO

- [ ] Add error handling
- [ ] Improve docstrings and add type hints
- [ ] Print matching lines to stdout (like standard grep)
- [ ] Add support for more regex features
- [ ] Improve performance for large files
- [ ] Add unit tests
- [ ] Add support for colored output (maybe with Rich library?)
- [ ] Create setup.py for pip install

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

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
