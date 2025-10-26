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

    def test_combined_before_and_after_context(self, tmp_path, capsys):
        """Test that both before and after context lines are printed correctly."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nline2\nmatch\nline4\nline5\nline6")
        assert search_file(str(p), "match", before_context=4, after_context=2) is True
        out = capsys.readouterr().out
        expected_output = "line1\nline2\nmatch\nline4\nline5\n"
        assert expected_output in out

    def test_no_duplicate_lines_in_context(self, tmp_path, capsys):
        """Ensure no duplicate lines are printed when contexts overlap."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nmatch\nline3\nmatch\nline5")
        assert search_file(str(p), "match", before_context=1, after_context=1) is True
        out = capsys.readouterr().out
        expected_output = "line1\nmatch\nline3\nmatch\nline5\n"
        assert out.count("match") == 2
        assert expected_output in out

    def test_multiple_matches_with_varied_spacing(self, tmp_path, capsys):
        """Check context lines for multiple matches with different spacing."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nmatch1\nline3\nline4\nmatch2\nline6")
        assert search_file(str(p), "match", before_context=1, after_context=1) is True
        out = capsys.readouterr().out
        expected_output = "line1\nmatch1\nline3\nline4\nmatch2\nline6\n"
        assert expected_output in out


class TestPatternSourceMatching:
    """Tests search_file() function with multiple patterns.

    Verifies that when multiple patterns are provided via the patterns parameter,
    lines match if any pattern matches (OR logic).
    """

    def test_single_pattern_in_patterns_list(self, tmp_path, capsys):
        """Test that search_file matches when a single pattern
        is provided via patterns parameter."""
        p = tmp_path / "data.txt"
        p.write_text("foo\nbar\nbaz")
        assert search_file(str(p), "dummy", patterns=["foo"]) is True
        out = capsys.readouterr().out
        assert "foo" in out
        assert "bar" not in out
        assert "baz" not in out

    def test_multiple_patterns_or_logic(self, tmp_path, capsys):
        """Test that search_file uses OR logic when multiple patterns are provided."""
        p = tmp_path / "data.txt"
        p.write_text("foo\nbar\nbaz")
        assert search_file(str(p), "dummy", patterns=["foo", "baz"]) is True
        out = capsys.readouterr().out
        assert "foo" in out
        assert "baz" in out
        assert "bar" not in out

    def test_patterns_list_and_single_pattern_combined(self, tmp_path, capsys):
        """Test that search_file combines both patterns list and pattern parameter."""
        p = tmp_path / "data.txt"
        p.write_text("foo\nbar\nbaz")
        assert search_file(str(p), "bar", patterns=["foo", "baz"]) is True
        out = capsys.readouterr().out
        assert "foo" in out
        assert "bar" in out
        assert "baz" in out


class TestQuietMode:
    """Tests for quiet mode functionality in file search."""

    def test_quiet_mode_no_output_when_match_found(self, tmp_path, capsys):
        """Verify that quiet mode suppresses all output when a match is found."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nmatch\nline3")
        assert search_file(str(p), "match", quiet=True) is True
        out = capsys.readouterr().out
        assert out == ""

    def test_quiet_mode_returns_true_on_first_match(self, tmp_path):
        """Verify that quiet mode returns True when a match is found."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nmatch\nline3")
        result = search_file(str(p), "match", quiet=True)
        assert result is True

    def test_quiet_mode_returns_false_when_no_match(self, tmp_path):
        """Verify that quiet mode returns False when no match is found."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nline2\nline3")
        result = search_file(str(p), "nomatch", quiet=True)
        assert result is False

    def test_quiet_mode_exits_early_on_first_match(self, tmp_path, capsys):
        """
        Verify that quiet mode exits immediately on first match without
        processing remaining lines.
        """
        p = tmp_path / "data.txt"
        lines = [f"line{i}" for i in range(1000)]
        lines[100] = "match"
        p.write_text("\n".join(lines))

        result = search_file(str(p), "match", quiet=True)
        assert result is True
        out = capsys.readouterr().out
        assert out == ""

    def test_quiet_mode_with_patterns_list(self, tmp_path, capsys):
        """Verify that quiet mode works with patterns list parameter."""
        p = tmp_path / "data.txt"
        p.write_text("foo\nbar\nbaz")
        result = search_file(str(p), "dummy", patterns=["foo", "baz"], quiet=True)
        assert result is True
        out = capsys.readouterr().out
        assert out == ""

    def test_quiet_mode_search_multiple_files_returns_true(self, tmp_path, capsys):
        """
        Verify that quiet mode in search_multiple_files returns True on first match.
        """
        p1 = tmp_path / "a.txt"
        p2 = tmp_path / "b.txt"
        p1.write_text("line1\nline2")
        p2.write_text("match\nline4")
        result = search_multiple_files([str(p1), str(p2)], "match", quiet=True)
        assert result is True
        out = capsys.readouterr().out
        assert out == ""

    def test_quiet_mode_search_directory_recursively_returns_true(
        self, tmp_path, capsys
    ):
        """
        Verify that quiet mode in search_directory_recursively returns True
        on first match.
        """
        sub = tmp_path / "sub"
        sub.mkdir()
        f1 = tmp_path / "root.txt"
        f2 = sub / "nested.txt"
        f1.write_text("line1\nline2")
        f2.write_text("match\nline4")
        result = search_directory_recursively(str(tmp_path), "match", quiet=True)
        assert result is True
        out = capsys.readouterr().out
        assert out == ""


