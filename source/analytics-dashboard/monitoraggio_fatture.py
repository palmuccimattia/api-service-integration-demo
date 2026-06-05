import streamlit as st
import pandas as pd
from config_scripts.aws_secret_loader import get_secret
from sqlalchemy import create_engine
from datetime import date
import os, json, uuid
import numpy as np
import altair as alt
from datetime import datetime

MONITOR_FILE = "monitors_fatture.json"  # file esterno con le preferenze salvate

def _ensure_monitor_file(path=MONITOR_FILE):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"monitors": []}, f, ensure_ascii=False, indent=2)

def load_monitors(path=MONITOR_FILE):
    _ensure_monitor_file(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f).get("monitors", [])

def save_monitors(monitors, path=MONITOR_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"monitors": monitors}, f, ensure_ascii=False, indent=2)

def upsert_monitor(monitors, monitor):
    # aggiorna se esiste per id, altrimenti inserisce
    found = False
    for i, m in enumerate(monitors):
        if m["id"] == monitor["id"]:
            monitors[i] = monitor
            found = True
            break
    if not found:
        monitors.append(monitor)
    save_monitors(monitors)

def delete_monitor(monitors, monitor_id):
    new_list = [m for m in monitors if m["id"] != monitor_id]
    save_monitors(new_list)
    return new_list

@st.cache_data(show_spinner=False)
def get_timeseries_for_keyword(_engine, keyword, start_date, end_date, supplier=None):
    """
    Ritorna serie temporali (Data, prezzo_ponderato, spesa_totale) per i prodotti
    con Nome che contiene 'keyword', nel range selezionato. Se 'supplier' Ã¨ valorizzato,
    filtra anche per fornitore (f.Nome).
    NB: '_engine' Ã¨ ignorato dall'hash della cache.
    """
    # Normalizzo le date in stringhe ISO per evitare ambiguitÃ  lato cache/SQL
    start_iso = pd.to_datetime(start_date).date().isoformat()
    end_iso = pd.to_datetime(end_date).date().isoformat()

    query = """
    SELECT 
        o.Data AS Data,
        o.IdOrdine,
        p.Nome AS Prodotto,
        p.Quantita,
        p.PrezzoUnitario,
        p.PrezzoTotale
    FROM Prodotti p
    JOIN Ordini o     ON o.IdOrdine = p.IdOrdine
    JOIN Fornitori f  ON o.IdFornitore = f.IdFornitore
    WHERE o.Data BETWEEN %(start)s AND %(end)s
      AND p.Nome LIKE %(kw)s
    """
    params = {"start": start_iso, "end": end_iso, "kw": f"%{keyword}%"}

    if supplier:  # filtro opzionale per fornitore
        query += " AND f.Nome = %(supplier)s"
        params["supplier"] = supplier

    df = pd.read_sql(query, con=_engine, params=params)

    if df.empty:
        empty = pd.DataFrame(columns=["Data", "prezzo_ponderato", "spesa_totale", "ordini_giorno"])
        empty = empty.astype({"Data": "datetime64[ns]"})
        empty.attrs["ordini_periodo"] = 0
        empty.attrs["prodotti_unici"] = []
        return empty

    def _agg(g):
        q  = g["Quantita"].fillna(0)
        pt = g["PrezzoTotale"].fillna(0)

        qsum = q.sum()
        # Prezzo medio per data = somma PrezzoTotale / somma QuantitÃ  (sulla stessa data)
        prezzo_medio = (pt.sum() / qsum) if qsum else np.nan

        # numero di ordini distinti in quel giorno:
        ordini_giorno = g["IdOrdine"].nunique()

        return pd.Series({
            "prezzo_ponderato": prezzo_medio,   # mantengo il nome per compatibilitÃ  con la UI
            "spesa_totale": pt.sum(),
            "ordini_giorno": ordini_giorno
        })

    out = (df.groupby("Data", as_index=False)
             .apply(_agg)
             .reset_index(drop=True)
             .sort_values("Data"))

    # metadati utili alla UI
    out.attrs["ordini_periodo"]  = int(df["IdOrdine"].nunique())
    out.attrs["prodotti_unici"]  = sorted(df["Prodotto"].dropna().unique().tolist())
    return out

