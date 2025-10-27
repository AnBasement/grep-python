import unittest
import json
import subprocess
import tempfile
import os
import shutil
from src.output_formatters import JSONFormatter, MatchResult


class TestJSONFormatter(unittest.TestCase):
    """Test the JSON output formatter"""

    def setUp(self):
        """Run before each test - set up common test data"""

        self.sample_matches = [
            MatchResult("file1.txt", 1, "test line", 0, 4),
            MatchResult("file1.txt", 5, "another test", 8, 12),
            MatchResult("file2.txt", 10, "test here", 0, 4),
        ]
        self.formatter = JSONFormatter("test", {})

    def test_output_is_valid_json(self):
        """Verify the output can be parsed as JSON"""
        output = self.formatter.format(self.sample_matches)

        try:
            parsed = json.loads(output)
            self.assertIsInstance(parsed, dict)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_output_structure(self):
        """Verify the JSON has expected structure"""
        output = self.formatter.format(self.sample_matches)
        data = json.loads(output)

        self.assertIn("results", data)
        self.assertIn("metadata", data)

        self.assertIsInstance(data["results"], list)

        self.assertEqual(data["metadata"]["pattern"], "test")

    def test_matches_grouped_by_file(self):
        """Verify matches are grouped by filename"""
        output = self.formatter.format(self.sample_matches)
        data = json.loads(output)

        results = data["results"]

        self.assertEqual(len(results), 2)

        file1_entry = next(r for r in results if r["file"] == "file1.txt")

        self.assertEqual(len(file1_entry["matches"]), 2)

    def test_empty_results(self):
        """Handle case with no matches"""
        output = self.formatter.format([])
        data = json.loads(output)

        self.assertEqual(len(data["results"]), 0)
        self.assertEqual(data["metadata"]["total_matches"], 0)

    def test_special_characters_in_content(self):
        """Verify special characters are properly escaped"""
        matches = [
            MatchResult("file.txt", 1, 'line with "quotes"', 0, 4),
            MatchResult("file.txt", 2, "line with\nnewline", 0, 4),
            MatchResult("file.txt", 3, "line with\ttab", 0, 4),
        ]

        output = self.formatter.format(matches)

        data = json.loads(output)

        lines = [m["line_content"] for m in data["results"][0]["matches"]]
        self.assertIn('line with "quotes"', lines)

    def test_unicode_content(self):
        """Handle unicode characters in matches"""
        matches = [
            MatchResult("file.txt", 1, "Søk etter mønster 🔍", 0, 3),
            MatchResult("file.txt", 2, "日本語のテキスト", 0, 3),
        ]

        output = self.formatter.format(matches)

        self.assertIn("Søk", output)

    def test_cli_json_output(self):
        """
        Integration test: Run the CLI with --json flag
        This goes in a separate test file like tests/test_cli_integration.py
        """

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("test line 1\n")
            f.write("another line\n")
            f.write("test line 3\n")
            test_file = f.name

        try:
            result = subprocess.run(
                ["./pygrep.sh", "--json", "test", test_file],
                capture_output=True,
                text=True,
                check=True,
            )

            output = json.loads(result.stdout)

            self.assertEqual(len(output["results"]), 1)
            self.assertEqual(len(output["results"][0]["matches"]), 2)

        finally:

            if os.path.exists(test_file):
                os.unlink(test_file)


class TestJSONFormatterIntegration(unittest.TestCase):
    """Integration tests for JSON output with multiple files and recursive search."""

    def setUp(self):
        """Create temp files and directories for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.file1 = os.path.join(self.temp_dir, "file1.txt")
        self.file2 = os.path.join(self.temp_dir, "file2.txt")
        with open(self.file1, "w", encoding="utf-8") as f:
            f.write("test line 1\nno match here\nanother test line\n")
        with open(self.file2, "w", encoding="utf-8") as f:
            f.write("test line 2\nsomething else\nfinal test\n")

    def tearDown(self):
        """Clean up temp files and directories."""
        shutil.rmtree(self.temp_dir)

    def test_json_output_multiple_files(self):
        """Verify JSON output works with multiple files and contains match data."""
        result = subprocess.run(
            ["./pygrep.sh", "--json", "test", self.file1, self.file2],
            capture_output=True,
            text=True,
            check=True,
        )
        output = json.loads(result.stdout)
        self.assertEqual(len(output["results"]), 2)
        for file_entry in output["results"]:
            self.assertGreaterEqual(len(file_entry["matches"]), 1)
            for match in file_entry["matches"]:
                self.assertIn("line_content", match)
                self.assertIn("line_num", match)
                self.assertIn("filename", match)

    def test_json_output_recursive_search(self):
        """
        Verify JSON output works with recursive directory search & contains match data.
        """
        sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub_dir)
        sub_file = os.path.join(sub_dir, "subfile.txt")
        with open(sub_file, "w", encoding="utf-8") as f:
            f.write("test in subdir\nno match\n")

        result = subprocess.run(
            ["./pygrep.sh", "--json", "-r", "test", self.temp_dir],
            capture_output=True,
            text=True,
            check=True,
        )
        output = json.loads(result.stdout)
        file_names = [entry["file"] for entry in output["results"]]
        self.assertIn(self.file1, file_names)
        self.assertIn(self.file2, file_names)
        self.assertIn(sub_file, file_names)
        for file_entry in output["results"]:
            self.assertGreaterEqual(len(file_entry["matches"]), 1)

    def test_json_output_not_empty(self):
        """Verify results array is not empty when matches exist."""
        result = subprocess.run(
            ["./pygrep.sh", "--json", "test", self.file1],
            capture_output=True,
            text=True,
            check=True,
        )
        output = json.loads(result.stdout)
        self.assertGreater(len(output["results"]), 0)
        self.assertGreater(len(output["results"][0]["matches"]), 0)
