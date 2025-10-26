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