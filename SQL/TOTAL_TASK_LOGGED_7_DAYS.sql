--------------- TOTAL TASK LOGGED LAST WEEK FOR INSURED COMPANIES
SELECT
COUNT(*) AS "Total Task Logged Last Week"
FROM [dbo].[Policy_BrokersDetails] BD
LEFT JOIN [dbo].[Policy_Diary] PD
ON BD.ReportID = PD.ReportID
WHERE BD.CompanyID IN ('1','24','25','30','62','64','72','75','77','90','97','109')
AND CAST(BD.LoggedDate AS DATE) BETWEEN DATEADD(day, -7, CONVERT(date, GETDATE())) AND  CAST(GETDATE() as DATE);