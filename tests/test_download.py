"""Tests for the download package."""

from unittest.mock import patch

import pytest

from pyesef.download import Filing, _cleanup_package_dict, _extract_alpha_2_code
from pyesef.download.api_extractor import api_to_filing_record_list


def test_parse_file_ending() -> None:
    """Test function _parse_file_ending."""
    function_result = _extract_alpha_2_code(
        path="549300CSLHPO6Y1AZN37/2021-12-31/ESEF/SE/0"
    )

    assert function_result == "se"


@pytest.mark.parametrize(
    "test_data, expected_result",
    [
        # Test inputting only one item
        (
            {
                "5493004ARP9VPUIX5B73": [
                    Filing(
                        country="dk",
                        file_name="alk-2020-12-31.zip",
                        path="529900SGCREUZCZ7P020/2020-12-31/ESEF/DK/0",
                    )
                ],
            },
            [
                Filing(
                    country="dk",
                    file_name="alk-2020-12-31.zip",
                    path="529900SGCREUZCZ7P020/2020-12-31/ESEF/DK/0",
                )
            ],
        ),
        # Test inputting multiple items
        (
            {
                "5493004ARP9VPUIX5B73": [
                    Filing(
                        country="dk",
                        file_name="alk-2020-12-31.zip",
                        path="529900SGCREUZCZ7P020/2020-12-31/ESEF/DK/0",
                    ),
                ],
                "5493004ARP9VPUIX5B74": [
                    Filing(
                        country="is",
                        file_name="5493004ARP9VPUIX5B73-2021-12-31-en.zip",
                        path="5493004ARP9VPUIX5B73/2021-12-31/ESEF/IS/0",
                    ),
                    Filing(
                        country="is",
                        file_name="5493004ARP9VPUIX5B73-2022-12-31-is.zip",
                        path="5493004ARP9VPUIX5B73/2022-12-31/ESEF/IS/1",
                    ),
                ],
            },
            [
                Filing(
                    country="dk",
                    file_name="alk-2020-12-31.zip",
                    path="529900SGCREUZCZ7P020/2020-12-31/ESEF/DK/0",
                ),
                Filing(
                    country="is",
                    file_name="5493004ARP9VPUIX5B73-2021-12-31-en.zip",
                    path="5493004ARP9VPUIX5B73/2021-12-31/ESEF/IS/0",
                ),
                Filing(
                    country="is",
                    file_name="5493004ARP9VPUIX5B73-2022-12-31-is.zip",
                    path="5493004ARP9VPUIX5B73/2022-12-31/ESEF/IS/1",
                ),
            ],
        ),
    ],
)
def test_cleanup_package_dict(test_data, expected_result) -> None:
    """Test function _cleanup_package_dict."""
    function_result = _cleanup_package_dict(test_data)
    assert function_result == expected_result


def test_filing_property__file_url() -> None:
    """Return Filing.file_url."""
    model = Filing(country="se", file_name="abc", path="a/b/c")
    assert model.file_url == "https://filings.xbrl.org/a/b/c/abc"


def test_filing_property__download_country_folder() -> None:
    """Return Filing.download_country_folder."""
    model = Filing(country="se", file_name="abc", path="a/b/c")
    assert "/pyesef/archives/se" in model.download_country_folder


def test_filing_property__write_location() -> None:
    """Return Filing.write_location."""
    model = Filing(country="se", file_name="abc", path="a/b/c")
    assert "/pyesef/archives/se/abc" in model.write_location


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
