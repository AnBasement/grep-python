<!-- markdownlint-disable MD024 -->
# Examples

Usage examples for grep-python.

## Basic Usage

### Simple Text Search

Search for a word in a file:

```bash
./pygrep.sh -E "hello" example.txt
```

Search multiple files:

```bash
./pygrep.sh -E "error" log1.txt log2.txt log3.txt
```

Search from stdin:

```bash
echo "hello world" | ./pygrep.sh -E "hello"
cat file.txt | ./pygrep.sh -E "pattern"
```

## Command-Line Options

### Line Numbers (`-n`, `--line-number`)

Display line numbers with matching lines:

```bash
# Show line numbers for matches
./pygrep.sh -n -E "error" log.txt

# Useful for identifying specific locations
./pygrep.sh --line-number -E "TODO" src/main.py
```

Output format:

```text
15:First matching line
42:Second matching line
```

### Case-Insensitive Search (`-i`, `--ignore-case`)

Ignore case distinctions in pattern and input:

```bash
# Match "error", "Error", "ERROR", etc.
./pygrep.sh -i -E "error" log.txt

# Find function names regardless of case
./pygrep.sh --ignore-case -E "getuser" code.py
```

### Inverted Match (`-v`, `--invert-match`)

Select lines that do NOT match the pattern:

```bash
# Show all lines except comments
./pygrep.sh -v -E "^#" config.txt

# Exclude empty lines
./pygrep.sh -v -E "^$" data.txt

# Find non-error lines
./pygrep.sh --invert-match -E "error" log.txt
```

### Count Matches (`-c`, `--count`)

Print only the count of matching lines:

```bash
# Count error occurrences
./pygrep.sh -c -E "error" log.txt

# Count TODO items
./pygrep.sh --count -E "TODO" src/*.py
```

Output format:

```text
log.txt:42
```

### After-Context (`-A`, `--after-context`)

Display lines after each match for additional context:

```bash
# Show 2 lines after each match
./pygrep.sh -A 2 -E "error" log.txt

# Show 5 lines after function definitions
./pygrep.sh --after-context 5 -E "^def " code.py

# Combine with line numbers
./pygrep.sh -n -A 3 -E "TODO" notes.txt
```

Output format (example):

```text
15:Error: File not found
16:  at line 42
17:  in module main
```

### Before-Context (`-B`, `--before-context`)

Display lines before each match to see what led up to it:

```bash
# Show 3 lines before each error
./pygrep.sh -B 3 -E "error" log.txt

# Show context before function calls
./pygrep.sh --before-context 2 -E "execute\(" code.py

# Find matches with preceding context
./pygrep.sh -B 5 -E "CRITICAL" system.log
```

Output format (example):

```text
42:  Processing request
43:  Validating input
44:  Checking permissions
45:Error: Access denied
```

### Combined Context (`-C`, `--context`)

Display lines both before and after matches:

```bash
# Show 2 lines of context around each match
./pygrep.sh -C 2 -E "exception" log.txt

# Show 3 lines before and after
./pygrep.sh --context 3 -E "TODO" code.py

# Useful for understanding match context
./pygrep.sh -C 1 -E "import numpy" *.py
```

Output format (example):

```text
10:import sys
11:import os
12:import numpy as np
13:import pandas
14:from typing import List
```

**Note:** Context lines are automatically deduplicated when match regions overlap, ensuring each line is printed only once.

### Combining Options

Options can be combined for powerful searches:

```bash
# Case-insensitive search with line numbers
./pygrep.sh -i -n -E "error" log.txt

# Count non-matching lines (inverted count)
./pygrep.sh -v -c -E "^#" config.txt

# Recursive case-insensitive search with line numbers
./pygrep.sh -r -i -n -E "TODO" src/

# Context with line numbers for debugging
./pygrep.sh -n -C 3 -E "exception" log.txt

# Case-insensitive context search
./pygrep.sh -i -A 2 -E "error" *.log

# Recursive search with before-context
./pygrep.sh -r -B 5 -E "def main" src/

# Find and count empty lines recursively
./pygrep.sh -r -c -E "^$" .
```

