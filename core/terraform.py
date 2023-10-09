import os
import shutil
import datetime
from python_terraform import *


mydir = os.path.join(
    "../projects", datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
os.makedirs(mydir)
shutil.copyfile("../baseboxes/ubuntu22/main.tf", mydir + "/main.tf")

tf = Terraform(working_dir=mydir)
tf.init()
tf.apply(skip_plan=True, capture_output=False)

# not finished
