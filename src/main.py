import sys
from .pattern_matcher import match_pattern
from .file_search import file_search, multi_file_search, search_in_directories
from .constants import EXIT_MATCH_FOUND, EXIT_NO_MATCH, EXIT_ERROR


def main():
    try:
        recursive = False

        if len(sys.argv) >= 2 and sys.argv[1] == "-r":
            recursive = True

            if len(sys.argv) < 3 or sys.argv[2] != "-E":
                print("Expected '-E' after '-r'", file=sys.stderr)
                sys.exit(EXIT_NO_MATCH)

            pattern = sys.argv[3]
            search_paths = sys.argv[4:]
        else:
            if sys.argv[1] != "-E":
                print("Expected first argument to be '-E'")
                sys.exit(EXIT_NO_MATCH)

            pattern = sys.argv[2]
            search_paths = sys.argv[3:]

        if len(search_paths) == 0:
            input_line = sys.stdin.read()
            try:
                if match_pattern(input_line, pattern):
                    sys.exit(EXIT_MATCH_FOUND)
                else:
                    sys.exit(EXIT_NO_MATCH)
            except Exception as e:
                print(f"Error matching pattern in input: {e}", file=sys.stderr)
                sys.exit(EXIT_ERROR)

        if recursive:
            any_match_found = False

            for path in search_paths:
                try:
                    if search_in_directories(path, pattern):
                        any_match_found = True
                except Exception as e:
                    print(
                        f"Error searching in directory '{path}': {e}",
                        file=sys.stderr
                    )

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
            except Exception as e:
                print(f"Error during file search: {e}", file=sys.stderr)
                sys.exit(EXIT_ERROR)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)


if __name__ == "__main__":
    main()
