import streamlit as st
from user_pages.user_cliente import *
from user_pages.user_admin_user import *
from calculus_pages.costo_prodotti import *
from config_scripts.aws_secret_loader import *

st.set_page_config(
    page_title="ApiConnectorDemo",
    page_icon="ðŸ•",
    initial_sidebar_state="collapsed",
    layout="wide"
)

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    users = get_secret_users_app()

    if not st.session_state.logged_in:

        with st.form("login_form"):

            st.markdown("## ðŸ” Effettua il login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:

                for user in users:

                    if username == user["username"] and password == user["password"]:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("Login riuscito!")
                        st.rerun()

                else:
                    st.error("Username o password errati.")
    
    return st.session_state.logged_in, st.session_state.username

# Uso del login
log_success, username = check_login()

if log_success:

    with st.sidebar:
        st.markdown(f"ðŸ‘‹ Benvenuto **{username}**")
        if st.button("ðŸšª Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

    if username == "cliente":
        cliente()

    if username == "demo_admin":
        cliente()

    if username == "a.admin_user":
        admin_user()

    # elif username == "demo_user":
    #     demo_user()

else:
    st.stop()