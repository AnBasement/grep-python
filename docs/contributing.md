<!-- markdownlint-disable MD024 -->
# Contributing

Guidelines for contributing to grep-python.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- Virtual environment (recommended)

### Development Setup

1. **Fork and Clone**

   ```bash
   git clone https://github.com/yourusername/grep-python.git
   cd grep-python
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Tests**

   ```bash
   python -m pytest tests/
   ```

## Development Workflow

### Code Style

This project uses Black for formatting and Pylint for code quality:

```bash
# Format code (run before committing)
black src/ tests/

# Check code quality
pylint src/

# Combined workflow
black src/ tests/ && pylint src/
```

### Testing

Always add tests for new features:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_pattern_matcher.py

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test
python -m pytest tests/test_pattern_matcher.py::test_basic_literal_matching
```

### Version Management

This project uses [bump-my-version](https://github.com/callowayproject/bump-my-version):

```bash
# Check current version and bump options
bump-my-version show-bump

# Bump version (maintainers only)
bump-my-version bump patch
```

## Contribution Types

### Bug Fixes

1. **Create Issue**: Report the bug with reproduction steps
2. **Write Test**: Add a failing test that demonstrates the bug
3. **Fix Bug**: Implement the fix
4. **Verify**: Ensure the test passes and no regressions occur

Example bug fix workflow:

```bash
# Create feature branch
git checkout -b fix-issue-123

# Write failing test
# Edit tests/test_pattern_matcher.py

# Run test to confirm it fails
python -m pytest tests/test_pattern_matcher.py::test_bug_fix -v

# Implement fix
# Edit src/pattern_matcher.py

# Verify fix
python -m pytest tests/test_pattern_matcher.py::test_bug_fix -v
python -m pytest tests/  # Run all tests

# Format and lint
black src/ tests/ && pylint src/
```

### New Features

1. **Discuss First**: Open an issue to discuss the feature
2. **Design**: Consider impact on existing API and performance
3. **Implement**: Add feature with comprehensive tests
4. **Document**: Update documentation and examples

Feature development checklist:

- [ ] Issue created and discussed
- [ ] Tests written (including edge cases)
- [ ] Implementation completed
- [ ] Documentation updated
- [ ] Examples added
- [ ] Performance impact assessed

### Documentation

Documentation contributions are highly valued:

- Fix typos or improve clarity
- Add more examples
- Improve API documentation
- Update architecture documentation

## Code Guidelines

### Python Style

- **Formatting**: Use Black (88-character line length)
- **Quality**: Follow Pylint recommendations (configured in `pyproject.toml`)
- **Naming**: Use snake_case for functions/variables, PascalCase for classes
- **Imports**: Group imports logically, use absolute imports

### Testing

- **Coverage**: Aim for high test coverage (>90%)
- **Test Names**: Use descriptive test function names
- **Test Structure**: Arrange-Act-Assert pattern
- **Edge Cases**: Test boundary conditions and error cases

Example test structure:

```python
def test_pattern_matching_with_quantifiers():
    """Test pattern matching behavior with + quantifiers."""
    # Arrange
    pattern = "a+"
    test_cases = [
        ("a", True),
        ("aa", True),
        ("aaa", True),
        ("", False),
        ("b", False),
    ]
    
    # Act & Assert
    for input_line, expected in test_cases:
        result = match_pattern(input_line, pattern)
        assert result == expected, f"Pattern '{pattern}' on input '{input_line}'"
```

### Documentation

- **Docstrings**: Use comprehensive docstrings for all public functions
- **Comments**: Explain complex logic, not obvious code
- **Examples**: Include usage examples in docstrings
- **Type Hints**: Add type hints for function parameters and returns

Example docstring:

```python
def match_pattern(input_line: str, pattern: str, ignore_case: bool = False) -> bool:
    """
    Check if a pattern matches anywhere in the input line.
    
    Args:
        input_line: The string to search within
        pattern: Regular expression pattern to match
        ignore_case: Whether to ignore case distinctions
        
    Returns:
        True if pattern matches, False otherwise
        
    Examples:
        >>> match_pattern("hello world", "hello")
        True
        >>> match_pattern("hello world", "goodbye")
        False
        
    Raises:
        ValueError: If pattern is malformed
    """
```

## Commit Guidelines

### Commit Message Format

Use conventional commit format:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Examples:

```bash
feat(parser): add support for character ranges in classes

fix(matcher): resolve backtracking issue with nested groups

docs(readme): update installation instructions

test(parser): add tests for edge cases in group parsing
```

### Commit Best Practices

- **Atomic commits**: One logical change per commit
- **Clear messages**: Describe what and why, not how
- **Test before commit**: Ensure all tests pass
- **Format before commit**: Run Black and Pylint

## Pull Request Process

### Before Submitting

1. **Rebase**: Rebase your branch on latest main
2. **Test**: Run full test suite
3. **Format**: Apply Black formatting
4. **Lint**: Fix Pylint issues
5. **Documentation**: Update relevant docs

```bash
# Pre-submission checklist
git rebase main
python -m pytest tests/
black src/ tests/
pylint src/
# Update CHANGELOG.md if needed
```

### Pull Request Template

Include this information in your PR:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] All existing tests pass
- [ ] New tests added for changes
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if needed)
```

### Review Process

- **Automated checks**: Must pass CI/CD checks
- **Code review**: At least one maintainer review required
- **Testing**: Verify functionality works as expected
- **Documentation**: Ensure docs are accurate and complete

## Issue Guidelines

### Bug Reports

Include this information:

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version:
- Operating system:
- grep-python version:

## Additional Context
Any other relevant information
```

### Feature Requests

Include this information:

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Implementation
How might this be implemented?

## Alternatives Considered
Other approaches that were considered
```

## Code Architecture

### Adding New Pattern Features

When adding new regex features:

1. **Parser**: Update `pattern_parser.py` to recognize new syntax
2. **Matcher**: Update `pattern_matcher.py` to handle new token types
3. **Tests**: Add comprehensive tests for the new feature
4. **Documentation**: Update pattern syntax documentation

### Performance Considerations

- **Benchmark**: Test performance impact of changes
- **Optimize**: Consider algorithmic improvements
- **Profile**: Use profiling tools for complex changes
- **Memory**: Consider memory usage patterns

### Backward Compatibility

- **API**: Maintain existing API compatibility
- **Behavior**: Preserve existing pattern behavior
- **Migration**: Provide migration path for breaking changes

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update CHANGELOG.md**: Document all changes
2. **Version bump**: Use bump-my-version
3. **Tag release**: Create Git tag
4. **Documentation**: Ensure docs are current
5. **Testing**: Full test suite pass

## Getting Help

### Resources

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions for questions
- **Code**: Read existing code for patterns

### Community

- **Be respectful**: Follow code of conduct
- **Be patient**: Maintainers are volunteers
- **Be helpful**: Help other contributors
- **Be constructive**: Provide actionable feedback

## Recognition

Contributors will be:

- Listed in CHANGELOG.md for their contributions
- Mentioned in release notes for significant features
- Added to contributors list (if they desire)

Thank you for contributing to grep-python!
