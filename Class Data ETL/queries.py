students = """
SELECT DISTINCT
    nm.FIRST_NAME [First Name],
    nm.LAST_NAME [Last Name],
    nm.EMAIL_ADDRESS [Email],
    ISNULL(ai.IDENTIFIER,nm.ID_NUM) [School ID]
FROM
    NAME_MASTER nm
INNER JOIN
    STUDENT_CRS_HIST sch ON nm.id_num = sch.id_num
INNER JOIN
    section_master_v sm ON sch.crs_cde = sm.CRS_CDE
	    AND sch.TRM_CDE = sm.TRM_CDE
		AND sch.YR_CDE = sm.YR_CDE 
LEFT OUTER JOIN
    IDENTITY ai ON nm.id_num = ai.id_num
	    AND IDENTIFIER_TYPE = 'NETWK'
LEFT OUTER JOIN
    FACULTY_LOAD_TABLE flt  ON sch.crs_cde = flt.CRS_CDE
	    AND sch.TRM_CDE = flt.TRM_CDE
		AND sch.YR_CDE = flt.YR_CDE 
WHERE
	DATEADD(DAY, 14, GETDATE())  >= FIRST_BEGIN_DTE
	AND DATEADD(DAY, -14, GETDATE()) <= LAST_END_DTE
    AND sch.DROP_FLAG IS NULL
    AND sch.WITHDRAWAL_DTE IS NULL
    AND flt.LEAD_INSTRCTR_FLG = 'Y'
    AND ai.end_dte IS NULL
ORDER BY LAST_NAME
"""

faculty_and_staff = """
SELECT DISTINCT
    nm.FIRST_NAME [First Name],
    nm.LAST_NAME [Last Name],
    nm.EMAIL_ADDRESS [Email],
    nm.ID_NUM [Employee ID]
FROM
    NAME_MASTER nm
LEFT OUTER JOIN
    FACULTY_MASTER fm ON nm.id_num = fm.id_num
INNER JOIN
    COURSE_LOAD ftl ON nm.id_num = ftl.INSTRCTR_ID_NUM
INNER JOIN
    SECTION_MASTER_V smv ON ftl.YR_CDE = smv.YR_CDE
	    AND ftl.TRM_CDE = smv.TRM_CDE
		AND ftl.CRS_CDE = smv.CRS_CDE
LEFT OUTER JOIN
    IDENTITY ai ON nm.ID_NUM = ai.ID_NUM 
	    AND IDENTIFIER_TYPE = 'NETWK'
		AND ISNUMERIC(ai.IDENTIFIER) = 0
LEFT OUTER JOIN
    TABLE_DETAIL td ON td.COLUMN_NAME = 'INSTRCTR_TYPE'
	    AND td.TABLE_VALUE = fm.INSTRCTR_TYPE   
WHERE
	DATEADD(DAY, 14, GETDATE())  >= FIRST_BEGIN_DTE
	AND DATEADD(DAY, -14, GETDATE()) <= LAST_END_DTE
    AND (ai.END_DTE >= GETDATE() or ai.END_DTE IS NULL)
"""

courses = """
SELECT DISTINCT
	FORMATTED_COURSE_TITLE [Title],
	DEPT_COMP_CDE [Parent Academic Unit],
	ISNULL(FORMATTED_CATALOG_CDE, CONCAT(CRS_COMP1, CRS_COMP2)) [Abbreviation]
FROM 
    SECTION_MASTER_V v
LEFT OUTER JOIN
    FACULTY_LOAD_TABLE flt ON v.CRS_CDE = flt.CRS_CDE
        AND v.YR_CDE = flt.YR_CDE
        AND v.TRM_CDE = flt.TRM_CDE
WHERE 
	DATEADD(DAY, 14, GETDATE())  >= FIRST_BEGIN_DTE
	AND DATEADD(DAY, -14, GETDATE()) <= LAST_END_DTE
"""

terms = """
SELECT
	YR_TRM_DESC [YR_TRM_DESC],
	TRM_BEGIN_DTE [Start Date],
	TRM_END_DTE [End Date]
FROM
	YEAR_TERM_TABLE
WHERE
	GETDATE() >= TRM_BEGIN_DTE
	AND GETDATE() <= TRM_END_DTE
"""

course_sections = """
SELECT 
    RTRIM(CRS_TITLE+isnull(CRS_TITLE_2,'')) [Title],
	RTRIM(isnull(FORMATTED_CATALOG_CDE, CONCAT(CRS_COMP1, CRS_COMP2))) [Course ID],
    RTRIM(v.FORMATTED_CRS_CDE) [Section ID],
    FIRST_BEGIN_DTE [Start Date],
	LAST_END_DTE [End Date],
	ytt.YR_TRM_DESC [Term],
    '' [Cross-List Code],
	CASE
		WHEN X_LISTED_SECTION = 'C' THEN NULL
		ELSE X_LISTED_SECTION
	END [Is Primary Course]
FROM 
    SECTION_MASTER_V v
LEFT OUTER JOIN
	YEAR_TERM_TABLE ytt ON v.YR_CDE = ytt.YR_CDE
		AND v.TRM_CDE = ytt.TRM_CDE
WHERE 
	DATEADD(DAY, 14, GETDATE())  >= FIRST_BEGIN_DTE
	AND DATEADD(DAY, -14, GETDATE()) <= LAST_END_DTE
"""


student_enrollments = """
SELECT
	RTRIM(sm.FORMATTED_CRS_CDE) [Section ID],
	ytt.YR_TRM_DESC [Term],
    nm.EMAIL_ADDRESS [Email]
FROM
    NAME_MASTER nm
INNER JOIN
	STUDENT_CRS_HIST sch ON nm.ID_NUM = sch.ID_NUM
INNER JOIN
	SECTION_MASTER_V sm ON sch.crs_cde = sm.CRS_CDE
		AND sch.TRM_CDE = sm.TRM_CDE
		AND sch.YR_CDE = sm.YR_CDE
LEFT OUTER JOIN
	YEAR_TERM_TABLE ytt ON sm.YR_CDE = ytt.YR_CDE
		AND sm.TRM_CDE = ytt.TRM_CDE
WHERE
	DATEADD(DAY, 14, GETDATE())  >= FIRST_BEGIN_DTE
	AND DATEADD(DAY, -7, GETDATE()) <= LAST_END_DTE
    AND sch.DROP_FLAG IS NULL
    AND sch.WITHDRAWAL_DTE IS NULL
"""

instructor_assignments = """
SELECT 
    RTRIM(v.FORMATTED_CRS_CDE) [Section ID],
    ytt.YR_TRM_DESC [Term],
	CASE
		WHEN nm.ID_NUM = 111150969 THEN 'staff_TBA@greenville.edu'
		ELSE nm.EMAIL_ADDRESS
	END [Email],
	'Primary Instructor' [Role]
FROM 
    SECTION_MASTER_V v
LEFT JOIN
	NAME_MASTER nm ON v.LEAD_INSTRUCTR_ID = nm.ID_NUM
LEFT JOIN
	YEAR_TERM_TABLE ytt ON v.YR_CDE = ytt.YR_CDE
		AND v.TRM_CDE = ytt.TRM_CDE
WHERE
	DATEADD(DAY, 14, GETDATE())  >= FIRST_BEGIN_DTE
	AND DATEADD(DAY, -7, GETDATE()) <= LAST_END_DTE
"""

