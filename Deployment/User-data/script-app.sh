#!/bin/bash

sudo apt update

# install python and postgres
sudo DEBIAN_FRONTEND=noninteractive apt -y upgrade
python3 -V
sudo DEBIAN_FRONTEND=noninteractive apt install -y python3-pip
sudo DEBIAN_FRONTEND=noninteractive apt-get install libpq-dev -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install net-tools


# clonning repo
git clone https://github.com/darshil511/APMC-price-predictor/

# create and start virtual env
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv
python3 -m venv APMC-price-predictor/.venv
source APMC-price-predictor/.venv/bin/activate

# install libraries
pip install -r APMC-price-predictor/requirements.txt


# -> fill up.env and apmc-notifications-firebase-adminsdk-fbsvc-096b7561f5.json file