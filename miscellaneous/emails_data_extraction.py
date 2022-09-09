"""emails_project.py

XXXXX
XXXXX
XXXXX
## To be check: folder.unread_count

"""
# https://stackoverflow.com/questions/48655934/how-to-use-exchangelib-to-get-mail-for-non-inbox-folders


import os
import json
from tkinter import EXCEPTION
import pandas as pd
import exchangelib
from exchangelib import Credentials, Account
from exchangelib.ewsdatetime import EWSDateTime, EWSTimeZone
from src.clean_backup import clean_backup
import src.db as db
from dotenv import load_dotenv

load_dotenv()

#credentials for login in the email
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD_EMAIL')
global_credentials = Credentials(EMAIL, PASSWORD)

MAIN_FOLDER = os.getenv('MAIN_FOLDER')

emails_folder = os.path.join(MAIN_FOLDER, 'emails')
backup_folder =  os.path.join(MAIN_FOLDER, 'emails_backup')

#list of inboxes needed to check weekly
MAIL_BOXES = json.loads(os.getenv('MAIL_BOXES'))

def get_account(mail_box:str)->exchangelib.account.Account:
    """Function to return a exchangelib object based in a mail box email

    Args:
        mail_box (str): email of the mail box
    Returns:
        exchangelib.account.Account: Account with the conecction to the mail box
    """    
    return Account(mail_box, credentials=global_credentials, autodiscover=True)

def get_sub_folders(main_folder:exchangelib.folders.known_folders.Inbox)->exchangelib.folders.known_folders.Inbox or exchangelib.folders.known_folders.Messages:
    """Function to get all the subfolders from a main folder

    Args:
        main_folder (exchangelib.folders.known_folders.Inbox): Main folder to be explored

    Yields:
        Iterator[exchangelib.folders.known_folders.Inbox or exchangelib.folders.known_folders.Messages]: Yield tha main folder and all its sub children
    """    
    yield main_folder
    for sub_folder in main_folder.glob('**/*'):
        yield sub_folder

def get_all_emails_in_folder(account, folder:(exchangelib.folders.known_folders.Inbox or exchangelib.folders.known_folders.Messages), after=None)->pd.DataFrame:
    """This function seeks to return a dataframe with all the emails that meet a search criteria

    Args:
        account (exchangelib.account.Account): Account with the conecction to the mail box
        folder (exchangelib.folders.known_folders.Inbox or exchangelib.folders.known_folders.Messages): folder to go through in search of emails
        after (_type_, optional): Without implementing, it is intended that this field be used as a filter and optimize the process.

    Returns:
        pd.DataFrame: Dataframe with all the mails inside the folder
    """    
    folder_id = folder.id
    emails = []
    if not after:
        after = '2022-01-01 00:00:00+00:00'
        after = EWSDateTime.from_string(after)
    else:
        after = EWSDateTime.from_string(after)
    tz = EWSTimeZone.localzone()
    now = EWSDateTime.now()
    print(folder)
    for item in folder.filter(datetime_received__range =(after.astimezone(tz), now.astimezone(tz))).only('conversation_id',
                            'subject', 'message_id', 'datetime_received', 'sender', 'is_from_me'): # This line needs to be fixed using "after" field to filter emails by last date of last email in data base.
        if item:
            email = {}
            email['email_id'] = item.message_id
            email['conversation_id'] = item.conversation_id.id
            email['date_received'] = str(item.datetime_received.astimezone(account.default_timezone))
            email['folder_id'] = folder_id
            email['folder_name'] = folder.name
            email['subject'] = item.subject
            email[ 'is_from_me'] = item.is_from_me
            try:
                email['sender_name'] = item.sender.name
                email['sender_email_address'] = item.sender.email_address
            except:
                pass
            emails.append(email)
    if emails:
        return pd.DataFrame(emails)
    else:
        return pd.DataFrame(columns=['email_id', 'conversation_id', 'date_received', 'folder_id', 'folder_name', 'subject', 'sender_name', 'sender_email_address'])

def get_last_date(account:exchangelib.account.Account)->str:
    """Function to get the last date of each mailbox in the 
    data base

    Args:
        account (exchangelib.account.Account):Account with the conecction to the mail box

    Returns:
        str: Date of the last email in the data base
    """    
    query = """SELECT mail_box, max(date_received) as date
    FROM [dbo].[emails_information]
    GROUP BY mail_box
    """
    df = db.sql_to_df(query)
    df['mail_box'] = df['mail_box'].str.lower()
    mail_box = str(account).lower()
    mail_box_name = mail_box.split('@')[0] + '_' + mail_box.split('@')[1].split('.')[0]
    try:
        after = df[df['mail_box']==mail_box_name]['date'].iloc[0]
        date = pd.Timestamp(after.split('.')[0]) + pd.Timedelta(1, unit='S')
        return date.strftime('%Y-%m-%d %H:%M:%S') + after.split(' ')[-1]
    except:
        return None


def get_all_emails_in_folders(account, folders:list)->pd.DataFrame:
    """Function that goes through a list of folders and searches within each one for emails

    Args:
        folders (list): List of all folders and subfolders to be searched

    Returns:
        pd.DataFrame: DataFrame with all the data inside the list of folders
    """    
    df_list = []
    after = get_last_date(account)
    for folder in folders:
        df_list.append(get_all_emails_in_folder(account, folder, after))

    return pd.concat(df_list, ignore_index=True)

def get_all_folders(account:exchangelib.account.Account)->list:
    """Function that returns the list of folders and subfolders of interest for a mail box

    Args:
        account (exchangelib.account.Account): account or mailbox

    Returns:
        list: List of all folders and subfolders of interest for an account
    """    
    main_folders = [account.inbox,
                    account.root / 'Top of Information Store' / 'Deleted Items',
                    account.root / 'Top of Information Store' / 'Sent Items']
    folders = []
    for folder in main_folders:
        folders.extend( list(get_sub_folders(folder)))

    return folders

def all_emails_in_box(account:exchangelib.account.Account)->pd.DataFrame:
    """Funcion para obtener una tabla de datos con todos los correo dentro de una mailbox

    Args:
        account (exchangelib.account.Account): target Mailbox

    Returns:
        pd.DataFrame: All the emails ("filtered") of a Mailbox
    """    
    folders = get_all_folders(account)
    df = get_all_emails_in_folders(account, folders)
    return df

def save_email_df(path, df:pd.DataFrame, email_box_name:str, verbose:bool=True, date:str=None)->None:
    if date:
        file_path = os.path.join(path, f'{email_box_name}_{date}.csv')
    else:
        file_path = os.path.join(path, f'{email_box_name}.csv')
    df.to_csv(file_path, index=False)
    if verbose:
        print(f'File save in: {file_path}')

def main():
    for mail_box in MAIL_BOXES[:]:
        mail_box_name = mail_box.split('@')[0] + '_' + mail_box.split('@')[1].split('.')[0]
        print('-*-'*20, mail_box_name)
        account = get_account(mail_box)
        df = all_emails_in_box(account).fillna('')
        df['mail_box'] = mail_box_name.lower()
        save_email_df(emails_folder, df, mail_box_name)
        date = pd.Timestamp.now().strftime('%Y%m%d%H%M')
        save_email_df(backup_folder, df, mail_box_name, date=date)
        if not df.empty:
            db.df_to_sql(df)

if __name__ == '__main__':
    main()
    clean_backup(backup_folder)