import streamlit as st
import pandas as pd
import numpy as np
from calculus_pages.vendite import *
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

def monitoraggio_dati_vendite():

    # Titolo
    st.markdown("## ðŸ“ˆ Monitoraggio vendite")
    st.markdown("---")
    
    # Sidebar â€‘ filtri
    start_date = st.sidebar.date_input("Data Inizio", date.today().replace(day=1))
    end_date = st.sidebar.date_input("Data Fine", date.today())

    # Download scontrini
    df_scontrini = dataset_scontrini(str(start_date), str(end_date))

    # Converti a datetime completo
    df_scontrini["date_time"] = pd.to_datetime(df_scontrini["date_time"], errors='coerce')

    # Creiamo una colonna separata per la sola data (senza ora), utile per aggregazione giornaliera
    df_scontrini["only_date"] = df_scontrini["date_time"].dt.date

    # Usiamo 'only_date' per l'intervallo filtro, ma manteniamo 'date_time' per il resample settimanale
    df_scontrini.set_index("only_date", inplace=True)


    # Filtriamo in base a 'only_date'
    mask = (df_scontrini.index >= start_date) & (df_scontrini.index <= end_date)
    df_scontrini = df_scontrini.loc[mask]

    # Ripristiniamo l'indice normale
    df_scontrini.reset_index(inplace=True)

    # â€‘â€‘ Fatturato Giornaliero
    daily = (
        df_scontrini
        .drop_duplicates(subset = ['zreport_id', 'scontrino_id'], keep='first')[["only_date", "totale_scontrino"]]
        .groupby("only_date", as_index=False)["totale_scontrino"].sum()
        .rename(columns={"only_date": "date", "totale_scontrino": "fatturato"})
    )

    fig_daily = px.line(
        daily,
        x="date",
        y="fatturato",
        markers=True,
        title="Fatturato Giornaliero",
    )
    fig_daily.update_layout(xaxis_title="", yaxis_title="â‚¬")

    # â€‘â€‘ Fatturato Settimanale
    # Serve indice datetime completo
    df_scontrini.set_index("date_time", inplace=True)  # questa colonna Ã¨ datetime64[ns]

    weekly = (
        df_scontrini.drop_duplicates(subset = ['zreport_id', 'scontrino_id'], keep='first')["totale_scontrino"]
        .resample("W-MON")  # settimane chiuse il lunedÃ¬
        .sum()
        .reset_index()
        .assign(week=lambda d: d["date_time"].dt.strftime("W%W %Y"))
        .rename(columns={"totale_scontrino": "fatturato"})
    )

    fig_weekly = px.bar(
        weekly,
        x="week",
        y="fatturato",
        title="Fatturato Settimanale",
    )
    fig_weekly.update_layout(xaxis_title="", yaxis_title="â‚¬")

    # --------------------------------------------------
    # -- Ticket Medio Giornaliero
    # --------------------------------------------------
    # 1 riga per scontrino â†’ eliminiamo i duplicati su scontrino_id
    receipts = (
        df_scontrini.sort_values("date_time")
        .drop_duplicates(subset=["zreport_id", "scontrino_id"], keep="first")
    )

    receipts_daily = (
        receipts.groupby("only_date")
        .agg(total_revenue=("totale_scontrino", "sum"), n_receipts=("scontrino_id", "nunique"))
        .reset_index()
        .assign(ticket_medio=lambda d: d["total_revenue"] / d["n_receipts"])
    )

    receipts_daily["date_time"] = receipts_daily["only_date"]

    receipts_daily = receipts_daily[["date_time", "ticket_medio"]]

    fig_ticket_daily = px.line(
        receipts_daily,
        x="date_time",
        y="ticket_medio",
        markers=True,
        title="Ticket Medio Giornaliero",
    )
    fig_ticket_daily.update_layout(xaxis_title="", yaxis_title="â‚¬")

    # --------------------------------------------------
    # Layout pagina
    # --------------------------------------------------
    st.markdown("### ðŸ“Š Fatturato")

    # --------------------------------------------------
    # KPI cards veloci
    # --------------------------------------------------
    total_revenue = daily["fatturato"].sum()
    avg_daily_revenue = daily["fatturato"].mean()
    period_avg_ticket = receipts["totale_scontrino"].mean()

    colA, colB, colC = st.columns(3)
    colA.metric("Totale periodo selezionato", f"â‚¬ {total_revenue:,.2f}")
    colB.metric("Media giornaliera", f"â‚¬ {avg_daily_revenue:,.2f}")
    colC.metric("Ticket medio", f"â‚¬ {period_avg_ticket:,.2f}")

    st.markdown("---")

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_daily, use_container_width=True)
    col2.plotly_chart(fig_weekly, use_container_width=True)

    st.plotly_chart(fig_ticket_daily, use_container_width=True)

    st.markdown("---")

    # --------------------------------------------------
    # Fine Sezione Fatturato
    # --------------------------------------------------

    # --------------------------------------------------
    # Sezione Fascie Orarie di Vendita
    # --------------------------------------------------    

    # --------------------------------------------------
    # Feature engineering: ora e giorno della settimana
    # --------------------------------------------------
    df_scontrini["hour"] = df_scontrini.index.hour  # 0â€‘23
    # 0=Monday, 6=Sunday â†’ label stringa per ordinamento
    weekday_map = {0: "LunedÃ¬", 1: "MartedÃ¬", 2: "MercoledÃ¬", 3: "GiovedÃ¬", 4: "VenerdÃ¬", 5: "Sabato", 6: "Domenica"}
    df_scontrini["weekday_num"] = df_scontrini.index.weekday

    # Per le heatâ€‘map vogliamo l'ordine naturale lunâ€“dom
    ordered_weekdays = [weekday_map[i] for i in range(7)]
    df_scontrini["weekday"] = df_scontrini["weekday_num"].map(weekday_map)

    # Titolo della pagina
    st.markdown("### â° Distribuzione vendite per fascia oraria")

    # Selettore metrica nel corpo della pagina
    metric = st.radio(
        "ðŸ“Š Seleziona la metrica da analizzare:",
        ["ðŸ’¶ Fatturato (â‚¬)", "ðŸ§¾ Numero scontrini"],
        horizontal=True
    )

    # --------------------------------------------------
    # Aggregazioni
    # --------------------------------------------------
    if metric.startswith("ðŸ’¶"):
        agg = df_scontrini.drop_duplicates(subset=["zreport_id", "scontrino_id"], keep="first")[
            ["weekday", "hour", "only_date", "totale_scontrino"]
        ].groupby(["weekday", "hour", "only_date"], as_index=False)['totale_scontrino'].sum()[
            ['weekday', 'hour', 'totale_scontrino']
        ].groupby(["weekday", "hour"], as_index=False)['totale_scontrino'].mean()
        
        value_col = "totale_scontrino"
        color_label = "Fatturato (â‚¬)"
    else:
        df_receipts = df_scontrini.drop_duplicates(subset=["zreport_id", "scontrino_id"])
        agg = df_receipts[["weekday", "hour", "only_date", "scontrino_id"]].groupby(
            ["weekday", "hour", "only_date"], as_index=False
        )["scontrino_id"].count()[["weekday", "hour", "scontrino_id"]].groupby(
            ["weekday", "hour"], as_index=False
        )["scontrino_id"].mean()

        value_col = "scontrino_id"
        color_label = "# Scontrini"

    # --------------------------------------------------
    # Heatmap preparation
    # --------------------------------------------------

    # Pivot per heatmap: indice = weekday, colonne = hour
    heatmap_df = (
        agg.pivot(index="weekday", columns="hour", values=value_col)
        .reindex(ordered_weekdays)  # mantiene l'ordine lunâ€“dom
        .fillna(0)
    )

    # Ensure all 24 ore (6â€“21) esistano
    for hour in range(6, 22):
        if hour not in heatmap_df.columns:
            heatmap_df[hour] = 0

    # Ordina colonne per ora
    heatmap_df = heatmap_df[sorted(heatmap_df.columns)]
    heatmap_df = heatmap_df.transpose()

    # --------------------------------------------------
    # Grafico Heatmap
    # --------------------------------------------------
    fig = px.imshow(
        heatmap_df,
        labels=dict(x="Giorno della settimana", y="Ora del giorno", color=color_label),
        x=heatmap_df.columns,
        y=heatmap_df.index,
        aspect="auto",
        color_continuous_scale="turbo",
        text_auto=False,
    )
    fig.update_xaxes(side="top")

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # Insight rapidi
    # --------------------------------------------------
    with st.expander("Come interpretare la heatâ€‘map â“"):
        st.markdown(
            """
    * **Colori piÃ¹ intensi** â†’ fasce orarie con maggior {}.
    * Puoi filtrare il periodo (es. solo weekend lunghi o solo mese di agosto) per capire pattern stagionali.
    * Valuta se introdurre promozioni nelle fasce "fredde" o aumentare personale nei momenti caldi.
            """.format("fatturato" if metric.startswith("ðŸ’¶") else "numero di scontrini")
        )

    st.markdown("---")

    # --------------------------------------------------
    # Fine Sezione Fascie Orarie di Vendite
    # --------------------------------------------------

    # --------------------------------------------------
    # Sezione Top / Flop Prodotti
    # --------------------------------------------------

    # --------------------------------------------------
    # Titolo e layout selettori in pagina
    # --------------------------------------------------
    st.markdown("## ðŸ“Š Analisi Top & Flop Prodotti")

    col1, col2 = st.columns([2, 3])

    with col1:
        metric2 = st.selectbox(
            "ðŸ”½ Seleziona la metrica di ordinamento",
            ["QuantitÃ ", "Ricavi (â‚¬)"],
            index=0,
            help="Scegli se ordinare le prodotti per quantitÃ  venduta o ricavi generati"
        )

    with col2:
        N = st.slider(
            "ðŸ“‰ Numero di prodotti da mostrare (Top / Flop)",
            min_value=3,
            max_value=20,
            value=10,
            step=1
        )

    # --------------------------------------------------
    # Assicuriamoci che qty e price esistano
    # --------------------------------------------------
    if "qty" not in df_scontrini.columns:
        df_scontrini["qty"] = 1

    if "price" not in df_scontrini.columns and "unit_price" in df_scontrini.columns:
        df_scontrini["price"] = df_scontrini["unit_price"] * df_scontrini["qty"]

    # --------------------------------------------------
    # Aggregazioni per pizza
    # --------------------------------------------------
    agg = (
        df_scontrini.groupby("product_descr", as_index=False)
        .agg(qty_sum=("qty", "sum"), ricavi=("price", "sum"))
    )

    # Ordinamento in base alla metrica scelta
    if metric2 == "QuantitÃ ":
        agg = agg.sort_values("qty_sum", ascending=False)
        value_col = "qty_sum"
        label_y = "QuantitÃ  venduta"
    else:
        agg = agg.sort_values("ricavi", ascending=False)
        value_col = "ricavi"
        label_y = "Ricavi (â‚¬)"

    # --------------------------------------------------
    # Top N e Flop N
    # --------------------------------------------------
    agg_top = agg.head(N)
    agg_flop = agg.tail(N).sort_values(value_col)  # ordina crescente per flop

    # --------------------------------------------------
    # Grafici
    # --------------------------------------------------
    fig_top = px.bar(
        agg_top,
        x="product_descr",
        y=value_col,
        title=f"ðŸ† Top {N} prodotti per {metric2.lower()}",
        text=value_col,
    )
    fig_top.update_layout(xaxis_title="", yaxis_title=label_y)
    fig_top.update_traces(texttemplate="%{text:.1f}")

    fig_flop = px.bar(
        agg_flop,
        x="product_descr",
        y=value_col,
        title=f"ðŸ’” Flop {N} prodotti per {metric2.lower()}",
        text=value_col,
    )
    fig_flop.update_layout(xaxis_title="", yaxis_title=label_y)
    fig_flop.update_traces(texttemplate="%{text:.1f}")

    # --------------------------------------------------
    # Layout pagina con grafici
    # --------------------------------------------------
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_top, use_container_width=True)
    col2.plotly_chart(fig_flop, use_container_width=True)

    # --------------------------------------------------
    # Insight tabellare opzionale
    # --------------------------------------------------
    with st.expander("ðŸ“‹ Tabella completa dei dati aggregati"):
        st.dataframe(
            agg.rename(columns={"qty_sum": "QuantitÃ ", "ricavi": "Ricavi (â‚¬)"}),
            use_container_width=True
        )

    st.markdown("---")

    # --------------------------------------------------
    # Fine Sezione Top / Flop Prodotti
    # --------------------------------------------------

    # --------------------------------------------------
    # Sezione Mix Pagamenti
    # --------------------------------------------------
    # Titolo iniziale
    st.markdown("### ðŸ’³ Analisi mix pagamento")

   # Selezione tipo grafico elegante e pulita
    chart_type = st.radio(
        label="Scegli il tipo di visualizzazione",
        options=["ðŸ¥§ Torta (periodo)", "ðŸ“Š Barre impilate (trend)"],
        horizontal=True,
        index=0
    )

    # ------------------------------
    # Selezione della granularitÃ  (se serve)
    # ------------------------------
    if chart_type == "ðŸ“Š Barre impilate (trend)":
        freq = st.selectbox("ðŸ“… Seleziona la granularitÃ ", ["Giorno", "Settimana", "Mese"], index=0)
        freq_map = {"Giorno": "D", "Settimana": "W", "Mese": "M"}
    else:
        freq = None

    # Copia dei dati
    filtered = df_scontrini.copy()

    # Verifica colonne pagamento
    if "contanti" not in filtered.columns:
        filtered["contanti"] = 0.0
    if "pag_elettronico" not in filtered.columns:
        filtered["pag_elettronico"] = 0.0

    # --------------------------------------------------
    # Grafici
    # --------------------------------------------------
    if chart_type == "ðŸ¥§ Torta (periodo)":
        cash = filtered["contanti"].sum()
        electronic = filtered["pag_elettronico"].sum()
        pie_df = pd.DataFrame({"Metodo": ["Contanti", "Elettronico"], "Importo": [cash, electronic]})
        fig = px.pie(pie_df, values="Importo", names="Metodo", title="Mix pagamento â€“ totale periodo")
        st.plotly_chart(fig, use_container_width=True)

        # KPI rapidi
        st.markdown("### Breakdown")
        col1, col2 = st.columns(2)
        col1.metric("Contanti", f"â‚¬ {cash:,.2f}", help="Somma importi in contanti")
        col2.metric("Elettronico", f"â‚¬ {electronic:,.2f}", help="Somma importi con pagamenti elettronici")

    else:
        # barre impilate per trend
        if freq is not None:
            filtered.reset_index(drop=False, inplace=True)
            filtered["date_time"] = pd.to_datetime(filtered["date_time"])
            resampled = (
                filtered[["date_time", "contanti", "pag_elettronico"]]
                .set_index("date_time")
                .resample(freq_map[freq])
                .sum()
                .reset_index()
            )
            resampled["periodo"] = resampled["date_time"].dt.date
            resampled = resampled.rename(columns={"contanti": "Contanti", "pag_elettronico": "Elettronico"})

            fig = px.bar(
                resampled,
                x="periodo",
                y=["Contanti", "Elettronico"],
                title=f"Trend mix pagamento â€“ {freq.lower()}",
                labels={"value": "Importo (â‚¬)", "variable": "Metodo"},
                text_auto=".2s",
            )
            fig.update_layout(xaxis_title="Periodo", yaxis_title="â‚¬", barmode="stack")
            st.plotly_chart(fig, use_container_width=True)

            # Ratio medio su periodo selezionato
            tot_cash = resampled["Contanti"].sum()
            tot_elec = resampled["Elettronico"].sum()
            share_cash = tot_cash / (tot_cash + tot_elec) * 100 if (tot_cash + tot_elec) else 0
            st.markdown(f"**Quota contanti**: {share_cash:.1f}%")

    # --------------------------------------------------
    # Suggerimenti
    # --------------------------------------------------
    with st.expander("PerchÃ© monitorare il mix pagamento? â“"):
        st.markdown(
            """
    * **Costi di commissione**: ridurre i contanti puÃ² abbassare il rischio di errore ma aumenta le fee bancarie.
    * **VelocitÃ  di servizio**: osserva se l'introduzione di POS contactless ha realmente ridotto i tempi in cassa.
    * **Focus marketing**: se una promo online (es. app di delivery) spinge l'elettronico, attrezzati con posazioni POS extra.
    """
        )

    st.markdown("---")

    # --------------------------------------------------
    # Fine file
    # --------------------------------------------------

    # --------------------------------------------------
    # Sezione Anomalie di Vendite
    # --------------------------------------------------

    # Titolo della pagina
    st.markdown("### ðŸ” Rilevazione anomalie di vendite")

    # Slider per la soglia sigma
    sigma = st.slider("Soglia sigma (k)", min_value=1.0, max_value=4.0, value=3.0, step=0.5)

    # Copia e preparazione dati
    df_period = df_scontrini.copy()
    df_period.reset_index(inplace=True)

    # Raggruppamento per giorno
    daily = (
        df_period.groupby(df_period.date_time.dt.date)["totale_scontrino"].sum()
        .rename("fatturato")
        .reset_index()
        .rename(columns={"date_time": "date"})
    )

    # Verifica presenza dati
    if daily.empty:
        st.warning("Nessun dato nel periodo selezionato")
        st.stop()

    # Calcolo statistiche
    mean_rev = daily["fatturato"].mean()
    std_rev = daily["fatturato"].std(ddof=0)

    upper_lim = mean_rev + sigma * std_rev
    lower_lim = mean_rev - sigma * std_rev

    # Classificazione anomalie
    daily["anomaly"] = daily["fatturato"].apply(
        lambda x: "high" if x > upper_lim else ("low" if x < lower_lim else "normal")
    )

    # Creazione grafico
    fig = go.Figure()

    # Linea fatturato
    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["fatturato"],
        mode="lines+markers",
        name="Fatturato"
    ))

    # Linee soglia Â±sigma
    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=[upper_lim] * len(daily),
        mode="lines",
        name=f"Upper {sigma}Ïƒ",
        line=dict(dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=[lower_lim] * len(daily),
        mode="lines",
        name=f"Lower {sigma}Ïƒ",
        line=dict(dash="dash")
    ))

    # Punti anomali
    anomalies = daily[daily["anomaly"] != "normal"]
    fig.add_trace(go.Scatter(
        x=anomalies["date"],
        y=anomalies["fatturato"],
        mode="markers",
        name="Anomalia",
        marker=dict(size=10, color="red", symbol="circle-open")
    ))

    fig.update_layout(
        title="Calo / Picco anomalo di vendite",
        xaxis_title="Data",
        yaxis_title="â‚¬"
    )

    # Mostra grafico
    st.plotly_chart(fig, use_container_width=True)

    # Dettaglio anomalie
    if not anomalies.empty:
        with st.expander("Dettaglio giorni anomali"):
            st.dataframe(
                anomalies[["date", "fatturato", "anomaly"]].rename(columns={
                    "date": "Data",
                    "fatturato": "Fatturato (â‚¬)",
                    "anomaly": "Tipo"
                }),
                use_container_width=True
            )
    else:
        st.info(f"Nessuna anomalia rilevata con soglia Â±{sigma}Ïƒ nel periodo.")

    # Sezione "Come funziona"
    with st.expander("Come funziona? â“"):
        st.markdown(
            f"""
    * Calcolo la **media** e la **deviazione standard** del fatturato giornaliero nel periodo selezionato.
    * Segno come **anomalia** ogni giorno sopra **media + {sigma} Ã— Ïƒ** (picco) o sotto **media âˆ’ {sigma} Ã— Ïƒ** (calo).
    * Modifica il valore di *sigma* per rendere il rilevamento piÃ¹ o meno severo.
            """
        )

    st.markdown("---")
    # --------------------------------------------------
    # Fine Sezione Anomalie
    # --------------------------------------------------

    # --------------------------------------------------
    # Creazione cestini (basket)
    # --------------------------------------------------

    # Ogni scontrino unico: (zreport_id, scontrino_id)
    receipt_groups = df_scontrini.groupby(["zreport_id", "scontrino_id"])["product_descr"].apply(set).reset_index(name="items")

    # --------------------------------------------------
    # Parametri analisi â€“ fissi
    # --------------------------------------------------
    min_support = 0.01
    min_conf = 0.3

    # --------------------------------------------------
    # Oneâ€‘hot encoding dei cestini
    # --------------------------------------------------
    from sklearn.preprocessing import MultiLabelBinarizer
    mlb = MultiLabelBinarizer(sparse_output=True)
    X = mlb.fit_transform(receipt_groups["items"])
    basket_df = pd.DataFrame.sparse.from_spmatrix(X, columns=mlb.classes_)

    # --------------------------------------------------
    # Frequent Itemset (Apriori)
    # --------------------------------------------------
    try:
        from mlxtend.frequent_patterns import apriori, association_rules
    except ModuleNotFoundError:
        st.error("âš ï¸ Il pacchetto mlxtend non Ã¨ installato. Esegui `pip install mlxtend` e ricarica la pagina.")
        st.stop()

    # -- 1. Calcolo FULL itemset (serve a association_rules che richiede i singoli item)
    frequent_itemsets_full = apriori(basket_df, min_support=min_support, use_colnames=True)

    # -- 2. Regole su FULL itemset
    rules = association_rules(frequent_itemsets_full, metric="confidence", min_threshold=min_conf)

    # filtra eventuali anomalie/duplicati
    rules = rules[(rules["antecedents"].apply(len) > 0) & (rules["consequents"].apply(len) > 0)]

    # -- 3. Per la visualizzazione itemset, rimuoviamo i monoâ€‘item
    frequent_itemsets = frequent_itemsets_full[frequent_itemsets_full["itemsets"].apply(lambda s: len(s) > 1)]
    frequent_itemsets = frequent_itemsets.sort_values("support", ascending=False)

    rules = rules.sort_values("lift", ascending=False)

    # --------------------------------------------------
    # Layout Streamlit â€“ Titolo e slider parametri
    # --------------------------------------------------
    st.title("ðŸ›’ Basket / Frequent Itemset Analysis")

    # Spostato lo slider nel corpo della pagina
    N_top = st.slider("Top N prodotti per heatmap", 5, 20, value=10)

    # --------------------------------------------------
    # Heatâ€‘map coâ€‘occorrenza (senza diagonale)
    # --------------------------------------------------
    co_matrix = basket_df.astype(int).T.dot(basket_df.astype(int)).astype(float)
    np.fill_diagonal(co_matrix.values, np.nan)  # rimuove selfâ€‘combo visivamente

    support_series = basket_df.mean(axis=0).sort_values(ascending=False)

    top_products = support_series.head(N_top).index
    top_matrix   = co_matrix.loc[top_products, top_products]

    fig_heat = px.imshow(
        top_matrix,
        labels=dict(x="Prodotto", y="Prodotto", color="Ordini insieme"),
        x=top_products,
        y=top_products,
        text_auto=False,
        aspect="auto",
    )
    fig_heat.update_layout(title=f"Coâ€‘occorrenza Top {N_top} prodotti (selfâ€‘combo esclusi)")

    # --------------------------------------------------
    # Sezione Heatmap e Tabelle
    # --------------------------------------------------
    st.subheader("Heatâ€‘map coâ€‘occorrenza")
    st.plotly_chart(fig_heat, use_container_width=True)

    with st.expander("Frequent itemset (â‰¥ min_support, dimensione > 1)"):
        st.dataframe(
            frequent_itemsets
            .assign(**{"% support": lambda d: (d["support"] * 100).round(2)})
            .drop(columns=["support"])
            .rename(columns={"itemsets": "Itemset"}),
            use_container_width=True,
        )

    with st.expander("Regole di associazione (â‰¥ min_confidence)"):
        if rules.empty:
            st.info("Nessuna regola trovata con i parametri scelti.")
        else:
            rules_disp = (
                rules[["antecedents", "consequents", "support", "confidence", "lift"]]
                .assign(
                    antecedents=lambda d: d["antecedents"].apply(lambda x: ", ".join(sorted(x))),
                    consequents=lambda d: d["consequents"].apply(lambda x: ", ".join(sorted(x))),
                    **{"% support": lambda d: (d["support"] * 100).round(2)},
                )
                .drop(columns=["support"])
                .rename(columns={"antecedents": "Antecedent", "consequents": "Consequent"})
            )
            st.dataframe(rules_disp, use_container_width=True)

    with st.expander("Come leggere i risultati â“"):
        st.markdown(
            """
    * **Itemset completi** (compresi i singoli item) sono necessari per calcolare *confidence* e *lift*.
    * Per la visualizzazione ne mostriamo solo quelli con â‰¥ 2 prodotti, esclusi gli autoâ€‘combos.
    * Regola = *Antecedent* â‡’ *Consequent* con confidenza â‰¥ soglia e lift > 1 indica affinitÃ  oltre il caso.
            """
        )

    st.markdown("---")
    # --------------------------------------------------
    # Fine Sezione Basket Analysis
    # --------------------------------------------------