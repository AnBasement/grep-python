from src.file_search import (
    search_file,
    search_multiple_files,
    get_files_recursively,
    search_directory_recursively,
)


class TestFileSearch:
    """Tests file search functions for matching, output, and error handling."""

    def test_search_file_single_file_matches_and_prints_line(self, tmp_path, capsys):
        """Verify search_file finds a match and prints the matching line."""
        p = tmp_path / "sample.txt"
        p.write_text("hello\nworld\nfoo")
        assert search_file(str(p), "wo.+") is True
        captured = capsys.readouterr()
        assert "world" in captured.out

    def test_search_file_prints_filename_when_flag_true(self, tmp_path, capsys):
        """Check that search_file includes filename in output when requested."""
        p = tmp_path / "sample.txt"
        p.write_text("alpha\nbeta\n")
        assert search_file(str(p), "^a.+", print_filename=True) is True
        out = capsys.readouterr().out
        assert f"{p}:alpha" in out

    def test_search_file_handles_nonexistent_and_directory(self, tmp_path, capsys):
        """Confirm search_file handles missing files and directories with errors."""
        missing = tmp_path / "missing.txt"
        assert search_file(str(missing), "a") is False
        assert "no such file or directory" in capsys.readouterr().err.lower()

        assert search_file(str(tmp_path), "a") is False
        assert "is a directory" in capsys.readouterr().err.lower()

    def test_search_multiple_files(self, tmp_path, capsys):
        """Test searching across multiple files and correct output formatting."""
        p1 = tmp_path / "a.txt"
        p2 = tmp_path / "b.txt"
        p1.write_text("xxx\nyyy")
        p2.write_text("abc\nzzz")
        assert search_multiple_files([str(p1), str(p2)], "^ab") is True
        out = capsys.readouterr().out
        assert f"{p2}:abc" in out

    def test_get_files_recursively_and_search_directory_recursively(
        self, tmp_path, capsys
    ):
        """Check recursive file discovery and directory search for matches."""
        sub = tmp_path / "sub"
        sub.mkdir()
        f1 = tmp_path / "root.txt"
        f2 = sub / "nested.txt"
        f1.write_text("foo")
        f2.write_text("bar")

        files = get_files_recursively(str(tmp_path))
        assert str(f1) in files
        assert str(f2) in files

        assert search_directory_recursively(str(tmp_path), "ba+") is True
        out = capsys.readouterr().out
        assert f"{f2}:bar" in out

    def test_get_files_recursively_errors(self, tmp_path, capsys):
        """Verify error handling for invalid paths in get_files_recursively."""
        not_there = tmp_path / "nope"
        files = get_files_recursively(str(not_there))
        assert not files
        assert "no such file or directory" in capsys.readouterr().err.lower()

        filep = tmp_path / "f.txt"
        filep.write_text("x")
        files = get_files_recursively(str(filep))
        assert not files
        assert "not a directory" in capsys.readouterr().err

class TestContextLines:
    """Tests for before and after context line functionality in file searches."""

    def test_after_context_shows_correct_number_of_lines(self, tmp_path, capsys):
        """Verify after context lines are printed correctly after a match."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nmatch\nline3\nline4\nline5\nline6")
        assert search_file(str(p), "match", after_context=2) is True
        out = capsys.readouterr().out
        expected_output = "match\nline3\nline4\n"
        assert expected_output in out

    def test_after_context_without_matches_returns_nothing(self, tmp_path, capsys):
        """Check that no output is produced when there are no matches."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nline2\nline3")
        assert search_file(str(p), "nomatch", after_context=2) is False
        out = capsys.readouterr().out
        assert out == ""

    def test_after_context_within_bounds(self, tmp_path, capsys):
        """Ensure after context does not exceed file bounds."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nmatch\nline3")
        assert search_file(str(p), "match", after_context=5) is True
        out = capsys.readouterr().out
        expected_output = "match\nline3\n"
        assert expected_output in out

    def test_before_context_shows_correct_number_of_lines(self, tmp_path, capsys):
        """Verify before context lines are printed correctly before a match."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nline2\nmatch\nline4\nline5")
        assert search_file(str(p), "match", before_context=3) is True
        out = capsys.readouterr().out
        expected_output = "line1\nline2\nmatch\n"
        assert expected_output in out

    def test_before_context_at_start_of_file(self, tmp_path, capsys):
        """Check that before context at start of file does not crash."""
        p = tmp_path / "data.txt"
        p.write_text("match\nline2\nline3")
        assert search_file(str(p), "match", before_context=2) is True
        out = capsys.readouterr().out
        expected_output = "match\n"
        assert expected_output in out

    def test_before_context_with_first_line_match(self, tmp_path, capsys):
        """Ensure before context works when the first line is a match."""
        p = tmp_path / "data.txt"
        p.write_text("match\nline2\nline3")
        assert search_file(str(p), "match", before_context=1) is True
        out = capsys.readouterr().out
        expected_output = "match\n"
        assert expected_output in out