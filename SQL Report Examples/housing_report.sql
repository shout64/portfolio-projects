SELECT DISTINCT
	gvcas.id_num as 'ID Number',
	nm.FIRST_NAME as 'First Name',
	nm.LAST_NAME as 'Last Name',
	nm.EMAIL_ADDRESS as 'Email Address',
	sdm.CLASS_CDE as 'Class Code',
	sm.LOC_CDE as 'Location',
	csm.SESS_CDE as 'Session Code',
	sar.Room,
	sar.MealPlan as 'Meal Plan',
	(SELECT STRING_AGG(st.SPORTS_CDE_DESCRIPTION, ', ')
		FROM SPORTS_TRACKING_V st
		WHERE st.ID_NUM = gvcas.id_num
		AND (CAST(st.YR_CDE as varchar) + st.TRM_CDE) = csm.SESS_CDE
		GROUP BY st.id_num
	) as Sports
FROM GVC_VW_ACTIVE_STUDENTS gvcas
	LEFT OUTER JOIN Name_Master nm		   ON gvcas.id_num = nm.ID_NUM
	INNER JOIN		STUDENT_DIV_MAST sdm   ON gvcas.id_num = sdm.ID_NUM
	INNER JOIN		STUDENT_MASTER sm	   ON gvcas.id_num = sm.ID_NUM
	LEFT OUTER JOIN SAApplicantRoster sar  ON nm.ID_NUM = sar.StudentIdNum 
	LEFT OUTER JOIN CM_SESSION_MSTR csm    ON csm.GOID = sar.SessionGoid 
	LEFT OUTER JOIN STUD_TERM_SUM_DIV stsd ON gvcas.id_num = stsd.ID_NUM and (CAST(stsd.YR_CDE as varchar) + stsd.TRM_CDE) = csm.SESS_CDE
	LEFT OUTER JOIN SPORTS_TRACKING_V st   ON nm.ID_NUM = st.ID_NUM AND gvcas.id_num = st.ID_NUM AND (CAST(st.YR_CDE as varchar) + st.TRM_CDE) = csm.SESS_CDE
WHERE 
	stsd.DIV_CDE = 'UG'
	AND stsd.transaction_sts <> 'd'
	AND (csm.SESS_CDE = :SessionCode or csm.SESS_CDE IS NULL)
ORDER BY nm.LAST_NAME