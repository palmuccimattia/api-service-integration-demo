import streamlit as st
from calculus_pages.costo_prodotti import *
from calculus_pages.vendite import *
from monitoraggio_fatture import monitoraggio_fatture
from monitoraggio_costi_prodotti import monitoraggio_costi_prodotti
from monitoraggio_dati_vendite import monitoraggio_dati_vendite
from andamento_vendite_per_prodotto import vendite_per_prodotto
# from gestione_orari import gestione_orari
# from foto_orari import pagina_foto_orari_ai

def cliente():
    st.markdown("# ðŸ• ApiConnectorDemo")

    # Stato per controllo selezione
    if "pagina_attiva" not in st.session_state:
        st.session_state.pagina_attiva = None

    st.markdown("---")

    # Bottoni in orizzontale
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("ðŸ’¼ Monitoraggio Fatture"):
            st.session_state.pagina_attiva = "fatture"

    with col2:
        if st.button("ðŸ“ˆ Monitoraggio costo prodotti"):
            st.session_state.pagina_attiva = "prodotti"

    with col3:
        if st.button("ðŸ“Š Monitoraggio vendite"):
            st.session_state.pagina_attiva = "vendite"
    
    with col4:
        if st.button("ðŸ” Confronto vendite"):
            st.session_state.pagina_attiva = "confronto"

    # with col5:
    #     if st.button("ðŸ—“ï¸ Gestione orari"):
    #         st.session_state.pagina_attiva = "orari"

    # with col6:
    #     if st.button("ðŸ—“ï¸ Calendario lavoro"):
    #         st.session_state.pagina_attiva = "calendario"

    st.markdown("---")

    # --- Contenuto sotto i bottoni ---
    if st.session_state.pagina_attiva == "fatture":
        monitoraggio_fatture()

    elif st.session_state.pagina_attiva == "prodotti":
        monitoraggio_costi_prodotti()

    elif st.session_state.pagina_attiva == "vendite":
        monitoraggio_dati_vendite()

    elif st.session_state.pagina_attiva == "confronto":
        vendite_per_prodotto()

    # elif st.session_state.pagina_attiva == "orari":
    #     gestione_orari()

    # elif st.session_state.pagina_attiva == "calendario":
    #     pagina_foto_orari_ai()