import streamlit as st
from calculus_pages.costo_prodotti import *
from calculus_pages.vendite import *
from monitoraggio_fatture import monitoraggio_fatture
from monitoraggio_costi_prodotti import monitoraggio_costi_prodotti
from monitoraggio_dati_vendite import monitoraggio_dati_vendite
from andamento_vendite_per_prodotto import vendite_per_prodotto
from monitoraggio_fatture_no_api import monitoraggio_fatture_no_api
# from gestione_orari import gestione_orari
# from foto_orari import pagina_foto_orari_ai

def admin_user():
    st.markdown("# ðŸ• ApiConnectorDemo")

    # Inizializza stato per mostrare/nascondere video
    if "mostra_video" not in st.session_state:
        st.session_state.mostra_video = True

    # === VIDEO TUTORIAL (se attivo) ===
    if st.session_state.mostra_video:
        col_banner, col_close = st.columns([20, 1])
        
        with col_banner:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 12px; padding: 20px; margin: 20px 0;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="font-size: 48px;">ðŸŽ¥</div>
                    <div style="flex: 1;">
                        <h3 style="margin: 0; color: white; font-size: 22px;">
                            âœ¨ Scopri come usare la WebApp di DemoIntegrationStudio in pochi minuti!
                        </h3>
                        <p style="margin: 8px 0 0 0; color: #f0f0f0; font-size: 16px;">
                            Guarda il video tutorial completo e impara a gestire fatture, costi e vendite come un professionista ðŸš€
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_close:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("âŒ", key="close_video", help="Nascondi video tutorial"):
                st.session_state.mostra_video = False
                st.rerun()
        
        # Video YouTube embedded
        st.video("https://www.youtube.com/watch?v=HjU7Y5ZIvCQ")
    else:
        # Bottone per mostrare nuovamente il video
        if st.button("ðŸŽ¥ Mostra video tutorial", help="Clicca per vedere il tutorial"):
            st.session_state.mostra_video = True
            st.rerun()
    
    st.markdown("---")

    # Stato per controllo selezione
    if "pagina_attiva" not in st.session_state:
        st.session_state.pagina_attiva = None

    # Bottoni in orizzontale
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("ðŸ’¼ Monitoraggio Fatture"):
            st.session_state.pagina_attiva = "fatture"

    with col2:
        if st.button("ðŸ’¼ Monitoraggio Fatture (no API)"):
            st.session_state.pagina_attiva = "fatture_no_api"

    with col3:
        if st.button("ðŸ“ˆ Monitoraggio costo prodotti"):
            st.session_state.pagina_attiva = "prodotti"

    with col4:
        if st.button("ðŸ“Š Monitoraggio vendite"):
            st.session_state.pagina_attiva = "vendite"
    
    with col5:
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

    elif st.session_state.pagina_attiva == "fatture_no_api":
        monitoraggio_fatture_no_api()

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