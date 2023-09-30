import vagrant
import os
import shutil
import datetime

mydir = os.path.join(
    "../projects", datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
os.makedirs(mydir)
shutil.copyfile("../baseboxes/centos7/Vagrantfile", mydir + "/Vagrantfile")

v1 = vagrant.Vagrant(mydir)
v1.up()
