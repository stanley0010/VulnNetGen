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
            else:
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
            vm_config = vm_config.replace('$machine_name', f'{machine_name}')
            vm_config = '\t'.join(('\n'+vm_config.lstrip()).splitlines(True))
            with open(vagrantfile_output_path, "r+") as f:
                vagrant_text = f.readlines()[:-1]
                f.seek(0)
                f.truncate(0)
                f.writelines(vagrant_text + vm_config.splitlines(True))
                f.write("end\n")
    except IOError:
        raise
        