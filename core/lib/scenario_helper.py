import shutil
import os, datetime
import vagrant
import shutil
import lib.ansible_helper as ansible_helper
import lib.vagrant_helper as vagrant_helper
import random
import time
from yaml import safe_load
from lib.ansible_helper import create_flag_playbook, create_users, create_vulnerability_playbook
from lib.vagrant_helper import init_vm, create_vagrantfile

def create_vm_playbook(project_path: str, system_name: str, users, flag, vulnerabilities) -> None:
    with open(project_path + f"/playbooks/{system_name}/playbook.yaml", 'w') as f:
        if users or flag:
            f.write(f"- name: playbook of {system_name} \n  hosts: {system_name}\n")
            f.write("  tasks:\n")
        if users:
            f.write(f"    - include_tasks: ./users.yaml\n")
        if flag:
            f.write(f"    - include_tasks: ./flag.yaml\n")
        for vuln in vulnerabilities:
            f.write(f"\n- name: {vuln['name']}\n  ansible.builtin.import_playbook: vuln_{vuln['name'].rsplit('/',1)[1]}.yaml\n")
        f.close()
        
def get_dict_by_key_from_list(list: list, key, value) -> dict:
    """Get a dictionary in a list the key value pair matches"""
    for i, item in enumerate(list):
        if item.get(key) == value:
            return list[i]
    return None

def get_setting_from_scenario(scenario_path: str, system_name: str, key: str) -> str:
    """Get a setting from a scenario file, given the system name and the target key to read"""
    try:
        f = open(scenario_path + "/scenario.yaml", 'r')
    except FileNotFoundError:
        print("Scenario file not found")
        return None
    else:
        with open(scenario_path + "/scenario.yaml", 'r') as f:
            scenario = safe_load(f)
            system = get_dict_by_key_from_list(
                scenario["systems"], "name", system_name)
            if key not in system:
                return None
            return system[key]
            # if type(system[key]) is list and len(system[key]) == 1:
            #     return system[key]
            # else:
            #     return system[key]

def get_systems_name(scenario_path: str) -> list:
    """Return a list of system(s) name"""
    try:
        f = open(scenario_path + "/scenario.yaml", 'r')
    except FileNotFoundError:
        print("Scenario file not found")
        return None
    else:
        with open(scenario_path + "/scenario.yaml", 'r') as f:
            scenario = safe_load(f)
            return [elem['name'] for elem in scenario["systems"]]

def start_scenario(scenario_name: str):

    start_time = time.time()

    project_dir = os.path.join(
        "../projects", datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.makedirs(project_dir)
    os.makedirs(project_dir + "/playbooks")

    scenario_path = "../scenarios/" + scenario_name
    shutil.copyfile(scenario_path + "/scenario.yaml", project_dir + "/scenario.yaml")

    try:
        with open(project_dir + "/ansible.cfg", "w") as ansible_write:
            ansible_write.write("[defaults]\ninventory = hosts\nhost_key_checking = False")
    except IOError:
        raise 

    create_vagrantfile(project_dir)

    system_names = get_systems_name(scenario_path)

    for system_name in system_names:
        os.makedirs(project_dir + f"/playbooks/{system_name}")

        ip = get_setting_from_scenario(
            scenario_path, system_name, "ip")
        base = get_setting_from_scenario(scenario_path,system_name,"base")
        users = get_setting_from_scenario(scenario_path,system_name,"accounts")
        vulnerabilities = get_setting_from_scenario(
            scenario_path, system_name, "vulnerabilities")
        
        if get_setting_from_scenario(scenario_path, system_name, "generators"):
            flag = get_setting_from_scenario(scenario_path, system_name, "generators")[0]['args']['flag']
            if flag == 'random':
                flag = f'flag{{{hex(random.getrandbits(128))[2:]}}}'
        else:
            flag = None
        
        # Write the hosts file
        with open(project_dir + "/hosts", "a") as hosts_write:
            hosts_write.write(f"{system_name} ansible_host={ip} ansible_ssh_private_key_file=.vagrant/machines/{system_name}/virtualbox/private_key\n\n")
        
        # initialize the Vagrantfile for each VM
        init_vm(base, ip, system_name, project_dir + "/Vagrantfile")

        if flag:
            create_flag_playbook(flag, system_name, project_dir)

        create_users(users, system_name, project_dir)

        for vuln in vulnerabilities:
            create_vulnerability_playbook(system_name, vuln, project_dir)
            
        create_vm_playbook(project_dir, system_name, users, flag, vulnerabilities)

    log_cm = vagrant.make_file_cm(project_dir + '/deployment.log')
    v1 = vagrant.Vagrant(project_dir, out_cm=log_cm, err_cm=log_cm)

    try:
        v1.up()
    except Exception:
        v1.destroy()
        raise

    # v1.up()

    # End timer
    end_time = time.time()

    # Calculate elapsed time
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time) 