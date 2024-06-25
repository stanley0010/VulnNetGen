# https://www.thehacker.recipes/ad/movement/kerberos/delegations/constrained#with-protocol-transition
Set-ADUser -Identity "$username" -ServicePrincipalNames @{Add='$service_principal_name.$domain_name'}
Get-ADUser -Identity "$username" | Set-ADAccountControl -TrustedToAuthForDelegation $true
Set-ADUser -Identity "$username" -Add @{'msDS-AllowedToDelegateTo'=@('$service_principal_name.$domain_name','$service_principal_name')}