from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from lib.scenario_helper import start_scenario
import os, yaml, shutil, threading, time

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
@app.errorhandler(404)
def home():
    return render_template('home.html')

@app.route("/create/configure-ad-domains")
def configure_ad_domains():
    return render_template('configure_scenario_ad_domains.html', import_scenario=False)

@app.route("/create/configure-ad-machines")
def configure_ad_machines():
    return render_template('configure_scenario_ad_machines.html', import_scenario=False)

@app.route("/create/design")
def create_design_scenario():
    return render_template('design_scenario.html', import_scenario=False)

@app.route("/create/configure")
def create_configure_scenario():
    return render_template('configure_scenario.html', import_scenario=False)

@app.route("/create/deploy")
def create_deploy_scenario():
    return render_template('deploy_scenario.html', import_scenario=False)

@app.route("/import")
def import_scenario():
    return render_template('import_scenario.html', import_scenario=True)

@app.route("/import/design")
def import_design_scenario():
    return render_template('design_scenario.html', import_scenario=True)

@app.route("/import/configure")
def import_configure_scenario():
    return render_template('configure_scenario.html', import_scenario=True)

@app.route("/import/deploy")
def import_deploy_scenario():
    return render_template('deploy_scenario.html', import_scenario=True)

@app.route("/api", methods=['POST'])
def api():
    if request.method == "POST":
        req_json = request.json
        option = req_json.get('option')
        data = {}
        match option:
            case "os-list":
                os_list = []
                with open('../baseboxes/vm_box_list.ini', 'r') as f:
                    line = f.readline()
                    while line:
                        os_list.append(line.split('=')[0])
                        line = f.readline()
                    f.close()
                data = {"return" : os_list}
            case "vulnerabilities-list":
                linux_vuln_list = [f'linux/{f.name}' for f in os.scandir('../components/linux') if f.is_dir()]
                windows_vuln_list = [f'windows/{f.name}' for f in os.scandir('../components/windows') if f.is_dir()]
                data = {"return" : linux_vuln_list + windows_vuln_list}
            case "plugin-list":
                plugin_list = [f.name for f in os.scandir('../components/plugins') if f.is_dir()]
                plugin_list.remove("user")
                data = {"return" : plugin_list}
            case "argument-list":
                component = req_json.get('component')
                path = f'../components/{component}/args.list'
                argument_list = []
                if (os.path.isfile(path)):
                    with open(path, 'r') as f:
                        argument_list = [line.rstrip('\n') for line in f]
                data = {"return" : argument_list}
            case "scenario-list":
                scenario_list = [f.name for f in os.scandir('../scenarios') if f.is_dir()]
                data = {"return": scenario_list}
            case "json-to-file":
                scenarioObject = req_json.get('scenarioObject')
                folder_name = jsonToScenario(scenarioObject)
                data = {"return" : folder_name}
            case "file-to-json":
                scenarioName = req_json.get('scenarioName')
                scenarioObject = scenarioToJson(scenarioName)
                data = {"return" : scenarioObject}
            case "run-scenario":
                scenarioName = req_json.get('scenarioName')
                scenario_thread = threading.Thread(target=start_scenario,  args=[scenarioName])
                scenario_thread.start()
                time.sleep(1)
                list_dir = ['../projects/'+d.name for d in os.scandir('../projects') if d.is_dir()]
                # while not os.path.exists(file_path):
                #     time.sleep(1)
                latest_project = max(list_dir, key=os.path.getctime) # FIXME can get wrong dir
                while (True):
                    time.sleep(1)
                    if os.path.exists(f'{latest_project}/deployment.log'):
                        with open(f'{latest_project}/deployment.log', 'r') as f:
                            socketio.emit('log', {'log': f.read()})
                    if not scenario_thread.is_alive():
                        break
            case _:
                data = {"return" : "Invalid option!"}
        return jsonify(data)
    
    
def scenarioToJson(scenarioName):
    with open(f'../scenarios/{scenarioName}/scenario.yaml', 'r') as f:
        try:
            d = yaml.load(f, Loader=yaml.SafeLoader)
            if ('AD' in d) and (d['AD'] == True):
                scenarioObject = ADScenarioToJson(d)
            else:
                scenarioObject = normalScenarioToJson(d)
            return scenarioObject
        except yaml.YAMLError as e:
            print(e)
            
