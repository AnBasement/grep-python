from typing import Optional
import os
import sys
from collections import deque
from .pattern_matcher import match_pattern


def _format_line_output(
    line_text: str,
    line_number: int,
    filename: Optional[str] = None,
    show_filename: bool = False,
    show_line_number: bool = False,
) -> str:
    """
    Helper function to format the output line with optional prefixes.

    Args:
        line_text (str): The content of the line.
        line_number (int): The line number in the file.
        filename (str, optional): The name of the file. Defaults to None.
        show_filename (bool, optional):
            Whether to include filename in output.
            Default is False.
        show_line_number (bool, optional):
            Whether to include the line number in output.
            Default is False.

    Returns:
        str: Formatted output line, like "file.txt:42:content" or just "content".
    """
    output = ""
    if show_filename and filename is not None:
        output += f"{filename}:"
    if show_line_number:
        output += f"{line_number}:"
    output += line_text
    return output


def search_file(
    filename: str,
    pattern: str,
    print_filename: bool = False,
    print_line_number: bool = False,
    ignore_case: bool = False,
    invert_match: bool = False,
    count_only: bool = False,
    after_context: int = 0,
    before_context: int = 0,
    patterns: Optional[list[str]] = None,
    quiet: bool = False,
    max_count: int = 0,
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
        after_context (int): Number of lines to print after a matching line.
        before_context (int): Number of lines to print before a matching line.
        patterns (list[str], optional): Alternative patterns to match against.
            Overrides pattern parameter. Defaults to None.
        quiet (bool): If True, suppress all normal output and exit on first match.
        max_count (int): Maximum number of matching lines to find before stopping.
            A value of 0 means no limit. Defaults to 0.

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
    after_context_counter = 0
    printed_lines = set()
    patterns_to_check = []
    matches_found = 0
    if patterns:
        patterns_to_check.extend(patterns)
    if pattern:
        patterns_to_check.append(pattern)
    if before_context > 0:
        before_context_buffer = deque(maxlen=before_context)
    else:
        before_context_buffer = None
    try:
        with open(filename, encoding="utf-8") as file:
            for idx, line in enumerate(file, start=1):
                line = line.rstrip("\n")
                matches = False
                for p in patterns_to_check:
                    if match_pattern(line, p, ignore_case=ignore_case):
                        matches = True
                        break

                if invert_match:
                    matches = not matches

                if matches:
                    matches_found += 1
                    match_found = True
                    if matches:
                        matches_found += 1
                        match_found = True
                        if quiet:
                            return True
                        if not quiet:
                            if before_context_buffer:
                                for buf_idx, buf_line in before_context_buffer:
                                    if buf_idx not in printed_lines:
                                        print(
                                            _format_line_output(
                                                line_text=buf_line,
                                                line_number=buf_idx,
                                                filename=filename,
                                                show_filename=print_filename,
                                                show_line_number=print_line_number,
                                            )
                                        )
                                        printed_lines.add(buf_idx)

                        if count_only:
                            match_count += 1
                        else:
                            if idx not in printed_lines:
                                print(
                                    _format_line_output(
                                        line_text=line,
                                        line_number=idx,
                                        filename=filename,
                                        show_filename=print_filename,
                                        show_line_number=print_line_number,
                                    )
                                )
                                printed_lines.add(idx)
                            after_context_counter = after_context

                        if 0 < max_count <= matches_found:
                            return True
                elif after_context_counter > 0:
                    if idx not in printed_lines:
                        print(
                            _format_line_output(
                                line_text=line,
                                line_number=idx,
                                filename=filename,
                                show_filename=print_filename,
                                show_line_number=print_line_number,
                            )
                        )
                        printed_lines.add(idx)
                    after_context_counter -= 1

                if before_context_buffer is not None and not quiet:
                    before_context_buffer.append((idx, line))

    except (PermissionError, OSError):
        print(f"{filename}: permission denied", file=sys.stderr)
        return False
    except UnicodeDecodeError:
        print(f"{filename}: could not decode file with UTF-8 encoding", file=sys.stderr)
        return False

    if count_only:
        if print_filename:
            print(f"{filename}:{match_count}")
        else:
            print(match_count)
        return match_count > 0

    return match_found


def search_multiple_files(
    filenames: list[str],
    pattern: str,
    print_line_number: bool = False,
    ignore_case: bool = False,
    invert_match: bool = False,
    count_only: bool = False,
    after_context: int = 0,
    before_context: int = 0,
    patterns: Optional[list[str]] = None,
    quiet: bool = False,
    max_count: int = 0,
) -> bool:
    """
    Searches through multiple files for lines matching a given pattern.

    Calls `search_file()` for the actual searching logic after iterating
    over all provided filenames. Collects results and returns True if any
    file contains a line matching the pattern.

    Args:
        filenames (list[str]): Paths of files to search.
        pattern (str): Regex pattern to match.
        print_line_number (bool): Include line numbers in output if True.
        ignore_case (bool): Ignore case sensitivity if True.
        invert_match (bool): Print lines that don't match if True.
        count_only (bool): Print only the number of matching lines.
        after_context (int): Number of lines to print after a matching line.
        before_context (int): Number of lines to print before a matching line.
        patterns (list[str], optional): Alternative patterns to match against.
            Overrides pattern parameter. Defaults to None.
        quiet (bool): If True, suppress all normal output and exit on first match.
        max_count (int): Maximum number of matching lines to find before stopping.
            A value of 0 means no limit. Defaults to 0.

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
            after_context=after_context,
            before_context=before_context,
            patterns=patterns,
            quiet=quiet,
            max_count=max_count,
        )
        if file_with_match:
            match_found = True
            if quiet:
                return True

    return match_found


def get_files_recursively(directory: str) -> list[str]:
    """
    Recursively collect all file paths under a given directory.

    Uses the os module with `os.walk()` to scan the directory tree and
    collects full file paths. Handles missing paths or permission errors.

    Args:
        directory (str): Path to the root directory to scan.

    Returns:
        list[str]: A list of absolute file paths found in the directory
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
        for root, _dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                all_files.append(filepath)

    except (PermissionError, OSError):
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
    after_context: int = 0,
    before_context: int = 0,
    patterns: Optional[list[str]] = None,
    quiet: bool = False,
    max_count: int = 0,
) -> bool:
    """
    Recursively search all files in a directory for lines matching a pattern.

    Calls `get_files_recursively()` to collect file paths in a given directory,
    then calls `search_file()` to find matching lines in each file.
    Returns True if a match is found in any of the files.

    Args:
        directory (str): Path to the directory to search.
        pattern (str): Regex pattern to match.
        print_line_number (bool): Include line numbers in output if True.
        ignore_case (bool): Ignore case sensitivity if True.
        invert_match (bool): Print lines that don't match if True.
        count_only (bool): Print only the number of matching lines.
        after_context (int): Number of lines to print after a matching line.
        before_context (int): Number of lines to print before a matching line.
        patterns (list[str], optional): Alternative patterns to match against.
            Overrides pattern parameter. Defaults to None.
        quiet (bool): If True, suppress all normal output and exit on first match.
        max_count (int): Maximum number of matching lines to find before stopping.
            A value of 0 means no limit. Defaults to 0.

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
            after_context=after_context,
            before_context=before_context,
            patterns=patterns,
            quiet=quiet,
            max_count=max_count,
        )
        if file_had_match:
            any_match_found = True
            if quiet:
                return True

    return any_match_found
