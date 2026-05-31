import streamlit as st
from ia import chat_con_datos, generar_nombre_chat
from chats import guardar_mensaje, actualizar_chat, obtener_chat


def chat() -> None:
    st.divider()
    st.subheader("Conversacion")

    mensaje_placeholder = st.container()

    with mensaje_placeholder:
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    if prompt := st.chat_input("Escribe tu mensaje..."):
        with mensaje_placeholder:
            with st.chat_message("user"):
                st.markdown(prompt)

        chat_id = st.session_state.get("active_chat_id")

        # Renombrar con IA si es el primer mensaje del usuario
        es_primer_mensaje = not any(m["role"] == "user" for m in st.session_state.messages)
        if es_primer_mensaje and chat_id:
            chat_data = obtener_chat(chat_id)
            if chat_data and chat_data["name"] == "Nuevo chat":
                nombre = generar_nombre_chat(prompt)
                if nombre:
                    actualizar_chat(chat_id, name=nombre)

        st.session_state.messages.append({"role": "user", "content": prompt})
        if chat_id:
            guardar_mensaje(chat_id, "user", prompt)

        with mensaje_placeholder:
            with st.chat_message("assistant"):
                with st.spinner("Pensando..."):
                    respuesta = chat_con_datos(st.session_state.messages)
                st.markdown(respuesta)

        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        if chat_id:
            guardar_mensaje(chat_id, "assistant", respuesta)

        st.rerun()