def ADScenarioToJson(d):
    scenarioObject = {}
    scenarioObject['scenario_name'] = d['name']
    scenarioObject['description'] = d['description']
    scenarioObject['author'] = d['author']
    scenarioObject['difficulty'] = d['difficulty']
    scenarioObject['AD'] = True
    # scenarioObject['domain_name'] = d['domain_name'] # This is not needed, removed later
    scenarioObject['systems'] = {}
    for machine_index in range(1, len(d['systems']) + 1):
        scenarioObject['systems'][machine_index] = {}
        scenarioObject['systems'][machine_index]['hostname'] = d['systems'][machine_index-1]['hostname']
        scenarioObject['systems'][machine_index]['ip'] = d['systems'][machine_index-1]['ip']
        scenarioObject['systems'][machine_index]['type'] = d['systems'][machine_index-1]['type']
        if ('dc_type' in d['systems'][machine_index-1]):
            scenarioObject['systems'][machine_index]['dc_type'] = d['systems'][machine_index-1]['dc_type']
        else:
            scenarioObject['systems'][machine_index]['dc_type'] = ''
        scenarioObject['systems'][machine_index]['dns_domain'] = d['systems'][machine_index-1]['dns_domain']
        scenarioObject['systems'][machine_index]['local_admin_password'] = d['systems'][machine_index-1]['local_admin_password']
        scenarioObject['systems'][machine_index]['domain'] = d['systems'][machine_index-1]['domain']
        scenarioObject['systems'][machine_index]['path'] = d['systems'][machine_index-1]['path']
        scenarioObject['systems'][machine_index]['local_groups'] = {}
        if ('local_groups' in d['systems'][machine_index-1]):
            local_groups_count = 0
            for local_group in d['systems'][machine_index-1]['local_groups'].keys():
                # print(d['systems'][machine_index-1]['local_groups'][local_group])
                for i in range(0, len(d['systems'][machine_index-1]['local_groups'][local_group])):
                    local_groups_count += 1
                    scenarioObject['systems'][machine_index]['local_groups'][local_groups_count] = {}
                    scenarioObject['systems'][machine_index]['local_groups'][local_groups_count]['group_name'] = local_group
                    scenarioObject['systems'][machine_index]['local_groups'][local_groups_count]['user'] = d['systems'][machine_index-1]['local_groups'][local_group][i]
        scenarioObject['systems'][machine_index]['vulnerabilities'] = {}
        if ('vulnerabilities' in d['systems'][machine_index-1]):
            for vuln_count in range(1, len(d['systems'][machine_index-1]['vulnerabilities']) + 1):
                scenarioObject['systems'][machine_index]['vulnerabilities'][vuln_count] = d['systems'][machine_index-1]['vulnerabilities'][vuln_count-1]
        scenarioObject['systems'][machine_index]['services'] = {}     
        if ('services' in d['systems'][machine_index-1]):
            for service_count in range(1, len(d['systems'][machine_index-1]['services']) + 1):
                 scenarioObject['systems'][machine_index]['services'][service_count] = d['systems'][machine_index-1]['services'][service_count-1]
        scenarioObject['systems'][machine_index]['plugins'] = {}     
        if ('plugins' in d['systems'][machine_index-1]):
            for plugin_count in range(1, len(d['systems'][machine_index-1]['plugins']) + 1):
                 scenarioObject['systems'][machine_index]['plugins'][plugin_count] = d['systems'][machine_index-1]['plugins'][plugin_count-1]
    scenarioObject['domains'] = {}
    for (domain_index, domain_name) in list(enumerate(d['domains'], start=1)):
        scenarioObject['domains'][domain_index] = {}
        scenarioObject['domains'][domain_index][domain_name] = {}
        scenarioObject['domains'][domain_index][domain_name]['dc'] = d['domains'][domain_name]['dc']
        scenarioObject['domains'][domain_index][domain_name]['domain_password'] = d['domains'][domain_name]['domain_password']
        scenarioObject['domains'][domain_index][domain_name]['netbios_name'] = d['domains'][domain_name]['netbios_name']
        scenarioObject['domains'][domain_index][domain_name]['trust'] = d['domains'][domain_name]['trust']
        scenarioObject['domains'][domain_index][domain_name]['laps_path'] = d['domains'][domain_name]['laps_path']
        scenarioObject['domains'][domain_index][domain_name]['organisation_units'] = {}
        for (organisation_count, organisation_name) in list(enumerate(d['domains'][domain_name]['organisation_units'], start=1)):
            scenarioObject['domains'][domain_index][domain_name]['organisation_units'][organisation_count] = {}
            scenarioObject['domains'][domain_index][domain_name]['organisation_units'][organisation_count][organisation_name] = d['domains'][domain_name]['organisation_units'][organisation_name]
        scenarioObject['domains'][domain_index][domain_name]['groups'] = {}
        scenarioObject['domains'][domain_index][domain_name]['groups']['universal'] = {}
        scenarioObject['domains'][domain_index][domain_name]['groups']['global'] = {}
        for (global_group_count, global_group_name) in list(enumerate(d['domains'][domain_name]['groups']['global'], start=1)):
            scenarioObject['domains'][domain_index][domain_name]['groups']['global'][global_group_count] = {}
            scenarioObject['domains'][domain_index][domain_name]['groups']['global'][global_group_count][global_group_name] = d['domains'][domain_name]['groups']['global'][global_group_name]
        scenarioObject['domains'][domain_index][domain_name]['groups']['domainlocal'] = {}
        for (local_group_count, local_group_name) in list(enumerate(d['domains'][domain_name]['groups']['domainlocal'], start=1)):
            scenarioObject['domains'][domain_index][domain_name]['groups']['domainlocal'][local_group_count] = {}
            scenarioObject['domains'][domain_index][domain_name]['groups']['domainlocal'][local_group_count][local_group_name] = d['domains'][domain_name]['groups']['domainlocal'][local_group_name]
        scenarioObject['domains'][domain_index][domain_name]['multi_domain_groups_member'] = {}
        scenarioObject['domains'][domain_index][domain_name]['acls'] = {}
        for (acl_count, acl_name) in list(enumerate(d['domains'][domain_name]['acls'], start=1)):
            scenarioObject['domains'][domain_index][domain_name]['acls'][acl_count] = {}
            scenarioObject['domains'][domain_index][domain_name]['acls'][acl_count][acl_name] = d['domains'][domain_name]['acls'][acl_name]
        scenarioObject['domains'][domain_index][domain_name]['users'] = {}
        for (user_count, user_name) in list(enumerate(d['domains'][domain_name]['users'], start=1)):
            scenarioObject['domains'][domain_index][domain_name]['users'][user_count] = {}
            scenarioObject['domains'][domain_index][domain_name]['users'][user_count][user_name] = d['domains'][domain_name]['users'][user_name]
    return scenarioObject
    
