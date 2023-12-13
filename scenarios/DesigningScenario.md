This document outlines the format and syntax of the scenario file. Lab designers can use this document to create their own scenarios. The scenario file is a YAML file.

For each scenario, the following information is required: name, description, author and difficulty.

For each system in the scenario, the following information is required: name, base, ip, accounts, services, vulnerabilities.

The following customization is available:
    base: name of the basebox. Can be found in "/basesboxes"
    ip: an IPv4 address or "dhcp"
    accounts:
      - username: root
        password: <root_password>
      - username: www-data
        password: <www-data_password>
    vulnerabilities:
      - name: "web/sql_injection"
      - name: "web/weak_admin_password"