import pytest
import sys
from src.cli import parse_arguments
from src.constants import EXIT_ERROR


class TestParseArguments:
    def test_parse_basic_pattern_and_file(self, monkeypatch):
        """Test basic pattern and file parsing"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-E", "test", "file.txt"])
        recursive, pattern, search_paths = parse_arguments()
        assert recursive is False
        assert pattern == "test"
        assert search_paths == ["file.txt"]

    def test_parse_recursive_flag(self, monkeypatch):
        """Test recursive flag parsing"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-r", "-E", "test", "dir/"])
        recursive, pattern, search_paths = parse_arguments()
        assert recursive is True
        assert pattern == "test"
        assert search_paths == ["dir/"]

    def test_parse_multiple_files(self, monkeypatch):
        """Test multiple file parsing"""
        monkeypatch.setattr(
            sys, "argv", ["pygrep", "-E", "test", "file1.txt", "file2.txt"]
        )
        recursive, pattern, search_paths = parse_arguments()
        assert recursive is False
        assert pattern == "test"
        assert search_paths == ["file1.txt", "file2.txt"]

    def test_parse_no_files_returns_empty_list(self, monkeypatch):
        """Test parsing with no files (stdin mode)"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-E", "test"])
        recursive, pattern, search_paths = parse_arguments()
        assert recursive is False
        assert pattern == "test"
        assert search_paths == []

    def test_insufficient_arguments_exits(self, monkeypatch):
        """Test that insufficient arguments causes exit"""
        monkeypatch.setattr(sys, "argv", ["pygrep"])
        with pytest.raises(SystemExit) as exc_info:
            parse_arguments()
        assert exc_info.value.code == EXIT_ERROR

    def test_missing_E_flag_still_works(self, monkeypatch):
        """Test that -E flag is optional with argparse"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "test", "file.txt"])
        recursive, pattern, search_paths = parse_arguments()
        assert recursive is False
        assert pattern == "test"
        assert search_paths == ["file.txt"]

    def test_recursive_without_E_still_works(self, monkeypatch):
        """Test -r flag without -E (argparse makes -E optional)"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-r", "test", "dir/"])
        recursive, pattern, search_paths = parse_arguments()
        assert recursive is True
        assert pattern == "test"
        assert search_paths == ["dir/"]

    def test_recursive_missing_pattern_exits(self, monkeypatch):
        """Test -r -E without pattern"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-r", "-E"])
        with pytest.raises(SystemExit) as exc_info:
            parse_arguments()
        assert exc_info.value.code == EXIT_ERROR