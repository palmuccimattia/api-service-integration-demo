import json
import requests
import boto3
from botocore.exceptions import ClientError
from datetime import date, timedelta
from typing import Dict, Any, List
import pandas as pd
from sqlalchemy import create_engine

# ------------------------ CONFIG -------------------------------------
API_BASE = "https://api.example-pos-provider.local/sales-data/v1"
AUTH_URL = "https://auth.example-pos-provider.local/login"
PER_PAGE = 20                     # max consentito dall'API

# Credenziali dal file
# secrets = json.loads(Path("secrets_PosProviderAPI.json").read_text(encoding="utf-8"))
# SITE_ID: int = int(secrets["SITE_ID"])

def get_secret_db():

    secret_name = "demo-db-credentials"
    region_name = "eu-west-1"

    # Create a Secrets Manager client
    client = boto3.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])

    # Your code goes here.
    return secret

def get_secret_pos_provider_api():

    secret_name = "pos_provider_api-api"
    region_name = "eu-west-1"

    # Create a Secrets Manager client
    client = boto3.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])

    return secret

secrets = get_secret_pos_provider_api()
SITE_ID: int = int(secrets["SITE_ID"])


# ------------------------ HELPER HTTP --------------------------------

def bearer_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def paged_get(url: str, token: str, **params) -> List[Dict[str, Any]]:
    """Scarica TUTTE le pagine di un endpoint e restituisce una lista di dict."""
    params.update(per_page=PER_PAGE, page=1)
    rows: list = []
    while True:
        resp = requests.get(url, headers=bearer_headers(token), params=params, timeout=45)
        resp.raise_for_status()
        chunk = resp.json()
        rows.extend(chunk["data"])
        meta = chunk.get("pagination") or chunk.get("meta", {})
        last = meta.get("last_page") or 1
        if params["page"] >= last:
            break
        params["page"] += 1
    return rows


def get_token() -> str:

    payload = {
        "username":      secrets["POS_API_USERNAME"],
        "password":      secrets["POS_API_PASSWORD"],
        "client_id":     secrets["POS_API_CLIENT_ID"],
        "client_secret": secrets["POS_API_CLIENT_SECRET"],
        "grant_type":    "password",
    }
    r = requests.post(
        AUTH_URL,
        data=payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=45,
    )
    r.raise_for_status()
    return r.json().get("access_token") or r.headers.get("Authorization", "").split()[-1]

# ------------------------ API WRAPPER --------------------------------

def zreports(token: str, start: str, stop: str) -> list:
    url = f"{API_BASE}/sites/{SITE_ID}/zreports"
    return paged_get(url, token, start_date=start, stop_date=stop)


def zreport_documents(token: str, z_id: int) -> list:
    url = f"{API_BASE}/sites/{SITE_ID}/zreports/{z_id}/documents-raw"
    return paged_get(url, token)


def dt_table(token: str, table: str) -> pd.DataFrame:
    """Scarica una DataTable completa (PLUS, GROUPSâ€¦)"""
    url = f"{API_BASE}/sites/{SITE_ID}/dt/{table}/[]"
    rows = paged_get(url, token)
    return pd.json_normalize(rows)

# ------------------------ DATAFRAME TOOLS ----------------------------

