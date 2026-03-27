import streamlit as st
import pandas as pd
from ia import analizar_datos, chat_con_datos
from graficas import generar_grafica
from chat import chat


def mostrar_dashboard() -> None:
    st.title("Asistente de Ventas con IA")

    # Inicializar el estado de la sesión si no existe (Memoria con los mensajes)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Inicializar el estado de la sesión si no existe (Memoria con los datos)
    if "data_context" not in st.session_state:
        st.session_state.data_context = ""

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

            # Si el archivo es nuevo o ha cambiado, reiniciamos el contexto
            if st.session_state.data_context != data_sample:
                st.session_state.data_context = data_sample
                # Creamos el prompt del sistema con los datos
                st.session_state.messages = [
                    {
                        "role": "system", 
                        "content": f"Eres un analista de negocios experto en ventas. Utiliza el siguiente fragmento de datos para responder cualquier consulta del usuario. Sé conciso y claro.\n\nDatos:\n{data_sample}"
                    }
                ]
                
                with st.spinner("Realizando análisis inicial con IA..."):
                    resultado = analizar_datos(data_sample)
                
                # Agregamos el primer análisis al historial
                st.session_state.messages.append({"role": "assistant", "content": resultado})
                st.success("✅ Análisis inicial completado")
            else:
                st.success("✅ Archivo cargado en memoria, listo para conversar.")

        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")
            st.warning("Asegúrate de que el archivo tenga formato correcto.")

    # Si hay contexto guardado, mostramos el chat y el generador de gráficas
    if st.session_state.data_context:
        col_chat= st.container()
        with col_chat:
            chat()
        with st.sidebar:
            generar_grafica(df)
