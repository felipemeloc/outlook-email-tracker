--------------- TOTAL FOR ACKNOWLEDGED LETTER
SELECT
SUBSTRING(UP.Email,0,CHARINDEX('@',UP.Email)) AS "Name",
COUNT(*) as 'Acknowledged Letter Actions'
FROM
[dbo].[Policy_History] PH
LEFT JOIN [dbo].[UserProfile] UP
ON PH.ActionedBy = UP.UserId
WHERE PH.StatusID = 9
AND CAST(PH.ActionedDate AS DATE) BETWEEN DATEADD(day, -7, CONVERT(date, GETDATE())) AND  CAST(GETDATE() as DATE)
GROUP BY UP.Email
ORDER BY COUNT(*) DESC