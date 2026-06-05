from config_scripts.aws_secret_loader import get_secret
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime

def dataset_scontrini(start_date = "2024-01-01", end_date = datetime.now().strftime("%Y-%m-%d")):

    secret = get_secret()
    database = 'api_connector_demo'
    host = 'demo-db.example.internal'
    port = '3306'

    # String connection for mysql
    connection_string = f'mysql+pymysql://{secret["username"]}:{secret["password"]}@{host}:{port}/{database}'

    # SQLAlchemy engine
    engine = create_engine(connection_string)

    # Query
    query = f"""
    SELECT * FROM Scontrini
    WHERE date_time BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY date_time;
    """

    df = pd.read_sql(query, engine)

    return df


def vendite_giornaliere_per_prodotto():

    secret = get_secret()
    database = 'api_connector_demo'
    host = 'demo-db.example.internal'
    port = '3306'

    # String connection for mysql
    connection_string = f'mysql+pymysql://{secret["username"]}:{secret["password"]}@{host}:{port}/{database}'

    # SQLAlchemy engine
    engine = create_engine(connection_string)

    # Query
    query = """
    SELECT
        DATE(date_time)        AS Data,
        product_descr          AS prodotto,
        SUM(price)             AS valore_vendite
    FROM   Scontrini
    GROUP BY
        Data,
        prodotto
    ORDER BY
        Data,
        prodotto;
    """

    df = pd.read_sql(query, engine)

    df = df.pivot(index='Data', columns='prodotto', values='valore_vendite')

    df['Data'] = df.index

    df = df.reset_index(drop=True)

    df = df.fillna(0)

    return df

if __name__ == '__main__':
    vendite_giornaliere_per_prodotto()
