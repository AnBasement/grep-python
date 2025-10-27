import importlib
import argparse
import textwrap


def get_version() -> str:
    """
    Return the current version of the package as a string.

    Attempts to import the 'src' module and read its __version__ attribute.
    If the module or attribute is unavailable, returns 'unknown' to avoid
    breaking the program.
    """
    try:
        version_str = importlib.import_module("src").__version__
    except (ModuleNotFoundError, AttributeError):
        version_str = "unknown"
    return version_str


def parse_arguments() -> argparse.Namespace:
    """
    Parse and return command-line arguments for the pygrep tool.

    Uses argparse to define available options and positional arguments,
    including pattern, files, and flags for extended regex, recursion, line
    numbers, case sensitivity, inverted matches, and count mode. Validates
    that at least one pattern is specified and at least one file is provided
    for recursive searches.

    Returns:
        argparse.Namespace: Parsed command-line arguments as attributes.

    Example:
        $ ./pygrep.sh -r -n -i "\\d+" data.txt
        args.pattern       -> "\\d+"
        args.files         -> ["data.txt"]
        args.recursive     -> True
        args.line_number   -> True
        args.ignore_case   -> True
    """
    parser = argparse.ArgumentParser(
        prog="pygrep",
        description="Search for patterns in files using custom regex engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
        Pattern Syntax:
          literals      Match exact characters
          (group)       Capture group with alternation support
          a|b           Alternation (match a or b)
          +             One or more of previous token
          ?             Zero or one of previous token
          [abc]         Character class
          [^abc]        Negated character class
          ^             Start of line anchor
          $             End of line anchor
          \\1, \\2        Backreferences to captured groups
          \\d, \\w        Digit and word character classes
          .             Any character wildcard
        
        Examples:
          ./pygrep.sh -E "error" log.txt
          ./pygrep.sh -r -E "^import" src/
          ./pygrep.sh -n -E "\\d+" data.txt
        """
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
    )

    parser.add_argument(
        "pattern",
        nargs="?",
        help="Regular expression pattern to search for (optional if -e or -f is used)",
    )

    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Files to search through (defaults to stdin if none provided)",
    )

    parser.add_argument(
        "-E",
        "--extended-regexp",
        action="store_true",
        help="Uses extended regular expression syntax (enabled by default)",
    )

    parser.add_argument(
        "-r",
        "-R",
        "--recursive",
        action="store_true",
        dest="recursive",
        help="Recursively search all files under each directory",
    )

    parser.add_argument(
        "-n",
        "--line-number",
        action="store_true",
        help="Prefix each line of output with the line number in the file",
    )

    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Ignore case distinctions",
    )

    parser.add_argument(
        "-v",
        "--invert-match",
        action="store_true",
        help="Select lines that do not match",
    )

    parser.add_argument(
        "-c",
        "--count",
        action="store_true",
        help="Only print a count of matching lines and suppress normal output",
    )

    parser.add_argument(
        "-A",
        "--after-context",
        help="Print NUM lines of trailing context after each match",
        type=int,
        default=0,
        metavar="NUM",
    )

    parser.add_argument(
        "-B",
        "--before-context",
        help="Print NUM lines of leading context before each match",
        type=int,
        default=0,
        metavar="NUM",
    )

    parser.add_argument(
        "-C",
        "--context",
        help="Print NUM lines of context before and after each match",
        type=int,
        default=0,
        metavar="NUM",
    )

    parser.add_argument(
        "-e",
        "--regexp",
        action="append",
        dest="patterns",
        default=[],
        help="Pattern to search for (can be used multiple times)",
    )

    parser.add_argument(
        "-f",
        "--file",
        dest="pattern_file",
        metavar="FILE",
        type=str,
        help="Read patterns from FILE, one per line",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        "--silent",
        action="store_true",
        help=(
            "Suppress all normal output; exit with status 0 immediately "
            "on first match"
        ),
    )

    parser.add_argument(
        "-m",
        "--max-count",
        type=int,
        metavar="NUM",
        default=0,
        help="Stop reading a file after NUM matching lines",
    )

    parser.add_argument(
        "-l",
        "--files-with-matches",
        action="store_true",
        help="Only print names of files with matching lines",
    )

    parser.add_argument(
        "-L",
        "--files-without-match",
        action="store_true",
        help="Only print names of files without matching lines",
    )

    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON format"
    )

    args = parser.parse_args()

    if (args.patterns or args.pattern_file) and args.pattern and not args.files:
        args.files = [args.pattern]
        args.pattern = None

    all_patterns = []

    if args.files_with_matches and args.files_without_match:
        parser.error("cannot use -l and -L together")

    if len(args.files) == 0 and (args.files_with_matches or args.files_without_match):
        parser.error("cannot use -l or -L with stdin input")

    if args.json and (args.count or args.files_with_matches or args.files_without_match or args.quiet):
        parser.error("--json cannot be used with -c, -l, -L, or -q flags")

    if args.pattern:
        all_patterns.append(args.pattern)

    if args.patterns:
        all_patterns.extend(args.patterns)

    if args.pattern_file:
        try:
            with open(args.pattern_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        all_patterns.append(line)
        except FileNotFoundError:
            parser.error(f"pattern file not found: {args.pattern_file}")
        except IsADirectoryError:
            parser.error(f"pattern file is a directory: {args.pattern_file}")
        except PermissionError:
            parser.error(f"permission denied: {args.pattern_file}")

    if not all_patterns:
        parser.error("no pattern specified")

    args.pattern_list = all_patterns

    if args.recursive and not args.files:
        parser.error("at least one FILE required for recursive search")

    if args.context > 0:
        args.before_context = args.context
        args.after_context = args.context

    return args