## Multiple Patterns

Search for multiple patterns at once using the `-e` flag or read patterns from a file with the `-f` flag. Lines match if **ANY** pattern matches (OR logic).

### Multiple `-e` Flags

Specify multiple patterns directly on the command line:

```bash
# Search for "error" OR "warning"
./pygrep.sh -e "error" -e "warning" log.txt

# Find multiple function names
./pygrep.sh -e "^def parse" -e "^def match" code.py

# Search for different severities
./pygrep.sh -e "ERROR" -e "WARN" -e "CRITICAL" system.log
```

Output example:

```text
15:ERROR: Connection failed
42:WARN: Retry attempt 3
89:CRITICAL: Out of memory
```

### Pattern File (`-f`)

Read patterns from a file (one pattern per line):

```bash
# Create a patterns file
cat > patterns.txt << 'EOF'
error
warning
exception
EOF

# Search using the patterns file
./pygrep.sh -f patterns.txt log.txt

# Combine with other options
./pygrep.sh -i -n -f patterns.txt *.log
```

**Pattern file format:**

- One pattern per line
- Empty lines are ignored
- UTF-8 encoding
- No special syntax (each line is treated as a pattern)

### Combining Pattern Sources

Mix positional patterns, `-e` flags, and `-f` files:

```bash
# Combine all three sources
./pygrep.sh -e "error" -f patterns.txt "manual" log.txt

# Multiple -e flags with a pattern file
./pygrep.sh -e "CRITICAL" -e "FATAL" -f common_errors.txt system.log

# Positional pattern with -e flags
./pygrep.sh "error" -e "warning" -e "exception" log.txt
```

All patterns are combined with OR logic—a line matches if it matches **any** of the patterns.

### Practical Examples

```bash
# Monitor logs for multiple error types
./pygrep.sh -e "error" -e "exception" -e "fatal" -A 2 /var/log/app.log

# Find todos from multiple developers
./pygrep.sh -e "TODO: alice" -e "TODO: bob" -e "FIXME" -r src/

# Search for multiple file types recursively
./pygrep.sh -e "\\.py$" -e "\\.js$" -e "\\.java$" -r .

# Case-insensitive search for multiple status codes
./pygrep.sh -i -e "200 OK" -e "404 NOT FOUND" -e "500 ERROR" access.log

# Combine patterns from file with additional patterns
./pygrep.sh -f banned_words.txt -e "URGENT" -e "ASAP" emails.txt
```

## Quiet Mode

Suppress all normal output and exit immediately with status 0 on the first match. Useful in shell scripts where you only care whether a match exists.

### Basic Quiet Mode

```bash
# Check if file contains errors (no output)
./pygrep.sh -q -E "error" log.txt
echo $?  # 0 if match found, 1 if not

# Use in conditional
if ./pygrep.sh -q -E "CRITICAL" system.log; then
    echo "Critical errors detected!"
    # Send alert, restart service, etc.
fi

# Short form with --quiet or --silent
./pygrep.sh --quiet -E "pattern" file.txt
./pygrep.sh --silent -E "pattern" file.txt
```

### Exit Codes

Quiet mode uses standard grep exit codes:

- **0**: Match found (success)
- **1**: No match found
- **2**: Error occurred (file not found, permission denied, etc.)

### Practical Examples

```bash
# Check multiple files for any matches
if ./pygrep.sh -q -e "error" -e "warning" *.log; then
    echo "Issues found in logs"
fi

# Exit early from script on match
./pygrep.sh -q "BUILD FAILED" build.log && exit 1

# Find first file with pattern in directory
for file in src/*.py; do
    if ./pygrep.sh -q "TODO" "$file"; then
        echo "Found TODO in: $file"
        break
    fi
done

# Combine with other flags (quiet overrides output options)
./pygrep.sh -q -n -i "pattern" file.txt  # -n has no effect in quiet mode

# Use in monitoring script
while true; do
    if ./pygrep.sh -q "OutOfMemoryError" /var/log/app.log; then
        send_alert "Memory issue detected"
        sleep 300  # Wait 5 minutes before checking again
    fi
    sleep 60
done
```

