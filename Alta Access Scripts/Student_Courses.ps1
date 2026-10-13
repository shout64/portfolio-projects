Import-Module ActiveDirectory

$Connection = "Data Source=STUDENTDATABASE;Initial Catalog=PROD;Integrated Security=True;ApplicationIntent=ReadOnly""

# Honors checks the institutional division code to allow access to Laude.
# The SQL Query does an extra check to make sure they get added to the group along with the actual honors courses.

$CourseQuery = Invoke-Sqlcmd -Query @"
SELECT
	sch.IDNUMBER,
	CASE
		WHEN 
			LEFT(sch.INSTITUT_DIV_CDE, 2) IN ('HS', 'HL', 'EN', 'LL', 'ML', 'HU')
			OR dh.MAJOR_1 IN ('TMIN', 'THEL', 'TBIB', 'SWRK')
			OR dh.MAJOR_2 IN ('TMIN', 'THEL', 'TBIB', 'SWRK')
			OR dh.MAJOR_3 IN ('TMIN', 'THEL', 'TBIB', 'SWRK')
		THEN 'Honors'
	ELSE sch.CRS_CDE
	END AS [CRS_CDE],
	sch.INSTITUT_DIV_CDE,
	dh.MAJOR_1,
	BEGIN_DATE,
	END_DATE
FROM
	dbo.STUDENT_COURSES sch
INNER JOIN
	SECTIONS sm ON sch.TRM_CDE = sm.TRM_CDE AND sch.YR_CDE = sm.YR_CDE AND sch.CRS_CDE = sm.CRS_CDE
INNER JOIN
	DEGREE_HISTORY dh ON dh.IDNUMBER = sch.IDNUMBER AND dh.CUR_DEGREE = 'Y'
where
	sch.STATUS IN ('C', 'H')
	AND GETDATE() BETWEEN DATEADD(DAY,-7,first_begin_dte)
	AND DATEADD(DAY,+7,last_end_dte)
"@ -ConnectionString $Connection

# If new automations are needed, add a line to this CourseGroups dictionary with the AD Group name as the Key and the class pattern(s) as the value.

$CourseGroups = @{
    'Course - Science 24-7'    = 'BIO 339*'
    'Course - DM Student'      = 'DMA*'
    'Course - DMA 220'	       = 'DMA 220*'
    'Course - MUL 110'	       = 'MUL 110*'
    'Course - MUL 115'	       = 'MUL 115*'
    'Course - MUS 111'	       = 'MUS 111*'
    'Course - MUS 121' 	       = 'MUS 121*'
    'Course - MUS 122' 	       = 'MUS 122*'
    'Course - MUS 120-220-320' = @('MUS 120*', 'MUS 220*', 'MUS 320*')
    'Course - MUS 222' 	       = 'MUS 222*'
    'Course - MUS 226'         = 'MUS 226*'
    'Course - MUS-DM 227'      = 'MUS 227*'
    'Course - MUS 229'         = 'MUS 229*'
    'Course - MUS 235'         = 'MUS 235*'
    'Course - MUS 260'         = 'MUS 260*'
    'Course - MUS 312'         = 'MUS 312*'
    'Course - MUS 322' 	       = 'MUS 322*'
    'Course - MUS 326' 	       = 'MUS 326*'
    'Course - MUS 327' 	       = 'MUS 327*'
    'Course - MUS 329' 	       = 'MUS 329*'
    'Course - MUS 342' 	       = 'MUS 342*'
    'Course - MUS 360'         = 'MUS 360*'
    'Course - MUS 361-362'     = @('MUS 361*', 'MUS 362*')
    'Course - MUS 419' 	       = 'MUS 419*'
    'Course - MUS 426'         = 'MUS 426*'
    'Course - Honors'	       = @('HONR*', 'PR*', 'Honors')
}

foreach ($Entry in $CourseGroups.GetEnumerator()) {
    $GroupName = $Entry.Key
    $Patterns  = @($Entry.Value)

    Write-Host "Syncing Group: $GroupName" -ForegroundColor Cyan

    # Get current group members
    $CurrentMembers = Get-ADGroupMember -Identity $GroupName | Select-Object -ExpandProperty SamAccountName

    # Find all students matching ANY of the patterns for THIS group
    $TargetStudentIDs = $CourseQuery | Where-Object {
        $row = $_
        $matches = $false
        foreach ($p in $Patterns) {
            if ($row.crs_cde -like $p) { $matches = $true; break }
        }
        $matches -and (Get-Date) -lt [DateTime]::Parse($row.last_end_dte)
    } | Select-Object -ExpandProperty IDNUMBER -Unique

    # Add Missing Students
    $UsersToAdd = $TargetStudentIDs | Where-Object { $_ -notin $CurrentMembers }
    foreach ($User in $UsersToAdd) {
        Add-ADGroupMember -Identity $GroupName -Members $User
        Write-Host " + Added $User" -ForegroundColor Green
    }

    # Remove Invalid Students
    $UsersToRemove = $CurrentMembers | Where-Object { $_ -notin $TargetStudentIDs }
    foreach ($User in $UsersToRemove) {
        Remove-ADGroupMember -Identity $GroupName -Members $User -Confirm:$false
        Write-Host " - Removed $User" -ForegroundColor Yellow
    }
}