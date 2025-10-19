# Pattern Syntax Reference

Regex syntax reference for grep-python.

## Overview

grep-python has a custom regex engine that supports common regex features. It uses recursive backtracking and covers most basic patterns you'll need.

## Supported Features

### Literal Characters

Match exact characters.

```bash
./pygrep.sh -E "hello" file.txt
```

Matches lines with the exact string "hello".

### Anchors

Control where matches happen in a line.

| Anchor | Description | Example | Matches |
|--------|-------------|---------|---------|
| `^` | Start of line | `^hello` | Lines starting with "hello" |
| `$` | End of line | `world$` | Lines ending with "world" |
| `^...$` | Entire line | `^hello$` | Lines containing only "hello" |

### Character Classes

Match any character from a set.

| Syntax | Description | Example | Matches |
|--------|-------------|---------|---------|
| `[abc]` | Any of a, b, or c | `[aeiou]` | Any vowel |
| `[^abc]` | Anything except a, b, or c | `[^0-9]` | Any non-digit |
| `[a-z]` | Range from a to z | `[a-zA-Z]` | Any letter |

### Escape Sequences

Special character patterns.

| Sequence | Description | Equivalent | Example |
|----------|-------------|------------|---------|
| `\d` | Any digit | `[0-9]` | `\d+` matches "123" |
| `\w` | Word character | `[a-zA-Z0-9_]` | `\w+` matches "hello_world" |
| `\.` | Literal dot | | `3\.14` matches "3.14" |
| `\\` | Literal backslash | | `\\n` matches "\n" |

### Wildcards

| Symbol | Description | Example | Matches |
|--------|-------------|---------|---------|
| `.` | Any single character | `c.t` | "cat", "cot", "cut", "c3t" |

### Quantifiers

Control how many times a pattern should match.

| Quantifier | Description | Example | Matches |
|------------|-------------|---------|---------|
| `+` | One or more | `a+` | "a", "aa", "aaa", etc. |
| `?` | Zero or one | `colou?r` | "color", "colour" |

**Note**: Quantifiers apply to the immediately preceding element:

- `ab+` matches "a" followed by one or more "b"
- `(ab)+` matches one or more repetitions of "ab"

### Groups and Alternation

| Feature | Syntax | Description | Example |
|---------|--------|-------------|---------|
| Grouping | `(...)` | Group patterns together | `(cat)+` |
| Alternation | `(a\|b)` | Match either a or b | `(cat\|dog)` |
| Nested Groups | `((a\|b)c)+` | Groups within groups | Complex patterns |

### Backreferences

Reference previously captured groups.

| Syntax | Description | Example | Matches |
|--------|-------------|---------|---------|
| `\1` | First captured group | `(cat) and \1` | "cat and cat" |
| `\2` | Second captured group | `(cat) (dog) \2 \1` | "cat dog dog cat" |

**Limitations**: Currently supports up to 9 backreferences (`\1` through `\9`).

## Pattern Examples

### Basic Patterns

```bash
# Exact match
./pygrep.sh -E "hello" file.txt

# Case-sensitive matching (default)
./pygrep.sh -E "Hello" file.txt  # Different from "hello"

# Case-insensitive matching
./pygrep.sh -i -E "hello" file.txt  # Matches "hello", "Hello", "HELLO", etc.
```

### Anchored Patterns

```bash
# Lines starting with "Error"
./pygrep.sh -E "^Error" log.txt

# Lines ending with semicolon
./pygrep.sh -E ";$" code.js

# Empty lines
./pygrep.sh -E "^$" file.txt

# Lines with exactly 5 characters
./pygrep.sh -E "^.....$" file.txt
```

### Character Class Patterns

```bash
# Lines containing vowels
./pygrep.sh -E "[aeiou]" file.txt

# Lines with no digits
./pygrep.sh -E "^[^0-9]*$" file.txt

# Hexadecimal numbers
./pygrep.sh -E "[0-9a-fA-F]+" file.txt

# Lines starting with uppercase letter
./pygrep.sh -E "^[A-Z]" file.txt
```

### Quantifier Patterns

```bash
# One or more digits
./pygrep.sh -E "\d+" file.txt

# Optional 's' at end of word
./pygrep.sh -E "cats?" file.txt  # matches "cat" or "cats"

# Multiple spaces
./pygrep.sh -E " +" file.txt  # one or more spaces

# Word followed by optional punctuation
./pygrep.sh -E "\w+[.,!?]?" file.txt
```

