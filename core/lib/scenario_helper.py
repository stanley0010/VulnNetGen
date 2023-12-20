from yaml import safe_load
import os, datetime
import vagrant
import shutil
import lib.ansible_helper as ansible_helper
import lib.vagrant_helper as vagrant_helper

def get_dict_by_key_from_list(list: list, key, value) -> dict:
    """Get a dictionary in a list the key value pair matches"""
    for i, item in enumerate(list):
        if item.get(key) == value:
            return list[i]
    return None

# TODO: delete system_name
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
            if type(system[key]) is list and len(system[key]) == 1:
                return system[key][0]
            else:
                return system[key]

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

def create_scenario(scenario_name: str):
    project_dir = os.path.join(
        "../projects", datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.makedirs(project_dir)
    os.makedirs(project_dir + "/playbooks")

    scenario_path = "../scenarios/" + scenario_name

    for system_name in get_systems_name(scenario_path):
        ip = get_setting_from_scenario(
            scenario_path, system_name, "ip")
        base = get_setting_from_scenario(scenario_path,system_name,"base")
        users = get_setting_from_scenario(scenario_path,system_name,"accounts")
        vulnerabilities = get_setting_from_scenario(
            scenario_path, system_name, "vulnerabilities")['name']
        
        flag = get_setting_from_scenario(
            scenario_path, system_name, "generators")['args']['flag']
    
    vagrant_helper.create_vagrantfile_from_template(
        f"../baseboxes/{base}", project_dir)
    
    vagrant_helper.write_vagrantfile_ip(ip , project_dir + "/Vagrantfile")

    ansible_helper.replace_flag(flag, project_dir)

    ansible_helper.create_users(users, project_dir)

    shutil.copyfile(f"../components/{vulnerabilities}/main.yaml", project_dir + f"/playbooks/vuln.yaml")

    shutil.copyfile('../components/generators/playbook_template.yaml', project_dir + "/playbook.yaml")

    log_cm = vagrant.make_file_cm(project_dir + '/deployment.log')
    v1 = vagrant.Vagrant(project_dir, out_cm=log_cm, err_cm=log_cm)
    v1.up()