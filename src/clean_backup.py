"""clean_backup.py

This is a custom module to delete all the empty CSV in a folder

This script needs the installation of the following packages:
* os: For path management and file deletion
* pandas: CSV readind and writting

Contains the following function:
* clean_backup: search in a folder all the empty csv and delete them. use:

    from clean_backup import clean_backup
    clean_backup(path)
"""

import os
import pandas as pd

def clean_backup(path:str)->None:
    """Delete all the empty CSV in a folder

    Args:
        path (str): Path to the folder
    """    
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if '.csv' in file:
            if pd.read_csv(file_path).empty:
                os.remove(file_path)
