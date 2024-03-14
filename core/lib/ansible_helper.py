import os
import shutil
from yaml import safe_load, safe_dump
from passlib.hash import sha512_crypt

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

def create_flag_playbook(flag:str, system_name:str, output_path: str) -> None:
    """Replace the flag in the main.yaml file and return the new text"""
    with open('../components/generators/flag/main.yaml', 'r') as f:
        with open(output_path + f"/playbooks/{system_name}/flag.yaml", 'w') as f2:
            data = safe_load(f)
            data[0]['lineinfile']['line'] = flag
            if data:
                safe_dump(data, f2, sort_keys=False)

def create_user_password(password: str) -> str:
    """Create a password hash for a user"""
    password_hash = sha512_crypt.using(rounds=5000).hash(password)
    return password_hash

def create_users(users: list, system_name: str, output_path: str) -> None:
    """Create users in the main.yaml file and return the new text"""
    if users is None:
        return None
    else:
        try:
            with open('../components/generators/user/main.yaml', 'r') as input_file:
                with open(output_path + f"/playbooks/{system_name}/users.yaml", 'w') as output_file:
                    output_file.truncate(0)
                    for user in users:
                        input_file.seek(0)
                        text = input_file.read()
                        text = text.replace('test_user', user['name'])
                        hash_password = create_user_password(user['password'])
                        text = text.replace('test_password', hash_password)
                        if (user['privileged'] == True):
                            text = text.replace('system: false', 'system: true')
                            text += "    groups: admin, sudo\n"
                            text += "    append: true\n"
                        output_file.write(text)
        except IOError:
            raise

def create_vulnerability_playbook(system_name: str, vuln: dict, output_path: str) -> None:
    """Create a vulnerability playbook and return the new text"""
    # vuln['name'] is in the format of "linux/<vuln_name>", so we need to extract the vulnerability name
    vuln_name = vuln['name'].rsplit('/', 1)[1]
    vuln_args = vuln.get('args')
    try:
        # create a new playbook for the vulnerability first
        shutil.copyfile(f"../components/{vuln['name']}/main.yaml", output_path + f"/playbooks/{system_name}/vuln_{vuln_name}.yaml")
        # replace the host name in the playbook to "system_name"
        with open(output_path + f"/playbooks/{system_name}/vuln_{vuln_name}.yaml", 'r+') as f:
            text = f.read()
            text = text.replace('$hostname', system_name)
            f.seek(0)
            f.truncate(0)
            f.write(text)
        # for the dict "arguments", replace the key with the value in the playbook
        if vuln_args is not None:
            with open(output_path + f"/playbooks/{system_name}/vuln_{vuln_name}.yaml", 'r+') as f:
                text = f.read()
                for key, value in vuln_args.items():
                    text = text.replace(f"${key}", str(value)) # str() to convert the any value, e.g. bool, to string
                f.seek(0)
                f.truncate(0)
                f.write(text)

        if vuln_args and vuln_args.get('copy_files') is True:
            if os.path.exists(f"../components/{vuln['name']}/files"):
                shutil.copytree(f"../components/{vuln['name']}/files", output_path + f"/playbooks/{system_name}/files")
                # FIXME: two vulnerabilities with files to copy will overwrite each other's files?
            else:
                raise FileNotFoundError(f"'../components/{vuln['name']}/files' folder does not exist")
    except IOError:
        raise
