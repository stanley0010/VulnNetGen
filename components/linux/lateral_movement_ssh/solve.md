## SSH from jumphost to target

This vulnerability captures a scenario where an attacker has gained access to a jumphost and is attempting to move laterally to a target machine using SSH. 

The private key to target machine is stored in the jumphost at `/home/ubuntu/secret/jump_host_key`. The attacker can use the private key to SSH into the target machine.