<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Max count support via `-m` / `--max-count` CLI flag to stop searching after N matches (0 = unlimited).
- `max_count` parameter to all search functions (`search_file`, `search_multiple_files`, `search_directory_recursively`).
- Early exit optimization when max count limit is reached for improved performance on large files or recursive searches.
- Comprehensive tests for max count functionality covering basic usage, edge cases (first match, no matches, fewer than limit, patterns list, context combinations).
- Detailed documentation and examples for max count feature including basic usage, flag combinations, and practical use cases.

### Changed

- Return semantics for max count mode: returns `True` if limit reached, `False` if fewer matches exist than the limit.
- CLI exit codes now include max count behavior: 0 if max count reached, 1 if fewer matches found than limit.

## [0.3.14] - 2025-10-25

### Added

- Comprehensive tests for quiet mode functionality covering output suppression, return values, and early exit behavior.
- Added documentation and examples for the new quiet mode functionality.

## [0.3.13] - 2025-10-25

### Added

- Quiet mode support via `-q`, `--quiet`, and `--silent` flags to suppress all output and exit immediately on first match.
- `quiet` parameter to all search functions (`search_file`, `search_multiple_files`, `search_directory_recursively`).
- Early exit optimization in quiet mode for improved performance with large files.

## [0.3.12] - 2025-10-25

### Added

- Comprehensive tests for `-e` flag parsing and matching behavior.
- Comprehensive tests for `-f` flag pattern loading and error handling.

### Changed

- Comprehensive update of documentation, including examples and OR logic explanation.

## [0.3.11] - 2025-10-25

### Added

- Support for multiple pattern matching via `-e` flag (can be used multiple times to specify additional patterns).
- Support for reading patterns from a file with the `-f` flag (one pattern per line, empty lines ignored, UTF-8 encoding).
- Pattern validation requiring at least one pattern from any source (positional, `-e`, or `-f`).
- OR logic for multiple patterns: a line matches if it matches ANY of the provided patterns.
- Added `patterns` parameter to `search_file()`, `search_multiple_files()`, and `search_directory_recursively()` functions.

### Changed

- Made positional pattern argument optional (`nargs="?"`), allowing patterns to be specified via `-e` or `-f` instead.
- All search functions now accept and combine patterns from multiple sources.
- CLI argument parsing builds combined pattern list from all sources (positional, `-e` flags, `-f` file).

### Fixed

- Removed unnecessary explicit `"r"` mode in `open()` calls (default mode).
- Moved before-context buffer append to after match processing to prevent matched lines appearing in their own context.

## [0.3.10] - 2025-10-25

### Added

- Support for specifying patterns with the `-e` / `--regexp` flag (can be used multiple times).
- Pattern validation logic: pygrep now requires at least one pattern to be specified via positional argument, `-e`, or `-f` flag.
- Support for reading patterns from a file with the `-f` / `--file` flag. Blank lines are skipped and an error is shown if the file does not exist.

### Changed

- Made the positional pattern argument optional by adding `nargs="?"`

## [0.3.9] - 2025-10-25

### Added

- Comprehensive documentation update for completed context feature.
- Comprehensive tests for context matching.

### Fixed

- Moved buffer append for before-context to after all match processing logic to ensure the buffer only contains the lines before the match.

## [0.3.8] - 2025-10-25

### Added

- Adding `after_context` and `before_context` params to `search_multiple_files()` function and passing them through calls to `search_file()`.
- Adding `after_context` and `before_context` params to `search_directory_recursively()` function and passing them through calls to `search_file()`.

## [0.3.7] - 2025-10-25

### Fixed

- Fixed overlapping context lines for before-context (`-B`), after-context (`-A`), and combined context (`-C`) flags. Lines that appear in multiple context windows are now only printed once.

## [0.3.6] - 2025-10-24

### Added

- `-B` / `--before-context` CLI flag for showing lines before each match.
- Added `before_context` parameter to `search_file()` and related functions.
- Integrated circular buffer using `collections.deque` to store and print before-context lines.
- Implemented before-context logic: prints up to N lines before each match, matching grep's behavior.
- Wired `-B` flag through CLI and `main.py` so before-context works end-to-end.

### Changed

- Removed `"r"` from `open()` in `search_file()` as it's the default mode.

## [0.3.5] - 2025-10-24

### Added

- Added `-B` / `--before-context` and `-C` / `--context` CLI flags to argument parser to show context before and after matches. `-C` overrides `-A` and `-B`.
- Added `-A` / `--after-context` CLI flag to argument parser for specifying number of lines to show after each match.
- Added docstrings to all test files.
- Added helper function `_format_line_output()` in `file_search.py` for consistent output of match and context lines.
- Added after-context logic (`-A`) to `search_file()` and wired it through main.py.

### Changed

- Project specifies Python 3.12+ required.
- Replaced `Dict`, `List` and `Tuple` in type hints with `dict`, `list` and `tuple` for consistency.

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
