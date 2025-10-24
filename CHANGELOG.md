<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added `-B` / `--before-context` and `-C` / `--context` CLI flags to argument parser to show context before and after matches. `-C` overrides `-A` and `-B`.
- Added `-A` / `--after-context` CLI flag to argument parser for specifying number of lines to show after each match.
- Added docstrings to all test files.

### Fixed

- Resolved a series of pylint issues in the test files.

## [0.3.4] - 2025-10-21

### Fixed

- Removed unused argument `has_end_anchor` from function `calculate_start_indices()`.
- Improved error handling in `get_version()` by catching only `ModuleNotFoundError` and `AttributeError` instead of all exceptions.
- Updated file reading in `search_file()` to specify `encoding="utf-8"` and handle `UnicodeDecodeError` gracefully, ensuring consistent behavior across platforms.
- Improved error handing in `search_file()` and `get_files_recursively()` by catching `PermissionError` and `OSError` instead of all exceptions.
- Resolved pylint warning about unused `dirs` variable in `get_files_recursively()` by prefixing with underscore.
- Specifying `encoding="utf-8"` in `search_file()` and handling encoding mismatch with `UnicodeDecodeError`.
- Replaced broad `except Exception:` blocks in `main.py` with specific exception handling (`ValueError`, `IndexError`, `KeyError` for pattern errors; `PermissionError`, `OSError`, `FileNotFoundError` for file system errors) for more precise error reporting.
- Resolved pylint warnings in `main.py` by removing unused exception variable captures and eliminating redundant exception re-raise handler.

## [0.3.3] - 2025-10-21

### Added

- Added comprehensive docstrings to all 18 functions across `src/` modules
- Documented all function parameters, return values, and usage examples
- Standardized docstring format following Google/NumPy style guide

### Changed

- Enhanced code documentation for better maintainability and developer experience
- All functions now have clear descriptions of behavior, inputs, and outputs

## [0.3.2] - 2025-10-19

### Added

- Added full type hints to all functions in `src/` modules, including parameter and return types.

### Changed

- Updated API documentation in `docs/api.md` to show function signatures with type hints for clarity and consistency.
- Updated example code in `docs/contributing.md` to use type hints.

### Fixed

- Resolved minor inconsistencies in function signatures between code and documentation.

## [0.3.1] - 2025-10-19

### Changed

- Standardized function naming in `file_search.py`:

  - `file_search` → `search_file`
  - `multi_file_search` → `search_multiple_files`
  - `get_all_files_in_directory` → `get_files_recursively`
  - `search_in_directories` → `search_directory_recursively`

- Updated all imports and references in `src/` and `tests/` to use new function names
- Improved code readability and consistency across the codebase

## [0.3.0] - 2025-10-19

### Added

- Line number display with `-n` or `--line-number` flag
- Case-insensitive matching with `-i` or `--ignore-case` flag
- Inverted matching with `-v` or `--invert-match` flag
- Match counting with `-c` or `--count` flag

### Changed

- Migrated CLI from manual argument parsing to argparse
- Improved help text with automatic `--help` generation
- Changed CLI return format from tuple to namespace object
- Enhanced error messages for invalid arguments

### Removed

- Manual `sys.argv` parsing logic from `cli.py`

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
