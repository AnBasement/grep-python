from typing import List
import os
import sys
from .pattern_matcher import match_pattern


def search_file(
    filename: str,
    pattern: str,
    print_filename: bool = False,
    print_line_number: bool = False,
    ignore_case: bool = False,
    invert_match: bool = False,
    count_only: bool = False,
) -> bool:
    """
    Searches a file for lines matching a given pattern.
    """
    if not os.path.isfile(filename):
        if os.path.isdir(filename):
            print(f"{filename}: is a directory", file=sys.stderr)
        else:
            print(f"{filename}: no such file or directory", file=sys.stderr)
        return False

    match_count = 0
    match_found = False
    try:
        with open(filename, "r") as file:
            for idx, line in enumerate(file, start=1):
                line = line.rstrip("\n")
                matches = match_pattern(line, pattern, ignore_case=ignore_case)

                if invert_match:
                    matches = not matches

                if matches:
                    match_found = True
                    if count_only:
                        match_count += 1
                    else:
                        output = ""
                        if print_filename:
                            output += f"{filename}:"
                        if print_line_number:
                            output += f"{idx}:"
                        output += line
                        print(output)

    except PermissionError:
        print(f"{filename}: permission denied", file=sys.stderr)
        return False
    except Exception:
        print(f"{filename}: permission denied", file=sys.stderr)
        return False

    if count_only:
        if print_filename:
            print(f"{filename}:{match_count}")
        else:
            print(match_count)
        return match_count > 0

    return match_found


def search_multiple_files(
    filenames: List[str],
    pattern: str,
    print_line_number: bool = False,
    ignore_case: bool = False,
    invert_match: bool = False,
    count_only: bool = False,
) -> bool:
    """
    Searches through multiple files for lines matching the pattern.
    """
    match_found = False

    for filename in filenames:
        file_with_match = search_file(
            filename,
            pattern,
            print_filename=True,
            print_line_number=print_line_number,
            ignore_case=ignore_case,
            invert_match=invert_match,
            count_only=count_only,
        )
        if file_with_match:
            match_found = True

    return match_found


def get_files_recursively(directory: str) -> List[str]:
    """
    Recursively finds all files in a directory and subdirectories.
    """
    if not os.path.exists(directory):
        print(f"{directory}: no such file or directory", file=sys.stderr)
        return []

    if not os.path.isdir(directory):
        print(f"{directory}: not a directory", file=sys.stderr)
        return []

    all_files = []

    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                all_files.append(filepath)

    except PermissionError:
        print(f"{directory}: permission denied", file=sys.stderr)
        return []

    except Exception:
        print(f"{directory}: permission denied", file=sys.stderr)
        return []

    return all_files


def search_directory_recursively(
    directory: str,
    pattern: str,
    print_line_number: bool = False,
    ignore_case: bool = False,
    invert_match: bool = False,
    count_only: bool = False,
) -> bool:
    """
    Recursively search files in a directory for lines matching
    the given pattern.
    """
    files = get_files_recursively(directory)
    any_match_found = False

    for filepath in files:
        file_had_match = search_file(
            filepath,
            pattern,
            print_filename=True,
            print_line_number=print_line_number,
            ignore_case=ignore_case,
            invert_match=invert_match,
            count_only=count_only,
        )
        if file_had_match:
            any_match_found = True

    return any_match_found
