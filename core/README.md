# For developers

## Prerequisites
1. `brew install cdktf` (if prompted "terraform is already installed", uninstall terraform first)
2. `brew install pipenv`
3. `brew install ansible`


## Run main.py
1. Install `pipenv` by `brew install pipenv` (MacOS) or `pip install pipenv` (Linux)
2. Run `pipenv install` to install dependencies
3. Run `make run` in this folder

## Finding IP of Vagrant VM
Type this in the produced project folder: `vagrant ssh -c "hostname -I | cut -d' ' -f2" 2> /dev/null`