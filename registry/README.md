# How to run the iGEM characterization script

This folder contains a script called `contrib.py`.
This runs the ToeholdTools test suite based on a team configuration file.
The script autogenerates MediaWiki&ndash;formatted inserts for the Registry of Standard Biological Parts.

See the `config-example.toml` and the files in `config/` for examples of how to write the configuration file.
You may wish to chunk up the configuration file into multiple files, since the number of full tests/part is in the order of 10.

To run the script:
```sh
python3 contrib.py <path/to/config/file.toml>
```
This will create a folder with the results in the `contributions/` folder.

## Running on GitHub Actions

Please see [here](https://github.com/lkn849/thtools/blob/master/.github/workflows/contribution.yml) for our GitHub Action running this script.