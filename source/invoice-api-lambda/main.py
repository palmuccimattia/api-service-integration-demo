"""
download_invoices.py â€“ AWSÂ Lambda ready (autoâ€range oggi & ieri)
===============================================================

Scarica automaticamente le fatture passive tramite le API TSâ€¯Digital per
lâ€™intervallo *ieri â†’ oggi* (UTC) ogni volta che la Lambda viene invocata.
Se nel payload invii esplicitamente `start_date` / `end_date`, questi valori
overrideranno lâ€™intervallo di default.

Uso locale:
    python download_invoices.py  # scarica intervallo di default (ieriâ€‘oggi)

Uso in AWSÂ Lambda:
    â€¢ carica questo file come `download_invoices.py`
    â€¢ Handler: `download_invoices.lambda_handler`
    â€¢ Layer o zip con la dipendenza `requests`
    â€¢ Environment variables: INVOICE_API_ID, INVOICE_API_SECRET, INVOICE_API_APP_NAME, INVOICE_API_OWNER_ID, â€¦

"""
from __future__ import annotations
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine, text
from botocore.exceptions import ClientError
import json
import boto3
import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
import requests

# ----------------------------------------------------------------------------
# Configurazione funzioni di riempimento database
# ----------------------------------------------------------------------------
def ordine_id_by_uid(engine, uid: str) -> bool:
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM Ordini WHERE uid = :uid"), {"uid": uid}).scalar()
        return count > 0

def get_or_create_fornitore(engine, nome, indirizzo, cap, comune, provincia, nazione, telefono, email):
    with engine.connect() as conn:
        params = {"nome": nome}
        query = text("SELECT IdFornitore FROM Fornitori WHERE Nome = :nome")
        result = conn.execute(query, params).fetchone()

        if result:
            fornitore_id = result[0]

            # Recupera tutti i dati attuali
            current_data = conn.execute(
                text("""
                    SELECT Indirizzo, CAP, Comune, Provincia, Nazione, Telefono, Email 
                    FROM Fornitori WHERE IdFornitore = :id
                """),
                {"id": fornitore_id}
            ).fetchone()

            column_names = ["Indirizzo", "CAP", "Comune", "Provincia", "Nazione", "Telefono", "Email"]
            new_values = [indirizzo, cap, comune, provincia, nazione, telefono, email]

            update_fields = {}
            changes = []

            if current_data is None:
                return fornitore_id

            for col_name, new_val, old_val in zip(column_names, new_values, current_data):
                if str(new_val) != str(old_val):
                    update_fields[col_name] = new_val
                    changes.append(f"{col_name}: {old_val} â†’ {new_val}")

            if update_fields:
                update_fields["id"] = fornitore_id
                update_query = text(f"""
                    UPDATE Fornitori
                    SET {', '.join([f"{k} = :{k}" for k in update_fields if k != 'id'])}
                    WHERE IdFornitore = :id
                """)
                conn.execute(update_query, update_fields)
                conn.commit()

                # Notifica SNS
                sns_client = boto3.client('sns', region_name='eu-west-1')  # Modifica regione se necessario
                SNS_TOPIC_ARN = 'arn:aws:sns:eu-west-1:123456789012:aggiornamenti-fornitori-api_connector_demo'

                sns_client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject=f"Aggiornato fornitore: {nome}",
                    Message="\n".join(changes)
                )

            return fornitore_id

        else:
            # Inserisci nuovo fornitore
            insert = text("""
                INSERT INTO Fornitori (Nome, Indirizzo, CAP, Comune, Provincia, Nazione, Telefono, Email)
                VALUES (:nome, :indirizzo, :cap, :comune, :provincia, :nazione, :telefono, :email)
            """)
            conn.execute(insert, {
                "nome": nome, "indirizzo": indirizzo, "cap": cap, "comune": comune,
                "provincia": provincia, "nazione": nazione, "telefono": telefono, "email": email
            })
            conn.commit()

            # Recupera l'id appena inserito
            result = conn.execute(query, {"nome": nome}).fetchone()
            return result[0]

