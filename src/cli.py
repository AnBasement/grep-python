import sys
from .constants import EXIT_ERROR, ERROR_USAGE, ERROR_EXPECTED_E_AFTER_R, ERROR_EXPECTED_E
import importlib
import argparse
import textwrap

def get_version():
    try:
        version_str = importlib.import_module("src").__version__
    except Exception:
        version_str = "unknown"
    return version_str


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='pygrep',
        description='Search for patterns in files using custom regex engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''
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
        ''')
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}"
    )

    parser.add_argument(
        "pattern",
        help="Regular expression pattern to search for"
    )

    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Files to search through (defaults to stdin if none provided)"
    )

    parser.add_argument(
        "-E",
        "--extended-regexp",
        action="store_true",
        help="Uses extended regular expression syntax (enabled by default)"
    )

    parser.add_argument(
        "-r", "-R", "--recursive",
        action="store_true",
        dest="recursive",
        help="Recursively search all files under each directory"
    )

    parser.add_argument(
        "-n", "--line-number",
        action="store_true",
        help="Prefix each line of output with the line number in the file"
    )

    parser.add_argument(
        "-i", "--ignore-case",
        action="store_true",
        help="Ignore case distinctions"
    )

    parser.add_argument(
        "-v", "--invert-match",
        action="store_true",
        help="Select lines that do not match"
    )

    parser.add_argument(
        "-c", "--count",
        action="store_true",
        help="Only print a count of matching lines and suppress normal output"
    )

    args = parser.parse_args()

    if args.recursive and not args.files:
        parser.error("at least one FILE required for recursive search")

    return args