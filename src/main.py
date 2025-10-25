import sys
from .pattern_matcher import match_pattern
from .file_search import (
    search_file,
    search_multiple_files,
    search_directory_recursively,
)
from .constants import (
    EXIT_MATCH_FOUND,
    EXIT_NO_MATCH,
    EXIT_ERROR,
    ERROR_INVALID_PATTERN,
    ERROR_SEARCH_FAILED,
)
from .cli import parse_arguments


def main() -> None:
    """
    Entry point for the pygrep CLI.

    This function dictates the flow of the program. It parses arguments,
    determines input source and coordinates pattern matching. Calls helper
    functions: reads from stdin for input, searches file(s) by calling
    `search_file()` / `search_multiple_files()`, or scans directories with
    `search_directory_recursively()`. Utilizes standard grep status codes
    for exit based on results of matching.
    """
    try:
        args = parse_arguments()

        if len(args.files) == 0:
            match_count = 0
            match_found = False
            for line in sys.stdin:
                line = line.rstrip("\n")
                try:
                    matches = match_pattern(
                        line, args.pattern, ignore_case=args.ignore_case
                    )

                    if args.invert_match:
                        matches = not matches

                    if matches:
                        match_found = True
                        if args.count:
                            match_count += 1
                        else:
                            print(line)
                except (ValueError, IndexError, KeyError):
                    print(f"grep: {ERROR_INVALID_PATTERN}", file=sys.stderr)
                    sys.exit(EXIT_ERROR)

            if args.count:
                print(match_count)
                sys.exit(EXIT_MATCH_FOUND if match_count > 0 else EXIT_NO_MATCH)
            else:
                sys.exit(EXIT_MATCH_FOUND if match_found else EXIT_NO_MATCH)

        if args.recursive:
            any_match_found = False

            for path in args.files:
                try:
                    if search_directory_recursively(
                        path,
                        args.pattern,
                        print_line_number=args.line_number,
                        ignore_case=args.ignore_case,
                        invert_match=args.invert_match,
                        count_only=args.count,
                        after_context=args.after_context,
                        before_context=args.before_context,
                    ):
                        any_match_found = True
                except (PermissionError, OSError, FileNotFoundError):
                    print(f"{path}: {ERROR_SEARCH_FAILED}", file=sys.stderr)

            if any_match_found:
                sys.exit(EXIT_MATCH_FOUND)
            else:
                sys.exit(EXIT_NO_MATCH)

        else:
            num_files = len(args.files)

            try:
                if num_files == 1:
                    if search_file(
                        args.files[0],
                        args.pattern,
                        print_filename=False,
                        print_line_number=args.line_number,
                        ignore_case=args.ignore_case,
                        invert_match=args.invert_match,
                        count_only=args.count,
                        after_context=args.after_context,
                        before_context=args.before_context,
                    ):
                        sys.exit(EXIT_MATCH_FOUND)
                    else:
                        sys.exit(EXIT_NO_MATCH)

                else:
                    if search_multiple_files(
                        args.files,
                        args.pattern,
                        print_line_number=args.line_number,
                        ignore_case=args.ignore_case,
                        invert_match=args.invert_match,
                        count_only=args.count,
                        after_context=args.after_context,
                        before_context=args.before_context,
                    ):
                        sys.exit(EXIT_MATCH_FOUND)
                    else:
                        sys.exit(EXIT_NO_MATCH)
            except (PermissionError, OSError, FileNotFoundError):
                print(f"grep: {ERROR_SEARCH_FAILED}", file=sys.stderr)
                sys.exit(EXIT_ERROR)
    except (PermissionError, OSError, FileNotFoundError):
        print(f"grep: {ERROR_SEARCH_FAILED}", file=sys.stderr)
        sys.exit(EXIT_ERROR)


if __name__ == "__main__":
    main()