def insert_ordine(engine, id_fornitore, uid, data, data_ritiro, numero_colli, peso_lordo, importo_totale):
    with engine.connect() as conn:
        insert = text("""
            INSERT INTO Ordini (IdFornitore, uid, Data, DataOraRitiro, NumeroColli, PesoLordo, ImportoTotale)
            VALUES (:id_fornitore, :uid, :data, :ritiro, :colli, :peso, :importo)
        """)
        conn.execute(insert, {
            "id_fornitore": id_fornitore, "uid": uid, "data": data, "ritiro": data_ritiro, "colli": numero_colli,
            "peso": peso_lordo, "importo": importo_totale
        })
        conn.commit()

        # Recupera ultimo ID
        result = conn.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
        return result[0]

def insert_prodotti(engine, prodotti, id_ordine):
    with engine.connect() as conn:
        insert = text("""
            INSERT INTO Prodotti (IdOrdine, Nome, Quantita, UnitaMisura, PrezzoUnitario, PrezzoTotale, AliquotaIVA)
            VALUES (:id_ordine, :nome, :quantita, :unita, :prezzo_unitario, :prezzo_totale, :aliquota)
        """)
        for prod in prodotti:
            conn.execute(insert, {
                "id_ordine": id_ordine,
                "nome": prod['nome'],
                "quantita": prod['quantita'],
                "unita": prod['unita'],
                "prezzo_unitario": prod['prezzo_unitario'],
                "prezzo_totale": prod['prezzo_totale'],
                "aliquota": prod['aliquota']
            })
        conn.commit()

def get_secret_db():

    secret_name = "demo-db-credentials"
    region_name = "eu-west-1"

    # Create a Secrets Manager client
    # session = boto3.session.Session()
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

    secret = get_secret_value_response['SecretString']

    # Your code goes here.
    secret = json.loads(secret)

    return secret


# with open("secrets.json") as f:
#     secrets = json.load(f)

# ---------------------------------------------------------------------------
# Configurazione da variabili dâ€™ambiente (obbligatorio in Lambda)
# ---------------------------------------------------------------------------
# ID: str | None = secrets.get("INVOICE_API_ID")          # id chiave tecnica
# SECRET: str | None = secrets.get("INVOICE_API_SECRET")  # secret chiave tecnica
# APP_NAME: str | None = secrets.get("INVOICE_API_APP_NAME")
# APP_VERSION: str = secrets.get("INVOICE_API_APP_VERSION", "1.0")
# OWNER_ID: str | None = secrets.get("INVOICE_API_OWNER_ID")
# ITEM_ID: str | None = secrets.get("INVOICE_API_ITEM_ID", OWNER_ID)
# ENV: str = secrets.get("INVOICE_API_ENV", "test").lower()  # "test" o "prod"

ID: str | None = os.environ.get("INVOICE_API_ID")          # id chiave tecnica
SECRET: str | None = os.environ.get("INVOICE_API_SECRET")  # secret chiave tecnica
APP_NAME: str | None = os.environ.get("INVOICE_API_APP_NAME")
APP_VERSION: str = os.environ.get("INVOICE_API_APP_VERSION", "1.0")
OWNER_ID: str | None = os.environ.get("INVOICE_API_OWNER_ID")
ITEM_ID: str | None = os.environ.get("INVOICE_API_ITEM_ID", OWNER_ID)
ENV: str = os.environ.get("INVOICE_API_ENV", "test").lower()  # "test" o "prod"

if not all([ID, SECRET, APP_NAME, OWNER_ID]):
    raise RuntimeError("Variabili INVOICE_API_ID, INVOICE_API_SECRET, INVOICE_API_APP_NAME, INVOICE_API_OWNER_ID obbligatorie")

AUTH_BASE = f"https://auth{'-test' if ENV == 'test' else ''}.example-invoice-provider.local/api/v3"
INVOICE_BASE = f"https://api{'-test' if ENV == 'test' else ''}.example-invoice-provider.local/api/v2"

###############################################################################
# Logging                                                                    #
###############################################################################

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

###############################################################################
# Helper                                                                     #
###############################################################################

def _uuid() -> str:  # UUID4 per header tracing
    return str(uuid.uuid4())


