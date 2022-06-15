
import plotly.express as px
import pandas as pd
import os
import src.db as db
from dotenv import load_dotenv

load_dotenv()


MAIN_FOLDER = os.getenv('MAIN_FOLDER')
query_path = os.path.join(MAIN_FOLDER, 'SQL\AVERAGE_EMAILS.sql')
image_path = os.path.join(MAIN_FOLDER, 'images')

def get_data(query_path:str)->pd.DataFrame:

    with open(query_path, 'r') as f:
        query = f.read()

    df = db.sql_to_df(query)
    df['no_week'] = df['no_week']-1
    df['mail_box'] = df['mail_box'].apply(lambda x: x.replace('_',' ').capitalize())
    df['date'] = df[['date_year', 'no_week']].apply(lambda x: f'{x[0]}-{x[1]}-0', axis=1)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%W-%w')
    df.sort_values('date', inplace=True)
    return df

def make_export_graph(df):
    fig = px.line(df, x="date", y="average_emails", color='mail_box')

    png_path = os.path.join(image_path, 'avg.png')
    with open(png_path, 'wb') as f:
        f.write(fig.to_image('png', width=900))
    print(png_path)

    html_path = os.path.join(image_path, 'avg.html')
    with open(html_path, 'w') as f:
        f.write(fig.to_html())
    print(html_path)

def main():
    df = get_data(query_path)
    make_export_graph(df)

if __name__ == '__main__':
    main()