def normalScenarioToJson(d):
    scenarioObject = {}
    scenarioObject['scenario_name'] = d['name']
    scenarioObject['description'] = d['description']
    scenarioObject['author'] = d['author']
    scenarioObject['difficulty'] = d['difficulty']
    for machine_index in range(0, len(d['systems'])):
        machine_id = 'machine_' + str(machine_index + 1)
        scenarioObject[machine_id] = {}
        scenarioObject[machine_id]['machine_name'] = d['systems'][machine_index]['name']
        scenarioObject[machine_id]['ip_address'] = d['systems'][machine_index]['ip']
        scenarioObject[machine_id]['operating_system'] = d['systems'][machine_index]['base']
        scenarioObject[machine_id]['accounts'] = {}
        if ('accounts' in d['systems'][machine_index]):
            for account_index in range(0, len(d['systems'][machine_index]['accounts'])):
                scenarioObject[machine_id]['accounts'][account_index+1] = {}
                scenarioObject[machine_id]['accounts'][account_index+1]['username'] = d['systems'][machine_index]['accounts'][account_index]['name']
                scenarioObject[machine_id]['accounts'][account_index+1]['password'] = d['systems'][machine_index]['accounts'][account_index]['password']
                scenarioObject[machine_id]['accounts'][account_index+1]['privileged'] = d['systems'][machine_index]['accounts'][account_index]['privileged']
        if ('vulnerabilities' in d['systems'][machine_index]):
            scenarioObject[machine_id]['vulnerabilities'] = {}
            for vul_index in range(0, len(d['systems'][machine_index]['vulnerabilities'])):
                scenarioObject[machine_id]['vulnerabilities'][vul_index+1] = {}
                scenarioObject[machine_id]['vulnerabilities'][vul_index+1]['name'] = d['systems'][machine_index]['vulnerabilities'][vul_index]['name']
                if ('args' in d['systems'][machine_index]['vulnerabilities'][vul_index]):
                    scenarioObject[machine_id]['vulnerabilities'][vul_index+1]['args'] = d['systems'][machine_index]['vulnerabilities'][vul_index]['args']
                else:
                    scenarioObject[machine_id]['vulnerabilities'][vul_index+1]['args'] = {}
        if ('plugins' in d['systems'][machine_index]):
            scenarioObject[machine_id]['plugins'] = {}
            for plugin_index in range(0, len(d['systems'][machine_index]['plugins'])):
                scenarioObject[machine_id]['plugins'][plugin_index+1] = {}
                scenarioObject[machine_id]['plugins'][plugin_index+1]['name'] = d['systems'][machine_index]['plugins'][plugin_index]['name']
                if ('args' in d['systems'][machine_index]['plugins'][plugin_index]):
                    scenarioObject[machine_id]['plugins'][plugin_index+1]['args'] = d['systems'][machine_index]['plugins'][plugin_index]['args']
                    # Speical case: mode
                    if ('mode' in scenarioObject[machine_id]['plugins'][plugin_index+1]['args']):
                        if isinstance(scenarioObject[machine_id]['plugins'][plugin_index+1]['args']['mode'], str):
                            scenarioObject[machine_id]['plugins'][plugin_index+1]['args']['mode'] = '{:04d}'.format(int(scenarioObject[machine_id]['plugins'][plugin_index+1]['args']['mode'], 8))
                        else:
                            scenarioObject[machine_id]['plugins'][plugin_index+1]['args']['mode'] = '{:04d}'.format(int(oct(scenarioObject[machine_id]['plugins'][plugin_index+1]['args']['mode'])[2:]))
                else:
                    scenarioObject[machine_id]['plugins'][plugin_index+1]['args'] = {}
    return scenarioObject

