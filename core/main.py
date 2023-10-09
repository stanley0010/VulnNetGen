import vagrant
import os
import shutil
import datetime
from yaml import safe_load, safe_dump

def concat_ansible_playbooks(path1, path2, output_path) -> None:
    """Concatenate two ansible playbooks and output to a playbook.yaml file"""
    with open(path1, 'r') as f1:
        with open(path2, 'r') as f2:
            with open(output_path + "/playbook.yaml", 'w') as f3:
                data = safe_load(f1)
                data2 = safe_load(f2)
                data[0]['tasks'].append(data2[0])
                if data:
                    safe_dump(data, f3, sort_keys=False)


def main():

    project_dir = os.path.join(
        "../projects", datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.makedirs(project_dir)
    shutil.copyfile("../baseboxes/ubuntu22/Vagrantfile",
                    project_dir + "/Vagrantfile")

    concat_ansible_playbooks("../components/linux/vsftpd/main.yaml",
                             "../components/generators/flag/main.yaml", project_dir)
    log_cm = vagrant.make_file_cm(project_dir + 'deployment.log')
    v1 = vagrant.Vagrant(project_dir, out_cm=log_cm, err_cm=log_cm)
    v1.up()


main()