def _nice_delta_pct(series):
    if len(series) < 2 or np.isnan(series.iloc[-1]) or np.isnan(series.iloc[0]):
        return "n/d"
    start, end = float(series.iloc[0]), float(series.iloc[-1])
    if start == 0:
        return "âˆž" if end != 0 else "0%"
    return f"{(end/start-1):+.1%}"

def _card_color(value, neutral="#222222"):
    try:
        if value is None or np.isnan(value):
            return neutral
        return "#19361A" if value >= 0 else "#3A1717"
    except:
        return neutral


def monitoraggio_fatture():

    # if st.session_state.username != "cliente":
    #     st.error("Accesso negato: non hai i permessi per visualizzare questa pagina.")
    #     st.stop()

    st.markdown("# ðŸ’¼ Monitoraggio Fatture")
    st.markdown("### Ciao Manuela ðŸ‘‹, controlla le fatture che ti sono arrivate...")
    st.markdown("---")

    # DB connection
    secret = get_secret()
    database = 'api_connector_demo'
    host = 'demo-db.example.internal'
    port = '3306'
    connection_string = f'mysql+pymysql://{secret["username"]}:{secret["password"]}@{host}:{port}/{database}'
    engine = create_engine(connection_string)

    # Carica fornitori per il filtro
    fornitori_df = pd.read_sql("SELECT DISTINCT Nome FROM Fornitori ORDER BY Nome", con=engine)
    fornitori = ["Tutti"] + fornitori_df["Nome"].tolist()

    # --- SIDEBAR FILTRI ---
    st.sidebar.header("ðŸ” Filtri")
    search_term = st.sidebar.text_input("Cerca prodotto in fattura", value="")
    selected_fornitore = st.sidebar.selectbox("Fornitore", fornitori)
    start_date = st.sidebar.date_input("Data Inizio", date.today().replace(day=1))
    end_date = st.sidebar.date_input("Data Fine", date.today())

    # Imposta limite iniziale
    if "limit" not in st.session_state:
        st.session_state.limit = 10

    # --- QUERY SQL con filtri e LIMIT dinamico ---
    where_clauses = [
        "o.Data BETWEEN %(start)s AND %(end)s"
    ]
    params = {
        "start": start_date,
        "end": end_date
    }

    if selected_fornitore != "Tutti":
        where_clauses.append("f.Nome = %(fornitore)s")
        params["fornitore"] = selected_fornitore

    # Filtro per NOME PRODOTTO (LIKE) con subquery EXISTS
    if search_term.strip():
        where_clauses.append("""
        EXISTS (
            SELECT 1
            FROM Prodotti p
            WHERE p.IdOrdine = o.IdOrdine
              AND p.Nome LIKE %(search)s
        )
        """)
        params["search"] = f"%{search_term.strip()}%"

    where_sql = " AND ".join(where_clauses)

    query_ordini = f"""
    SELECT 
        o.IdOrdine,
        f.Nome AS Fornitore,
        o.Data,
        o.ImportoTotale
    FROM Ordini o
    JOIN Fornitori f ON o.IdFornitore = f.IdFornitore
    WHERE {where_sql}
    ORDER BY o.Data DESC
    LIMIT {st.session_state.limit};
    """

    ordini_df = pd.read_sql(query_ordini, con=engine, params=params)

    if ordini_df.empty:
        st.info("Nessun ordine trovato con i filtri selezionati.")
        return

    # --- MOSTRA ORDINI ---
    for _, row in ordini_df.iterrows():
        query_prodotti = """
        SELECT 
            Nome AS Prodotto,
            Quantita,
            UnitaMisura,
            PrezzoUnitario,
            PrezzoTotale,
            AliquotaIVA
        FROM Prodotti
        WHERE IdOrdine = %(idordine)s
        """
        prodotti_df = pd.read_sql(query_prodotti, con=engine, params={"idordine": int(row["IdOrdine"])})

        if not prodotti_df.empty:
            prodotti_df['AliquotaIVA'] = prodotti_df['AliquotaIVA'].fillna(22)
            prodotti_df['IVA'] = prodotti_df['PrezzoTotale'] * prodotti_df['AliquotaIVA'] / 100
            imponibile_totale = float(prodotti_df['PrezzoTotale'].sum())
            iva_totale = float(prodotti_df['IVA'].sum())
            aliquota_iva_media = round((iva_totale / imponibile_totale * 100), 2) if imponibile_totale else 0
        else:
            imponibile_totale = 0
            iva_totale = 0
            aliquota_iva_media = 0

        with st.expander(f"{row['Fornitore']} - {row['Data'].strftime('%d/%m/%Y')} - ðŸ’° â‚¬ {row['ImportoTotale']:.2f}"):
            data_str = row['Data'].strftime('%d %b %Y')
            fornitore = row['Fornitore']
            importo = f"{row['ImportoTotale']:.2f}"
            importo_float = float(row['ImportoTotale'])

            if importo_float < 100:
                colore_box = "#04B814"
                background_color = "#DFFFE5"
            elif importo_float < 1000:
                colore_box = "#FF8C00"
                background_color = "#FFF4E3"
            else:
                colore_box = "#C41E28"
                background_color = "#FFD6D6"

            box_html = f"""
            <div style="border: 1px solid #333; border-radius: 12px; padding: 12px 20px; margin-bottom: 10px;
                        background-color: #111111;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 18px; font-weight: bold;">ðŸ“¦ {fornitore}</div>
                    <div style="color: #999999;">ðŸ“… {data_str}</div>
                    <div style="background-color: {background_color}; padding: 6px 10px; border-radius: 8px; font-weight: bold;
                                color: {colore_box};">ðŸ’° â‚¬ {importo}</div>
                </div>
            </div>
            """
            st.markdown(box_html, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            col1.metric("Imponibile", f"â‚¬ {imponibile_totale:.2f}", border=True)
            col2.metric("IVA", f"â‚¬ {iva_totale:.2f} ({aliquota_iva_media}%)", border=True)

            st.markdown("### ðŸ“¦ Prodotti inclusi")
            if not prodotti_df.empty:
                df_show = prodotti_df.copy()
                df_show["PrezzoUnitario"] = df_show["PrezzoUnitario"].map("â‚¬ {:.2f}".format)
                df_show["PrezzoTotale"] = df_show["PrezzoTotale"].map("â‚¬ {:.2f}".format)
                df_show["Quantita"] = df_show["Quantita"].round(2).map("{:.2f}".format)
                df_show["AliquotaIVA"] = df_show["AliquotaIVA"].round(2).map("{:.2f}".format)
                df_show["IVA"] = df_show["IVA"].round(2).map("{:.2f}".format)
                st.table(df_show)
            else:
                st.write("_Nessun prodotto trovato per questo ordine._")

    # --- MOSTRA ALTRI ORDINI (allunga lista) ---
    if len(ordini_df) == st.session_state.limit:
        if st.button("Mostra altri ordini"):
            st.session_state.limit += 10
            st.rerun()

    # === STRUMENTO: Monitor materie prime ===
    st.markdown("---")
    st.subheader("ðŸ§ª Monitor materie prime nelle fatture")

    with st.expander("Crea o gestisci monitor personalizzati", expanded=True):
        monitors = load_monitors()

        # Retro-compatibilitÃ : assicuro il campo 'supplier'
        changed = False
        for m in monitors:
            if "supplier" not in m:
                m["supplier"] = None
                changed = True
        if changed:
            save_monitors(monitors)

        # --- form creazione/aggiornamento monitor ---
        st.markdown("#### âž• Nuovo monitor")
        with st.form("new_monitor_form", clear_on_submit=False):
            colA, colB = st.columns([2,2])
            with colA:
                titolo = st.text_input("Titolo monitor", placeholder="Es. 'Pomodori pelati Mutti'")
            with colB:
                parola = st.text_input("Parola da cercare nel nome prodotto", placeholder="Es. 'pomodoro'")

            # Fornitore per il monitor
            fornitore_monitor = st.selectbox("Fornitore per questo monitor", fornitori, index=0)

            metric = st.selectbox(
                "Cosa vuoi monitorare?",
                ["Prezzo unitario medio (ponderato)", "Spesa totale giornaliera"],
                index=0
            )

            colC, colD = st.columns([1,1])
            with colC:
                colore_grafico = st.color_picker("Colore grafico", value="#4caf50")
            with colD:
                mostra_valori = st.checkbox("Mostra valore puntuale sul grafico", value=False)

            mostra_toast = st.checkbox("Mostra notifiche toast per questo monitor", value=True)
            submitted = st.form_submit_button("ðŸ’¾ Salva monitor")
            if submitted:
                if not titolo.strip() or not parola.strip():
                    st.warning("Compila sia *Titolo monitor* sia *Parola da cercare*.")
                else:
                    new_m = {
                        "id": str(uuid.uuid4()),
                        "title": titolo.strip(),
                        "keyword": parola.strip(),
                        "metric": "prezzo" if metric.startswith("Prezzo") else "spesa",
                        "color": colore_grafico,
                        "show_points": bool(mostra_valori),
                        "toasts": bool(mostra_toast),
                        "supplier": None if fornitore_monitor == "Tutti" else fornitore_monitor,
                        "created_at": datetime.now().isoformat()
                    }
                    upsert_monitor(monitors, new_m)
                    st.success(
                        f"Creato monitor **{new_m['title']}** per â€œ{new_m['keyword']}â€ "
                        + (f"(Fornitore: {new_m['supplier']})" if new_m['supplier'] else "(Tutti i fornitori)")
                    )
                    st.toast(
                        f"âœ… Monitor â€œ{new_m['title']}â€ creato per â€œ{new_m['keyword']}â€ "
                        + (f"â†’ {new_m['supplier']}" if new_m['supplier'] else "â†’ Tutti"),
                        icon="ðŸŽ¯"
                    )
                    monitors = load_monitors()

        if monitors:
            st.markdown("#### ðŸ”­ Monitor salvati")
            # Mostra ogni monitor con card + grafichetto + azioni
            for mon in monitors:
                box = st.container(border=True)
                with box:
                    # layout: titolo | ultimo | Î” | spesa | n_ordini | cestino | toast
                    top = st.columns([4,2,2,2,2,1,2])
                    with top[0]:
                        supplier_label = mon.get("supplier") or "Tutti"
                        st.markdown(
                            f"**{mon['title']}**  \n"
                            f"<small style='color:#aaa'>Parola: â€œ{mon['keyword']}â€ â€¢ Fornitore: {supplier_label}</small>",
                            unsafe_allow_html=True
                        )

                    with top[5]:
                        if st.button("ðŸ—‘ï¸", key=f"del_{mon['id']}"):
                            monitors = delete_monitor(monitors, mon["id"])
                            st.toast(f"Monitor â€œ{mon['title']}â€ rimosso.", icon="ðŸ—‘ï¸")
                            st.rerun()
                    with top[6]:
                        with st.form(f"form_toasts_{mon['id']}", border=False, clear_on_submit=False):
                            toasts_on = st.toggle("Toast", value=mon.get("toasts", True), key=f"toggle_{mon['id']}")
                            save_pref = st.form_submit_button("Salva")
                            if save_pref:
                                mon["toasts"] = bool(toasts_on)
                                upsert_monitor(monitors, mon)
                                st.toast(f"Impostazione toast aggiornata per â€œ{mon['title']}â€ â†’ {'ON' if toasts_on else 'OFF'}", icon="ðŸ”§")

                    # timeseries con filtro fornitore
                    ts = get_timeseries_for_keyword(
                        engine, mon["keyword"], start_date, end_date, supplier=mon.get("supplier")
                    )
                    metric_col = "prezzo_ponderato" if mon["metric"] == "prezzo" else "spesa_totale"
                    label = "Prezzo unitario medio (â‚¬)" if mon["metric"] == "prezzo" else "Spesa totale (â‚¬)"

                    # === Etichette prodotto uniche (senza expander annidato) ===
                    prodotti_unici = ts.attrs.get("prodotti_unici", [])
                    if prodotti_unici:
                        st.caption("ðŸ§¾ Etichette prodotti trovate")
                        chips_html = """
                        <div style="border:1px dashed #333; border-radius:8px; padding:8px; margin-top:4px; background:#0f0f0f;">
                          <div style="max-height:120px; overflow:auto; line-height:1.6;">
                            {items}
                          </div>
                        </div>
                        """.format(items=", ".join(f"<code>{p}</code>" for p in list(set(prodotti_unici))))
                        st.markdown(chips_html, unsafe_allow_html=True)

                    latest = None
                    if not ts.empty and metric_col in ts.columns:
                        latest = float(ts[metric_col].iloc[-1]) if not np.isnan(ts[metric_col].iloc[-1]) else None

                    with top[1]:
                        st.metric("Ultimo valore", "n/d" if latest is None else f"â‚¬ {latest:.2f}")
                    with top[2]:
                        delta_pct = _nice_delta_pct(ts[metric_col]) if not ts.empty else "n/d"
                        st.metric("Î” periodo", delta_pct)
                    with top[3]:
                        tot_ordini = int(ts.attrs.get("ordini_periodo", 0))
                        st.metric("N. ordini (periodo)", f"{tot_ordini}")
                    with top[4]:
                        tot_spesa = ts["spesa_totale"].sum() if "spesa_totale" in ts.columns else 0.0
                        st.metric("Spesa totale (periodo)", f"â‚¬ {tot_spesa:.2f}")

                    # Grafico compatto
                    if ts.empty:
                        st.info("Nessun dato trovato per questo monitor nel periodo selezionato.")
                    else:
                        # âœ… Assicuriamoci che Data sia datetime e le metriche numeriche
                        ts["Data"] = pd.to_datetime(ts["Data"], errors="coerce")
                        ts[metric_col] = pd.to_numeric(ts[metric_col], errors="coerce")

                        base = alt.Chart(ts.dropna(subset=["Data", metric_col])).encode(
                            x=alt.X("Data:T", title="Data")
                        )

                        line = base.mark_line(
                            point=bool(mon.get("show_points", False)),
                            stroke=mon.get("color", "#4caf50")
                        ).encode(
                            y=alt.Y(f"{metric_col}:Q", title=label),
                            tooltip=[
                                alt.Tooltip("Data:T", title="Data"),
                                alt.Tooltip(f"{metric_col}:Q", title=label, format=".2f"),
                                alt.Tooltip("ordini_giorno:Q", title="N. ordini (giorno)")
                            ]
                        )

                        area = base.mark_area(
                            opacity=0.08,
                            color=mon.get("color", "#4caf50")
                        ).encode(
                            y=alt.Y(f"{metric_col}:Q", title=label)
                        )

                        chart = (area + line).properties(height=180)
                        st.altair_chart(chart, use_container_width=True)

                        # === Toast variazioni (rispettano il toggle per monitor) ===
                        if mon.get("toasts", True):
                            diff = ts[metric_col].diff()
                            soglia = 0.01 if mon["metric"] == "prezzo" else 1.0
                            mask = diff.abs() >= soglia

                            if mask.any():
                                recent = ts.loc[mask, ["Data", metric_col]].copy()
                                recent["Delta"] = diff[mask]
                                recent = recent.sort_values("Data").tail(3)

                                for _, r in recent.iterrows():
                                    data_str = pd.to_datetime(r["Data"]).strftime("%d %b %Y")
                                    delta = float(r["Delta"])
                                    valore = float(r[metric_col])
                                    segno = "ðŸ“ˆ" if delta > 0 else "ðŸ“‰"
                                    unit = "â‚¬"
                                    titolo = "Prezzo" if mon["metric"] == "prezzo" else "Spesa"

                                    st.toast(
                                        f"{segno} {mon['title']} â€” {data_str}: {titolo} {delta:+.2f}{unit} (valore: {valore:.2f}{unit})",
                                        icon="ðŸ””"
                                    )

                        # highlight ultime variazioni (soglia diversa per prezzo/spesa)
                        diff = ts[metric_col].diff()
                        if mon["metric"] == "prezzo":
                            mask = diff.abs() >= 0.01
                        else:
                            mask = diff.abs() >= 1.0

                        if mask.any():
                            st.caption("ðŸ”” Variazioni recenti:")
                            for d, v, dv in zip(ts.loc[mask, "Data"], ts.loc[mask, metric_col], diff[mask]):
                                segno = "ðŸ“ˆ" if dv > 0 else "ðŸ“‰"
                                st.write(f"{segno} {pd.to_datetime(d).strftime('%d %b %Y')}: {dv:+.2f} (valore: {v:.2f})")
        else:
            st.info("Non hai ancora nessun monitor salvato. Usa il form qui sopra per crearne uno âœ¨")