def jsonToScenario(scenarioObject):
    if ('AD' in scenarioObject) and (scenarioObject['AD'] == True):
        yamlObject = jsonToADScenario(scenarioObject)
    else:
        yamlObject = jsonToNormalScenario(scenarioObject)
    return yamlObject
            
def jsonToADScenario(scenarioObject):
    yamlObject = {}
    yamlObject['name'] = scenarioObject['scenario_name']
    yamlObject['description'] = scenarioObject['description']
    yamlObject['author'] = scenarioObject['author']
    yamlObject['difficulty'] = scenarioObject['difficulty']
    yamlObject['AD'] = True
    # yamlObject['domain_name'] = scenarioObject['domain_name'] # This is not needed, removed later
    yamlObject['systems'] = []
    for system_index in scenarioObject['systems'].keys():
        system = {}
        system['hostname'] = scenarioObject['systems'][system_index]['hostname']
        system['ip'] = scenarioObject['systems'][system_index]['ip']
        system['type'] = scenarioObject['systems'][system_index]['type']
        if (scenarioObject['systems'][system_index]['dc_type'] != ''):
            system['dc_type'] = scenarioObject['systems'][system_index]['dc_type']
        else:
            system['dc_type'] = ''            
        system['dns_domain'] = scenarioObject['systems'][system_index]['dns_domain']
        system['local_admin_password'] = scenarioObject['systems'][system_index]['local_admin_password']
        system['domain'] = scenarioObject['systems'][system_index]['domain']
        system['path'] = scenarioObject['systems'][system_index]['path']
        system['local_groups'] = {}
        for local_group_index in scenarioObject['systems'][system_index]['local_groups']:
            group_name = scenarioObject['systems'][system_index]['local_groups'][local_group_index]['group_name']
            user = scenarioObject['systems'][system_index]['local_groups'][local_group_index]['user']
            if (group_name in system['local_groups']):
                system['local_groups'][group_name].append(user)
            else:
                system['local_groups'][group_name] = [user]
        system['vulnerabilities'] = []
        for key, value in scenarioObject['systems'][system_index]['vulnerabilities'].items():
            vulnerability = {'name': value['name']}
            if 'args' in value:
                vulnerability['args'] = value['args']
            system['vulnerabilities'].append(vulnerability)
        system['services'] = []
        # for service_index in scenarioObject['systems'][system_index]['services'].keys():
        #     service_object = scenarioObject['systems'][system_index]['services'][service_index];
        #     if ('args' in service_object and len(service_object['args']) == 0):
        #         del service_object['args']
        #     system['services'].append(service_object)
        for key, value in scenarioObject['systems'][system_index]['services'].items():
            service = {'name': value['name']}
            if 'args' in value:
                service['args'] = value['args']
            system['services'].append(service)
        system['plugins'] = []
        # for plugin_index in scenarioObject['systems'][system_index]['plugins'].keys():
        #     plugin_object = scenarioObject['systems'][system_index]['plugins'][plugin_index];
        #     if ('args' in plugin_object and len(plugin_object['args']) == 0):
        #         del plugin_object['args']
        #     system['plugins'].append(plugin_object)
        for key, value in scenarioObject['systems'][system_index]['plugins'].items():
            plugin = {'name': value['name']}
            if 'args' in value:
                plugin['args'] = value['args']
            system['plugins'].append(plugin)
        yamlObject['systems'].append(system)
    yamlObject['domains'] = {}
    for domain_index in scenarioObject['domains']:
        domain = {}
        domain_name = list(scenarioObject['domains'][domain_index].keys())[0]
        domain['dc'] = scenarioObject['domains'][domain_index][domain_name]['dc']
        domain['domain_password'] = scenarioObject['domains'][domain_index][domain_name]['domain_password']
        domain['netbios_name'] = scenarioObject['domains'][domain_index][domain_name]['netbios_name']
        domain['trust'] = scenarioObject['domains'][domain_index][domain_name]['trust']
        if ('laps_path' in scenarioObject['domains'][domain_index][domain_name]):
            domain['laps_path'] = scenarioObject['domains'][domain_index][domain_name]['laps_path']
        else:
            domain['laps_path'] = False
        domain['organisation_units'] = {}
        for organisation_index in scenarioObject['domains'][domain_index][domain_name]['organisation_units'].keys():
            domain['organisation_units'].update(scenarioObject['domains'][domain_index][domain_name]['organisation_units'][organisation_index])
        domain['groups'] = {}
        domain['groups']['universal'] = {}
        domain['groups']['global'] = {}
        for global_index in scenarioObject['domains'][domain_index][domain_name]['groups']['global'].keys():
            domain['groups']['global'].update(scenarioObject['domains'][domain_index][domain_name]['groups']['global'][global_index])
        domain['groups']['domainlocal'] = {}
        for domainlocal_index in scenarioObject['domains'][domain_index][domain_name]['groups']['domainlocal'].keys():
            domain['groups']['domainlocal'].update(scenarioObject['domains'][domain_index][domain_name]['groups']['domainlocal'][domainlocal_index])
        domain['multi_domain_groups_member'] = {}
        domain['acls'] = {}
        for acl_index in scenarioObject['domains'][domain_index][domain_name]['acls'].keys():
            domain['acls'].update(scenarioObject['domains'][domain_index][domain_name]['acls'][acl_index])
        domain['users'] = {}
        for user_index in scenarioObject['domains'][domain_index][domain_name]['users'].keys():
            domain['users'].update(scenarioObject['domains'][domain_index][domain_name]['users'][user_index])
        yamlObject['domains'][domain_name] = domain
    folder_name = yamlObject['name'].lower().replace(' ', '_')
    if (not os.path.exists(f'../scenarios/{folder_name}')):
        os.mkdir(f'../scenarios/{folder_name}')
    else:
        count = 1
        while True:
            if (not os.path.exists(f'../scenarios/{folder_name}_edited_{count}')):
                break
            count += 1
        old_folder_name = folder_name
        folder_name = f'{folder_name}_edited_{count}'
        os.mkdir(f'../scenarios/{folder_name}')
        # copy the folder "/files" from the original scenario to the new folder
        shutil.copytree(f'../scenarios/{old_folder_name}/files', f'../scenarios/{folder_name}/files', dirs_exist_ok=True)
    with open(f'../scenarios/{folder_name}/scenario.yaml', 'w') as f:
        yaml.safe_dump(yamlObject, f, default_style=None, default_flow_style=False, sort_keys=False)
        return folder_name


