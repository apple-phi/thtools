# How to run the iGEM characterization script

This folder contains a script called `contrib.py`.
This runs the test suite based on a team configuration file.
The script autogenerates MediaWiki&ndash;formatted inserts for the Registry of Standard Biological Parts.

See files ending in `.toml` in this folder for examples of the configuration file.

To run the script:
```sh
python3 contrib.py <team name>.toml
```
This will create a folder with the results at the path `contributions/<team name>`.

## Running the script on Google Cloud
We used a Google Cloud virtual machine to run the script.
See the GitHub Action named `iGEM Contribution` to see our full setup.

In order to connect GitHub Actions with the virtual machine, run:
```sh
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.281.1.tar.gz -L https://github.com/actions/runner/releases/download/v2.281.1/actions-runner-linux-x64-2.281.1.tar.gz
echo "04f6c17235d4b29fc1392d5fae63919a96e7d903d67790f81cffdd69c58cb563  actions-runner-linux-x64-2.281.1.tar.gz" | shasum -a 256 -c
tar xzf ./actions-runner-linux-x64-2.281.1.tar.gz
```
Then go your `your GitHub repository -> Settings -> Actions -> Runners -> New self-hosted runner` and follow the instructions after the `Download` step.