class TestMaxCount:
    """Tests for max_count functionality in file search."""

    def test_max_count_stops_after_limit(self, tmp_path, capsys):
        """Verify that max_count stops printing after reaching the limit."""
        p = tmp_path / "data.txt"
        p.write_text("match1\nmatch2\nmatch3\nmatch4\nmatch5")
        assert search_file(str(p), "match", max_count=2) is True
        out = capsys.readouterr().out
        assert out.count("match") == 2

    def test_max_count_with_count_only_flag(self, tmp_path, capsys):
        """Verify that max_count respects count_only flag and stops at limit."""
        p = tmp_path / "data.txt"
        p.write_text("match1\nmatch2\nmatch3\nmatch4")
        assert search_file(str(p), "match", max_count=3, count_only=True) is True
        out = capsys.readouterr().out
        assert "3" in out

    def test_max_count_zero_means_no_limit(self, tmp_path, capsys):
        """Verify that max_count=0 (default) means no limit on matches."""
        p = tmp_path / "data.txt"
        p.write_text("match1\nmatch2\nmatch3\nmatch4\nmatch5")
        assert search_file(str(p), "match", max_count=0) is True
        out = capsys.readouterr().out
        assert out.count("match") == 5

    def test_max_count_returns_true_when_limit_reached(self, tmp_path):
        """Verify that max_count returns True when the limit is reached."""
        p = tmp_path / "data.txt"
        p.write_text("match1\nmatch2\nmatch3")
        result = search_file(str(p), "match", max_count=2)
        assert result is True

    def test_max_count_returns_false_when_no_matches(self, tmp_path):
        """Verify that max_count returns False when no matches are found."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nline2\nline3")
        result = search_file(str(p), "nomatch", max_count=2)
        assert result is False

    def test_max_count_returns_false_when_fewer_matches_than_limit(
        self, tmp_path, capsys
    ):
        """Verify that max_count returns False when fewer matches exist than limit."""
        p = tmp_path / "data.txt"
        p.write_text("match1\nmatch2\nline3")
        result = search_file(str(p), "match", max_count=10)
        assert result is False
        out = capsys.readouterr().out
        assert out.count("match") == 2

    def test_max_count_with_patterns_list(self, tmp_path, capsys):
        """Verify that max_count works with multiple patterns (OR logic)."""
        p = tmp_path / "data.txt"
        p.write_text("foo\nbar\nbaz\nfoo\nbar\nbaz")
        result = search_file(str(p), "dummy", patterns=["foo", "bar"], max_count=3)
        assert result is True
        out = capsys.readouterr().out
        assert out.count("\n") == 3

    def test_max_count_with_before_context(self, tmp_path, capsys):
        """Verify that max_count stops after N matches even with before_context."""
        p = tmp_path / "data.txt"
        p.write_text("line0\nmatch1\nline2\nmatch2\nline4\nmatch3")
        result = search_file(str(p), "match", max_count=2, before_context=1)
        assert result is True
        out = capsys.readouterr().out
        assert out.count("match") == 2


class TestFilesOnlyModes:
    """Tests for files-only output modes (-l and -L)."""

    def test_files_with_matches_shows_filename(self, tmp_path, capsys):
        """Verify that -l flag shows only filename when match is found."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nmatch\nline3")
        assert search_file(str(p), "match", files_with_matches=True) is True
        out = capsys.readouterr().out
        assert str(p) in out
        assert "line1" not in out
        assert "line3" not in out

    def test_files_with_matches_returns_false_on_no_match(self, tmp_path, capsys):
        """Verify that -l flag returns False when no match is found."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nline2\nline3")
        assert search_file(str(p), "nomatch", files_with_matches=True) is False
        out = capsys.readouterr().out
        assert out == ""

    def test_files_without_match_shows_filename_on_no_match(self, tmp_path, capsys):
        """Verify that -L flag shows filename when no match is found."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nline2\nline3")
        assert search_file(str(p), "nomatch", files_without_match=True) is True
        out = capsys.readouterr().out
        assert str(p) in out

    def test_files_without_match_returns_false_on_match(self, tmp_path, capsys):
        """Verify that -L flag returns False when match is found."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nmatch\nline3")
        assert search_file(str(p), "match", files_without_match=True) is False
        out = capsys.readouterr().out
        assert out == ""

    def test_files_with_matches_with_multiple_patterns(self, tmp_path, capsys):
        """Verify that -l works with multiple patterns (OR logic)."""
        p = tmp_path / "data.txt"
        p.write_text("apple\nbanana\ncherry")
        result = search_file(
            str(p),
            "dummy",
            patterns=["error", "banana"],
            files_with_matches=True,
        )
        assert result is True
        out = capsys.readouterr().out
        assert str(p) in out
        assert "apple" not in out
        assert "banana" not in out

    def test_files_with_matches_with_invert_match(self, tmp_path, capsys):
        """Verify that -l respects invert_match (-v) flag."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nline2\nline3")
        result = search_file(
            str(p),
            "nomatch",
            files_with_matches=True,
            invert_match=True,
        )
        assert result is True
        out = capsys.readouterr().out
        assert str(p) in out

    def test_files_with_matches_with_ignore_case(self, tmp_path, capsys):
        """Verify that -l respects ignore_case (-i) flag."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nMATCH\nline3")
        result = search_file(
            str(p),
            "match",
            files_with_matches=True,
            ignore_case=True,
        )
        assert result is True
        out = capsys.readouterr().out
        assert str(p) in out

    def test_files_with_matches_multiple_files_with_matches(self, tmp_path, capsys):
        """Verify -l shows filenames for multiple files that have matches."""
        file1 = tmp_path / "file1.txt"
        file1.write_text("error in file1")
        file2 = tmp_path / "file2.txt"
        file2.write_text("error in file2")
        file3 = tmp_path / "file3.txt"
        file3.write_text("no problem here")

        result = search_multiple_files(
            [str(file1), str(file2), str(file3)],
            "error",
            files_with_matches=True,
        )
        assert result is True
        out = capsys.readouterr().out
        assert str(file1) in out
        assert str(file2) in out
        assert str(file3) not in out

    def test_files_without_match_multiple_files_without_matches(self, tmp_path, capsys):
        """Verify -L shows filenames for multiple files that don't have matches."""
        file1 = tmp_path / "file1.txt"
        file1.write_text("no problem here")
        file2 = tmp_path / "file2.txt"
        file2.write_text("all good")
        file3 = tmp_path / "file3.txt"
        file3.write_text("error in file3")

        result = search_multiple_files(
            [str(file1), str(file2), str(file3)],
            "error",
            files_without_match=True,
        )
        assert result is True
        out = capsys.readouterr().out
        assert str(file1) in out
        assert str(file2) in out
        assert str(file3) not in out

    def test_files_with_matches_mixed_files(self, tmp_path, capsys):
        """Verify -l shows only files with matches when mixed."""
        file1 = tmp_path / "file1.txt"
        file1.write_text("match here")
        file2 = tmp_path / "file2.txt"
        file2.write_text("nothing found")
        file3 = tmp_path / "file3.txt"
        file3.write_text("another match")

        result = search_multiple_files(
            [str(file1), str(file2), str(file3)],
            "match",
            files_with_matches=True,
        )
        assert result is True
        out = capsys.readouterr().out
        assert str(file1) in out
        assert str(file3) in out
        assert str(file2) not in out

    def test_files_only_ignores_line_numbers_flag(self, tmp_path, capsys):
        """Verify that print_line_number is ignored in files-only mode."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nmatch\nline3")
        search_file(
            str(p),
            "match",
            files_with_matches=True,
            print_line_number=True,
        )
        out = capsys.readouterr().out
        assert str(p) in out
        assert ":" not in out or out.count(":") == 1

    def test_files_only_ignores_context_flags(self, tmp_path, capsys):
        """Verify that context flags are ignored in files-only mode."""
        p = tmp_path / "data.txt"
        p.write_text("line1\nmatch\nline3\nline4")
        search_file(
            str(p),
            "match",
            files_with_matches=True,
            after_context=2,
            before_context=2,
        )
        out = capsys.readouterr().out
        assert str(p) in out
        assert "line1" not in out
        assert "line3" not in out
        assert "line4" not in out
