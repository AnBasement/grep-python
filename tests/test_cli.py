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


class TestEFlagParsing:
    """Tests CLI argument parsing for the -e flag.

    Verifies that single and multiple -e flags are parsed correctly,
    and that -e flags combine with positional patterns as expected.
    """

    def test_single_e_flag(self, monkeypatch):
        """Test that a single -e flag is parsed correctly."""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-e", "foo", "file.txt"])
        args = parse_arguments()
        assert args.patterns == ["foo"]
        assert args.pattern == "file.txt"
        assert args.files == []
        assert args.pattern_list == ["file.txt", "foo"]

    def test_multiple_e_flags(self, monkeypatch):
        """Test that multiple -e flags are combined into a list."""
        monkeypatch.setattr(
            sys, "argv", ["pygrep", "-e", "foo", "-e", "bar", "file.txt"]
        )
        args = parse_arguments()
        assert args.patterns == ["foo", "bar"]
        assert args.pattern == "file.txt"
        assert args.files == []
        assert args.pattern_list == ["file.txt", "foo", "bar"]

    def test_e_flag_and_positional_pattern(self, monkeypatch):
        """Test that both -e and positional pattern are parsed."""
        monkeypatch.setattr(sys, "argv", ["pygrep", "-e", "foo", "bar", "file.txt"])
        args = parse_arguments()
        assert args.patterns == ["foo"]
        assert args.pattern == "bar"
        assert args.files == ["file.txt"]
        assert args.pattern_list == ["bar", "foo"]

    def test_patterns_loaded_from_file(self, tmp_path, monkeypatch):
        """Test that -f flag loads patterns from file."""
        pattern_file = tmp_path / "patterns.txt"
        pattern_file.write_text("foo\nbaz\n")
        monkeypatch.setattr(
            sys, "argv", ["pygrep", "-f", str(pattern_file), "file.txt"]
        )

        args = parse_arguments()
        assert args.pattern_list == ["file.txt", "foo", "baz"]

    def test_empty_lines_skipped_in_pattern_file(self, tmp_path, monkeypatch):
        """Test that empty lines in pattern file are skipped when using -f flag."""
        pattern_file = tmp_path / "patterns.txt"
        pattern_file.write_text("foo\n\nbaz\n")
        monkeypatch.setattr(sys, "argv", ["pygrep", "-f", str(pattern_file)])

        args = parse_arguments()
        assert args.pattern_list == ["foo", "baz"]

    def test_f_flag_missing_pattern_file_exits(self, tmp_path, monkeypatch):
        """Test that using -f with a missing pattern file
        causes parse_arguments() to exit."""
        missing = tmp_path / "missing.txt"
        monkeypatch.setattr(sys, "argv", ["pygrep", "-f", str(missing)])
        with pytest.raises(SystemExit) as exc_info:
            parse_arguments()
        assert exc_info.value.code == EXIT_ERROR
