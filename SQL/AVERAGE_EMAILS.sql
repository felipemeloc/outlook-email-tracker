--------------- AVERAGE EMAILS OVER TIME
SELECT 
DATEPART(WEEK, date_received) AS no_week,
DATEPART(YEAR, date_received) AS date_year,
AVG(no_emails) AS average_emails,
mail_box
FROM
(
SELECT 
COUNT (*) AS no_emails,
CAST(date_received as DATE) AS date_received,
mail_box
FROM [dbo].[emails_information]
WHERE is_from_me = '0'
AND folder_name <> 'Sent Items'
GROUP BY 
CAST(date_received as DATE),
mail_box
) as a
GROUP BY
DATEPART(WEEK, date_received),
DATEPART(YEAR, date_received),
mail_box