import json
from unittest.mock import patch

import pytest
import requests
from strip_ansi import strip_ansi

from pybites_search.tip import ContentPiece, TipSearch

EXPECTED_TABLE = """
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Title              ┃ Url                                             ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ import antigravity │ https://codechalleng.es/tips/import-antigravity │
│ for ... else       │ https://codechalleng.es/tips/for-else           │
└────────────────────┴─────────────────────────────────────────────────┘
"""


@pytest.fixture
def mock_data():
    with open("tests/data/tips.json") as f:
        return json.loads(f.read())


def test_match_tip_content(mock_data):
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = json.dumps(mock_data).encode()

    with patch("requests.get", return_value=mock_response):
        searcher = TipSearch()

        results = searcher.match_content("zen")
        expected = [
            ContentPiece(
                title="Zen of Python", url="https://codechalleng.es/tips/zen-of-python"
            )
        ]
        assert results == expected

        results = searcher.match_content(" a")
        expected = [
            ContentPiece(
                title="import antigravity",
                url="https://codechalleng.es/tips/import-antigravity",
            ),
            ContentPiece(
                title="for ... else", url="https://codechalleng.es/tips/for-else"
            ),
        ]
        assert results == expected


def test_show_tip_matches(mock_data, capfd):
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = json.dumps(mock_data).encode()

    with patch("requests.get", return_value=mock_response):
        searcher = TipSearch()
        results = searcher.match_content(" a")
        searcher.show_matches(results)
        output = capfd.readouterr()[0]
        assert strip_ansi(output.strip()) == EXPECTED_TABLE.strip()

        results = searcher.match_content("bogus")
        searcher.show_matches(results)
        err_output = capfd.readouterr()[1]
        assert strip_ansi(err_output.strip()) == "No results found"
