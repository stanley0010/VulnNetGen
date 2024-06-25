import shutil
import os, datetime
import vagrant
import shutil
import random
import time
import click
from yaml import safe_load
from lib.ansible_helper import (
    create_flag_playbook,
    create_users,
    create_vulnerability_playbook,
    ansible_ad,
)
from lib.vagrant_helper import (
    init_vm,
    create_vagrantfile,
    check_all_vms_up,
    vagrant_up_ad,
)
from lib.ad_helper import generate_config, copy_vuln_files


def create_vm_playbook(
    project_path: str, system_name: str, users, flag, vulnerabilities
) -> None:
    with open(project_path + f"/playbooks/{system_name}/playbook.yaml", "w") as f:
        if users or flag:
            f.write(f"- name: playbook of {system_name} \n  hosts: {system_name}\n")
            f.write("  tasks:\n")
        if users:
            f.write(f"    - include_tasks: ./users.yaml\n")
        if flag:
            f.write(f"    - include_tasks: ./flag.yaml\n")
        for vuln in vulnerabilities:
            f.write(
                f"\n- name: {vuln['name']}\n  ansible.builtin.import_playbook: vuln_{vuln['name'].rsplit('/',1)[1]}.yaml\n"
            )
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
        f = open(scenario_path + "/scenario.yaml", "r")
    except FileNotFoundError:
        print("Scenario file not found")
        return None
    else:
        with open(scenario_path + "/scenario.yaml", "r") as f:
            scenario = safe_load(f)
            system = get_dict_by_key_from_list(scenario["systems"], "name", system_name)
            if key not in system:
                return None
            return system[key]


def get_systems_name(scenario_path: str) -> list:
    """Return a list of system(s) name"""
    try:
        f = open(scenario_path + "/scenario.yaml", "r")
    except FileNotFoundError:
        print("Scenario file not found")
        return None
    else:
        with open(scenario_path + "/scenario.yaml", "r") as f:
            scenario = safe_load(f)
            return [elem["name"] for elem in scenario["systems"]]


