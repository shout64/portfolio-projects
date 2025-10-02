USE [Prod]
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


-- =============================================
-- Author:		dchaney
-- Create date: 2025/08/14
-- Description:	Creates import log in Custom..STUDENT_CHARGES_IMPORT_LOG for student charges imports. The query to pull reports only looks at
--				cleared charges based on the transaction date.

	-- IMPORTANT: If the query is updated and the WHERE clause is changed, you must change it for the INSERT statement AND the SELECT statement.
-- =============================================
CREATE PROCEDURE [dbo].[SP_FINANCIAL_STUDENT_CHARGES_REPORT]

AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

	BEGIN TRANSACTION;

	--Create temp table to log new TRANIDs
	DECLARE @NewTransactionIDs TABLE (TRANID INTEGER);
	
	--Insert data into the import log
	INSERT INTO
        Custom..STUDENT_CHARGES_IMPORT_LOG(TRANID, JOB_TIME, TRANDATE, IMPORT_TIME)
	OUTPUT INSERTED.TRANID INTO @NewTransactionIDs
	SELECT
        TH.APPID,
        TH.JOB_TIME,
        TH.TRANS_DTE,
        GETDATE()
	FROM
        TRANS_HIST TH
	LEFT JOIN
        Custom..STUDENT_CHARGES_IMPORT_LOG IL on TH.APPID = IL.TRANID 
	WHERE
        IL.TRANID IS NULL
		AND TH.TRANS_DTE >= DATEADD(MONTH, -1, GETDATE()) AND TH.TRANS_DTE < GETDATE()
		AND TH.SOURCE_CDE in ('JL', 'CG', 'RC', 'MS', 'TP', 'FA', 'IV', 'VD')
		AND TH.ENCUMB_GL_TRANS_ST in ('C', 'Y')
		AND TH.ID_NUM IS NOT NULL

	--Retrieve data for use in Financial Automation script
	SELECT DISTINCT
        TH.APPID as 'tranid',
        CASE
            WHEN SUBSTRING(TH.ACCT_CDE, 1, 1) = 6 THEN 7
            WHEN SUBSTRING(TH.ACCT_CDE, 1, 1) = 7 THEN 6
            WHEN SUBSTRING(TH.ACCT_CDE, 1, 1) = 2 or SUBSTRING(TH.ACCT_CDE, 1, 1) = 5 THEN 9
            ELSE SUBSTRING(TH.ACCT_CDE, 1, 1)
        END AS subsidiary,
        CONCAT(TH.SOURCE_CDE, TH.GROUP_NUM) AS memo,
        '' AS postingperiod,
        FORMAT(TH.TRANS_DTE, 'MM/dd/yyyy') AS trandate,
        TH.JOB_TIME,
        TH.ACCT_CDE,
        SUBSTRING(TH.ACCT_CDE, 21, 4) AS journalItemLine_account,
        CASE 
            WHEN TH.TRANS_AMT > 0 THEN TH.TRANS_AMT
            ELSE str('')
        END AS journalItemLine_debitAmount,
        CASE 
            WHEN TH.TRANS_AMT < 0 THEN abs(TH.TRANS_AMT)
            ELSE str('')
        END AS journalItemLine_creditAmount,
        TH.TRANS_DESC AS journalItemLine_memo,
        TH.ID_NUM AS journalItemLine_studentID,
        CONCAT(TH.CHG_YR_TRAN_HIST, TH.CHG_TRM_TRAN_HIST) AS journalItemLine_term,
        SUBSTRING(TH.ACCT_CDE, 16, 4) AS journalItemLine_department,
        CASE
            WHEN SUBSTRING(TH.ACCT_CDE, 6, 1) = 1 THEN 5
            WHEN SUBSTRING(TH.ACCT_CDE, 6, 1) = 2 THEN 4
            WHEN SUBSTRING(TH.ACCT_CDE, 6, 1) = 3 THEN 4
            ELSE 5
        END AS journalItemLine_restriction,
        SUBSTRING(TH.ACCT_CDE, 11, 2) AS journalItemLine_functions
	FROM
        TRANS_HIST TH
	LEFT JOIN
        STUDENT_MASTER SM ON TH.ID_NUM = SM.ID_NUM
	LEFT OUTER JOIN
        STUD_TERM_SUM_DIV STS ON TH.ID_NUM = STS.ID_NUM 
            AND CONCAT(TH.CHG_YR_TRAN_HIST, TH.CHG_TRM_TRAN_HIST) = CONCAT(STS.YR_CDE, STS.TRM_CDE)
            AND sts.DIV_CDE <> 'PD'
	LEFT JOIN
        STUD_LIFE_CHGS ON SM.ID_NUM = STUD_LIFE_CHGS.ID_NUM
            AND TH.BILLING_PERIOD_ID = STUD_LIFE_CHGS.BILLING_PERIOD_ID
            AND LEN(ISNULL(STUD_LIFE_CHGS.MEAL_PLAN,''))+ LEN(ISNULL(STUD_LIFE_CHGS.RESID_COMMUTER_STS,'')) + LEN(ISNULL(STUD_LIFE_CHGS.BLDG_CDE,'')) > 0
	INNER JOIN
        @NewTransactionIDs nti on TH.APPID = nti.TRANID
	WHERE
		TH.TRANS_DTE >= DATEADD(MONTH, -1, GETDATE()) AND TH.TRANS_DTE < GETDATE()
		AND TH.SOURCE_CDE in ('JL', 'CG', 'RC', 'MS', 'TP', 'FA', 'IV', 'VD')
		AND TH.ENCUMB_GL_TRANS_ST in ('C', 'Y')
		AND TH.ID_NUM IS NOT NULL
	ORDER BY TH.JOB_TIME



	COMMIT TRANSACTION;
END
GO
