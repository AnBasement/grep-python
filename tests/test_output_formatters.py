import unittest
import json
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
        data = json.loads(output)

        self.assertIn("Søk", output)

    def test_cli_json_output(self):
        """
        Integration test: Run the CLI with --json flag
        This goes in a separate test file like tests/test_cli_integration.py
        """
        
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test line 1\n")
            f.write("another line\n")
            f.write("test line 3\n")
            test_file = f.name

        try:
            result = subprocess.run(
                ['./pygrep.sh', '--json', 'test', test_file],
                capture_output=True,
                text=True
            )

            output = json.loads(result.stdout)

            self.assertEqual(len(output["results"]), 1)
            self.assertEqual(len(output["results"][0]["matches"]), 2)

        finally:
            import os
            os.unlink(test_file)