### Performance Benefits

Quiet mode is optimized for performance:

- **Early exit**: Stops reading file immediately after first match
- **No formatting**: Skips all output formatting operations
- **Minimal I/O**: Returns as soon as possible

This makes it ideal for checking large files where you only need to know if a pattern exists.

## Max Count

Stop searching after N matches with the `-m` flag. Useful for finding the first few occurrences without processing the entire file.

### Basic Max Count Usage

```bash
# Stop after first match
./pygrep.sh -m 1 -E "error" log.txt

# Find first 5 errors
./pygrep.sh -m 5 -E "ERROR" system.log

# Combine with line numbers
./pygrep.sh -m 3 -n -E "warning" output.log

# Use with case-insensitive search
./pygrep.sh -m 10 -i -E "todo" src/*.py
```

### Max Count with Other Features

```bash
# Max count with context (show first 2 matches with context)
./pygrep.sh -m 2 -A 2 -B 1 -E "exception" app.log

# Max count with multiple patterns
./pygrep.sh -m 5 -e "error" -e "critical" log.txt

# Max count with inverted match
./pygrep.sh -m 10 -v -E "^#" config.txt

# Max count with count-only flag
./pygrep.sh -m 100 -c -E "request" access.log

# Quiet mode with max count (useful in scripts)
if ./pygrep.sh -q -m 1 "CRITICAL" system.log; then
    echo "Critical error found"
    alert_admin
fi
```

### Practical Examples

```bash
# Monitor logs - show first 3 critical events
./pygrep.sh -m 3 -n -A 2 "CRITICAL" /var/log/app.log

# Find first few files with issues
for file in src/*.py; do
    if ./pygrep.sh -m 1 -q "TODO" "$file"; then
        echo "TODO in: $file"
    fi
done

# Get limited sample of matches for review
./pygrep.sh -m 20 -E "deprecated_function" codebase.txt | head -20

# Combined with recursive search - find first occurrence in any file
./pygrep.sh -r -m 1 "TODO" src/

# Process matches in batches
batch_size=10
offset=0
while true; do
    count=$(./pygrep.sh -m $((offset + batch_size)) "pattern" file.txt | wc -l)
    if [ $count -lt $batch_size ]; then
        break
    fi
    offset=$((offset + batch_size))
done
```

### Performance Benefits

Max count is optimized for performance:

- **Early exit**: Stops searching immediately after reaching the limit
- **Reduced I/O**: Doesn't read the entire file if limit is reached
- **Lower memory**: Doesn't need to store all matches

Especially useful for:

- Large log files (millions of lines)
- Recursive searches across many files
- Monitoring scripts that just need to know if matches exist
- Sampling/previewing matches without full processing

## Files-Only Output

Print only filenames instead of matching lines, useful for finding which files need attention or processing.

### Files with Matches (`-l`, `--files-with-matches`)

Print only the names of files containing matches:

```bash
# List Python files containing TODO comments
./pygrep.sh -l -E "TODO" src/*.py

# Find configuration files with errors
./pygrep.sh --files-with-matches -E "error" config/*.conf

# Combine with case-insensitive search
./pygrep.sh -l -i -E "fixme" src/*.py

# Use with multiple patterns
./pygrep.sh -l -e "TODO" -e "FIXME" -e "HACK" src/*.py
```

Output format (only filenames):

```text
src/main.py
src/utils.py
src/config.py
```

### Files without Matches (`-L`, `--files-without-match`)

Print only the names of files that do NOT contain any matches:

```bash
# Find Python files without tests
./pygrep.sh -L -E "def test_" src/*.py

# List files without TODO comments
./pygrep.sh --files-without-match -E "TODO" src/*.py

# Find source files without documentation
./pygrep.sh -L -E "\"\"\"" src/*.py

# Combine with case-insensitive search
./pygrep.sh -L -i -E "copyright" *.py
```

