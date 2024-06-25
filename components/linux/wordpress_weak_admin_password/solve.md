## Weak password in WordPress admin account

The WordPress admin account is a prime target for attackers. If the password is weak, it can be easily guessed or cracked. This component sets the admin password to `admin`.

Players can visit `http://<TARGET_IP>/wp-admin` and log in with the username `admin` and password `admin`.

Further attack, such as uploading a malicious plugin or theme to get RCE in target machine, is possible.