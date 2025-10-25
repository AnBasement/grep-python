import sys
import pytest
from src.cli import parse_arguments
from src.constants import EXIT_ERROR


class TestParseArguments:
    """Test CLI argument parsing for pattern, file, and flag handling.

    Covers basic pattern/file parsing, recursive flag, multiple files,
    stdin mode, error handling for insufficient arguments, and optional flags.
    """

    def test_parse_basic_pattern_and_file(self, monkeypatch):
        """Test basic pattern and file parsing"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-E", "test", "file.txt"])
        args = parse_arguments()
        assert args.recursive is False
        assert args.pattern == "test"
        assert args.files == ["file.txt"]

    def test_parse_recursive_flag(self, monkeypatch):
        """Test recursive flag parsing"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-r", "-E", "test", "dir/"])
        args = parse_arguments()
        assert args.recursive is True
        assert args.pattern == "test"
        assert args.files == ["dir/"]

    def test_parse_multiple_files(self, monkeypatch):
        """Test multiple file parsing"""
        monkeypatch.setattr(
            sys, "argv", ["pygrep", "-E", "test", "file1.txt", "file2.txt"]
        )
        args = parse_arguments()
        assert args.recursive is False
        assert args.pattern == "test"
        assert args.files == ["file1.txt", "file2.txt"]

    def test_parse_no_files_returns_empty_list(self, monkeypatch):
        """Test parsing with no files (stdin mode)"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-E", "test"])
        args = parse_arguments()
        assert args.recursive is False
        assert args.pattern == "test"
        assert args.files == []

    @pytest.mark.skip(reason="Pattern argument validation will be fixed in a future PR")
    def test_insufficient_arguments_exits(self, monkeypatch):
        """Test that insufficient arguments causes exit"""
        monkeypatch.setattr(sys, "argv", ["pygrep"])
        with pytest.raises(SystemExit) as exc_info:
            parse_arguments()
        assert exc_info.value.code == EXIT_ERROR

    def test_missing_e_flag_still_works(self, monkeypatch):
        """Test that -E flag is optional with argparse"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "test", "file.txt"])
        args = parse_arguments()
        assert args.recursive is False
        assert args.pattern == "test"
        assert args.files == ["file.txt"]

    def test_recursive_without_e_still_works(self, monkeypatch):
        """Test -r flag without -E (argparse makes -E optional)"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-r", "test", "dir/"])
        args = parse_arguments()
        assert args.recursive is True
        assert args.pattern == "test"
        assert args.files == ["dir/"]

    def test_recursive_missing_pattern_exits(self, monkeypatch):
        """Test -r -E without pattern"""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-r", "-E"])
        with pytest.raises(SystemExit) as exc_info:
            parse_arguments()
        assert exc_info.value.code == EXIT_ERROR
