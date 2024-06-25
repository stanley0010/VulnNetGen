#!/bin/sh
# run with sudo
sudo apt-get update
sudo apt-get install pipenv -y
sudo apt-get install ansible -y
sudo apt-get install vagrant -y
sudo apt-get install virtualbox -y
ansible-galaxy collection install community.windows

# Run the following to use Windows Box
sudo gem install evil-winrm
sudo bash -c "echo $'\n' >> /etc/ssl/openssl.cnf"
sudo bash -c "echo '[provider_sect]' >> /etc/ssl/openssl.cnf"
sudo bash -c "echo 'default = default_sect' >> /etc/ssl/openssl.cnf"
sudo bash -c "echo 'legacy = legacy_sect' >> /etc/ssl/openssl.cnf"
sudo bash -c "echo $'\n' >> /etc/ssl/openssl.cnf"
sudo bash -c "echo '[default_sect]' >> /etc/ssl/openssl.cnf"
sudo bash -c "echo 'activate = 1' >> /etc/ssl/openssl.cnf"
sudo bash -c "echo $'\n' >> /etc/ssl/openssl.cnf"
sudo bash -c "echo '[legacy_sect]' >> /etc/ssl/openssl.cnf"
sudo bash -c "echo 'activate = 1' >> /etc/ssl/openssl.cnf"

sudo chmod +x VulnNetGen
cd core
pipenv install