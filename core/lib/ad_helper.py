import yaml
import json
import shutil
import os

def copy_vuln_files(scenario_dir: str, project_dir: str):
    shutil.copytree(scenario_dir, project_dir)
    
def handle_script(project_dir: str, script_name: str, args):
    """
    Replace hardcoded value in Powershell script to key-value pair in args.
    Then copy to project folder.
    """
    with open(project_dir + f"/scripts/{script_name}.ps1", 'r+') as script_file:
        script_text = script_file.read()
        if os.path.isfile(f"../components/ad/{script_name}/args.list"):
            with open(f"../components/ad/{script_name}/args.list", 'r') as arg_list_file:
                arg_list = arg_list_file.read().splitlines()
                for arg in arg_list:
                    if args.get(arg): # argument in args.list is in scenario args
                        script_text = script_text.replace(f'${arg}', args.get(arg)) # get value from args by key
                    else:
                        raise ValueError(f"Missing {arg} for {script_name} in Scenario File")
                    
        script_file.seek(0)
        script_file.truncate(0)
        script_file.write(script_text)

def write_machine_to_inventory(project_dir: str, system):
    system_name = system['hostname']
    dns_domain = system['dns_domain']
    ip = system['ip']
    with open(f"{project_dir}/inventory", 'r+') as f:
        content = f.readlines()
        
        # Add machine names, ansible_host, dns_domain and dict_key to inventory default tag
        section_index = [i for i, line in enumerate(content) if line.startswith("[default]")][0]
        content.insert(section_index + 1, f"{system_name} ansible_host={ip} dns_domain={dns_domain} dict_key={system_name}\n")

        # Add machine names to domain tag
        section_index = [i for i, line in enumerate(content) if line.startswith("[domain]")][0]
        content.insert(section_index + 1, f"{system_name}\n")        
        
        ## Add machine names to basic tags: dc, server, workstation
        match system['type']:
            case "dc":
                section_index = [i for i, line in enumerate(content) if line.startswith("[dc]")][0]
            case "server":
                section_index = [i for i, line in enumerate(content) if line.startswith("[server]")][0]
            case "workstation":
                section_index = [i for i, line in enumerate(content) if line.startswith("[workstation]")][0]
            case _:
                raise ValueError("Invalid system type")
        content.insert(section_index + 1, f"{system_name}\n")
        
        ## Add machine names to tags: parent_dc, child_dc
        if (system['type'] == 'dc') and ('dc_type' not in system):
            raise ValueError("Missing dc_type in dc system")
        if (system['type'] == 'dc'):
            match system['dc_type']:
                case "parent_dc":
                    section_index = [i for i, line in enumerate(content) if line.startswith("[parent_dc]")][0]
                case "child_dc":
                    section_index = [i for i, line in enumerate(content) if line.startswith("[child_dc]")][0]
                # case "''":
                #     print("got an emoty dc_type");
                # case _:
                #     print(f"dc_type: {system['dc_type']}");
                #     raise ValueError("Invalid dc type")
            content.insert(section_index + 1, f"{system_name}\n")

        for service in system['services']:
            ## Handle services args
            if 'args' in service:
                system.update({service['name'] : service['args']})
    
            ## Add services to inventory
            # Find the section header
            section_index = [i for i, line in enumerate(content) if line.startswith(f"[{service['name']}]")][0]
            # Insert items after the section header
            content.insert(section_index + 1, f"{system_name}\n")
        # Write the updated content back to the file
        f.seek(0)
        f.writelines(content)

def copy_vuln_script(project_dir: str, script_name: str):
    """Fetch user selected vuln scripts to project folders"""
    # TODO test if same script name in same/difffernt machines in Scneario File works
    count = 1
    if os.path.isfile(project_dir + f"/scripts/{script_name}.ps1"):
        shutil.copyfile(f"../components/ad/{script_name}/{script_name}.ps1", project_dir + f"/scripts/{script_name}_{count}.ps1")
        count += 1
    else:
        shutil.copyfile(f"../components/ad/{script_name}/{script_name}.ps1", project_dir + f"/scripts/{script_name}.ps1")
        
def generate_config(project_dir: str):
    """Convert scenario.yaml to config.json and Inventory for Ansible, 
    Vagrantfile for Vagrant."""
    ###############################################
    # Scenario Data
    # Load the YAML file
    with open(f'{project_dir}/scenario.yaml', 'r') as file:
        data = yaml.safe_load(file)

    # Convert the data to JSON
    scenario_json_text = json.dumps(data, indent=4)
    scenario_json_data = json.loads(scenario_json_text)

    # Process YAML Data
    config = { "lab" : { "hosts" : {}, "domains" : {}}}
    systems = scenario_json_data["systems"]
    for system in systems:
        
        # Add all machine data to the "hosts" dict
        hosts = config["lab"]["hosts"]
        hosts.update({ system["hostname"] : system})
        config["lab"]["hosts"] = hosts

        # Handle vulnerabilities and vulns_vars
        scripts = []
        vulns = []
        vulns_vars = {}
        for vuln in system['vulnerabilities']:
            if "ad/scripts" in vuln['name']:
                name = vuln['name'].replace("ad/scripts/", "")
                copy_vuln_script(project_dir, name)
                                
                if 'args' in vuln:
                    handle_script(project_dir, name, vuln['args'])
                
                name = name + ".ps1"
                scripts.append(name)
            else:
                name = vuln['name'].replace("ad/", "")
                vulns.append(name)
                if 'args' in vuln:
                    vulns_vars[name] = vuln['args']


        # Handle flag plugin
        # TODO only handle 1 flag now
        for plugin in system['plugins']:
            if plugin.get('name') == 'flag':
                flag_dict = plugin.get('args')
                vulns_vars['files'].update({'flag' : flag_dict}) 
                # Remove flag plugin in plugins
                system['plugins'] = [plugin for plugin in system['plugins'] if plugin.get('name') != 'flag']
                break
        
        # After processing all plugins
        
        output = {
            'scripts': scripts,
            'vulns': vulns,
            'vulns_vars': vulns_vars
        }
        system.update(output)
        # Handle inventory
        write_machine_to_inventory(project_dir, system)
        
        ###############################################
        # Replace hardcoded values in Vagrant File
        # Read the Vagrantfile
        with open(f'{project_dir}/Vagrantfile', 'r+') as vagrant_file:
            content = vagrant_file.readlines()
            section_index = [i for i, line in enumerate(content) if line.startswith("boxes = [")][0]
            content.insert(section_index + 1, "{:name => '%s', :ip => '%s', :box => 'StefanScherer/windows_2019', :box_version => '2021.05.15', :os => 'windows'},\n" % (system['hostname'], system['ip']))        
        
            vagrant_file.seek(0)
            vagrant_file.writelines(content)

        ## Delete dicts for json dumping at the end
        del system["ip"]
        del system['plugins']
        del system['vulnerabilities']
        del system['services']

    # Change project_folder path in Inventory
    with open(f"{project_dir}/inventory", 'r+') as f:
        content = f.readlines()
        section_index = [i for i, line in enumerate(content) if line.startswith("[all:vars]")][0]
        content.insert(section_index + 1, f"project_folder={scenario_json_data['name']}\n")        
        f.seek(0)
        f.writelines(content)


    ###############################################
    # Domain Data

    domain_data = scenario_json_data["domains"]

    domains = config["lab"]["domains"]
    domains.update(domain_data)

    ###############################################
    # Generate config.json
    # Write all JSON data to config.json
    with open(f'{project_dir}/config.json', 'w+') as file:
        json.dump(config, file, ensure_ascii=False, indent=4)