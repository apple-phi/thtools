NAME="thtools-1"
ZONE=europe-west1-c

gcloud compute instances create $NAME \
    --image-family=ubuntu-minimal-2004-lts  \
    --image-project=ubuntu-os-cloud \
    --machine-type=n2d-highcpu-8 \
    --scopes userinfo-email,cloud-platform \
    --metadata-from-file startup-script=startup-script.sh \
    --zone $ZONE \
    --tags http-server

gcloud compute instances get-serial-port-output $NAME --zone $ZONE