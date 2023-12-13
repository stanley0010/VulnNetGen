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

def replace_flag(flag:str, output_path: str) -> None:
    """Replace the flag in the main.yaml file and return the new text"""
    with open('../components/generators/flag/main.yaml', 'r') as f:
        with open(output_path + "/playbooks/flag.yaml", 'w') as f2:
            data = safe_load(f)
            data[0]['lineinfile']['line'] = flag
            if data:
                safe_dump(data, f2, sort_keys=False)

def create_user_password(password: str) -> str:
    """Create a password hash for a user"""
    password_hash = sha512_crypt.using(rounds=5000).hash(password)
    return password_hash

def create_users(users: list, output_path: str) -> None:
    """Create users in the main.yaml file and return the new text"""
    try:
        with open('../components/generators/user/main.yaml', 'r') as input_file:
            with open(output_path + "/playbooks/users.yaml", 'w') as output_file:
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
    except IOError as err:
        print(err)
        return None