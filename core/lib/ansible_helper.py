import os
import shutil
from yaml import safe_load, safe_dump
from passlib.hash import sha512_crypt
from subprocess import Popen, PIPE, STDOUT
import time
import re


def concat_ansible_playbooks(path1, path2, output_path) -> None:
    """Concatenate two ansible playbooks and output to a playbook.yaml file"""
    with open(path1, "r") as f1:
        with open(path2, "r") as f2:
            with open(output_path + "/playbook.yaml", "w") as f3:
                data = safe_load(f1)
                data2 = safe_load(f2)
                data[0]["tasks"].append(data2[0])
                if data:
                    safe_dump(data, f3, sort_keys=False)


def create_flag_playbook(
    flag: str,
    flag_path: str,
    owner: str,
    group: str,
    mode: str,
    system_name: str,
    output_path: str,
    windows: bool,
) -> None:
    """Replace the flag in the main.yaml file and return the new text"""
    with open(
        f"../components/plugins/flag_{'win' if windows else 'linux'}/main.yaml", "r"
    ) as f:
        with open(output_path + f"/playbooks/{system_name}/flag.yaml", "w") as f2:
            data = safe_load(f)

            # Use regex to extract the directory path from the flag path
            pattern = r"(.*)[\\/][^\\/]+$"
            match = re.search(pattern, flag_path)
            if match:
                flag_dir = match.group(1)
            else:
                raise ValueError("Flag path is invalid")

            # Ensure the directories exist by creating them
            if windows:
                data[0]["ansible.windows.win_file"]["path"] = flag_dir
                data[1]["community.windows.win_lineinfile"]["line"] = flag
                data[1]["community.windows.win_lineinfile"]["path"] = flag_path
            else:
                data[0]["ansible.builtin.file"]["path"] = flag_dir
                data[1]["lineinfile"]["line"] = flag
                data[1]["lineinfile"]["path"] = flag_path

            # owner, group, mode settings not available for Windows machines now
            if not windows:
                data[1]["lineinfile"]["owner"] = owner
                data[1]["lineinfile"]["group"] = group
                data[1]["lineinfile"]["mode"] = mode
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
            with open("../components/plugins/user/main.yaml", "r") as input_file:
                with open(
                    output_path + f"/playbooks/{system_name}/users.yaml", "w"
                ) as output_file:
                    output_file.truncate(0)
                    for user in users:
                        input_file.seek(0)
                        text = input_file.read()
                        text = text.replace("test_user", user["name"])
                        hash_password = create_user_password(user["password"])
                        text = text.replace("test_password", hash_password)
                        if user["privileged"] == True:
                            text = text.replace("system: false", "system: true")
                            text += "    groups: admin, sudo\n"
                            text += "    append: true\n"
                        output_file.write(text)
        except IOError:
            raise


def create_vulnerability_playbook(
    system_name: str, vuln: dict, output_path: str
) -> None:
    """Create a vulnerability playbook and return the new text"""
    # vuln['name'] is in the format of "linux/<vuln_name>", so we need to extract the vulnerability name
    vuln_name = vuln["name"].rsplit("/", 1)[1]
    vuln_args = vuln.get("args")
    try:
        # create a new playbook for the vulnerability first
        shutil.copyfile(
            f"../components/{vuln['name']}/main.yaml",
            output_path + f"/playbooks/{system_name}/vuln_{vuln_name}.yaml",
        )
        # replace the host name in the playbook to "system_name"
        with open(
            output_path + f"/playbooks/{system_name}/vuln_{vuln_name}.yaml", "r+"
        ) as f:
            text = f.read()
            text = text.replace("$hostname", system_name)
            f.seek(0)
            f.truncate(0)
            f.write(text)
        # for the dict "arguments", replace the key with the value in the playbook
        if vuln_args is not None:
            with open(
                output_path + f"/playbooks/{system_name}/vuln_{vuln_name}.yaml", "r+"
            ) as f:
                text = f.read()
                for key, value in vuln_args.items():
                    text = text.replace(
                        f"${key}", str(value)
                    )  # str() to convert the any value, e.g. bool, to string
                f.seek(0)
                f.truncate(0)
                f.write(text)

        if vuln_args and vuln_args.get("copy_files") is True:
            if os.path.exists(f"../components/{vuln['name']}/files"):
                shutil.copytree(
                    f"../components/{vuln['name']}/files",
                    output_path + f"/playbooks/{system_name}/files",
                )
                # FIXME: two vulnerabilities with files to copy will overwrite each other's files?
            else:
                raise FileNotFoundError(
                    f"'../components/{vuln['name']}/files' folder does not exist"
                )
    except IOError:
        raise


def ansible_ad(project_dir: str):
    """Run Ansible playbooks on AD machines"""

    # spliting two batch because 5 mins sleep is needed after child domain creation
    # ansible_playbooks_first_batch = ["build.yml","ad-servers.yml","ad-parent_domain.yml","ad-child_domain.yml"]
    # ansible_playbooks_second_batch = ["ad-members.yml","ad-trusts.yml","ad-data.yml","ad-gmsa.yml","laps.yml","ad-relations.yml","adcs.yml","ad-acl.yml","servers.yml","security.yml","vulnerabilities.yml"]

    root_dir = os.path.dirname(os.getcwd())

    start_time = time.time()

    with open(f"{project_dir}/deployment.log", "a") as log_file:
        os.chdir(f"{root_dir}/baseboxes/ad/ansible")
        Popen(
            ["bash", f"{root_dir}/baseboxes/ad/ansible/provisioning.sh", project_dir],
            stdout=PIPE,
            stderr=PIPE,
        )

        # Read the output of the script line by line
        # while True:
        #     line = process.stdout.readline().decode('utf-8')
        #     if not line:
        #         break
        #     print(line.strip())  # Print the output line

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Ansible Elapsed time: ", elapsed_time)
