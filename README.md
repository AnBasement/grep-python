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

## TODO

- [ ] Add error handling
- [ ] Print matching lines to stdout (like standard grep)
- [ ] Add support for more regex features
- [ ] Improve performance for large files
- [ ] Add unit tests
- [ ] Add support for colored output (maybe with Rich library?)

## License

MIT License
