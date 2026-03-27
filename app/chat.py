import streamlit as st
from ia import chat_con_datos

def chat() -> None:
    st.divider()
    st.subheader("💬 Conversación sobre tus datos")

    # Contenedor para el historial de mensajes
    # Esto asegura que los nuevos mensajes aparezcan arriba del cuadro de entrada
    mensaje_placeholder = st.container()

    # Mostrar historial existente
    with mensaje_placeholder:
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    # Input del usuario (siempre al final o anclado abajo)
    if prompt := st.chat_input("Escribe tu pregunta sobre el archivo subido..."):
        #Mostrar el mensaje del usuario inmediatamente
        with mensaje_placeholder:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        # Guardar en session_state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generar y mostrar la respuesta de la IA
        with mensaje_placeholder:
            with st.chat_message("assistant"):
                with st.spinner("Pensando..."):
                    respuesta = chat_con_datos(st.session_state.messages)
                st.markdown(respuesta)
        
        # Guardar la respuesta en session_state
        st.session_state.messages.append({"role": "assistant", "content": respuesta})

        # Forzar reinicio para que todo el historial se renderice en el bloque superior
        st.rerun()

