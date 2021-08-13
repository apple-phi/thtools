#!/bin/bash
# Script to run when the Google Cloud Compute Engine is instantiated.

# Self-terminate https://cloud.google.com/community/tutorials/create-a-self-deleting-virtual-machine 
function terminate {
    export NAME=$(curl -X GET http://metadata.google.internal/computeMetadata/v1/instance/name -H 'Metadata-Flavor: Google')
    export ZONE=$(curl -X GET http://metadata.google.internal/computeMetadata/v1/instance/zone -H 'Metadata-Flavor: Google')
    gcloud --quiet compute instances delete $NAME --zone=$ZONE
}

# Send results to bucket
# try / catch from https://stackoverflow.com/a/15656652
function bucket {
    {
        zip -r contributions.zip contributions && gsutil cp contributions.zip gs://thtools-bucket/ &&
    } || terminate
}

# https://stackoverflow.com/a/61024169
export PYTHONUNBUFFERED=True

# Install Stackdriver logging agent
curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
sudo bash install-logging-agent.sh

# Install tools
sudo apt-get update
sudo apt-get install -y python3.8 python3-pip git zip

# Install NUPACK
git clone https://github.com/beliveau-lab/NUPACK.git
pip install nupack -f NUPACK/src/package
rm -r NUPACK

# Install ToeholdTools
git clone https://github.com/lkn849/thtools.git
cd thtools
pip install .

# Prepare for contribution scripts
cd registry
pip install -r requirements.txt

# Bucket sanity check
gsutil cp contrib.py gs://thtools-bucket/

# Run contrib.py
{
    python3 contrib.py &&
} || bucket

bucket
terminate