"""Tests for the download package."""

import pytest

from pyesef.download import Filing, _cleanup_package_dict, _extract_alpha_2_code


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
                        file_name="5493004ARP9VPUIX5B73-2021-12-31-is.zip",
                        path="5493004ARP9VPUIX5B73/2021-12-31/ESEF/IS/1",
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
            ],
        ),
    ],
)
def test_cleanup_package_dict(test_data, expected_result) -> None:
    """Test function _cleanup_package_dict."""
    function_result = _cleanup_package_dict(test_data)
    assert function_result == expected_result