SELECT DISTINCT
	nm.FIRST_NAME AS 'First Name',
	nm.LAST_NAME AS 'Last Name',
	LOWER(nm.EMAIL_ADDRESS) AS 'email',
	'FALSE' AS 'Remote unlock',
	sch.ID_NUM AS 'External ID',
	nmu.PROX_ID AS 'Card ID',
	'SAMPLE' AS 'Card Type',
	'SAMPLE' AS 'Card Format',
	'TRUE' AS 'Use for gateway',
	000000 AS 'Facility code'
FROM 
	dbo.STUDENT_CRS_HIST_V sch
	INNER JOIN NAME_MASTER nm on sch.ID_NUM = nm.ID_NUM
	INNER JOIN NAME_MASTER_UDF nmu on nm.ID_NUM = nmu.ID_NUM
	INNER JOIN BIOGRAPH_MASTER bm on sch.ID_NUM = bm.ID_NUM
	INNER JOIN dbo.year_Term_table ytt on sch.trm_cde = ytt.trm_cde AND sch.yr_cde = ytt.YR_CDE
WHERE
	GETDATE() between dateadd(day,-3,
			(SELECT  min(first_begin_dte)
			FROM  student_crs_hist sch1
				INNER JOIN  section_master sm on sch1.crs_cde = sm.crs_cde AND sch1.yr_cde = sm.yr_cde AND sch1.trm_cde = sm.trm_cde
			WHERE  sch1.ID_NUM = sch.ID_NUM
				AND sch1.TRM_CDE != 'TR'))
		AND
			(SELECT max(last_end_dte)
			FROM  student_crs_hist sch1
				INNER JOIN  section_master sm on sch1.crs_cde = sm.crs_cde AND sch1.yr_cde = sm.yr_cde AND sch1.trm_cde = sm.trm_cde
			WHERE  sch1.ID_NUM = sch.ID_NUM
			AND sch1.TRM_CDE != 'TR')
	AND nmu.PROX_ID IS NOT NULL
	AND bm.EMPLOYEE_OF_COLLEG = 'N'
	--AND nm.ID_NUM = xxxxxxxxx --remove comment for testing single user
ORDER BY [Last Name]
