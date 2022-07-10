"""Main."""
from pyesef.helpers import read_filings, to_dataframe


def main() -> None:
    """Run main."""
    filings = read_filings(filter_year=2021)
    data_frame = to_dataframe(filings)

    data_frame.to_csv("output.csv", sep=";", index=False)


if __name__ == "__main__":
    main()
