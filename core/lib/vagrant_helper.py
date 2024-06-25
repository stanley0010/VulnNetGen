from subprocess import Popen, PIPE, STDOUT
import vagrant
import time
import datetime

def create_vagrantfile(vagrantfile_output_folder_path: str) -> None:
    """Create new Vagrantfile in project folder."""
    try:
        with open(vagrantfile_output_folder_path + "/Vagrantfile", "w") as vagrantfile_write:
            vagrantfile_write.write('Vagrant.configure("2") do |config|\n')
            vagrantfile_write.write('\tconfig.vm.synced_folder ".", "/vagrant", disabled: false\n')
            vagrantfile_write.write('end')
    except IOError:
        raise

def get_vm_box_from_list(base:str) -> str:
    with open("../baseboxes/vm_box_list.ini", "r") as vm_box_list_read:
        for line in vm_box_list_read:
            line = line.strip()
            (key, val) = line.split("=",1)
            if base == key:
                return val
        return None

def init_vm(base: str, ip: str, machine_name: str, vagrantfile_output_path: str) -> None:
    """Read from the 'vm_vagrantfile_template' and replace the ip and machine name. Finally, write to the Vagrantfile."""
    try:
        with open("../baseboxes/vm_vagrantfile_template", "r") as vagrantfile_read:
            vm_config = vagrantfile_read.read()
            vm_box = get_vm_box_from_list(base)
            if vm_box:
                vm_config = vm_config.replace('$box_name', f'{vm_box}')
            else:
                raise ValueError(f"Base {base} not found in vm_box_list.ini")
            vm_config = vm_config.replace('ip: "dhcp"', f'ip: "{ip}"')
            vm_config = vm_config.replace('v.name = "$machine_name"', f'v.name = "{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}_{machine_name}"')
            vm_config = vm_config.replace('$machine_name', f"{machine_name}")
            vm_config = '\t'.join(('\n'+vm_config.lstrip()).splitlines(True))
            with open(vagrantfile_output_path, "r+") as f:
                vagrant_text = f.readlines()[:-1]
                f.seek(0)
                f.truncate(0)
                f.writelines(vagrant_text + vm_config.splitlines(True))
                f.write("end\n")
    except IOError:
        raise
        
def vagrant_up_ad(project_dir: str):
    """Use Vagrant to provision AD machines"""
    start_time = time.time()

    log_cm = vagrant.make_file_cm(project_dir + '/deployment.log')
    v1 = vagrant.Vagrant(project_dir, out_cm=log_cm, err_cm=log_cm)
    try:
        v1.up()
    except Exception:
        v1.destroy()
        raise ValueError(f"Vagrant up failed. See deployment.log at {project_dir}")

    print("Vagrant provisioning...")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Vagrant up Elapsed time: ", elapsed_time)

def check_all_vms_up(project_dir: str):
    # Run the 'vagrant status' command
    process = Popen(['vagrant', 'status'], cwd=f"{project_dir}", stdout=PIPE, stderr=STDOUT)
    output = process.communicate()[0].decode('utf-8')

    # Print the output of the command
    print(output)

    # Check if any machine is "not created"
    if 'not created' not in output:
        print("All machines are running.")
        return True
    else:
        print("At least one machine is not running or not created.")
        return False