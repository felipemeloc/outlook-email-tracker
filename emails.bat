@echo off
set LOGFILE="C:\Users\FelipeMelo\Soter Professional Services\Soter Data Analysts - Emails_project\outlook-email-tracker\logs\batch.log"
call :LOG > %LOGFILE%
exit /B

:LOG
python "C:\Users\FelipeMelo\Soter Professional Services\Soter Data Analysts - Emails_project\outlook-email-tracker\emails_data_extraction.py" %*
python "C:\Users\FelipeMelo\Soter Professional Services\Soter Data Analysts - Emails_project\outlook-email-tracker\send_emails.py" %*