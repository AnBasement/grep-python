from src import __version__, __author__


def test_package_metadata_present_and_values():
    """Check that __version__ and __author__ are present and have expected values."""
    assert isinstance(__version__, str) and __version__ == "0.3.9"
    assert isinstance(__author__, str) and __author__ == "Kristoffer Avaldsnes Gilje"
