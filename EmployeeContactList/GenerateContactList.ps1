Get-ADGroupMember -identity "PhoneDirectory-Employees" |   
Get-ADUser -properties displayName, title, department, physicalDeliveryOfficeName, mail, telephoneNumber |   
Select-Object displayName, title, department, physicalDeliveryOfficeName, mail, telephoneNumber |   
Export-CSV C:\'Create Contact List'\contactlist.csv -NoTypeInformation