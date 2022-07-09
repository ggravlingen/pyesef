"""Main."""
from pyesef.helpers.read_filings import read_filings
from pyesef.helpers.to_dataframe import to_dataframe


def main():
    """Run main."""
    filings = read_filings()
    df = to_dataframe(filings)

    df.to_csv("a.csv", sep=";", index=False)


if __name__ == "__main__":
    main()
