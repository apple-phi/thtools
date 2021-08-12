#!/bin/sh

NAME="thtools-1"
ZONE=europe-west2-c

gcloud compute instances create $NAME \
    --image-family=ubuntu-minimal-2004-lts  \
    --image-project=ubuntu-os-cloud \
    --machine-type=n2d-highcpu-8 \
    --metadata-from-file startup-script=startup.sh \
    --zone $ZONE \
    --scopes cloud-platform

gcloud compute instances get-serial-port-output $NAME --zone $ZONE