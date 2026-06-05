import streamlit as st
import altair as alt
import pandas as pd
from datetime import datetime
from calculus_pages.vendite import vendite_giornaliere_per_prodotto

def vendite_per_prodotto():
    st.markdown("## 📈 Andamento vendite per prodotto")
    st.markdown("---")

    df = vendite_giornaliere_per_prodotto()
    df["Data"] = pd.to_datetime(df["Data"])
    df = df[df["Data"] >= datetime(2025, 5, 1)]

    prodotti = df.columns.tolist()[1:]

    st.markdown("#### Quante serie vuoi confrontare?")
    num_serie = st.slider("Numero di serie", min_value=1, max_value=min(10, len(prodotti)), value=3)

    st.markdown("#### Seleziona i prodotti da visualizzare")
    selectors = []

    for i in range(num_serie):
        cols = st.columns([3, 1])
        with cols[0]:
            prodotto_selezionato = st.selectbox(
                f"Serie {i + 1}", prodotti, index=i if i < len(prodotti) else 0, key=f"sel_{i}"
            )
        with cols[1]:
            attivo = st.checkbox("Attiva", value=True if i == 0 else False, key=f"chk_{i}")
        selectors.append((prodotto_selezionato, attivo))

    prodotti_attivi = [nome for nome, attivo in selectors if attivo]

    if not prodotti_attivi:
        st.info("Seleziona almeno una serie per visualizzare il grafico.")
        st.stop()

    data_long = (
        df[["Data"] + prodotti_attivi]
        .melt(id_vars="Data", var_name="Prodotto", value_name="Vendite")
        .sort_values("Data")
    )

    base = (
        alt.Chart(data_long)
        .encode(
            x=alt.X('Data:T', title='Data'),
            y=alt.Y('Vendite:Q', title='Numero di vendite'),
            color=alt.Color('Prodotto:N', legend=alt.Legend(title='Prodotto'))
        )
    )

    hover = alt.selection_point(
        fields=['Data', 'Prodotto'],
        nearest=True,
        on='mouseover',
        empty='none'
    )

    linee = base.mark_line(interpolate='monotone')
    punti = base.mark_circle(size=60).encode(
        opacity=alt.condition(hover, alt.value(1), alt.value(0))
    ).add_params(hover)

    testo = base.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(hover, 'Vendite:Q', alt.value('')),
        tooltip=['Data:T', 'Prodotto:N', 'Vendite:Q']
    )

    chart = (linee + punti + testo).properties(height=450).interactive()

    st.altair_chart(chart, use_container_width=True)