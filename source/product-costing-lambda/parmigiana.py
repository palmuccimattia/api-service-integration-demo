from aws_secret_loader import get_secret
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime, timedelta, date
from utility import *

def get_data_parmigiana(start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"), end_date = datetime.now().strftime("%Y-%m-%d")):

    # Segna il prezzo di vendita    
    prezzo = 2

    # Database connection
    secret = get_secret()
    database = 'api_connector_demo'
    host = 'demo-db.example.internal'
    port = '3306'

    # String connection for mysql
    connection_string = f'mysql+pymysql://{secret["username"]}:{secret["password"]}@{host}:{port}/{database}'

    # SQLAlchemy engine
    engine = create_engine(connection_string)

    serie_data = pd.date_range(start=start_date, end=end_date, freq='D')

    df = pd.DataFrame(
        {
            "Data": serie_data,
            "Farina": pd.Series([0] * len(serie_data)),
            "Olio": pd.Series([0] * len(serie_data)),
            "Sale": pd.Series([0] * len(serie_data)),
            "Zucchero": pd.Series([0] * len(serie_data)),
            "Lievito": pd.Series([0] * len(serie_data)),
            "Mozzarella": pd.Series([0] * len(serie_data)),
            "Melanzane": pd.Series([0] * len(serie_data)),
            "Pomodorini": pd.Series([0] * len(serie_data)),
            "Salsiccia": pd.Series([0] * len(serie_data)),
            "GranaPadano": pd.Series([0] * len(serie_data)),
            "Olio_d_oliva": pd.Series([0] * len(serie_data)),
            "Totale_CV": pd.Series([0] * len(serie_data)),
            "Totale_CF_Manodopera": pd.Series([0] * len(serie_data)),
            "Totale_CF_Generali": pd.Series([0] * len(serie_data)),
            "CostoPizza": pd.Series([0] * len(serie_data)),
            "PrezzoPizza": pd.Series([prezzo] * len(serie_data)),        
        }
    )

    # Start collect data for the calculation

    # Farina (10 kg di farina per 24 teglie, ogni teglia 10 pezzi)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%%FARINA%%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    pesi_farina = []
    for i, row in df_temp.iterrows():
        if row['UnitaMisura'].upper() == 'KG':
            pesi_farina.append(1)
        else:
            extracted_kg = extract_kg_farina(row['Nome'])
            
            if extracted_kg:
                pesi_farina.append(extracted_kg)
            else:
                extracted_kg = estrai_peso_bedrock(row['Nome'])
                if extracted_kg:
                    pesi_farina.append(extracted_kg)
                else:
                    pesi_farina.append(pesi_farina[-1] if len(pesi_farina) > 0 else 1)

    df_temp["Peso"] = pd.Series(pesi_farina)
    df_temp['Prezzo Farina Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Peso"] / 24
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], 'Farina'] = row['Prezzo Farina Pezzo']

    # Olio di semi (2 lt per 240 pezzi + 50gr a teglia)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%% OLIO %%' AND UPPER(P.Nome) LIKE '%% GIRASOLE %%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    df_temp["Litri"] = pd.Series([extract_lt(row) for row in df_temp["Nome"]])
    df_temp['Prezzo Olio Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Litri"] / 72.84
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], 'Olio'] = row['Prezzo Olio Pezzo']

    # Sale (300 gr per 240 pezzi)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%% SALE %%' AND UPPER(P.Nome) LIKE '%% FINO %%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    pesi_sale = []
    for i, row in df_temp.iterrows():
        valore = extract_kg_sale(row['Nome'])
        if valore:
            pesi_sale.append(valore)
        else:
            try:
                valore = estrai_peso_bedrock(row['Nome'])
                if valore:
                    pesi_sale.append(valore)
                else:
                    pesi_sale.append(pesi_sale[-1] if len(pesi_sale) > 0 else 1)
            except Exception as e:
                pesi_sale.append(pesi_sale[-1] if len(pesi_sale) > 0 else 1)
    df_temp["Peso"] = pd.Series(pesi_sale)
    df_temp['Prezzo Sale Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Peso"] / 800
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], 'Sale'] = row['Prezzo Sale Pezzo']

    # Zucchero (150 gr per 240 pezzi)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%% ZUCCHERO %%' AND UPPER(P.Nome) LIKE '%%DOL760%%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    pesi_zucchero = []
    for i, row in df_temp.iterrows():
        valore = extract_kg_zucchero(row['Nome'])
        if valore:
            pesi_zucchero.append(valore)
        else:
            try:
                valore = estrai_peso_bedrock(row['Nome'])
                if valore:
                    pesi_zucchero.append(valore)
                else:
                    pesi_zucchero.append(pesi_zucchero[-1] if len(pesi_zucchero) > 0 else 1)
            except Exception as e:
                pesi_zucchero.append(pesi_zucchero[-1] if len(pesi_zucchero) > 0 else 1)
    df_temp["Peso"] = pd.Series(pesi_zucchero)
    df_temp['Prezzo Zucchero Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Peso"] / 1600
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], 'Zucchero'] = row['Prezzo Zucchero Pezzo']

    # Lievito (300 gr per 240 pezzi)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%% LIEVITO %%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    df_temp["Peso"] = pd.Series([extract_gr_lievito(row) for row in df_temp["Nome"]])
    df_temp['Prezzo Lievito Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Peso"] / 800000
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], 'Lievito'] = row['Prezzo Lievito Pezzo']

    # Mozzarella (436 gr per 10 pezzi)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%%MOZZ.%%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    pesi_mozzarella = []
    for i, row in df_temp.iterrows():
        if row['UnitaMisura'].upper() == 'KG':
            pesi_mozzarella.append(1)
        else:
            pesi_mozzarella.append(pesi_mozzarella[-1] if len(pesi_mozzarella) > 0 else 1)
    df_temp["Peso"] = pd.Series(pesi_mozzarella)
    df_temp['Prezzo Mozzarella Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Peso"] / 22.9357798
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], 'Mozzarella'] = row['Prezzo Mozzarella Pezzo']

    # Melanzane (326 gr per 10 pezzi)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%%MELANZANA TONDA%%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    pesi_melanzane = []
    for i, row in df_temp.iterrows():
        if row['UnitaMisura'].upper() == 'KG':
            pesi_melanzane.append(1)
        else:
            pesi_melanzane.append(pesi_melanzane[-1] if len(pesi_melanzane) > 0 else 1)
    df_temp["Peso"] = pd.Series(pesi_melanzane)
    df_temp['Prezzo Melanzane Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Peso"] / 30.6748466
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], 'Melanzane'] = row['Prezzo Melanzane Pezzo']

    # Pomodorini (256 gr per 10 pezzi)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%%POMODORO ROSSO GRAPPOLO%%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    pesi_pomodorini = []
    for i, row in df_temp.iterrows():
        if row['UnitaMisura'].upper() == 'KG':
            pesi_pomodorini.append(1)
        else:
            pesi_pomodorini.append(pesi_pomodorini[-1] if len(pesi_pomodorini) > 0 else 1)
    df_temp["Peso"] = pd.Series(pesi_pomodorini)
    df_temp['Prezzo Pomodorini Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Peso"] / 39.0625
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], 'Pomodorini'] = row['Prezzo Pomodorini Pezzo']

    # Salsiccia (180 gr per 10 pezzi)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%%SALSICCIA%%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    pesi_salsiccia = []
    for i, row in df_temp.iterrows():
        if row['UnitaMisura'].upper() == 'KG':
            pesi_salsiccia.append(1)
        else:
            pesi_salsiccia.append(pesi_salsiccia[-1] if len(pesi_salsiccia) > 0 else 1)
    df_temp["Peso"] = pd.Series(pesi_salsiccia)
    df_temp['Prezzo Salsiccia Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Peso"] / 55.5555556
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], 'Salsiccia'] = row['Prezzo Salsiccia Pezzo']

    # Grana Padano (54 gr per 10 pezzi)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%%GRANA PADANO%%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    pesi_grana = []
    for i, row in df_temp.iterrows():
        valore = extract_grana_kg(row['Nome'])
        if valore:
            pesi_grana.append(valore)
        else:
            try:
                valore = estrai_peso_bedrock(row['Nome'])
                if valore:
                    pesi_grana.append(valore)
                else:
                    pesi_grana.append(pesi_grana[-1] if len(pesi_grana) > 0 else 1)
            except Exception as e:
                pesi_grana.append(pesi_grana[-1] if len(pesi_grana) > 0 else 1)
    df_temp["Peso"] = pd.Series(pesi_grana)
    df_temp['Prezzo Grana Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Peso"] / 185.185185
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], 'GranaPadano'] = row['Prezzo Grana Pezzo']
   
    # Olio_d_oliva (20 gr per 10 pezzi)
    query = """
    SELECT P.*, O.Data
    FROM api_connector_demo.Prodotti P
    JOIN api_connector_demo.Ordini O ON P.IdOrdine = O.IdOrdine
    WHERE UPPER(P.Nome) LIKE '%%EXTRA VERGINE%%';
    """
    df_temp = pd.read_sql(query, con=engine)
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])
    pesi_olio = []
    for i, row in df_temp.iterrows():
        valore = extract_olioliva_lt(row['Nome'])
        if valore:
            pesi_olio.append(valore)
        else:
            try:
                valore = estrai_peso_bedrock(row['Nome'])
                if valore:
                    pesi_olio.append(valore)
                else:
                    pesi_olio.append(pesi_olio[-1] if len(pesi_olio) > 0 else 1)
            except Exception as e:
                pesi_olio.append(pesi_olio[-1] if len(pesi_olio) > 0 else 1)
    df_temp["Peso"] = pd.Series(pesi_olio)
    df_temp['Prezzo Olio Pezzo'] = df_temp["PrezzoTotale"] / df_temp["Quantita"] / df_temp["Peso"] / 460.005111
    df_temp.sort_values("Data", inplace=True)

    for index, row in df_temp.iterrows():
        df.loc[df['Data'] >= row['Data'], "Olio_d_oliva"] = row["Prezzo Olio Pezzo"]

    # Totale_CF_Manodopera
    actual_year = datetime.now().year
    query = f"""
    SELECT 
        ma.costo / NULLIF(sc.tot_quantita, 0) AS costo_unitario
    FROM (
        SELECT SUM(costo) AS costo
        FROM ManodoperaAnnua
        WHERE Anno = {actual_year - 1}
    ) ma
    CROSS JOIN (
        SELECT SUM(qty) AS tot_quantita
        FROM (
            SELECT qty
            FROM Scontrini
            WHERE EXTRACT(YEAR FROM date_time) = {actual_year - 1}
            UNION ALL
            SELECT qty
            FROM Scontrini2
            WHERE EXTRACT(YEAR FROM date_time) = {actual_year - 1}
        ) t
    ) sc;
    """
    df_temp = pd.read_sql(query, con=engine)
    df['Totale_CF_Manodopera'] += df_temp['costo_unitario'][0]

    # Totale_CF_Generali
    query = f"""SELECT SUM(o.ImportoTotale) AS TotaleImporti
    FROM Ordini o
    WHERE o.IdFornitore IN (
    3, 4, 6, 11, 12, 14, 15, 18, 20, 21, 25,
    26, 27, 29, 30, 31, 32, 33, 34, 37, 38,
    39, 40, 41, 42, 45, 48, 51, 52, 53, 55,
    56, 59, 62, 65, 66, 67, 68, 69, 72, 73,
    74, 75, 76, 79, 81, 82
    )
    AND YEAR(o.Data) = {actual_year - 1};
    """
    df_temp = pd.read_sql(query, con=engine)
    
    query = f"""SELECT SUM(qty) AS qty_venduto_totale FROM Scontrini
    WHERE YEAR(date_time) = {actual_year - 1};
    """
    df_temp2 = pd.read_sql(query, con=engine)

    if not df_temp2.empty:
        totale_generale = float(df_temp['TotaleImporti'][0])
        qty_totale = float(df_temp2['qty_venduto_totale'][0])

        query = f"""SELECT SUM(qty) AS qty_venduto_totale FROM Scontrini2
        WHERE YEAR(date_time) = {actual_year - 1};
        """
        df_temp3 = pd.read_sql(query, con=engine)

        if not df_temp3.empty:
            qty_totale_2 = float(df_temp3['qty_venduto_totale'][0])
            
            if qty_totale and qty_totale > 0:
                costo_unitario_cf_generale = totale_generale / (qty_totale + qty_totale_2)
                df['Totale_CF_Generali'] = costo_unitario_cf_generale
            else:
                raise ValueError("QuantitÃ  totale margherite vendute non valida.")
        else:
            raise ValueError("Prodotto 'margherita' non trovato nei dati di vendita.")
            
    # Totale_CV
    df['Totale_CV'] = df['Farina'] + df['Olio'] + df['Sale'] + df['Zucchero'] + df['Lievito'] + df['Mozzarella'] + df['Melanzane'] + df['Pomodorini'] + df['Salsiccia'] + df['GranaPadano'] + df["Olio_d_oliva"]

    # Costo margherita
    df['CostoPizza'] = df['Totale_CV'] + df['Totale_CF_Manodopera'] + df['Totale_CF_Generali']

    return df, engine

if __name__ == "__main__":
    get_data_parmigiana("2024-01-01","2025-10-04")