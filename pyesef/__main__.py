"""Main."""
from pyesef.helpers import read_filings, to_dataframe


def main():
    """Run main."""
    filings = read_filings(filter_year=2021)
    df = to_dataframe(filings)

    df.to_csv("output.csv", sep=";", index=False)


if __name__ == "__main__":
    main()
