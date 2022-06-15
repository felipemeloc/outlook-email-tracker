import os
import smtplib
import src.graphs as graphs
import src.db as db
import csv
import pandas as pd
from tabulate import tabulate
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD_EMAIL')
MAIN_FOLDER = os.getenv('MAIN_FOLDER')
image_path = os.path.join(MAIN_FOLDER, 'images')
table_path_1 = os.path.join(MAIN_FOLDER, 'tables/week_emails.csv')
query_path_1 = os.path.join(MAIN_FOLDER, 'SQL/EMAILS_7_DAYS.sql')

table_path_2 = os.path.join(MAIN_FOLDER, 'tables/week_ack.csv')
query_path_2 = os.path.join(MAIN_FOLDER, 'SQL/ACK_LETTER.sql')

table_path_3 = os.path.join(MAIN_FOLDER, 'tables/closed_task.csv')
query_path_3 = os.path.join(MAIN_FOLDER, 'SQL/TOTAL_TASK_CLOSED_7_DAYS.sql')

table_path_4 = os.path.join(MAIN_FOLDER, 'tables/total_task.csv')
query_path_4 = os.path.join(MAIN_FOLDER, 'SQL/TOTAL_TASK_LOGGED_7_DAYS.sql')

emails_path = os.path.join(MAIN_FOLDER, 'tables/receivers.xlsx')


receivers = list(pd.read_excel(emails_path, sheet_name='mails')['email'])

# TEST
# receivers = list(pd.read_excel(emails_path, sheet_name='test')['email'])


def include_image(path, file_name):
    part = MIMEApplication(open(path, "rb").read(), _subtype='png')

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {file_name}",
    )
    return part

def get_data(query_path:str, destiny_path:str, use_live=False)->pd.DataFrame:

    with open(query_path, 'r') as f:
        query = f.read()

    df = db.sql_to_df(query, use_live)
    df.to_csv(destiny_path, index=False)


def main():
    mailserver = smtplib.SMTP("smtp.office365.com", 587) 
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.login(EMAIL, PASSWORD)
    mailserver.ehlo()

    subject = "[Automatic Email]: Mailbox weekly report"

    html = """
    <html><body><p>Hello,</p>
    <p>Below is the number of Emails received by mailbox and 
    the number of completed actions per person for the "Acknowledged Letter" action during the last week (Monday to Sunday).<br> 
    Additionally, you will find attached a graph with the average number of
    emails received per day (download the Html for a better interaction).</p>
    <p>Number of emails received by mailbox during the last week:<p>
    {table1}
    <p></p>
    <p>Number of completed actions per person for the "Acknowledged Letter" action during the last week:<p>
    {table2}
    <p></p>
    <p>Number of task closed during last week for insured companies:<p>
    {table3}
    <p></p>
    <p>Number of task logged during last week for insured companies:<p>
    {table4}
    <p></p>
    <p>Best regards,
    </p>
    <p>Soter Auto</p>
    </body></html>
    """
    with open(table_path_1) as input_file:
        reader = csv.reader(input_file)
        data_1 = list(reader)

    with open(table_path_2) as input_file:
        reader = csv.reader(input_file)
        data_2 = list(reader)

    with open(table_path_3) as input_file:
        reader = csv.reader(input_file)
        data_3 = list(reader)

    with open(table_path_4) as input_file:
        reader = csv.reader(input_file)
        data_4 = list(reader)

    body = tabulate(data_1, headers="firstrow", tablefmt="grid", numalign="left")
    html = html.format(table1=tabulate(data_1, headers="firstrow", tablefmt="html"),
                        table2=tabulate(data_2, headers="firstrow", tablefmt="html"),
                        table3=tabulate(data_3, headers="firstrow", tablefmt="html"),
                        table4=tabulate(data_4, headers="firstrow", tablefmt="html"))
    

    #Build message
    message = MIMEMultipart(
    "alternative", None, [MIMEText(body), MIMEText(html,'html')])
    message["From"] = EMAIL
    message["To"] = ", ".join(receivers)
    message["Subject"] = subject

    for file in os.listdir(image_path):
        full_path = os.path.join(image_path, file)
        message.attach(include_image(full_path, file))

    text = message.as_string()
    
    mailserver.sendmail(from_addr=EMAIL, to_addrs=receivers, msg=text)

    print ('sending email to outlook')

    mailserver.quit()

    

if __name__ == '__main__':
    graphs.main()
    get_data(query_path_1, table_path_1)
    get_data(query_path_2, table_path_2, use_live=True)
    get_data(query_path_3, table_path_3, use_live=True)
    get_data(query_path_4, table_path_4, use_live=True)
    main()