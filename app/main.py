import streamlit as st
from dashboard import mostrar_dashboard

st.set_page_config(page_title="Sistema de Gestión", layout="wide")

st.title("Sistema de Gestión")

mostrar_dashboard()