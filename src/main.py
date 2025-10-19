import sys
from .pattern_matcher import match_pattern
from .file_search import file_search, multi_file_search, search_in_directories
from .constants import (
    EXIT_MATCH_FOUND,
    EXIT_NO_MATCH,
    EXIT_ERROR,
    ERROR_INVALID_PATTERN,
    ERROR_SEARCH_FAILED,
    ERROR_EXPECTED_E,
    ERROR_EXPECTED_E_AFTER_R,
    ERROR_USAGE,
)
from .cli import parse_arguments


def main():
    try:
        recursive, pattern, search_paths = parse_arguments()
        if len(sys.argv) < 2:
            print(ERROR_USAGE, file=sys.stderr)
            sys.exit(EXIT_ERROR)

        recursive = False

        if len(sys.argv) >= 2 and sys.argv[1] == "-r":
            recursive = True

            if len(sys.argv) < 3 or sys.argv[2] != "-E":
                print(ERROR_EXPECTED_E_AFTER_R, file=sys.stderr)
                sys.exit(EXIT_NO_MATCH)

            pattern = sys.argv[3]
            search_paths = sys.argv[4:]
        else:
            if sys.argv[1] != "-E":
                print(ERROR_EXPECTED_E, file=sys.stderr)
                sys.exit(EXIT_NO_MATCH)

            if sys.argv[1] != "-E":
                print(ERROR_EXPECTED_E, file=sys.stderr)
                sys.exit(EXIT_NO_MATCH)

            if len(sys.argv) < 3:
                print(ERROR_USAGE, file=sys.stderr)
                sys.exit(EXIT_ERROR)

            pattern = sys.argv[2]
            search_paths = sys.argv[3:]

        if len(search_paths) == 0:
            input_line = sys.stdin.read()
            try:
                if match_pattern(input_line, pattern):
                    sys.exit(EXIT_MATCH_FOUND)
                else:
                    sys.exit(EXIT_NO_MATCH)
            except Exception:
                print(f"grep: {ERROR_INVALID_PATTERN}", file=sys.stderr)
                sys.exit(EXIT_ERROR)

        if recursive:
            any_match_found = False

            for path in search_paths:
                try:
                    if search_in_directories(path, pattern):
                        any_match_found = True
                except Exception:
                    print(f"{path}: {ERROR_SEARCH_FAILED}", file=sys.stderr)

            if any_match_found:
                sys.exit(EXIT_MATCH_FOUND)
            else:
                sys.exit(EXIT_NO_MATCH)

        else:
            filenames = search_paths
            num_files = len(filenames)

            try:
                if num_files == 1:
                    filename = filenames[0]
                    if file_search(filename, pattern, print_filename=False):
                        sys.exit(EXIT_MATCH_FOUND)
                    else:
                        sys.exit(EXIT_NO_MATCH)

                else:
                    if multi_file_search(filenames, pattern):
                        sys.exit(EXIT_MATCH_FOUND)
                    else:
                        sys.exit(EXIT_NO_MATCH)
            except Exception:
                print(f"grep: {ERROR_SEARCH_FAILED}", file=sys.stderr)
                sys.exit(EXIT_ERROR)
    except Exception:
        print(f"grep: {ERROR_SEARCH_FAILED}", file=sys.stderr)
        sys.exit(EXIT_ERROR)


if __name__ == "__main__":
    main()
