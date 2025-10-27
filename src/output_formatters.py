import json
from typing import Optional
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod


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

    def to_dict(self):
        """
        Convert the MatchResult to a dictionary for serialization.

        Returns:
            dict: Dictionary representation of the match result.
        """
        return asdict(self)


class OutputFormatter(ABC):
    """
    Base class for output formatters.

    Methods:
        format(results): Format a list of MatchResult objects.
    """


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

    def __init__(self, pattern: str, flags: dict):
        self.pattern = pattern
        self.flags = flags

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
