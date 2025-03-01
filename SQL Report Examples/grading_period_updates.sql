SELECT * FROM SectionMasterGradePeriod
WHERE GradePeriodDefAppID = 1

-----Add Grade Period to individual course
--INSERT INTO SectionMasterGradePeriod (SectionMasterAppID, GradePeriodDefAppID, GradePeriodOpenDate, GradePeriodCloseDate, GradeScaleDefAppID, CreditTypeDefAppID, GradesEntered, SentOpenMessage, SentCloseMessage, ChangeUser, ChangeJob, ChangeTime)
VALUES (00000, 1, '2024-01-22 00:00:00.000', '2024-02-19 00:00:00.000', 1, 13, 0, 0, 0, 'Devin Chaney', 'ManualGradePeriodUpdate', GETDATE())


--Courses that need 4 Week Check-In added
SELECT distinct sm.APPID
FROM SECTION_MASTER sm
	inner join SectionMasterGradePeriod smgp on sm.APPID = smgp.SectionMasterAppID
WHERE sm.yr_cde = 2023
AND sm.TRM_CDE = 'SP'
AND sm.SUBTERM_CDE = 'SP'
AND smgp.SectionMasterAppID NOT IN (SELECT SectionMasterAppID FROM SectionMasterGradePeriod WHERE GradePeriodDefAppID = 1)




----Fix individual course
--UPDATE SectionMasterGradePeriod
SET GradePeriodCloseDate = '2024-02-19 00:00:00.000'
--SELECT * FROM sectionmastergradeperiod
WHERE sectionmasterappid = 0000000
AND gradeperioddefappid = 1



----Add new grading period to all required Courses
--INSERT INTO SectionMasterGradePeriod (SectionMasterAppID, GradePeriodDefAppID, GradePeriodOpenDate, GradePeriodCloseDate, GradeScaleDefAppID, CreditTypeDefAppID, GradesEntered, SentOpenMessage, SentCloseMessage, ChangeUser, ChangeJob, ChangeTime)
SELECT DISTINCT
    sm.APPID AS SectionMasterAppID,
    1 AS GradePeriodDefAppID,
    '2024-02-01 00:00:00.000' AS GradePeriodOpenDate,
    '2024-02-12 00:00:00.000' AS GradePeriodCloseDate,
    1 AS GradeScaleDefAppID,
    13 AS CreditTypeDefAppID,
    0 AS GradesEntered,
    0 AS SentOpenMessage,
    0 AS SentCloseMessage,
    'Devin Chaney' AS ChangeUser,
    'ManualGradePeriodUpdate' AS ChangeJob,
    GETDATE() AS ChangeTime
FROM SECTION_MASTER sm
    INNER JOIN SectionMasterGradePeriod smgp ON sm.APPID = smgp.SectionMasterAppID
WHERE sm.yr_cde = 2023
    AND sm.TRM_CDE = 'SP'
    AND sm.SUBTERM_CDE = 'SP'
    AND smgp.SectionMasterAppID NOT IN (SELECT SectionMasterAppID FROM SectionMasterGradePeriod WHERE GradePeriodDefAppID = 1)



-----Fix courses with grade period issue
--UPDATE SectionMasterGradePeriod
SET GradePeriodOpenDate = NULL, GradePeriodCloseDate = NULL
--SELECT GradePeriodOpenDate, GradePeriodCloseDate FROM SectionMasterGradePeriod
WHERE GradePeriodDefAppID = 1
AND GradePeriodCloseDate IS NOT NULL

ROLLBACK