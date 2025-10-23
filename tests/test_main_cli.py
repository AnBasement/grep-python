import io
import sys

import pytest

from src.main import main
from src import main as mainmod
from src.constants import EXIT_MATCH_FOUND, EXIT_NO_MATCH, EXIT_ERROR


class TestMainCLI:
    """
    Test CLI entry point for argument parsing, file and stdin modes,
    error handling, and exit codes.
    """

    def run_main(self, argv, stdin_data=None):
        """
        Run the main() function with custom argv and optional stdin data.

        Returns the exit code from SystemExit.
        """
        old_argv = sys.argv
        old_stdin = sys.stdin
        try:
            sys.argv = argv
            if stdin_data is not None:
                sys.stdin = io.StringIO(stdin_data)
            with pytest.raises(SystemExit) as e:
                main()
            return e.value.code
        finally:
            sys.argv = old_argv
            sys.stdin = old_stdin

    def test_stdin_mode_match_and_no_match(self):
        """Check stdin mode returns correct exit codes for match and no match."""
        code = self.run_main(["prog", "-E", "ab"], stdin_data="xxabyy")
        assert code == EXIT_MATCH_FOUND

        code = self.run_main(["prog", "-E", "ab"], stdin_data="xyz")
        assert code == EXIT_NO_MATCH

    def test_invalid_first_arg(self):
        """Verify invalid CLI flag returns error exit code."""
        code = self.run_main(["prog", "-X", "pattern"])
        assert code == EXIT_ERROR

    def test_single_file_mode(self, tmp_path):
        """Test matching and non-matching patterns in single file mode."""
        f = tmp_path / "data.txt"
        f.write_text("hello\nworld\n")
        code = self.run_main(["prog", "-E", "^wor", str(f)])
        assert code == EXIT_MATCH_FOUND

        code = self.run_main(["prog", "-E", "^zzz", str(f)])
        assert code == EXIT_NO_MATCH

    def test_multi_file_mode(self, tmp_path):
        """Check multi-file search returns match exit code when any file matches."""
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("aaa\n")
        f2.write_text("bbb\naba\n")
        code = self.run_main(["prog", "-E", "ab", str(f1), str(f2)])
        assert code == EXIT_MATCH_FOUND

    def test_recursive_mode(self, tmp_path):
        """
        Test recursive directory search returns match exit code for matching files.
        """
        d1 = tmp_path / "dir1"
        d1.mkdir()
        (d1 / "x.txt").write_text("foo\nbar\n")
        code = self.run_main(["prog", "-r", "-E", "ba", str(tmp_path)])
        assert code == EXIT_MATCH_FOUND

    def test_recursive_without_e_works(self, tmp_path):
        """Verify recursive mode works without -E flag and returns correct exit code."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        test_file = test_dir / "test.txt"
        test_file.write_text("no match here\n")

        code = self.run_main(["prog", "-r", "pattern", str(test_dir)], stdin_data="")
        assert code == EXIT_NO_MATCH

    def test_unexpected_error_caught(self, monkeypatch):
        """
        Check that unexpected errors in match_pattern are caught
        and return error exit code.
        """
        def boom(*args, **kwargs):
            raise ValueError("boom")

        monkeypatch.setattr(mainmod, "match_pattern", boom)

        code = self.run_main(["prog", "-E", "x"], stdin_data="abc")
        assert code == EXIT_ERROR
