"""
check_db.py â€“ Controlla lo stato del database ApiConnectorDemo
"""
import boto3
import json
from sqlalchemy import create_engine, text
from botocore.exceptions import ClientError

def get_secret_db():
    client = boto3.client(service_name='secretsmanager', region_name='eu-west-1')
    try:
        resp = client.get_secret_value(SecretId='demo-db-credentials')
    except ClientError as e:
        raise e
    return json.loads(resp['SecretString'])

secret = get_secret_db()
engine = create_engine(
    f"mysql+pymysql://{secret['username']}:{secret['password']}"
    f"@demo-db.example.internal:3306/api_connector_demo"
)

with engine.connect() as conn:
    # Conteggi generali
    n_fornitori = conn.execute(text("SELECT COUNT(*) FROM Fornitori")).scalar()
    n_ordini    = conn.execute(text("SELECT COUNT(*) FROM Ordini")).scalar()
    n_prodotti  = conn.execute(text("SELECT COUNT(*) FROM Prodotti")).scalar()

    print(f"\n{'='*55}")
    print(f"  Fornitori : {n_fornitori}")
    print(f"  Ordini    : {n_ordini}")
    print(f"  Prodotti  : {n_prodotti}")
    print(f"{'='*55}\n")

    # Ultimi 10 ordini inseriti
    rows = conn.execute(text("""
        SELECT o.IdOrdine, f.Nome, o.Data, o.ImportoTotale, o.uid
        FROM Ordini o
        JOIN Fornitori f ON f.IdFornitore = o.IdFornitore
        ORDER BY o.IdOrdine DESC
        LIMIT 10
    """)).fetchall()

    print("Ultimi 10 ordini nel DB (per IdOrdine):")
    print(f"{'ID':<6} {'Fornitore':<28} {'Data':<12} {'Importo':>10}  uid")
    print("-" * 90)
    for r in rows:
        print(f"{r[0]:<6} {str(r[1])[:27]:<28} {str(r[2])[:10]:<12} {str(r[3]):>10}  {r[4]}")

    # Ordini 2026: uid campione
    print("\nCampione ordini con Data >= 2026-01-01 (primi 10):")
    rows_2026 = conn.execute(text("""
        SELECT o.IdOrdine, f.Nome, o.Data, o.uid
        FROM Ordini o
        JOIN Fornitori f ON f.IdFornitore = o.IdFornitore
        WHERE o.Data >= '2026-01-01'
        ORDER BY o.IdOrdine ASC
        LIMIT 10
    """)).fetchall()

    print(f"{'ID':<6} {'Fornitore':<28} {'Data':<12}  uid")
    print("-" * 80)
    for r in rows_2026:
        print(f"{r[0]:<6} {str(r[1])[:27]:<28} {str(r[2])[:10]:<12}  {r[3]}")

    # uid NULL o vuoti tra gli ordini 2026
    null_uid = conn.execute(text("""
        SELECT COUNT(*) FROM Ordini
        WHERE Data >= '2026-01-01' AND (uid IS NULL OR uid = '')
    """)).scalar()
    total_2026 = conn.execute(text("""
        SELECT COUNT(*) FROM Ordini WHERE Data >= '2026-01-01'
    """)).scalar()
    print(f"\nOrdini 2026 totali : {total_2026}")
    print(f"Di cui senza uid   : {null_uid}")
    print(f"Di cui con uid     : {total_2026 - null_uid}")

    # Ordini per mese
    print("\nOrdini per mese (Data fattura, ultimi 12 mesi):")
    monthly = conn.execute(text("""
        SELECT DATE_FORMAT(Data, '%Y-%m') AS mese, COUNT(*) AS n
        FROM Ordini
        WHERE Data >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY mese
        ORDER BY mese DESC
    """)).fetchall()
    for m in monthly:
        bar = "#" * m[1]
        print(f"  {m[0]}  {m[1]:>4}  {bar}")

    print()