Output format (only filenames):

```text
src/helpers.py
src/models.py
```

**Note:** The `-l` and `-L` flags are mutually exclusive and cannot be used together.

### Practical Examples

```bash
# Find all files that need attention
for file in $(./pygrep.sh -l "FIXME" src/*.py); do
    echo "File needs fixing: $file"
    ./pygrep.sh -n "FIXME" "$file"
done

# Check which test files are missing assertions
./pygrep.sh -L "assert" tests/test_*.py

# Find files without license headers
./pygrep.sh -L "Copyright" src/*.py > unlicensed.txt

# Combine with recursive search
./pygrep.sh -r -l "deprecated" src/

# Use in CI/CD pipeline
if ./pygrep.sh -l "console\.log" src/*.js | grep -q .; then
    echo "Error: Debug statements found in source"
    exit 1
fi

# Find files that need documentation
./pygrep.sh -L -E "^def \w+.*:" src/*.py

# Compare files with and without matches
echo "Files with TODOs:"
./pygrep.sh -l "TODO" src/*.py
echo -e "\nFiles without TODOs:"
./pygrep.sh -L "TODO" src/*.py

# Process only files containing a pattern
for file in $(./pygrep.sh -l -E "class \w+" src/*.py); do
    echo "Processing $file..."
    python analyze.py "$file"
done
```

### Performance Benefits

Files-only modes are optimized for efficiency:

- **Early exit**: `-l` stops reading a file after the first match
- **Minimal output**: No line formatting or processing overhead
- **Fast scanning**: Ideal for checking many files quickly

This makes files-only modes perfect for:

- Finding files that need updates across a large codebase
- CI/CD checks to detect prohibited patterns
- Pre-commit hooks to validate code quality
- Build scripts that process only relevant files
- Quick audits of project structure

## Pattern Examples

### Literal Text Matching

Find exact text:

```bash
# Find lines with "function"
./pygrep.sh -E "function" code.js

# Find lines with email addresses (simple)
./pygrep.sh -E "@gmail.com" contacts.txt

# Find specific error messages
./pygrep.sh -E "Error 404" access.log
```

### Using Anchors

Match text at specific positions:

```bash
# Lines starting with "import"
./pygrep.sh -E "^import" main.py

# Lines ending with semicolon
./pygrep.sh -E ";$" script.js

# Empty lines
./pygrep.sh -E "^$" document.txt

# Lines with only whitespace
./pygrep.sh -E "^ *$" file.txt

# Lines that are exactly "TODO"
./pygrep.sh -E "^TODO$" notes.txt
```

### Character Classes

Match character sets:

```bash
# Lines containing digits
./pygrep.sh -E "[0-9]" data.txt

# Lines containing vowels
./pygrep.sh -E "[aeiou]" words.txt

# Lines without digits
./pygrep.sh -E "^[^0-9]*$" text-only.txt

# Lines starting with uppercase letters
./pygrep.sh -E "^[A-Z]" sentences.txt

# Hexadecimal values
./pygrep.sh -E "[0-9a-fA-F]" colors.css
```

### Escape Sequences

Use predefined character classes:

```bash
# Find numbers
./pygrep.sh -E "\d+" measurements.txt

# Find word characters
./pygrep.sh -E "\w+" identifiers.txt

# Find literal dots (periods)
./pygrep.sh -E "\." config.txt

# Find backslashes
./pygrep.sh -E "\\\\" file-paths.txt
```

### Wildcards

Match any character:

```bash
# Three-letter words ending in 'at'
./pygrep.sh -E ".at" words.txt

# File extensions
./pygrep.sh -E "\...." files.txt

# License plates (letter-digit-letter format)
./pygrep.sh -E "[A-Z].[A-Z]" plates.txt
```

### Quantifiers

Control repetition:

