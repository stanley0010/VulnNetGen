# netdom trust sevenkingdoms.local /d:essos.local /enablesidhistory:yes
# trusting_domain means the domain that trusts the other domain
# trusted_domain means the domain that is trusted by the other domain
netdom trust $trusting_domain /d:$trusted_domain /enablesidhistory:yes