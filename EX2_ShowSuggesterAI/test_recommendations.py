import pytest
from app import get_favorites_shows


def test_at_least_two():
    assert get_favorites_shows(
        "Lupin,,,") == "You should enter at least two TV shows, separated by a comma"


def test_is_a_string():
    assert get_favorites_shows(111) == "You should enter a string!"


# def test_saperate_comma():
#     assert get_favorites_shows(
#         "Lupin Suits") == "You should separate the TV shows' name by comma"
