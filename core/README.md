# For developers

## Prerequisites
1. `brew install pipenv`
2. `brew install ansible`

## Run main.py
1. Install `pipenv` by `brew install pipenv` (MacOS) or `pip install pipenv` (Linux)
2. Run `pipenv install` to install dependencies in '/core' folder
3. Run `make run`

## Stopping and deleting virtualBox machines in Nuc Development Environment via CLI
1. `vboxmanage list vms`
2. `vboxmanage controlvm 20231214_204234_default_1702557765163_87466 poweroff`
3. `vboxmanage unregistervm 20231214_204234_default_1702557765163_87466 --delete`

## Finding IP of Vagrant VM
Type this in the produced project folder: `vagrant ssh -c "hostname -I | cut -d' ' -f2" 2> /dev/null`

## Q&A
1. If vagrant fails to connect to vm via ssh, and showed error message "Warning: Authentication failure. Retrying...", upgrade vagrant to latest version. The problem is in Vagrant's Ruby net-ssh module, not accepting ssh key with ssh-rsa signature anymore.