def jsonToNormalScenario(scenarioObject):
    yamlObject = {}
    yamlObject['name'] = scenarioObject['scenario_name']
    yamlObject['description'] = scenarioObject['description']
    yamlObject['author'] = scenarioObject['author']
    yamlObject['difficulty'] = scenarioObject['difficulty']
    machine_count = 0
    yamlObject['systems'] = []
    while (True):
        machine_count += 1
        machine_id = 'machine_' + str(machine_count)
        if (not machine_id in scenarioObject):
            break
        machine = {}
        machine['name'] = scenarioObject[machine_id]['machine_name']
        machine['base'] = scenarioObject[machine_id]['operating_system']
        machine['ip'] = scenarioObject[machine_id]['ip_address']
        if ('accounts' in scenarioObject[machine_id]):
            machine['accounts'] = []
            account_count = 0
            while (True):
                account_count += 1
                if (not str(account_count) in scenarioObject[machine_id]['accounts']):
                    break
                account = {}
                account['name'] = scenarioObject[machine_id]['accounts'][str(account_count)]['username']
                account['password'] = scenarioObject[machine_id]['accounts'][str(account_count)]['password']
                account['privileged'] = scenarioObject[machine_id]['accounts'][str(account_count)]['privileged']
                machine['accounts'].append(account)
            if (len(machine['accounts']) == 0):
                del machine['accounts']
            machine['vulnerabilities'] = []
            vul_count = 0
            while (True):
                vul_count += 1
                if (not str(vul_count) in scenarioObject[machine_id]['vulnerabilities']):
                    break
                vul = {}
                vul['name'] = scenarioObject[machine_id]['vulnerabilities'][str(vul_count)]['name']
                if (len(scenarioObject[machine_id]['vulnerabilities'][str(vul_count)]['args']) != 0): 
                    vul['args'] = scenarioObject[machine_id]['vulnerabilities'][str(vul_count)]['args']
                machine['vulnerabilities'].append(vul)
            if (len(machine['vulnerabilities']) == 0):
                del machine['vulnerabilities']
            machine['plugins'] = []
            plugin_count = 0
            while (True):
                plugin_count += 1
                if (not str(plugin_count) in scenarioObject[machine_id]['plugins']):
                    break
                plugin = {}
                plugin['name'] = scenarioObject[machine_id]['plugins'][str(plugin_count)]['name']
                if (len(scenarioObject[machine_id]['plugins'][str(plugin_count)]['args']) != 0):
                    plugin['args'] = scenarioObject[machine_id]['plugins'][str(plugin_count)]['args']
                machine['plugins'].append(plugin)
            if (len(machine['plugins']) == 0):
                del machine['plugins']
        yamlObject['systems'].append(machine)
    folder_name = yamlObject['name'].lower().replace(' ', '_')
    if (not os.path.exists(f'../scenarios/{folder_name}')):
        os.mkdir(f'../scenarios/{folder_name}')
    else:
        count = 1
        while True:
            if (not os.path.exists(f'../scenarios/{folder_name}_edited_{count}')):
                break
            count += 1
        folder_name = f'{folder_name}_edited_{count}'
        os.mkdir(f'../scenarios/{folder_name}')
    with open(f'../scenarios/{folder_name}/scenario.yaml', 'w') as f:
        yaml.safe_dump(yamlObject, f, default_style=None, default_flow_style=False, sort_keys=False)
        return folder_name