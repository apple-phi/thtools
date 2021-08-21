#!/bin/bash

NAME="thtools-1"
ZONE=us-west4-a


gcloud compute instances create $NAME \
    --zone $ZONE \
    --metadata-from-file startup-script=startup.sh \
    --scopes=compute-rw,cloud-platform,storage-rw,default \
    --image-family=ubuntu-minimal-2004-lts  \
    --image-project=ubuntu-os-cloud \
    --machine-type=n2d-highcpu-8

gcloud compute instances get-serial-port-output $NAME --zone $ZONE