def start_scenario(scenario_name: str):

    start_time = time.time()

    scenario_path = "../scenarios/" + scenario_name

    #### if scenario is AD
    with open(scenario_path + "/scenario.yaml", "r") as f:
        data = safe_load(f)
        # handle data without AD field
        if "AD" in data:
            project_dir = os.path.join("../projects", data["name"])
            if os.path.exists(project_dir):
                # Uncomment app.py "while not os.path.exists(file_path):" to use below lines
                # if click.confirm('Found existing scenario project folder. Do you want to delete it and create a new one?'):
                #     shutil.rmtree(project_dir)
                # else:
                raise ValueError(
                    "Project folder already exists. Please delete it or choose a different scenario name."
                )
            os.makedirs(project_dir)
            # Copy necessary files to project directory
            ## Copy scenario.yaml
            shutil.copyfile(
                scenario_path + "/scenario.yaml", project_dir + "/scenario.yaml"
            )
            ## Copy sample Vagrant file
            shutil.copyfile("../baseboxes/ad/Vagrantfile", project_dir + "/Vagrantfile")
            ## Copy sample Inventory file
            shutil.copyfile("../baseboxes/ad/inventory", project_dir + "/inventory")

            ## Copy vuln scripts (because they each need customization, now hardcoded values)
            os.makedirs(project_dir + "/scripts")

            ## Copy vuln "files" from scenario folder to project folder
            if os.path.exists(scenario_path + "/files"):
                copy_vuln_files(scenario_path + "/files", project_dir + "/files")

            # Generate config.json from scenario.yaml for Ansible
            generate_config(project_dir)

            # Vagrant Provisioning and Ansible Configuring
            if check_all_vms_up(project_dir):
                print("Skipping vagrant provision. VMs already up.")
            else:
                vagrant_up_ad(project_dir)
            ansible_ad(project_dir)
        else:
            ##### scenario is not AD
            project_dir = os.path.join(
                "../projects", datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            os.makedirs(project_dir)
            shutil.copyfile(
                scenario_path + "/scenario.yaml", project_dir + "/scenario.yaml"
            )

            os.makedirs(project_dir + "/playbooks")

            mitogen_dir = os.path.abspath(os.path.join(__file__, "../"))

            try:
                with open(project_dir + "/ansible.cfg", "w") as ansible_write:
                    if "windows" in f.read():
                        ansible_write.write(
                            f"[defaults]\ninventory = hosts\nhost_key_checking = False\nstrategy_plugins = {mitogen_dir}/mitogen-0.3.7/ansible_mitogen/plugins/strategy\nstrategy = mitogen_linear"
                        )
                    else:
                        ansible_write.write(
                            f"[defaults]\ninventory = hosts\nhost_key_checking = False\n"
                        )
            except IOError:
                raise

            create_vagrantfile(project_dir)

            system_names = get_systems_name(scenario_path)

            for system_name in system_names:
                os.makedirs(project_dir + f"/playbooks/{system_name}")

                ip = get_setting_from_scenario(scenario_path, system_name, "ip")
                base = get_setting_from_scenario(scenario_path, system_name, "base")

                users = get_setting_from_scenario(
                    scenario_path, system_name, "accounts"
                )
                vulnerabilities = get_setting_from_scenario(
                    scenario_path, system_name, "vulnerabilities"
                )

                if get_setting_from_scenario(scenario_path, system_name, "plugins"):
                    flag = get_setting_from_scenario(
                        scenario_path, system_name, "plugins"
                    )[0]["args"]["flag"]
                    flag_path = get_setting_from_scenario(
                        scenario_path, system_name, "plugins"
                    )[0]["args"]["path"]
                    owner = get_setting_from_scenario(
                        scenario_path, system_name, "plugins"
                    )[0]["args"]["owner"]
                    group = get_setting_from_scenario(
                        scenario_path, system_name, "plugins"
                    )[0]["args"]["group"]
                    mode = get_setting_from_scenario(
                        scenario_path, system_name, "plugins"
                    )[0]["args"]["mode"]
                    if flag == "random":
                        flag = f"flag{{{hex(random.getrandbits(128))[2:]}}}"
                else:
                    flag = None

                # Write the hosts file
                with open(project_dir + "/hosts", "a") as hosts_write:
                    hosts = f"{system_name} ansible_host={ip} ansible_ssh_private_key_file=.vagrant/machines/{system_name}/virtualbox/private_key "
                    if "windows" in base:
                        hosts += " ansible_conneciton=ssh"
                        hosts += " ansible_shell_type=cmd"
                        hosts += " ansible_password=vagrant"
                    hosts += "\n\n"
                    hosts_write.write(hosts)

                # initialize the Vagrantfile for each VM
                init_vm(base, ip, system_name, project_dir + "/Vagrantfile")

                if flag:
                    if "windows" in base:
                        create_flag_playbook(
                            flag,
                            flag_path,
                            owner,
                            group,
                            mode,
                            system_name,
                            project_dir,
                            windows=True,
                        )
                    else:
                        create_flag_playbook(
                            flag,
                            flag_path,
                            owner,
                            group,
                            mode,
                            system_name,
                            project_dir,
                            windows=False,
                        )

                create_users(users, system_name, project_dir)

                for vuln in vulnerabilities:
                    create_vulnerability_playbook(system_name, vuln, project_dir)

                create_vm_playbook(
                    project_dir, system_name, users, flag, vulnerabilities
                )

            log_cm = vagrant.make_file_cm(project_dir + "/deployment.log")
            v1 = vagrant.Vagrant(project_dir, out_cm=log_cm, err_cm=log_cm)

            try:
                v1.up()
            except Exception:
                v1.destroy()
                raise ValueError(
                    f"Vagrant up failed. See deployment.log at {project_dir}"
                )

    # End timer
    end_time = time.time()

    # Calculate elapsed time
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time)
