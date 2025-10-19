# grep-python

A grep tool written in Python while following the [Codecrafters.io guide](https://app.codecrafters.io/courses/grep/overview) with some added functionality.

## Features

- **Custom regex engine**: Supports literals, groups `()`, alternation `|`, quantifiers `+` and `?`, character classes `[]`, start `^` and end `$` anchors, and backreferences (`\1`, `\2`, etc.).
- **Recursive search**: Optionally search directories recursively.
- **Multiple file support**: Search one or more files at once.
- **Standard input support**: Reads from stdin if no files are specified.

## Usage

```sh
python app.py -E PATTERN [FILE...]
```

- `-E`: Indicates that the next argument is the regex pattern.
- `PATTERN`: The regex pattern to search for.
- `[FILE...]`: One or more files to search. If omitted, reads from stdin.

### Recursive Search

To search recursively through directories, use the `-r` flag:

```sh
python app.py -r -E PATTERN DIRECTORY...
```

### Examples

Search for lines containing "hello" in `file.txt`:

```sh
python app.py -E hello file.txt
```

Search recursively for lines matching a pattern in all files under `src/`:

```sh
python app.py -r -E "^def " src/
```

Pipe input from another command:

```sh
cat file.txt | python app.py -E "pattern"
```

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