```bash
# One or more digits
./pygrep.sh -E "\d+" numbers.txt

# Optional 's' for plurals
./pygrep.sh -E "cats?" animals.txt

# Multiple consecutive spaces
./pygrep.sh -E "  +" messy-format.txt

# Words with optional punctuation
./pygrep.sh -E "\w+[.,!?]?" sentences.txt
```

### Groups and Alternation

Match alternatives:

```bash
# Either "cat" or "dog"
./pygrep.sh -E "(cat|dog)" pets.txt

# Different greeting formats
./pygrep.sh -E "(Hello|Hi|Hey)" messages.txt

# File extensions
./pygrep.sh -E "\.(txt|md|py)" filenames.txt

# HTTP methods
./pygrep.sh -E "(GET|POST|PUT|DELETE)" access.log
```

### Backreferences

Reference captured groups:

```bash
# Repeated words
./pygrep.sh -E "(\w+) \1" text.txt

# Matching quotes
./pygrep.sh -E "(\".*\"|'.*')" code.txt

# HTML tags
./pygrep.sh -E "<(\w+)>.*</\1>" page.html

# Palindromes (3 characters)
./pygrep.sh -E "(.).\1" words.txt
```

## Real-World Scenarios

### Log File Analysis

Search web server logs:

```bash
# Error responses
./pygrep.sh -E " (404|500) " access.log

# POST requests
./pygrep.sh -E "POST " access.log

# IP addresses from specific subnet
./pygrep.sh -E "192\.168\.\d+\.\d+" access.log

# Today's entries (assuming YYYY-MM-DD format)
./pygrep.sh -E "2025-10-19" app.log
```

### Code Analysis

Search source code:

```bash
# Function definitions (Python)
./pygrep.sh -E "^def \w+" *.py

# TODO comments
./pygrep.sh -E "TODO:" src/*.py

# Import statements
./pygrep.sh -E "^import " main.py

# Variable assignments
./pygrep.sh -E "\w+ = " code.py
```

### Configuration Files

Search configuration:

```bash
# Database settings
./pygrep.sh -E "database" config.yml

# Port numbers
./pygrep.sh -E "port: \d+" settings.yaml

# Boolean values
./pygrep.sh -E "(true|false)" config.json

# Environment variables
./pygrep.sh -E "^\w+=" .env
```

### Data Processing

Search structured data:

```bash
# Email addresses (basic)
./pygrep.sh -E "\w+@\w+\.\w+" contacts.txt

# Phone numbers (XXX-XXX-XXXX)
./pygrep.sh -E "\d\d\d-\d\d\d-\d\d\d\d" directory.txt

# Dates (MM/DD/YYYY)
./pygrep.sh -E "\d\d/\d\d/\d\d\d\d" events.txt

# Currency amounts
./pygrep.sh -E "\$\d+\.\d\d" prices.txt
```

## Advanced Examples

### Complex Pattern Building

Start simple and add complexity:

```bash
# Step 1: Find any word
./pygrep.sh -E "\w+" text.txt

# Step 2: Find capitalized words
./pygrep.sh -E "[A-Z]\w+" text.txt

# Step 3: Find proper nouns (capitalized, not at start of line)
./pygrep.sh -E " [A-Z]\w+" text.txt

# Step 4: Find proper nouns with optional title
./pygrep.sh -E " (Mr\. |Mrs\. |Dr\. )?[A-Z]\w+" text.txt
```

### Combining Multiple Patterns

Use multiple searches for complex queries:

```bash
# Find Python files with TODO comments
./pygrep.sh -E "\.py$" filelist.txt | \
  xargs ./pygrep.sh -E "TODO:"

# Find error logs from specific time period
./pygrep.sh -E "^2025-10-19 1[0-5]:" app.log | \
  ./pygrep.sh -E "(ERROR|FATAL)"
```

### Recursive Directory Search

Search entire directory trees:

```bash
# Find all Python files with main functions
./pygrep.sh -r -E "def main" src/

# Find configuration errors in any config file
./pygrep.sh -r -E "error" config/

# Find TODO comments across entire project
./pygrep.sh -r -E "TODO:" .
```

