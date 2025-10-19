<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.3] - 2025-10-19

### Changed

- Removed duplicate argument parsing code from `main.py`
- Simplified `main.py` to focus on orchestration only
- Updated `docs/architecture.md` to reflect `cli.py` and `main.py` separation
- Updated `docs/api.md` with complete `cli.py` API documentation and examples

## [0.2.2] - 2025-10-19

### Added

- Unit tests for `parse_arguments()` function in `test_cli.py`

### Changed

- Extracted argument parsing logic from `main.py` to dedicated `parse_arguments()` function in `cli.py`
- Improved code organization and testability of CLI argument handling

### Fixed

- Fixed `.bumpversion.toml` missing a `=` and incorrectly updating `__init__.py`
- IndexError in `cli.py` when pattern argument is missing after `-E` flag

## [0.2.1] - 2025-10-19

### Fixed

- Test failures in `test_file_search.py` due to error message format changes
- Test failures in `test_main_cli.py` due to exit code changes
- Version mismatch in `test_init.py` (updated to 0.2.0)
- Updated `.bumpversion.toml` to update `__init__.py` on version bump

## [0.2.0] - 2025-10-19

### Added

- Created `/docs` directory with comprehensive project documentation
- `docs/pattern_syntax.md` - Regex syntax reference with examples
- `docs/examples.md` - Usage examples and scenarios
- `docs/architecture.md` - Internal design and code structure
- `docs/api.md` - Developer API reference with function specifications
- `docs/performance.md` - Performance optimization guide and benchmarking
- `docs/contributing.md` - Development guidelines and contribution process
- `docs/README.md` - Documentation navigation guide

### Changed

- Streamlined README.md, moved detailes to dedicated files in the docs/ folder
- README now focuses on quick start and navigation
- Removed redundant examples and syntax details from README
- Updated all script references from `./your_program.sh` to `./pygrep.sh` across all documentation

## [0.1.2] - 2025-10-19

### Added

- `pyproject.toml` configuration file for Black and Pylint integration
- Comprehensive code style documentation in README

### Changed

- Applied Black code formatting across all Python files for consistency
- Updated README.md with detailed Black + Pylint workflow instructions
- Configured Pylint to work harmoniously with Black (88-character line length)
- Disabled overly strict Pylint warnings for complex pattern matching functions

## [0.1.1] - 2025-10-19

### Added

- Error message constants in `constants.py` for consistent messaging
- Comprehensive version bumping documentation in `docs/version-bumping.md`

### Changed

- Standardized all error messages to follow `{filename}: {description}` format
- All error message descriptions now use lowercase for consistency
- Error messages now properly redirect to stderr across all modules
- Improved argument validation to prevent IndexError crashes

### Fixed

- IndexError when running program with insufficient command-line arguments
- Inconsistent error message formatting between `main.py` and `file_search.py`
- Missing stderr redirection for CLI error messages

## [0.1.0] - 2025-10-19

### Added

- Initial implementation of grep-python with custom regex engine
- Pattern parsing with support for:
  - Literal characters and escape sequences (`\d`, `\w`)
  - Character classes (`[abc]`, `[^xyz]`)
  - Wildcards (`.`)
  - Anchors (`^` start, `$` end)
  - Groups with alternation `(ab|cd)`
  - Quantifiers (`+` one or more, `?` zero or one)
  - Backreferences (`\1`, `\2`, etc.)
- File search capabilities:
  - Single file search
  - Multiple file search
  - Recursive directory search (`-r` flag)
  - Standard input support
- Command-line interface with `-E` flag for extended regex
- Comprehensive test suite with excellent coverage:
  - Unit tests for all modules
  - Integration tests for CLI functionality
  - Error condition and edge case testing
- Proper error handling for file operations and pattern matching
- Exit codes compatible with standard grep (0=match, 1=no match, 2=error)
- Shell script wrapper (`pygrep.sh`) for easy execution
- Modular code organization split into logical components:
  - `src/pattern_parser.py` - Pattern tokenization and parsing
  - `src/pattern_matcher.py` - Matching algorithms and logic
  - `src/file_search.py` - File operations and directory traversal
  - `src/main.py` - Main entry point and CLI logic
  - `src/constants.py` - Constants and exit codes
- pytest test framework with coverage reporting
- Code formatting with black
- Linting with pylint
- Virtual environment support
- MIT License