def explode_sells_data(self: pd.DataFrame, plus_raw: pd.DataFrame, groups_raw: pd.DataFrame, taxes_raw: pd.DataFrame) -> pd.DataFrame:
    """Ritorna un dataframe espanso con i dati di body, payments e taxes. In colonna e ben distribuiti sulle righe."""

    new_df = {
        'scontrino_id' : [],
        'zreport_id' : [],
        'date_time': [],
        'totale_scontrino': [],
        'ordine_id': [],
        'reference_id': [],
        'product_descr' : [],
        'group_descr': [],
        'qty' : [],
        'price' : [],
        'unit_price' : [],
        'contanti' : [],
        'pag_elettronico' : [],
        'tax_amount' : []
    }

    for i, row in self.iterrows():
        for product in row["body"]:
            new_df['scontrino_id'].append(int(row["global_counter"]))
            new_df['zreport_id'].append(int(row["zreport_id"]))
            new_df['date_time'].append(str(row['make_at_date']) + ' ' + str(row['make_at_time'])),
            new_df['totale_scontrino'].append(float(row['total_tax_included']))
            new_df['ordine_id'].append(int(product['id']))
            new_df['reference_id'].append(int(product['reference_id']))

            try:
                product_descr = plus_raw[plus_raw['id'] == product['reference_id']]['description'].iloc[0]
            except IndexError:
                product_descr = 'Unknown'

            try:
                group_descr = groups_raw[groups_raw['id'] == (plus_raw[plus_raw['id'] == product['reference_id']]['groups_id'].iloc[0])]['description'].iloc[0]
            except IndexError:
                group_descr = 'Unknown'

            new_df['product_descr'].append(product_descr)
            new_df['group_descr'].append(group_descr)
            new_df['qty'].append(int(product['qty']))
            new_df['price'].append(float(product['price']))
            new_df['unit_price'].append(float(product['unit_price']))

            contanti = 0
            pag_elettronico = 0
            for payment in row['payments']:
                if payment['payment_type'] == 'Contanti':
                    contanti += float(payment['amount'])
                elif payment['payment_type'] == 'PAG.ELETTRONICO':
                    pag_elettronico += float(payment['amount'])

            try:
                contanti = round(contanti * float(product['price']) / float(row['total_tax_included']),2)
            except ZeroDivisionError:
                contanti = 0.00
            try:
                pag_elettronico = round(pag_elettronico * float(product['price']) / float(row['total_tax_included']),2)
            except ZeroDivisionError:
                pag_elettronico = 0.00

            new_df['contanti'].append(contanti)
            new_df['pag_elettronico'].append(pag_elettronico)

            try:
                taxes_amount = taxes_raw[taxes_raw['id'] == product['taxes_id']]['percentage'].iloc[0]
            except IndexError:
                taxes_amount = 0

            new_df['tax_amount'].append(round(int(taxes_amount)/100 * float(product['price']),2))

    new_df = pd.DataFrame(new_df)
    new_df["date_time"] = pd.to_datetime(new_df["date_time"], format="%Y-%m-%d %H:%M:%S")

    return new_df


# ------------------------ MAIN LOGIC ---------------------------------

def lambda_handler(event, context):
    token = get_token()
    stop = date.today()
    start = stop - timedelta(days=1)

    # stop = date(2025, 8, 3)
    # start = date(2025, 8, 1)

    # ----- Zâ€‘REPORT & DOCUMENTI (grezzi) -----
    zr_list = zreports(token, start.isoformat(), stop.isoformat())
    z_ids = [z["z_id"] for z in zr_list]

    documents = [row for z in z_ids for row in zreport_documents(token, z)]
    docs_df = pd.json_normalize(documents)
    # docs_df.to_csv("zreports_documents_raw.csv", sep=";", index=False)

    # ----- DATA TABLES (scaricate UNA sola volta) -----
    plus_raw   = dt_table(token, "plus")
    groups_raw = dt_table(token, "groups")
    # gcat_raw   = dt_table(token, "group-categories") # non serve, non c'Ã¨ niente
    taxes_raw  = dt_table(token, "taxes") # non serve, niente di interessante

    
    # Explode data of body, payments and taxes
    docs_df = explode_sells_data(docs_df, plus_raw, groups_raw, taxes_raw)

    # docs_df.to_csv("zreports_documents_enriched.csv", sep=";", index=False)

    # SCRIVI LA FUNZIONE PER CARICARE I DATI SUL DB
    secret_db = get_secret_db()
    username = secret_db['username']
    password = secret_db['password']
    host = 'demo-db.example.internal'
    port = '3306'
    database = 'api_connector_demo'

    engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")
    docs_df.to_sql(name='Scontrini', con=engine, if_exists='append', index=False)
    

if __name__ == "__main__":
    # default: scarica ieriâ€‘oggi. Imposta days_back a 7 per tutta la settimana ecc.
    lambda_handler({}, {})