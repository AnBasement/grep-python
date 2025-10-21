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
    Search a file for lines matching a pattern.

    Opens and reads file one line at a time, calling `match_pattern()` 
    with optional flags for case-insensitive and inverted matching.
    Then prints matched lines either with filename and line numbers (optional)
    or a total count of matches. Missing files, directories and permissions
    are handled to prevent interruption.

    Args:
        filename (str): Path to the file being searched.
        pattern (str): Regex pattern to match.
        print_filename (bool): Prefix output with filename if True.
        print_line_number (bool): Prefix output with line number if True.
        ignore_case (bool): Ignore case sensitivity if True.
        invert_match (bool): Print lines that don't match if True.
        count_only (bool): Print only the number of matching lines.

    Returns:
        bool: True if at least one matching line is found, otherwise False.
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
    Searches through multiple files for lines matching a given pattern.

    Calls `search_file()` for the actual searching logic after iterating
    over all provided filenames. Collects results and returns True if any
    file contains a line matching the pattern.

    Args:
        filenames (List[str]): Paths of files to search.
        pattern (str): Regex pattern to match.
        print_line_number (bool): Include line numbers in output if True.
        ignore_case (bool): Ignore case sensitivity if True.
        invert_match (bool): Print lines that don't match if True.
        count_only (bool): Print only the number of matching lines.

    Returns:
        bool: True if at least one matching line is found, else False.
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
    Recursively collect all file paths under a given directory.

    Uses the os module with `os.walk()` to scan the directory tree and
    collects full file paths. Handles missing paths or permission errors.

    Args:
        directory (str): Path to the root directory to scan.

    Returns:
        List[str]: A list of absolute file paths found in the directory
        and subdirectories. Returns an empty list if no files are found
        or an error is encountered.
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
    Recursively search all files in a directory for lines matching a pattern.

    Calls `get_files_recursively()` to collect file paths in a given directory,
    then calls `search_file()` to find matching lines in each file.
    Returns True if a match is found in any of the files.

    Args:
        filenames (List[str]): Paths of files to search.
        pattern (str): Regex pattern to match.
        print_line_number (bool): Include line numbers in output if True.
        ignore_case (bool): Ignore case sensitivity if True.
        invert_match (bool): Print lines that don't match if True.
        count_only (bool): Print only the number of matching lines.

    Returns:
        bool: True if at least one matching line is found, else False.
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