def _base_headers() -> Dict[str, str]:
    return {
        "User-Agent": f"{APP_NAME}/{APP_VERSION}",
        "X-App-Name": APP_NAME,
        "X-App-Version": APP_VERSION,
        "X-Request-ID": _uuid(),
        "X-Correlation-ID": _uuid(),
        "X-Item-ID": ITEM_ID or "",
        "X-User-ID": ID,
        "Accept-Language": "it-IT",
    }


def _digest(app_id: str, secret: str, nonce: str) -> str:
    inner = hashlib.sha256(f"{app_id}{secret}".encode()).hexdigest()
    return hashlib.sha256(f"{inner}{nonce}".encode()).hexdigest()

###############################################################################
# 1. Token bearer (nonce â†’ digest)                                           #
###############################################################################

def _token() -> str:
    n = requests.post(
        f"{AUTH_BASE}/nonces",
        headers={**_base_headers(), "Accept": "application/json", "Content-Type": "application/json"},
        json={"id": ID},
        timeout=10,
    )
    n.raise_for_status()
    nonce = n.json()["nonce"]

    r = requests.post(
        f"{AUTH_BASE}/tokens",
        headers={**_base_headers(), "Accept": "application/json", "Content-Type": "application/json"},
        json={"id": ID, "digest": _digest(ID, SECRET, nonce)},
        timeout=10,
    )
    r.raise_for_status()
    js = r.json()
    return js.get("accessToken") or js.get("token") or js.get("access_token")

