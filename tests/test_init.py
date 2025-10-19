from src import __version__, __author__


def test_package_metadata_present_and_values():
    assert isinstance(__version__, str) and __version__ == "0.2.2"
    assert isinstance(__author__, str) and __author__ == "Kristoffer Avaldsnes Gilje"
