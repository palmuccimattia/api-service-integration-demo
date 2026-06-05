import streamlit as st
import pandas as pd
from calculus_pages.costo_prodotti import get_data_pizza
import numpy as np
import altair as alt
from datetime import datetime, timedelta

def monitoraggio_costi_prodotti():

    # Titolo pagina
    st.markdown("## ðŸ“ˆ Monitoraggio costi delle prodotti")
    st.markdown("---")

    # Seme per i dati finti
    np.random.seed(0)

    # Seleziona tipo di costo
    tipo_costo = st.radio(
        "Che tipo di costo vuoi visualizzare?",
        ["Vista Completa ðŸ”" , "Solo Variabili ã€°"],
        index=0,
        horizontal=False
    )

    # Intervallo di date (prima del selettore pizza)
    st.markdown("### ðŸ“… Seleziona intervallo di date")

    start_default = datetime.now() - timedelta(days=30)
    end_default = datetime.now()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data inizio", value=pd.to_datetime(start_default))
    with col2:
        end_date = st.date_input("Data fine", value=pd.to_datetime(end_default))

    # Validazione date
    if start_date > end_date:
        st.error("La data di inizio non puÃ² essere successiva alla data di fine.")

    # Pizze di Easy!
    dizionario_prodotti = {
        "Margherita" : "Margherita",
        "Alici" : "Alici",
        "Capricciosa" : "Capricciosa",
        "Carciofi" : "Carciofi",
        "Cipolla" : "Cipolla",
        "Prosciutto Cotto e Scamorza" : "CottoScamorza",
        "Prosciutto Crudo, Rucola, Grana e Stracciatella" : "CrudoRucolaGranaStracciatella",
        "Prosciutto Crudo, Rucola e Grana" : "CrudoRucolaGrana",
        "Funghi Bianca" : "FunghiBianca",
        "Funghi e Prosciutto Cotto" : "FunghiCotto",
        "Funghi e Salsiccia" : "FunghiSalsiccia",
        "Funghi" : "Funghi",
        "Grasselli" : "Grasselli",
        "Ortolana" : "Ortolana",
        "Parmigiana" : "Parmigiana",
        "Patate e Prosciutto Cotto" : "PatateCotto",
        "Patate e Pancetta" : "PatatePancetta",
        "Patate e Porcini" : "PatatePorcini",
        "Patate e Salsiccia" : "PatateSalsiccia",
        "Patate e Wurstel" : "PatateWurstel",
        "Patate" : "Patate",
        "Piccante" : "Piccante",
        "Pomodoro" : "Pomodoro",
        "4 Formaggi" : "QuattroFormaggi",
        "Rosmarino" : "Rosmarino",
        "Salsa Rosa e Gamberetti" : "SalsaRosaGamberetti",
        "Salsiccia" : "Salsiccia",
        "Spinaci e Salsiccia" : "SpinaciSalsiccia",
        "Sushi" : "Sushi",
        "Tartufata" : "Tartufata",
        "Tartufo e Porcini" : "TartufoPorcini",
        "Tartufo e Salsiccia" : "TartufoSalsiccia",
        "Tonno, Pomodorini e Rucola" : "TonnoPomodoriniRucola",
        "Vegana" : "Vegana",
        "Wurstel" : "Wurstel",
        "Zucchine e Prosciutto Cotto" : "ZucchineCotto",
        "Zucchine e Pancetta" : "ZucchinePancetta",
        "Zucchine e Pomodorini" : "ZucchinePomodorini",
        "Zucchine e Salsiccia" : "ZucchineSalsiccia",
        "Zucchine" : "Zucchine"
    }

    # === Selettore pizza ===
    pizza_scelta = st.selectbox("Seleziona una pizza:", list(dizionario_prodotti.keys()))

    # === Grafico ===
    if pizza_scelta:

        df = get_data_pizza(start_date, end_date, dizionario_prodotti[pizza_scelta])

        col_prezzo = "PrezzoPizza"
        col_costo = "CostoPizza" if tipo_costo == "Vista Completa ðŸ”" else "Totale_CV"

        chart_data = df[["Data", col_prezzo, col_costo]].rename(columns={
            col_prezzo: "Prezzo",
            col_costo: "Costo"
        })

        # Area prezzo (verde, sfondo)
        area_prezzo = alt.Chart(chart_data).mark_area(
            interpolate='monotone',
            line={'color': 'green'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='lightgreen', offset=0),
                    alt.GradientStop(color='white', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x='Data:T',
            y='Prezzo:Q',
            tooltip=['Data:T', 'Prezzo:Q']
        )

        # Area costo (rosso, in primo piano)
        area_costo = alt.Chart(chart_data).mark_area(
            interpolate='monotone',
            line={'color': 'darkred'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='lightcoral', offset=0),
                    alt.GradientStop(color='white', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x='Data:T',
            y='Costo:Q',
            tooltip=['Data:T', 'Costo:Q']
        )

        # Invertiamo l'ordine per mettere il costo in primo piano
        final_chart = (area_prezzo + area_costo).interactive()

        st.subheader(f"Andamento di prezzo e costi: {pizza_scelta}")
        st.altair_chart(final_chart, use_container_width=True)

    # === Tabella dati ===
    with st.expander("Visualizza dati"):
        st.dataframe(df.round(2), use_container_width=True)

    # === Notifiche variazioni ingredienti (day-over-day con LAG 1) ===
    st.markdown("---")
    st.markdown("### ðŸ”” Variazioni ingredienti (giorno su giorno)")

    if df.empty:
        st.info("Nessun dato disponibile per calcolare le variazioni.")
    else:
        # Ordina per data
        df_sorted = df.sort_values("Data").reset_index(drop=True)

        # Colonne da escludere (totali/prezzi)
        exclude_cols = {
            "Data", "Totale_CV", "Totale_CF_Manodopera", "Totale_CF_Generali", "CostoPizza", "PrezzoPizza"
        }
        ingredient_cols = [
            c for c in df_sorted.columns
            if c not in exclude_cols and pd.api.types.is_numeric_dtype(df_sorted[c])
        ]

        # Calcolo differenze laggate per ciascun ingrediente
        changes = []
        eps = 0.01  # soglia minima di 1 centesimo

        for col in ingredient_cols:
            prev = df_sorted[col].shift(1)
            diff = df_sorted[col] - prev
            mask = diff.abs() >= eps

            for idx in df_sorted.index[mask]:
                date = df_sorted.at[idx, "Data"]
                v0 = prev.iloc[idx]
                v1 = df_sorted.at[idx, col]
                delta = diff.iloc[idx]

                if pd.isna(v0) or v0 == 0:
                    rel = np.inf
                else:
                    rel = delta / v0

                costo = df_sorted.at[idx, "CostoPizza"] if "CostoPizza" in df_sorted.columns else np.nan
                if pd.isna(costo) or costo == 0:
                    incidenza = np.nan
                else:
                    incidenza = delta / costo

                changes.append({
                    "Data": date,
                    "Ingrediente": col,
                    "Valore_precedente_â‚¬": v0,
                    "Valore_attuale_â‚¬": v1,
                    "Delta_â‚¬": delta,
                    "Delta_%": rel,
                    "Incidenza_su_CostoPizza_%": incidenza
                })

        if not changes:
            st.success("âœ… Nessuna variazione â‰¥ 0,01 â‚¬ nel periodo selezionato.")
        else:
            st.toast(f"ðŸ”Ž Rilevate {len(changes)} variazioni di almeno 0,01 â‚¬ nel periodo.", icon="ðŸ””")

            # Mostra notifiche rapide per le ultime variazioni
            changes_sorted = sorted(changes, key=lambda x: x["Data"], reverse=True)
            for item in changes_sorted[:6]:
                data_str = pd.to_datetime(item["Data"]).strftime("%d %b %Y")
                delta_rel_txt = "âˆž" if not np.isfinite(item["Delta_%"]) else f"{item['Delta_%']:+.1%}"
                inc_txt = "n/d" if pd.isna(item["Incidenza_su_CostoPizza_%"]) else f"{item['Incidenza_su_CostoPizza_%']:+.1%}"
                segno = "ðŸ“ˆ" if item["Delta_â‚¬"] > 0 else "ðŸ“‰"

                st.info(
                    f"{segno} **{item['Ingrediente']}** â€” {data_str}  \n"
                    f"â€¢ Î” assoluto: **{item['Delta_â‚¬']:+.2f} â‚¬**  \n"
                    f"â€¢ Î” relativo: **{delta_rel_txt}**  \n"
                    f"â€¢ Incidenza su costo pizza: **{inc_txt}**",
                    icon="ðŸ•"
                )

            # Tabella riepilogativa
            df_changes = pd.DataFrame(changes)
            st.markdown("#### ðŸ“‹ Dettaglio variazioni (â‰¥ 0,01 â‚¬)")
            df_changes = df_changes.sort_values("Data")
            df_changes[["Valore_precedente_â‚¬","Valore_attuale_â‚¬","Delta_â‚¬"]] = df_changes[
                ["Valore_precedente_â‚¬","Valore_attuale_â‚¬","Delta_â‚¬"]
            ].astype(float).round(2)
            st.dataframe(df_changes, use_container_width=True)
