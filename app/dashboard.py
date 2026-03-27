import streamlit as st
import pandas as pd
from ia import analizar_datos


def mostrar_dashboard() -> None:
    st.title("Asistente de Ventas con IA")

    uploaded_file = st.file_uploader(
        "Sube tu archivo de ventas (CSV o Excel)",
        type=["csv", "xlsx"]
    )

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.subheader("Vista previa de los datos")
            st.dataframe(df.head())

            data_sample = df.head(20).to_string()

            with st.spinner("Analizando datos con IA..."):
                resultado = analizar_datos(data_sample)

            st.success("✅ Análisis completado")
            st.markdown(resultado)

        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")
            st.warning("Asegúrate de que el archivo tenga formato correcto.")