###############################################################################
# 2. Lista fatture passive                                                   #
###############################################################################
def _extract_invoices(body: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compat utility per gestire formati diversi delle response."""
    # Nuovo formato doc: _embedded.invoiceList
    if isinstance(body.get("_embedded"), dict) and isinstance(body["_embedded"].get("invoiceList"), list):
        return body["_embedded"]["invoiceList"]
    # Vecchio fallback: items
    return body.get("items", [])


def _list_invoices(tok: str, since_ms: int) -> List[Dict[str, Any]]:
    """Ritorna tutte le fatture passive modificate dopo *since_ms* (epochÂ ms)."""

    params: Dict[str, Any] = {
        "ownerId": OWNER_ID,
        "active": "false",           # false = passive, true = active (emesse)
        "lastTimestampFrom": since_ms,
    }

    invoices: List[Dict[str, Any]] = []
    cont: str | None = None

    while True:
        if cont:
            params["continuationToken"] = cont
        resp = requests.get(
            f"{INVOICE_BASE}/invoices",
            params=params,
            headers={"Authorization": f"Bearer {tok}", **_base_headers(), "Accept": "application/hal+json"},
            timeout=30,
        )
        if resp.status_code == 404:
            raise RuntimeError("404 su /v2/invoices â€“ controlla ownerId o permessi Digitalâ€¯Invoice")
        resp.raise_for_status()
        body = resp.json()
        invoices.extend(_extract_invoices(body))
        page = body.get("page", {})
        if page.get("hasNext"):
            cont = page.get("continuationToken")
        else:
            break
    return invoices

###############################################################################
# 3. Download XML singola fattura                                            #
###############################################################################

def _download_xml(tok: str, hub_id: str) -> bytes:
    resp = requests.get(
        f"{INVOICE_BASE}/invoices/{hub_id}/download",
        params={"format": "XML"},
        headers={"Authorization": f"Bearer {tok}", **_base_headers(), "Accept": "application/xml"},
        timeout=30,
    )
    if resp.status_code == 404:
        raise RuntimeError(f"404 on download hubId {hub_id} â€“ verifica ID e permessi")
    resp.raise_for_status()
    return resp.content

###############################################################################
# 4. Funzione pubblica                                                      #
###############################################################################

def download_invoices(start_date: str, end_date: str, engine: Any | None = None) -> List[bytes]:
    start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc, hour=0, minute=0, second=0)
    end_dt = (
        datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc, hour=23, minute=59, second=59)
        if end_date
        else datetime.now(timezone.utc)
    )

    since_ms = int(start_dt.timestamp() * 1000)
    log.info("Intervallo richiesto: %s â†’ %s", start_dt.isoformat(), end_dt.isoformat())

    token = _token()
    metas = _list_invoices(token, since_ms)
    metas = [m for m in metas if m.get("lastTimestamp", 0) <= int(end_dt.timestamp() * 1000)]
    log.info("Fatture trovate: %d", len(metas))

    xmls: List[bytes] = []
    for meta in metas:
        hub_id = meta.get("hubId") or meta.get("id") or meta.get("invoiceId")
        if not hub_id:  # se il campo non esiste logghiamo e continuiamo
            log.warning("Chiave hubId mancante in record: %s", meta)
            continue

        existing = ordine_id_by_uid(engine, hub_id)

        if existing:
            log.info("Fattura %s giaÌ€ scaricata", hub_id)
            continue

        xmls.append([_download_xml(token, hub_id), hub_id])
        log.info("Scaricata %s", hub_id)
    return xmls

###############################################################################
# 5. Lambda handler                                                         #
###############################################################################

def lambda_handler(event, context):
    today = datetime.now().date()
    past_90_days = today - timedelta(days=90)
    start = past_90_days.isoformat()
    end = today.isoformat()

    secret_db = get_secret_db()
    username = secret_db['username']
    password = secret_db['password']
    host = 'demo-db.example.internal'
    port = '3306'
    database = 'api_connector_demo'

    # Stringa di connessione per MySQL
    connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'

    # Crea il motore SQLAlchemy
    engine = create_engine(connection_string)

    # Download fatture
    xmls = download_invoices(start, end, engine)

    if len(xmls) == 0:
        return {'status': 'ok'}

    for xml in reversed(xmls):

        xml, uid = xml
        
        try:
            root = ET.fromstring(xml)
            nome = root.findtext(".//CedentePrestatore/DatiAnagrafici/Anagrafica/Denominazione")
            indirizzo = root.findtext(".//CedentePrestatore/Sede/Indirizzo")
            cap = root.findtext(".//CedentePrestatore/Sede/CAP")
            comune = root.findtext(".//CedentePrestatore/Sede/Comune")
            provincia = root.findtext(".//CedentePrestatore/Sede/Provincia")
            nazione = root.findtext(".//CedentePrestatore/Sede/Nazione")
            telefono = root.findtext(".//Contatti/Telefono")
            email = root.findtext(".//Contatti/Email")

            # Gestione eccezione dimostrativa per normalizzazione anagrafica fornitore
            if email == "supplier@example.com" or indirizzo == "DEMO STREET 1":
                nome = "DEMO SUPPLIER"                  

            id_fornitore = get_or_create_fornitore(engine, nome, indirizzo, cap, comune, provincia, nazione, telefono, email)

            # Estrai dati dellâ€™ordine
            data = root.findtext(".//DatiGeneraliDocumento/Data")
            data_ritiro = root.findtext(".//DataOraRitiro") or None
            numero_colli = root.findtext(".//DatiTrasporto/NumeroColli") or 0
            peso_lordo = root.findtext(".//DatiTrasporto/PesoLordo") or 0.0
            importo_totale = root.findtext(".//DatiGeneraliDocumento/ImportoTotaleDocumento")
            id_ordine = insert_ordine(engine, id_fornitore, uid, data, data_ritiro, numero_colli, peso_lordo,
                        importo_totale)

            prodotti = []
            for dettaglio in root.findall(".//DettaglioLinee"):
                prodotti.append({
                    "nome": dettaglio.findtext("Descrizione"),
                    "quantita": float(dettaglio.findtext("Quantita") or 0),
                    "unita": dettaglio.findtext("UnitaMisura") or "",
                    "prezzo_unitario": float(dettaglio.findtext("PrezzoUnitario") or 0),
                    "prezzo_totale": float(dettaglio.findtext("PrezzoTotale") or 0),
                    "aliquota": float(dettaglio.findtext("AliquotaIVA") or 0)
                })

            insert_prodotti(engine, prodotti, id_ordine)

            print(f"Ordine {id_ordine} inserito con successo")

        except Exception as e:
            import traceback
            print(f"Errore nel file uid={uid}: {e}")
            traceback.print_exc()
            continue

    return {"status": "ok"}

###############################################################################
# Esecuzione CLI                                                           #
###############################################################################

if __name__ == "__main__":

    lambda_handler({}, {})