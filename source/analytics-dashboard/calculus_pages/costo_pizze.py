from config_scripts.aws_secret_loader import get_secret
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime, timedelta

def get_data_pizza(start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"), end_date = datetime.now().strftime("%Y-%m-%d"), pizza = "Margherita"):

    secret = get_secret()
    database = 'api_connector_demo'
    host = 'demo-db.example.internal'
    port = '3306'

    # String connection for mysql
    connection_string = f'mysql+pymysql://{secret["username"]}:{secret["password"]}@{host}:{port}/{database}'

    # SQLAlchemy engine
    engine = create_engine(connection_string)
    query = f"""
        SELECT * FROM {pizza}
        WHERE Data BETWEEN '{start_date}' AND '{end_date}'
    """
    df = pd.read_sql(query, con=engine)

    return df