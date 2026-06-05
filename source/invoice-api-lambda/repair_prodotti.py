"""
repair_prodotti.py
Riscarica i prodotti per i 257 ordini che li hanno persi a causa del bug IdOrdine=NULL.

Passi:
  1. Elimina i 2.631 Prodotti orfani (IdOrdine=0)
  2. Per ogni ordine senza prodotti, riscarica l'XML da TS Digital
  3. Inserisce i Prodotti con il IdOrdine corretto
"""
from __future__ import annotations
import xml.etree.ElementTree as ET
import hashlib, json, uuid, logging, boto3
from botocore.exceptions import ClientError
from sqlalchemy import create_engine, text
from datetime import datetime, timezone
from typing import Any, Dict, List
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# --- Credenziali TS Digital (locale) ---
with open("secrets.json") as f:
    secrets = json.load(f)

ID       = secrets["INVOICE_API_ID"]
SECRET   = secrets["INVOICE_API_SECRET"]
APP_NAME = secrets["INVOICE_API_APP_NAME"]
APP_VERSION = secrets.get("INVOICE_API_APP_VERSION", "1.0")
OWNER_ID = secrets["INVOICE_API_OWNER_ID"]
ITEM_ID  = secrets.get("INVOICE_API_ITEM_ID", OWNER_ID)
ENV      = secrets.get("INVOICE_API_ENV", "prod").lower()

AUTH_BASE    = f"https://auth{'-test' if ENV == 'test' else ''}.example-invoice-provider.local/api/v3"
INVOICE_BASE = f"https://api{'-test' if ENV == 'test' else ''}.example-invoice-provider.local/api/v2"

# --- DB ---
def get_secret_db():
    client = boto3.client(service_name='secretsmanager', region_name='eu-west-1')
    try:
        resp = client.get_secret_value(SecretId='demo-db-credentials')
    except ClientError as e:
        raise e
    return json.loads(resp['SecretString'])

# --- API helpers ---
def _uuid(): return str(uuid.uuid4())

def _base_headers():
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

def _digest(app_id, secret, nonce):
    inner = hashlib.sha256(f"{app_id}{secret}".encode()).hexdigest()
    return hashlib.sha256(f"{inner}{nonce}".encode()).hexdigest()

def _token():
    n = requests.post(
        f"{AUTH_BASE}/nonces",
        headers={**_base_headers(), "Accept": "application/json", "Content-Type": "application/json"},
        json={"id": ID}, timeout=10,
    )
    n.raise_for_status()
    nonce = n.json()["nonce"]
    r = requests.post(
        f"{AUTH_BASE}/tokens",
        headers={**_base_headers(), "Accept": "application/json", "Content-Type": "application/json"},
        json={"id": ID, "digest": _digest(ID, SECRET, nonce)}, timeout=10,
    )
    r.raise_for_status()
    js = r.json()
    return js.get("accessToken") or js.get("token") or js.get("access_token")

def _download_xml(tok, hub_id):
    resp = requests.get(
        f"{INVOICE_BASE}/invoices/{hub_id}/download",
        params={"format": "XML"},
        headers={"Authorization": f"Bearer {tok}", **_base_headers(), "Accept": "application/xml"},
        timeout=30,
    )
    if resp.status_code == 404:
        raise RuntimeError(f"404 per hubId {hub_id}")
    resp.raise_for_status()
    return resp.content

def insert_prodotti(conn, prodotti, id_ordine):
    insert = text("""
        INSERT INTO Prodotti (IdOrdine, Nome, Quantita, UnitaMisura, PrezzoUnitario, PrezzoTotale, AliquotaIVA)
        VALUES (:id_ordine, :nome, :quantita, :unita, :prezzo_unitario, :prezzo_totale, :aliquota)
    """)
    for prod in prodotti:
        conn.execute(insert, {
            "id_ordine": id_ordine,
            "nome": prod["nome"],
            "quantita": prod["quantita"],
            "unita": prod["unita"],
            "prezzo_unitario": prod["prezzo_unitario"],
            "prezzo_totale": prod["prezzo_totale"],
            "aliquota": prod["aliquota"],
        })
    conn.commit()

# --- MAIN ---
if __name__ == "__main__":
    s = get_secret_db()
    engine = create_engine(
        f"mysql+pymysql://{s['username']}:{s['password']}"
        f"@demo-db.example.internal:3306/api_connector_demo"
    )

    with engine.connect() as conn:
        # STEP 1: elimina prodotti orfani
        count_orfani = conn.execute(text("SELECT COUNT(*) FROM Prodotti WHERE IdOrdine = 0")).scalar()
        log.info(f"Elimino {count_orfani} prodotti orfani (IdOrdine=0)...")
        conn.execute(text("DELETE FROM Prodotti WHERE IdOrdine = 0"))
        conn.commit()
        log.info("Prodotti orfani eliminati.")

        # STEP 2: recupera ordini senza prodotti
        ordini = conn.execute(text("""
            SELECT o.IdOrdine, o.uid, o.Data
            FROM Ordini o
            WHERE o.uid IS NOT NULL AND o.uid != ''
              AND NOT EXISTS (SELECT 1 FROM Prodotti p WHERE p.IdOrdine = o.IdOrdine)
            ORDER BY o.Data
        """)).fetchall()
        log.info(f"Ordini senza prodotti da riparare: {len(ordini)}")

    # STEP 3: scarica XML e reinserisci prodotti
    token = _token()
    token_calls = 1

    ok, skip, err = 0, 0, 0

    with engine.connect() as conn:
        for i, (id_ordine, uid, data) in enumerate(ordini):
            # Rinnova token ogni 50 chiamate
            if i > 0 and i % 50 == 0:
                token = _token()
                token_calls += 1
                log.info(f"Token rinnovato ({token_calls})")

            try:
                xml_bytes = _download_xml(token, uid)
                root = ET.fromstring(xml_bytes)

                prodotti = []
                for det in root.findall(".//DettaglioLinee"):
                    prodotti.append({
                        "nome": det.findtext("Descrizione"),
                        "quantita": float(det.findtext("Quantita") or 0),
                        "unita": det.findtext("UnitaMisura") or "",
                        "prezzo_unitario": float(det.findtext("PrezzoUnitario") or 0),
                        "prezzo_totale": float(det.findtext("PrezzoTotale") or 0),
                        "aliquota": float(det.findtext("AliquotaIVA") or 0),
                    })

                if not prodotti:
                    log.warning(f"Ordine {id_ordine} (uid={uid}): nessun DettaglioLinee nell'XML, salto.")
                    skip += 1
                    continue

                insert_prodotti(conn, prodotti, id_ordine)
                log.info(f"[{i+1}/{len(ordini)}] Ordine {id_ordine} ({str(data)[:10]}): {len(prodotti)} prodotti inseriti.")
                ok += 1

            except Exception as e:
                log.error(f"Ordine {id_ordine} (uid={uid}): ERRORE - {e}")
                err += 1

    log.info(f"\nRiepilogo: OK={ok}  Saltati={skip}  Errori={err}")
