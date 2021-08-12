# Script to run when the Google Cloud Compute Engine is instantiated.

# Install Stackdriver logging agent.
curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
sudo bash install-logging-agent.sh

# Install pip and zip -> python3 and git are included with ubuntu "focal".
sudo apt update
sudo apt install -y python3-pip zip mutt

# Install NUPACK.
git clone https://github.com/beliveau-lab/NUPACK.git
pip install nupack -f NUPACK/src/package
rm -r NUPACK

# Install ToeholdTools.
git clone https://github.com/lkn849/thtools.git
cd thtools
pip install .

# Prepare for contribution scripts
cd registry
pip install -r requirements.txt

# Run contrib.py.
python3 contrib.py

# Zip results
zip -r contributions.zip contributions


