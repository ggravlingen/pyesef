## pyesef

A library for extracting XBRL-files in the ESEF-format using the [Arelle module](https://github.com/Arelle/Arelle).

#### How to use

Download XBRL-reports in a zip-format and place them in the `archives` folder. Then run `python3 pyesef -x` to extract the files and place them in the `filings` folder. Run `python3 pyesef -e` to export all facts to a CSV-file.

#### Interesting resources:

https://filings.xbrl.org/: a list of available financial reports for European companies, per country.
