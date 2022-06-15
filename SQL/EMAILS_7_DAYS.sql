--------------- NUMBER EMAILS IN THE LAST 7 DAYS
SELECT 
mail_box as 'Mailbox',
COUNT (*) as "Last week's emails"
FROM [dbo].[emails_information]
WHERE is_from_me = '0'
AND folder_name <> 'Sent Items'
AND CAST(date_received as DATE) BETWEEN DATEADD(day, -7, CONVERT(date, GETDATE())) AND  CAST(GETDATE() as DATE)
GROUP BY mail_box;