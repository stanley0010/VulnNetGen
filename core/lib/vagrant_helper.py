import shutil
import re

def create_vagrantfile_from_template(vagrantfile_input_folder_path: str, vagrantfile_output_folder_path: str) -> None:
    """Read template Vagrantfile and copy to the new folder."""
    try:
        shutil.copyfile(vagrantfile_input_folder_path + "/Vagrantfile", vagrantfile_output_folder_path + "/Vagrantfile")
    except IOError as err:
        print(err)
        return None

def write_vagrantfile_ip(ip: str, vagrantfile_output_path: str) -> None:
    """Read the IP address from the scenario file and write to the Vagrantfile."""
    try:
        with open(vagrantfile_output_path, "r") as vagrantfile_read:
            text = vagrantfile_read.read()
            # only write ip when it is not dhcp
            if ip == "dhcp":
                newText = text.replace(r'ip:.*', 'type: "dhcp"')
            else:
                newText = text.replace('type: "dhcp"', f'ip: "{ip}"')
            with open(vagrantfile_output_path, "w") as vagrantfile_write:
                vagrantfile_write.write(newText)
    except IOError as err:
        print(err)
        return None
    
def change_vm_name(name: str, vagrantfile_output_path: str) -> None:
    """Change the VM name in the Vagrantfile."""
    try:
        with open(vagrantfile_output_path, "r") as vagrantfile_read:
            text = vagrantfile_read.read()
            newText = re.sub(r'vagrant_name = ".*"', f'vagrant_name = "{name}"', text)
            with open(vagrantfile_output_path, "w") as vagrantfile_write:
                vagrantfile_write.write(newText)
    except IOError as err:
        print(err)
        return None