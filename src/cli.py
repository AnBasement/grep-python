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
    that at least one file is provided for recursive searches.

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
        help="Regular expression pattern to search for",
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
        "--after-contextpy",
        help="Only print a count of matching lines and suppress normal output",
        type=int,
        default=0,
        metavar="NUM",
    )

    args = parser.parse_args()

    if args.recursive and not args.files:
        parser.error("at least one FILE required for recursive search")

    return args
