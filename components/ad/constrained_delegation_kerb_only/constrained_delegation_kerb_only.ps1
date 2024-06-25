# https://www.thehacker.recipes/ad/movement/kerberos/delegations/constrained#without-protocol-transition
Set-ADComputer -Identity "$machine_name$" -ServicePrincipalNames @{Add='$service_principal_name.$domain_name'}
Set-ADComputer -Identity "$machine_name$" -Add @{'msDS-AllowedToDelegateTo'=@('$service_principal_name.$domain_name','$service_principal_name')}
# Set-ADComputer -Identity "castelblack$" -Add @{'msDS-AllowedToDelegateTo'=@('CIFS/winterfell.north.sevenkingdoms.local','CIFS/winterfell')}