## Pattern Testing and Development

### Creating Test Cases

Build patterns incrementally:

```bash
# Create test file
cat > test.txt << EOF
hello world
Hello World
HELLO WORLD
goodbye world
123 hello 456
hello123
EOF

# Test basic pattern
./pygrep.sh -E "hello" test.txt

# Test case sensitivity
./pygrep.sh -E "(hello|Hello|HELLO)" test.txt

# Test word boundaries (approximate)
./pygrep.sh -E "\w*hello\w*" test.txt
```

### Debugging Patterns

When patterns don't work as expected:

```bash
# Start with simplest version
./pygrep.sh -E "cat" test.txt

# Add one feature at a time
./pygrep.sh -E "(cat)" test.txt
./pygrep.sh -E "(cat|dog)" test.txt
./pygrep.sh -E "(cat|dog)+" test.txt

# Test on minimal data
echo "cat dog cat" | ./pygrep.sh -E "(cat) \1"
```

## Performance Considerations

### Efficient Patterns

Choose faster patterns when possible:

```bash
# Faster: specific anchor
./pygrep.sh -E "^Error" large-log.txt

# Slower: general search
./pygrep.sh -E "Error" large-log.txt

# Faster: specific character class
./pygrep.sh -E "\d" numbers.txt

# Slower: general class
./pygrep.sh -E "[0-9]" numbers.txt
```

### Avoiding Slow Patterns

Some patterns can cause excessive backtracking:

```bash
# Potentially slow: many alternatives
./pygrep.sh -E "(a|a)*" file.txt

# Better: simplified pattern
./pygrep.sh -E "a+" file.txt

# Potentially slow: nested groups with quantifiers
./pygrep.sh -E "((a+)+)+" file.txt

# Better: flatten the pattern
./pygrep.sh -E "a+" file.txt
```

## Error Handling Examples

### Common Mistakes and Solutions

Pattern errors:

```bash
# Error: Missing -E flag
./pygrep.sh "pattern" file.txt
# Solution: Add -E flag
./pygrep.sh -E "pattern" file.txt

# Error: Unmatched parenthesis
./pygrep.sh -E "(cat" file.txt
# Solution: Close parenthesis
./pygrep.sh -E "(cat)" file.txt

# Error: Invalid backreference
./pygrep.sh -E "\1" file.txt
# Solution: Create group first
./pygrep.sh -E "(cat) \1" file.txt
```

File handling:

```bash
# Missing file
./pygrep.sh -E "pattern" nonexistent.txt
# Output: nonexistent.txt: no such file or directory

# Permission denied
./pygrep.sh -E "pattern" /root/secret.txt
# Output: /root/secret.txt: permission denied

# Directory instead of file
./pygrep.sh -E "pattern" directory/
# Output: directory/: is a directory
```

## Integration Examples

### With Other Tools

Combine with standard Unix tools:

```bash
# Count matches
./pygrep.sh -E "error" app.log | wc -l

# Get unique matches
./pygrep.sh -E "\w+@\w+\.\w+" contacts.txt | sort -u

# Process results
./pygrep.sh -E "^\d+" data.txt | while read line; do
  echo "Found number: $line"
done

# Combine with find
find . -name "*.py" -exec ./pygrep.sh -E "TODO:" {} \;
```

### Shell Scripts

Use in automation:

```bash
#!/bin/bash
# Check for sensitive data in code
if ./pygrep.sh -r -E "(password|secret|api_key)" src/; then
  echo "Warning: Sensitive data found in source code!"
  exit 1
fi

# Daily log analysis
LOG_FILE="/var/log/app.log"
DATE=$(date +%Y-%m-%d)

echo "Errors today:"
./pygrep.sh -E "^$DATE.*ERROR" "$LOG_FILE"

echo "Warnings today:"
./pygrep.sh -E "^$DATE.*WARN" "$LOG_FILE"
```

This comprehensive example collection should help users understand how to effectively use grep-python for a wide variety of text processing tasks.
