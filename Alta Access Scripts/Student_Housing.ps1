Import-Module ActiveDirectory

# Use the dorm name as the Key, the AD Group Name as the Value
# For DHALL we have a special condition in the query that appends the floor number to the hall name
$buildings = @{
    'EMH'   	= 'Res - Manny'
    'EAST' 	= 'Res - East'
    'WEST'  	= 'Res - West Hall'
    'SPRING'    = 'Res - Spring'
    'JEST'      = 'Res - Jester'
    'FRIEND'    = 'Res - Friend'
    'TECH'      = 'Res - Tech'
    'BOARD'     = 'Res - Board' 
    'DHALL1'    = 'Res - DHall 1st Floor'
    'DHALL2'    = 'Res - DHall 2nd Floor'
    'DHALL3'    = 'Res - DHall 3rd Floor'
    'DHALL4'    = 'Res - DHall 4th Floor'
    'RAFCUSTOM' = 'Role - RA - Female'
    'RAMCUSTOM' = 'Role - RA - Male'
    
}


# Get list of housing assignments 
# note that DHALL gets the floor number appended to the BLDG_CDE
# Board has 4 codes, they all need to be interpreted as 'BOARD'
# People with the RA role get added to a special group depending on gender

$DormAssignment = Invoke-Sqlcmd -Query @"
SELECT
	ra.StudentIdNumber as IDNUMBER,
	biom.GENDER,
	fc1.Name as 'BuildingName',
	CASE
		WHEN ssr.Position = 'RA' AND biom.GENDER = 'F' THEN 'RAFCUSTOM'
		WHEN ssr.Position = 'RA' AND biom.GENDER = 'M' THEN 'RAMCUSTOM'
		WHEN  fc1.AbbreviatedName = 'BURAN' OR  fc1.AbbreviatedName = 'BUEAN' OR  fc1.AbbreviatedName = 'DALAN' OR  				fc1.AbbreviatedName = 'BUWAN' THEN 'BURRITT'
		WHEN fc1.AbbreviatedName = 'UHALL' THEN fc1.AbbreviatedName + TRIM(STR(fs.OnWhichFloor))
		ELSE
			fc1.AbbreviatedName 
		END as [BLDG_CDE],
	ra.SpaceName,
	fs.OnWhichFloor,
	ssr.Position,
	st.SESS_BEGN_DTE,
	st.SESS_END_DTE
FROM
	SAStudentResidenceSummary ra
INNER JOIN 
	BIOGRAPH biom on ra.StudentIdNumber = biom.IDNUMBER
INNER JOIN
	dbo.SESSION_MSTR st on ra.SessionGoid = st.GOID
INNER JOIN
	Facility fc on ra.SpaceGoid = fc.GOID
INNER JOIN
	Facility fc1 on ra.PlaceGoid = fc1.GOID
INNER JOIN
	FacilitySpace fs on fc.AppID = fs.AppID
LEFT JOIN
	SAStaffRoster ssr on ssr.SessionGoid = ra.SessionGoid and ssr.StaffIdNumber = ra.StudentIdNumber
WHERE
	ra.StudentIdNumber is not null
	AND getdate() between dateadd(day,-1, st.SESS_BEGN_DTE) and dateadd(day, 7, st.SESS_END_DTE) --During residence session starts
	AND st.SESS_NAME NOT LIKE '%VOID%'
ORDER BY  SESS_END_DTE, BLDG_CDE,IDNUMBER
"@ -ConnectionString "Data Source=STUDENTDATABASE;Initial Catalog=PROD;Integrated Security=True;ApplicationIntent=ReadOnly"


# Loop through each building (defined in $buildings) and add/remove students from the AD group based off their J1 housing data

foreach($building in $buildings.GetEnumerator())
{
	$BuildingCode = $building.Key
	$GroupName = $building.Value

	$CurrentMembers = Get-ADGroupMember -Identity $GroupName | Select-Object -ExpandProperty SamAccountName

	$CurrentDate = Get-Date


	# Extract valid students from SQL results who SHOULD be in the group
	# This creates a list of IDs that meet the criteria (Correct Building + Not Expired)

	$ThisBuildingsStudentIDs = $DormAssignment | Where-Object {

		$sessEndDate = Get-Date $_.SESS_END_DTE
		$_.BLDG_CDE -eq $BuildingCode -and $CurrentDate -lt $sessEndDate

	} | Select-Object -ExpandProperty IDNUMBER

	# Add missing students

	foreach ($studentID in $ThisBuildingsStudentIDs) {

		if ($studentID -notin $CurrentMembers) {

			try {
				$user = Get-ADUser -Filter {SamAccountName -eq $studentID}
				Add-ADGroupMember -Identity $GroupName -Members $user
				Write-Host "Added $studentID to $GroupName" -ForegroundColor Green
			}
			catch {
				Write-Warning "Could not find or add user: $studentID"
			}

		}

	}

	# Remove students who have moved

	foreach ($memberID in $CurrentMembers) {

		if ($memberID -notin $ThisBuildingsStudentIDs) {

			try {
				#$user = Get-ADUser -Filter {SamAccountName -eq $memberID}
				#Remove-ADGroupMember -Identity $GroupName -Members $memberID -Confirm:$false
				Remove-ADGroupMember -Identity $GroupName -Members $memberID -Confirm:$false
				Write-Host "Removed $memberID from $GroupName (Assignment changed or expired)" -ForegroundColor Yellow
			}
			catch {
				Write-Warning "Failed to remove $memberID from $GroupName"
			}
		}

	}

}