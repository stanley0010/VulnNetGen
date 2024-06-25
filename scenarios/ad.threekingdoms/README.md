# README of AD_light Scenario

## Credit
This scenario and scripts to provision it are based on the work of [GOAD](https://github.com/Orange-Cyberdefense/GOAD). 

## Description
This scenario is a light version of the Active Directory scenario. It is a stripped down version of the original scenario, with less users, groups, and computers. It contains only 3 VMs, with 2 DCs and 1 server (installed with webdav, IIS, mssql).

## Scenario vulnerabilities (adopted from GOAD)
- You can find a lot of the available scenarios on [https://mayfly277.github.io/categories/ad/](https://mayfly277.github.io/categories/ad/)

NORTH.SEVENKINGDOMS.LOCAL
- STARKS:              RDP on WINTERFELL AND CASTELBLACK
  - arya.stark:        Execute as user on mssql
  - eddard.stark:      DOMAIN ADMIN NORTH/ (bot 5min) LLMRN request to do NTLM relay with responder
  - catelyn.stark:     
  - robb.stark:        bot (3min) RESPONDER LLMR
  - sansa.stark:       
  - brandon.stark:     ASREP_ROASTING
  - rickon.stark:      
  - theon.greyjoy:
  - jon.snow:          mssql admin / KERBEROASTING / group cross domain / mssql trusted link
  - hodor:             PASSWORD SPRAY (user=password)
- NIGHT WATCH:         RDP on CASTELBLACK
  - samwell.tarly:     Password in ldap description / mssql execute as login
                       GPO abuse (Edit Settings on "STARKWALLPAPER" GPO)
  - jon.snow:          (see starks)
  - jeor.mormont:      (see mormont)
- MORMONT:             RDP on CASTELBLACK
  - jeor.mormont:      ACL writedacl-writeowner on group Night Watch
- AcrossTheSea :       cross forest group

SEVENKINGDOMS.LOCAL
- LANISTERS
  - tywin.lannister:   ACL forcechangepassword on jaime.lanister
  - jaime.lannister:   ACL genericwrite-on-user joffrey.baratheon
  - tyron.lannister:   ACL self-self-membership-on-group Small Council
  - cersei.lannister:  DOMAIN ADMIN SEVENKINGDOMS
- BARATHEON:           RDP on KINGSLANDING
  - robert.baratheon:  DOMAIN ADMIN SEVENKINGDOMS
  - joffrey.baratheon: ACL Write DACL on tyron.lannister
  - renly.baratheon:
  - stannis.baratheon: ACL genericall-on-computer kingslanding / ACL writeproperty-self-membership Domain Admins
- SMALL COUNCIL :      ACL add Member to group dragon stone / RDP on KINGSLANDING
  - petyer.baelish:    ACL writeproperty-on-group Domain Admins
  - lord.varys:        ACL genericall-on-group Domain Admins / Acrossthenarrossea
  - maester.pycelle:   ACL write owner on group Domain Admins
- DRAGONSTONE :        ACL Write Owner on KINGSGUARD
- KINGSGUARD :         ACL generic all on user stannis.baratheon
- AccorsTheNarrowSea:       cross forest group

## Customizing your own AD Scenario
Note that scenario file of an AD environment is formatted slightly different to other scnearios. Also note that the `files` folder in this scenario folder is necessary for machines to be deployed correctly. 