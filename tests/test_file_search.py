from src.file_search import (
    search_file,
    search_multiple_files,
    get_files_recursively,
    search_directory_recursively,
)


class TestFileSearch:
    def test_search_file_single_file_matches_and_prints_line(self, tmp_path, capsys):
        p = tmp_path / "sample.txt"
        p.write_text("hello\nworld\nfoo")
        assert search_file(str(p), "wo.+") is True
        captured = capsys.readouterr()
        assert "world" in captured.out

    def test_search_file_prints_filename_when_flag_true(self, tmp_path, capsys):
        p = tmp_path / "sample.txt"
        p.write_text("alpha\nbeta\n")
        assert search_file(str(p), "^a.+", print_filename=True) is True
        out = capsys.readouterr().out
        assert f"{p}:alpha" in out

    def test_search_file_handles_nonexistent_and_directory(self, tmp_path, capsys):
        missing = tmp_path / "missing.txt"
        assert search_file(str(missing), "a") is False
        assert "no such file or directory" in capsys.readouterr().err.lower()

        assert search_file(str(tmp_path), "a") is False
        assert "is a directory" in capsys.readouterr().err.lower()

    def test_search_multiple_files(self, tmp_path, capsys):
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

    def test_get_files_recursively_errors(self, tmp_path, monkeypatch, capsys):
        not_there = tmp_path / "nope"
        files = get_files_recursively(str(not_there))
        assert files == []
        assert "no such file or directory" in capsys.readouterr().err.lower()

        filep = tmp_path / "f.txt"
        filep.write_text("x")
        files = get_files_recursively(str(filep))
        assert files == []
        assert "not a directory" in capsys.readouterr().err
