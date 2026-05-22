import streamlit as st
from auth import init_auth, protect_page

# Configurar la página (MANDATORIO ser el primer comando Streamlit ejecutado)
st.set_page_config(page_title="Sistema de Gestión", layout="wide")

# Inicializar autenticación y base de datos
init_auth()

# Proteger toda la página (detiene ejecución si no está autenticado)
if not protect_page():
    st.stop()

# --- A PARTIR DE AQUÍ, EL CÓDIGO EXISTENTE DE TU APLICACIÓN PRINCIPAL ---
from dashboard import mostrar_dashboard

st.title("Sistema de Gestión")

mostrar_dashboard()