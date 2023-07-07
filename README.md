## pyesef

A library for extracting XBRL-files in the ESEF-format using the [Arelle module](https://github.com/Arelle/Arelle).

#### How to use

- Download sample archives: `python3 -m pyesef -d`.

If you don't want to use the downloader, you should place the zip-files in the `archives` folder of the root folder:

```
.devcontainer
.github
.vscode
archives
    yourfile.zip
pyesef
```

Files in the `archives` folder will be extracted if you run `python3 -m pyesef -e`. This will create two files: `definitions.csv` and `output.csv`.

#### Interesting resources:

https://filings.xbrl.org/: a list of available financial reports for European companies, per country.