### Group and Alternation Patterns

```bash
# Either "cat" or "dog"
./pygrep.sh -E "(cat|dog)" file.txt

# Color variations
./pygrep.sh -E "(red|green|blue)" file.txt

# Repeated groups
./pygrep.sh -E "(na)+" file.txt  # "na", "nana", "nanana", etc.

# Complex alternation
./pygrep.sh -E "(Mr|Mrs|Dr)\.? \w+" file.txt
```

### Backreference Patterns

```bash
# Repeated words
./pygrep.sh -E "(\w+) \1" file.txt  # "the the", "word word"

# Palindromes (3 characters)
./pygrep.sh -E "(.).\1" file.txt  # "aba", "xyx"

# Matching quotes
./pygrep.sh -E "([\"\']).*\1" file.txt  # "hello" or 'hello'

# HTML tags
./pygrep.sh -E "<(\w+)>.*</\1>" file.txt  # <div>content</div>
```

### Advanced Patterns

```bash
# Email-like patterns (simplified)
./pygrep.sh -E "\w+@\w+\.\w+" file.txt

# IP address octets
./pygrep.sh -E "\d+\.\d+\.\d+\.\d+" file.txt

# Phone numbers (US format)
./pygrep.sh -E "\d\d\d-\d\d\d-\d\d\d\d" file.txt

# Time format (HH:MM)
./pygrep.sh -E "\d\d:\d\d" file.txt
```

## Pattern Composition

### Building Complex Patterns

Start simple and build complexity gradually:

```bash
# Step 1: Match any word
\w+

# Step 2: Match word followed by colon
\w+:

# Step 3: Match word, colon, and value
\w+: \w+

# Step 4: Make value optional
\w+:( \w+)?

# Step 5: Allow multiple formats
\w+:( \w+| \d+)?
```

### Common Pattern Idioms

```bash
# Optional whitespace
 ?

# One or more whitespace
 +

# Word boundaries (approximate)
\w+

# Non-greedy matching (not directly supported)
# Use specific patterns instead

# Line with only whitespace
^ *$

# Non-empty lines
^.+$
```

## Limitations

### Unsupported Features

- **Lazy quantifiers**: `*?`, `+?`, `??`
- **Repetition counts**: `{n}`, `{n,m}`
- **Word boundaries**: `\b`, `\B`
- **Unicode categories**: `\p{L}`, `\P{N}`
- **Lookahead/Lookbehind**: `(?=...)`, `(?<=...)`
- **Non-capturing groups**: `(?:...)`
- **Case-insensitive flags**: `(?i)`

### Performance Notes

- **Backtracking**: Complex patterns with many alternatives can be slow
- **Greedy quantifiers**: May cause excessive backtracking
- **Deep nesting**: Deeply nested groups increase recursion depth

### Workarounds

```bash
# Instead of {3} repetition
\d\d\d

# Instead of case-insensitive matching
(hello|Hello|HELLO)

# Instead of non-capturing groups
# Use regular groups and ignore the capture
```

## Error Messages

### Common Pattern Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Unmatched opening parenthesis" | Missing `)` | Add closing parenthesis |
| "Expected 'e' after 'r'" | Missing `-E` flag | Add `-E` before pattern |
| "Invalid pattern" | Malformed regex | Check pattern syntax |

### Debugging Tips

1. **Start simple**: Test basic pattern first
2. **Add complexity gradually**: Build up complex patterns step by step
3. **Test edge cases**: Empty lines, special characters
4. **Use test files**: Create small test files for pattern development

## Best Practices

### Pattern Design

1. **Be specific**: Use anchors when position matters
2. **Escape special characters**: Use `\.` for literal dots
3. **Group logically**: Use parentheses to clarify intent
4. **Test thoroughly**: Verify both positive and negative cases

### Performance

1. **Avoid deep nesting**: Keep group nesting shallow
2. **Use specific patterns**: Prefer `\d` over `[0-9]` when appropriate
3. **Anchor when possible**: Use `^` and `$` to reduce search space
4. **Test with large files**: Verify performance on realistic data

### Maintainability

1. **Document complex patterns**: Add comments explaining pattern purpose
2. **Use meaningful examples**: Test with realistic data
3. **Break down complex patterns**: Split into simpler components when possible
