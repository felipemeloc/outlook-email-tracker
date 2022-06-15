"""bd.py

This is a custom module to get a DataFrame based on a SQL query

This script needs the installation of the following packages:
* os:
* pyodbc: Create the database connection
* pandas: return a DataFrame object
* warnings: Ignore the warning to have a cleaner terminal
* dotenv:

Contains the following function:
* sql_to_df: Return a DataFrame base on a SQLquery. use:

    import db
    db.sql_to_df(query='YOUR QUERY')

*  df_to_sql: SQL data insertion into the table emails_information table. use:

    import db
    db.df_to_sql(df= YOUR_DATAFRAME)
"""

import os
import pyodbc
import pandas as pd
import warnings
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")

def get_conn(use_live=False)->pyodbc.Connection:
    """Function to make the connection with sql management studio

    Args:
        use_live (bool): Use or not the live database

    Returns:
        pyodbc.Connection: Database connection
    """
    if use_live:
        SERVER = os.getenv('SERVER_LIVE')
        DATABASE = os.getenv('DATABASE_LIVE')
        USER_NAME = os.getenv('USER_NAME_LIVE')
        PASSWORD = os.getenv('PASSWORD_LIVE')
    else:
        SERVER = os.getenv('SERVER')
        DATABASE = os.getenv('DATABASE')
        USER_NAME = os.getenv('USER_NAME')
        PASSWORD = os.getenv('PASSWORD')

    conn_str = ("Driver={SQL Server};"
                f"Server={SERVER};"
                f"Database={DATABASE};"
                f"UID={USER_NAME};"
                f"PWD={PASSWORD};")
    conn = pyodbc.connect(conn_str)
    return conn

def sql_to_df(query:str, use_live:bool=False)->pd.DataFrame:
    """Function to get info from a database base in a Query

    Args:
        query (str): String with the query statement
        use_live (bool): Use or not the live database

    Returns:
        pd.DataFrame: Dataframe with the info result of the query
    """    
    conn = get_conn(use_live)
    return pd.read_sql_query(query, conn)

def df_to_sql(df:pd.DataFrame)->None:
    """Function to make a SQL data insertion into the table emails_information table

    Args:
        df (pd.DataFrame): Dataframe with the information to be injected
    """    
    conn = get_conn()
    cursor = conn.cursor()
    # Insert Dataframe into SQL Server:
    for _, row in df.iterrows():
        cursor.execute("""INSERT INTO [dbo].[emails_information]
        (email_id,
        conversation_id,
        date_received,
        folder_id,
        folder_name,
        subject,
        is_from_me,
        sender_name,
        sender_email_address,
        mail_box)
        values(?,?,?,?,?,?,?,?,?,?)""",
        row.email_id,
        row.conversation_id,
        row.date_received,
        row.folder_id,
        row.folder_name,
        row.subject,
        row.is_from_me,
        row.sender_name,
        row.sender_email_address,
        row.mail_box)
    conn.commit()
    cursor.close()

if __name__ == '__main__':
    query = 'SELECT TOP 1 * FROM [dbo].[reviews_coplus]'
    df = sql_to_df(query)
    print(df)

    query = """SELECT TOP 1 * FROM [dbo].[Lookup_ClaimStatus];"""
    df = sql_to_df(query, use_live=True)