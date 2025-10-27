import json
import csv
import io
import re
from typing import Optional
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from pygments import lexers, highlight
from pygments.util import ClassNotFound
from pygments.formatters import Terminal256Formatter  # pylint: disable=no-name-in-module


@dataclass
class MatchResult:
    """
    Represents a single pattern match in a file.

    Args:
        filename (str): Name of the file where the match was found.
        line_num (int): Line number of the match.
        line_content (str): Full content of the matched line.
        match_start (int): Start index of the match in the line.
        match_end (int): End index of the match in the line.
    """

    filename: str
    line_num: int
    line_content: str
    match_start: Optional[int] = None
    match_end: Optional[int] = None

    def to_dict(self) -> dict:
        """
        Return a JSON-serializable dict of this match.

        The returned dictionary includes the fields:
        'filename', 'line_num', 'line_content', 'match_start', and
        'match_end'. Fields with value 'None' are preserved (caller can
        choose how to handle them during serialization).

        Returns:
            dict: Dictionary representation of the MatchResult.
        """

        return asdict(self)


class OutputFormatter(ABC):
    """
    Base class for output formatters.

    Subclasses must implement 'format(results)' which accepts a list of
    'MatchResult' and returns a formatted string representation.
    """

    # pylint: disable=too-few-public-methods

    @abstractmethod
    def format(self, results: list[MatchResult]) -> str:
        """
        Format a list of MatchResult objects.

        Args:
            results (list[MatchResult]): List of match results.

        Returns:
            str: Formatted output as a string.
        """
        raise NotImplementedError


class JSONFormatter(OutputFormatter):
    """
    Formats match results as a JSON string.

    Args:
        pattern (str): The search pattern used.
        flags (dict): Dictionary of CLI flags and options.

    Methods:
        format(results): Convert match results to a JSON string.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, pattern: str, flags: dict) -> None:
        self.pattern = pattern
        self.flags = {
            k: v
            for k, v in flags.items()
            if k
            in [
                "ignore_case",
                "invert_match",
                "line_number",
                "count",
                "after_context",
                "before_context",
                "recursive",
            ]
        }

    def format(self, results: list[MatchResult]) -> str:
        """
        Convert a list of MatchResult objects to a JSON string.

        Args:
            results (list[MatchResult]): List of match results.

        Returns:
            str: JSON-formatted string containing grouped results and metadata.
        """

        grouped = {}
        for result in results:
            if result.filename not in grouped:
                grouped[result.filename] = []
            grouped[result.filename].append(result)

        output = {
            "results": [],
            "metadata": {
                "pattern": self.pattern,
                "flags": self.flags,
                "total_matches": len(results),
            },
        }

        for filename, matches in grouped.items():
            file_entry = {
                "file": filename,
                "matches": [match.to_dict() for match in matches],
            }
            output["results"].append(file_entry)

        return json.dumps(output, indent=2, ensure_ascii=False)


class CSVFormatter(OutputFormatter):
    """Format results as CSV"""

    # pylint: disable=too-few-public-methods

    def __init__(self, include_header=True):
        self.include_header = include_header

    def format(self, results: list[MatchResult]) -> str:
        """
        Convert matches to CSV format.
        """

        output = io.StringIO()
        writer = csv.writer(output)

        if self.include_header:
            writer.writerow(["file", "line", "content", "match_start", "match_end"])

        for result in results:
            writer.writerow(
                [
                    result.filename,
                    result.line_num,
                    result.line_content,
                    result.match_start if result.match_start is not None else "",
                    result.match_end if result.match_end is not None else "",
                ]
            )

        return output.getvalue()


class MarkdownFormatter(OutputFormatter):
    """Format results as Markdown table"""

    # pylint: disable=too-few-public-methods

    def format(self, results: list[MatchResult]) -> str:
        """
        Create a Markdown table.
        """

        lines = []

        lines.append("| File | Line | Content |")
        lines.append("|------|------|---------|")

        for result in results:
            content = result.line_content.replace("|", "\\|")

            if len(content) > 80:
                content = content[:77] + "..."

            line = f"| {result.filename} | {result.line_num} | {content} |"
            lines.append(line)

        return "\n".join(lines)


def get_lexer_for_file(filename: str):
    """
    Get Pygments lexer for a file.

    Returns:
        Lexer object or None if can't detect
    """
    try:
        return lexers.get_lexer_for_filename(filename)
    except ClassNotFound:
        return None


def highlight_line(line: str, filename: str) -> str:
    """
    Apply syntax highlighting to a single line.

    Args:
        line: The line to highlight
        filename: Used to detect language

    Returns:
        Highlighted line with ANSI color codes, or original line if no lexer found
    """
    lexer = get_lexer_for_file(filename)

    if lexer is None:
        return line

    highlighted = highlight(line, lexer, Terminal256Formatter(style="monokai"))

    return highlighted.rstrip()


def apply_match_highlight(line: str, pattern: str) -> str:
    """
    Short helper to wrap the first regex match in ANSI codes.

    Args:
        line (str): Input line to search.
        pattern (str): Regular expression to match.

    Returns:
        str: Line with the first match wrapped in ANSI escape sequences
        for bold red text; unchanged if no match is found.
    """

    match = re.search(pattern, line)
    if match:
        start, end = match.span()
        return line[:start] + "\033[1;31m" + line[start:end] + "\033[0m" + line[end:]
    return line
