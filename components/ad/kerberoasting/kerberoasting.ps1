# Set-ADUser -Identity "$username" -ServicePrincipalNames @{Add='HTTP/thewallserver'}
Set-ADUser -Identity "$username" -ServicePrincipalNames @{Add='$service_principal_name'}