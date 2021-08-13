#!/bin/bash

NAME="thtools-1"
ZONE=us-west4-a

function create_vm {
    gcloud compute instances create $NAME \
        --zone $ZONE \
        --metadata-from-file startup-script=startup.sh \
        --scopes=compute-rw,cloud-platform,storage-rw,default \
        --image-family=ubuntu-minimal-2004-lts  \
        --image-project=ubuntu-os-cloud \
        --machine-type=n2d-highcpu-8 \
    ;
}

# https://linux.die.net/man/1/watch
function watch_vm {
    watch -n 60 --differences "gcloud compute instances get-serial-port-output $NAME --zone $ZONE";
}

create_vm && watch_vm;