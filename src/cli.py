import sys
from .constants import EXIT_ERROR, ERROR_USAGE, ERROR_EXPECTED_E_AFTER_R, ERROR_EXPECTED_E

def parse_arguments():
    """
    Parses command-line arguments.
    
    Returns:
        tuple: (recursive: bool, pattern: str, search_paths: list[str])
    
    Raises:
        SystemExit: If arguments are invalid
    """
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