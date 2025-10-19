import sys
from .constants import EXIT_ERROR, ERROR_USAGE, ERROR_EXPECTED_E_AFTER_R, ERROR_EXPECTED_E
import importlib
import argparse

def get_version():
    try:
        version_str = importlib.import_module("src").__version__
    except Exception:
        version_str = "unknown"
    return version_str


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="pygrep",
        description="Search for patterns in files using a custom regex engine",
        epilog="Pattern syntax: literals, groups (), alternation |, quantifiers +?, character classes [], anchors ^$"
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

    args = parser.parse_args()

    recursive = args.recursive
    pattern = args.pattern
    search_paths = args.files

    return recursive, pattern, search_paths

def parse_arguments_old():
    """
    Parses command-line arguments.
    
    Returns:
        tuple: (recursive: bool, pattern: str, search_paths: list[str])
    
    Raises:
        SystemExit: If arguments are invalid
    """
    if len(sys.argv) > 1:
        if sys.argv[1] == "--version":
            print(f"grep-python version {get_version()}")
            sys.exit(0)
        if sys.argv[1] in ("--help", "-h"):
            print("Usage: ./pygrep.sh [-r] -E PATTERN [FILE...]")
            print("\nSearch for PATTERN in each FILE")
            print("\nOptions:")
            print("  -E PATTERN    Pattern to search for")
            print("  -r            Recursively search directories")
            print("  --version     Show version information")
            print("  --help, -h    Show this help message")
            sys.exit(0)

    recursive = False

    if len(sys.argv) < 2:
        print(ERROR_USAGE, file=sys.stderr)
        sys.exit(EXIT_ERROR)

    if sys.argv[1] == "-r":
        recursive = True
        if len(sys.argv) < 3 or sys.argv[2] != "-E":
            print(ERROR_EXPECTED_E_AFTER_R, file=sys.stderr)
            sys.exit(EXIT_ERROR)
        if len(sys.argv) < 4:
            print(ERROR_USAGE, file=sys.stderr)
            sys.exit(EXIT_ERROR)
        pattern = sys.argv[3]
        search_paths = sys.argv[4:]
    else:
        if sys.argv[1] != "-E":
            print(ERROR_EXPECTED_E, file=sys.stderr)
            sys.exit(EXIT_ERROR)
        if len(sys.argv) < 3:
            print(ERROR_USAGE, file=sys.stderr)
            sys.exit(EXIT_ERROR)
        pattern = sys.argv[2]
        search_paths = sys.argv[3:]

    return recursive, pattern, search_paths