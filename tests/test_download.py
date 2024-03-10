"""Tests for the download package."""

from unittest.mock import patch

from pyesef.download.api_extractor import api_to_filing_record_list


def test_api_to_filing_record_list() -> None:
    """Test function api_to_filing_record_list."""
    with patch("urllib.request.urlopen") as mock_url:
        with open("tests/fixtures/api_page.json", "rb") as _file:
            # Set the return value of mock_urlopen
            mock_url.return_value.__enter__.return_value.read.return_value = (
                _file.read()
            )

            x = api_to_filing_record_list()
            assert len(x) == 2
