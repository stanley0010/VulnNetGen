# For developers

## Prerequisites
Run `setup.sh` in the project root with sudo. But if you want to install manually, you have to at least install these:
1. pipenv
2. ansible
3. vagrant
4. virtualbox
5. evil-winrm(to use Windows box)

## Run main.py
1. Install `pipenv` by `brew install pipenv` (MacOS) or `apt-get install pipenv` (Linux)
2. Run `pipenv install` to install dependencies in '/core' folder
3. Run `make run`

## Stopping and deleting virtualBox machines in Nuc Development Environment via CLI
1. `vboxmanage list vms`
2. `vboxmanage controlvm 20231214_204234_default_1702557765163_87466 poweroff`
3. `vboxmanage unregistervm 20231214_204234_default_1702557765163_87466 --delete`
or via vagrant
1. `vagrant global-status --prune`
2. `for i in `vagrant global-status | grep virtualbox | awk '{ print $1 }'` ; do vagrant destroy $i ; done`


## Finding IP of Vagrant VM
Type this in the produced project folder: `vagrant ssh -c "hostname -I | cut -d' ' -f2" 2> /dev/null`

## Connect to Windows Box
Make sure evil-winrm is installed. And modify `/etc/ssl/openssl.cnf` as in the Q&A session on evil-winrm. Connect the box via `evil-winrm -i 127.0.0.1 -P 55985 -u vagrant -p vagrant`. 

## Q&A
### Error message "Warning: Authentication failure. Retrying..." upon Vagrant boot up the box
If vagrant fails to connect to vm via ssh, upgrade vagrant to latest version. The problem is in Vagrant's Ruby net-ssh module, not accepting ssh key with ssh-rsa signature anymore.

### evil-winrm error message "OpenSSL::Digest::DigestError"
1. `sudo nano /etc/ssl/openssl.cnf`
2. add the following lines
```
[provider_sect]
default = default_sect
legacy = legacy_sect

[default_sect]
activate = 1

[legacy_sect]
activate = 1
```