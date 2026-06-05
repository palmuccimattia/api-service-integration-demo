import requests
import json
import os
import re

def estrai_peso_bedrock(nome_prodotto):
    url = "https://bedrock-runtime.eu-west-1.amazonaws.com/model/amazon.nova-lite-v1:0/converse"

    system_prompt = """
    Sei un assistente AI incaricato di estrarre il peso in chilogrammi (kg) dal nome di un prodotto.

    Istruzioni:
    - Estrai il peso indicato nel nome del prodotto.
    - Se il peso Ã¨ espresso in grammi (g), converti in chilogrammi (kg). Esempio: "500g" â†’ "0.5"
    - Non includere l'unitÃ  di misura nellâ€™output. Scrivi solo il numero in formato decimale.
    - Usa sempre il punto come separatore decimale.
    - Se misurata in chilogrammi, il numero che trovi non puÃ² essere tra 0 e 1, se trovi scritto "KG.25" sono il risultato Ã¨ 25. 
    - Limita la risposta a massimo 2 cifre decimali.
    - Se nel nome non Ã¨ presente alcuna informazione di peso, restituisci esattamente: **"null"**
    - Non aggiungere spiegazioni o testo extra. La risposta deve essere solo il numero (es. "1.5") o "null".

    Esempi:
    Input: "Farina di grano tenero 1kg" â†’ Output: "1"  
    Input: "Detersivo liquido 750g" â†’ Output: "0.75"  
    Input: "Zaino scuola Spiderman" â†’ Output: "null"  
    Input: "Riso basmati 5 kg confezione famiglia" â†’ Output: "5"  
    Input: "Fagioli 400 g" â†’ Output: "0.4"

    Ignora numeri che non rappresentano un peso (come litri, quantitÃ , codici, volumi, dimensioni, ecc).
    """

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [{"text":system_prompt + "\n Il prodotto presenta il seguente nome: " + nome_prodotto}]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.environ.get("AWS_BEDROCK_API_KEY"),
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    response = json.loads(response.text)

    try:
        return float(response['output']['message']['content'][0]['text'])
    except ValueError:
        return None 

def extract_kg_farina(r):

    regex_list = [
        re.compile(r'(?i)\b(\d+(?:\.\d+)?)\s*kg\b'),             # es: 25kg, 25 kg
        re.compile(r'(?i)\bkg[\s:.\-]*(\d+(?:\.\d+)?)\b'),       # es: kg.25, kg-25, kg 25
    ]

    kg_value = None
    for regex in regex_list:
        match = regex.search(r)
        if match:
            try:
                value = float(match.group(1))
                if value > 0:
                    kg_value = value
                    break  # Trovato valore valido, stoppa qui
            except ValueError:
                return None  # In caso di errore di conversione, passa alla prossima regex

    if kg_value:
        return kg_value
    else:
        return None

def extract_lt(r):
    match = re.search(r"LT\.?\s*(\d+)", r.upper())
    if match:
        return int(match.group(1))
    return None

def extract_kg_sale(r):
    match = re.search(r"KG\.?\s*(\d+)", r.upper())
    if match:
        return int(match.group(1))
    return None

def extract_carciofi_gr(r):
    match = re.search(r'(\d+)\s*G\b', r.upper())
    if match:
        return float(match.group(1))
    return None

def extract_tonno_gr(r):
    match = re.search(r'(\d+)\s*G\b', r.upper())
    if match:
        return float(match.group(1))
    return None

def extract_grana_kg(r):
    match = re.search(r'(\d+(?:[\.,]\d+)?)\s*KG', r.upper())
    if match:
        return float(match.group(1).replace(',', '.'))
    return None

def extract_alici_gr(r):
    match = re.search(r'(\d+)\s*G\b', r.upper())
    if match:
        return float(match.group(1))
    return None

def extract_tartufo_gr(r):
    match = re.search(r'(\d+)\s*G\b', r.upper())
    if match:
        return float(match.group(1))
    return None

def extract_mistofunghi_gr(r):
    match = re.search(r'(\d+)\s*G\b', r.upper())
    if match:
        return float(match.group(1))
    return None

def extract_olioliva_lt(r):
    match = re.search(r'(\d+(?:[\.,]\d+)?)\s*LT', r.upper())
    if match:
        return float(match.group(1).replace(',', '.'))
    return None

def extract_olive_gr(r):
    match = re.search(r'(\d+)\s*G\b', r.upper())
    if match:
        return float(match.group(1))
    return None

def extract_kg_zucchero(r):
    match = re.search(r"KG\.?\s*(\d+)", r.upper())
    if match:
        return int(match.group(1))
    return None

def extract_gr_lievito(r):
    match = re.search(r"GR\.?\s*(\d+)", r.upper())
    if match:
        return int(match.group(1))
    return None

def extract_pomodori_kg(r):
    match = re.search(r'KG(\d+)', r.upper())
    if match:
        return int(match.group(1))
    return None

def extract_rosmarino_kg(r):
    pattern = re.compile(r"[Kk][Gg]\.?\s*(\d+(?:[.,]\d+)?)")
    match = pattern.search(r)
    if match:
        return float(match.group(1).replace(",", "."))
    return None

def extract_mozzarella_kg(r):
    pattern = re.compile(
        r'(?i)(?:\b(\d+(?:\.\d+)?)\s*kg\.?\b|\bkg\.?\s*(\d+(?:\.\d+)?))'
    )
    match = pattern.search(r)
    kg_value = None
    if match:
        try:
            value = float(match.group(1) or match.group(2))
            if value > 0:
                kg_value = value
        except ValueError:
            return None  # In caso di errore di conversione, passa alla prossima regex

    if kg_value:
        return kg_value
    else:
        return None
    
def extract_wurstel_gr(r):
    match = re.search(r'(\d+)\s*GR', r.upper())
    if match:
        return float(match.group(1))
    return None

def aggrega_quantita_prezzo_zero(df):

    df = df.copy()
    righe_da_eliminare = []

    for idx, row in df.iterrows():
        if row['PrezzoTotale'] == 0:
            stessa_data = df[(df['Data'] == row['Data']) & (df['PrezzoTotale'] > 0)]
            if not stessa_data.empty:
                # Prende la prima riga compatibile
                idx_target = stessa_data.index[0]
                df.at[idx_target, 'Quantita'] += row['Quantita']
                righe_da_eliminare.append(idx)

    return df.drop(index=righe_da_eliminare).reset_index(drop=True)
