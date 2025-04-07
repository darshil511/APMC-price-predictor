#!/bin/bash

sudo apt update

# install python
sudo DEBIAN_FRONTEND=noninteractive apt -y upgrade
python3 -V
sudo DEBIAN_FRONTEND=noninteractive apt install -y python3-pip

# clonning repo
git clone https://github.com/darshil511/APMC-price-predictor/
pip install -r APMC-price-predictor/requirements.txt

