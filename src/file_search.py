import os
import sys
from .pattern_matcher import match_pattern


def file_search(filename, pattern, print_filename=False):
    """
    Searches a file for lines matching a given pattern.
    """
    if not os.path.isfile(filename):
        if os.path.isdir(filename):
            print(f"{filename}: Is a directory", file=sys.stderr)
        else:
            print(f"{filename}: Is not a valid file", file=sys.stderr)
        return False

    match_found = False
    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.rstrip("\n")
                if match_pattern(line, pattern):
                    if print_filename:
                        print(f"{filename}:{line}")
                    else:
                        print(line)

                    match_found = True

    except FileNotFoundError:
        print(f"{filename}: File not found", file=sys.stderr)
    except PermissionError:
        print(f"{filename}: Permission denied", file=sys.stderr)
    except Exception as e:
        print(f"{filename}: Error reading file: {e}", file=sys.stderr)
    return match_found


def multi_file_search(filenames, pattern):
    """
    Searches through multiple files for lines matching the pattern.
    """

    match_found = False

    for filename in filenames:
        file_with_match = file_search(
            filename,
            pattern,
            print_filename=True
        )

        if file_with_match:
            match_found = True

    return match_found


def get_all_files_in_directory(directory):
    """
    Finds all files in a directory and the subdirectories.
    """
    if not os.path.exists(directory):
        print(f"{directory}: No such file or directory", file=sys.stderr)
        return []

    if not os.path.isdir(directory):
        print(f"{directory}: Not a directory", file=sys.stderr)
        return []

    all_files = []

    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                all_files.append(filepath)

    except PermissionError:
        print(f"Permission denied: {directory}", file=sys.stderr)
        return []

    except Exception as e:
        print(f"{directory}: {e}", file=sys.stderr)
        return []

    return all_files


def search_in_directories(directory, pattern):
    """
    Recursively search files in a directory for lines matching
    the given pattern.
    """
    files = get_all_files_in_directory(directory)
    any_match_found = False

    for filepath in files:
        file_had_match = file_search(filepath, pattern, print_filename=True)

        if file_had_match:
            any_match_found = True

    return any_match_found
