# Performance Guide

Performance info, optimization tips, and benchmarking for grep-python.

## Performance Overview

grep-python uses recursive backtracking for pattern matching. This works well for most patterns but can be slow for complex ones.

### Time Complexity

#### Best Case: O(n)

Simple patterns without backtracking:

```bash
# Linear scan, no backtracking
./pygrep.sh -E "hello" file.txt
./pygrep.sh -E "^Error" log.txt  # Start anchor optimization
```

#### Average Case: O(n × m)

Most practical patterns where:

- n = input text length
- m = pattern complexity factor

```bash
# Typical patterns with moderate complexity
./pygrep.sh -E "[a-z]+" file.txt
./pygrep.sh -E "\d\d-\d\d-\d\d\d\d" dates.txt
```

#### Worst Case: O(2^n)

Bad patterns that cause excessive backtracking:

```bash
# Catastrophic backtracking patterns (avoid)
./pygrep.sh -E "(a+)+b" file.txt
./pygrep.sh -E "(a|a)*" file.txt
```

### Space Complexity

#### Memory Usage

- **Pattern parsing**: O(m) where m = pattern length
- **Recursion stack**: O(d) where d = max recursion depth
- **Capture groups**: O(g × c) where g = group count, c = capture length

#### Practical Limits

- **Recursion depth**: Limited by Python's recursion limit (~1000 levels)
- **File size**: No built-in limit, processes files line by line
- **Pattern complexity**: Exponential growth for nested groups with quantifiers

## Optimization Strategies

### Pattern Design

#### Use Anchors When Possible

Anchors dramatically reduce search space:

```bash
# Optimized: Only check line start
./pygrep.sh -E "^ERROR" large.log

# Slower: Check every position
./pygrep.sh -E "ERROR" large.log
```

#### Prefer Specific Patterns

Specific patterns are faster than general ones:

```bash
# Faster: Specific character class
./pygrep.sh -E "\d" numbers.txt

# Slower: General character class
./pygrep.sh -E "[0-9]" numbers.txt

# Faster: Exact length
./pygrep.sh -E "\d\d\d\d" years.txt

# Slower: Variable length
./pygrep.sh -E "\d+" years.txt
```

#### Avoid Catastrophic Backtracking

Recognize and avoid problematic patterns:

```bash
# Problematic: Nested quantifiers
(a+)+

# Better: Simplified
a+

# Problematic: Overlapping alternatives
(a|a)*

# Better: Single alternative
a*
```

### File Processing

#### Use Recursive Search Efficiently

Recursive search can be I/O bound:

```bash
# Process specific extensions only
find . -name "*.py" -exec ./pygrep.sh -E "pattern" {} \;

# Better than searching all files
./pygrep.sh -r -E "pattern" .
```

#### Consider File Size

Large files are processed line by line efficiently:

```bash
# Memory usage remains constant regardless of file size
./pygrep.sh -E "pattern" huge-file.txt
```

## Benchmarking

### Simple Benchmark Script

```bash
#!/bin/bash
# benchmark.sh - Simple performance testing

PATTERN="$1"
FILE="$2"

echo "Benchmarking pattern: $PATTERN"
echo "File: $FILE"
echo "File size: $(wc -c < "$FILE") bytes"
echo "Line count: $(wc -l < "$FILE")"
echo

# Time the search
time ./pygrep.sh -E "$PATTERN" "$FILE"
```

Usage:

```bash
chmod +x benchmark.sh
./benchmark.sh "error" /var/log/syslog
```

### Performance Testing Framework

```python
#!/usr/bin/env python3
# performance_test.py

import time
import subprocess
import sys

def benchmark_pattern(pattern, filename, iterations=5):
    """Benchmark a pattern against a file."""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        result = subprocess.run([
            "./pygrep.sh", "-E", pattern, filename
        ], capture_output=True)
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    return {
        'pattern': pattern,
        'filename': filename,
        'avg_time': avg_time,
        'times': times,
        'exit_code': result.returncode
    }

# Example usage
if __name__ == "__main__":
    pattern = sys.argv[1]
    filename = sys.argv[2]
    
    result = benchmark_pattern(pattern, filename)
    print(f"Pattern: {result['pattern']}")
    print(f"Average time: {result['avg_time']:.4f}s")
    print(f"Times: {result['times']}")
```

### Comparison Testing

```bash
#!/bin/bash
# compare_performance.sh

PATTERN="$1"
FILE="$2"

echo "Comparing grep-python vs GNU grep"
echo "Pattern: $PATTERN"
echo "File: $FILE"
echo

echo "GNU grep:"
time grep -E "$PATTERN" "$FILE" > /dev/null

echo
echo "grep-python:"
time ./pygrep.sh -E "$PATTERN" "$FILE" > /dev/null
```

## Performance Patterns

### Fast Patterns

These patterns are optimized for speed:

```bash
# Literal strings (fastest)
./pygrep.sh -E "exact_match" file.txt

# Start-anchored patterns
./pygrep.sh -E "^start" file.txt

# End-anchored patterns
./pygrep.sh -E "end$" file.txt

# Simple character classes
./pygrep.sh -E "[0-9]" file.txt

# Basic quantifiers
./pygrep.sh -E "a+" file.txt
```

### Medium Performance Patterns

These patterns have moderate complexity:

```bash
# Alternation with few options
./pygrep.sh -E "(cat|dog)" file.txt

# Character classes with ranges
./pygrep.sh -E "[a-zA-Z]" file.txt

# Simple groups
./pygrep.sh -E "(hello)" file.txt

# Basic backreferences
./pygrep.sh -E "(a)\1" file.txt
```

### Slow Patterns

These patterns may cause performance issues:

```bash
# Nested quantifiers (catastrophic backtracking)
./pygrep.sh -E "(a+)+" file.txt

# Complex alternation
./pygrep.sh -E "(a|b|c|d|e|f|g|h|i|j|k|l|m)+" file.txt

# Deep nesting
./pygrep.sh -E "((((a))))" file.txt

# Many backreferences
./pygrep.sh -E "(a)(b)(c)(d)(e)\1\2\3\4\5" file.txt
```

## Optimization Tips

### Pattern Optimization

1. **Simplify when possible**:

   ```bash
   # Instead of: (hello|hello)
   # Use: hello
   ```

2. **Use specific anchors**:

   ```bash
   # Instead of: .*error.*
   # Use: ^.*error.*$ (if you need full line)
   # Or: error (if anchor not needed)
   ```

3. **Avoid redundant groups**:

   ```bash
   # Instead of: (a)+
   # Use: a+ (unless you need the capture)
   ```

### File Processing Optimization

1. **Filter files first**:

   ```bash
   # Filter by extension first
   find . -name "*.py" | xargs ./pygrep.sh -E "pattern"
   ```

2. **Use appropriate tools**:

   ```bash
   # For simple literal searches, consider using grep first
   grep -l "literal" *.txt | xargs ./pygrep.sh -E "complex_pattern"
   ```

3. **Process in parallel**:

   ```bash
   # GNU parallel for multiple files
   find . -name "*.txt" | parallel ./pygrep.sh -E "pattern" {}
   ```

## Memory Optimization

### Understanding Memory Usage

grep-python uses memory for:

- Parsed pattern tokens
- Recursion stack
- Captured group content
- Line buffers (one line at a time)

### Memory-Efficient Patterns

```bash
# Low memory: No captures
./pygrep.sh -E "hello" file.txt

# Higher memory: Many captures
./pygrep.sh -E "(a)(b)(c)(d)(e)(f)" file.txt

# Efficient: Reuse captures
./pygrep.sh -E "(hello).*\1" file.txt
```

### Large File Handling

grep-python processes files line by line, so memory usage remains constant regardless of file size:

```bash
# Memory usage is the same for both
./pygrep.sh -E "pattern" small.txt
./pygrep.sh -E "pattern" huge.txt
```

## Performance Monitoring

### Built-in Timing

```bash
# Use time command for basic timing
time ./pygrep.sh -E "pattern" file.txt
```

### Detailed Profiling

For development and debugging:

```python
import cProfile
import sys
sys.path.insert(0, 'src')

from pattern_matcher import match_pattern

def profile_pattern(pattern, text):
    return match_pattern(text, pattern)

# Profile the function
cProfile.run('profile_pattern("(a+)+", "a" * 20)')
```

### Performance Regression Testing

```bash
#!/bin/bash
# regression_test.sh

# Set baseline performance
BASELINE_TIME=1.0  # seconds

# Test current performance
CURRENT_TIME=$(time -p ./pygrep.sh -E "pattern" file.txt 2>&1 | grep real | awk '{print $2}')

# Compare
if (( $(echo "$CURRENT_TIME > $BASELINE_TIME" | bc -l) )); then
    echo "Performance regression detected!"
    echo "Current: ${CURRENT_TIME}s, Baseline: ${BASELINE_TIME}s"
    exit 1
else
    echo "Performance acceptable: ${CURRENT_TIME}s"
fi
```

## Known Performance Issues

### Current Limitations

1. **Recursive implementation**: Stack overflow possible with very deep patterns
2. **No compilation**: Patterns are parsed on each use
3. **No caching**: Repeated searches re-parse patterns
4. **Single-threaded**: No parallel file processing

### Future Optimizations

Potential improvements for future versions:

1. **Pattern compilation**: Cache parsed patterns
2. **Iterative matching**: Replace recursion with loops
3. **NFA/DFA conversion**: Compile to finite automata
4. **Parallel processing**: Multi-threaded file search
5. **Memory mapping**: Use mmap for large files

### Workarounds

For performance-critical applications:

1. **Pre-filter with grep**: Use GNU grep for initial filtering
2. **Batch processing**: Process multiple patterns in one pass
3. **Pattern simplification**: Manually optimize complex patterns
4. **External tools**: Consider sed/awk for simple transformations

This performance guide should help users understand and optimize their usage of grep-python for their specific needs.
