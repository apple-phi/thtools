#!/bin/bash

NAME="thtools-1"
ZONE=europe-west2-c

gcloud compute instances create $NAME \
    --image-family=ubuntu-minimal-2004-lts  \
    --image-project=ubuntu-os-cloud \
    --custom-cpu=12 \
    --custom-memory=48GB
    --custom-vm-type=n2d \
    --metadata-from-file startup-script=startup.sh \
    --zone $ZONE \
    --scopes compute, cloud-platform, devstorage.read_write

# https://askubuntu.com/a/430383
watch -n 60 'gcloud compute instances get-serial-port-output $NAME --zone $ZONE'