#!/bin/bash

cd root

sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt-get install net-tools
sudo DEBIAN_FRONTEND=noninteractive  sudo apt install postgresql postgresql-client -y
sudo systemctl status postgresql

# ----------------------------------------------------------------------------------------------------------------
# root@test:~# sudo -i -u postgres
# postgres@test:~$
# postgres@test:~$
# postgres@test:~$ psql
# psql (14.17 (Ubuntu 14.17-0ubuntu0.22.04.1))
# Type "help" for help.

# postgres=#
# postgres=#
# postgres=# \password postgres
# Enter new password for user "postgres":
# Enter it again:
# postgres=#
# postgres=#
# postgres=#
# postgres=# create database apmc_db owner postgres;
# CREATE DATABASE
# postgres=# \c apmc_db
# You are now connected to database "apmc_db" as user "postgres".
# apmc_db=#
# apmc_db=#
# apmc_db=# \c
# You are now connected to database "apmc_db" as user "postgres".


# -----------------------------------------------------------------------------------------------------------------------
sudo systemctl enable postgresql