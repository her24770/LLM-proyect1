import streamlit as st
from ia import chat_con_datos
from chats import guardar_mensaje


def chat() -> None:
    st.divider()
    st.subheader("Conversación sobre tus datos")

    mensaje_placeholder = st.container()

    with mensaje_placeholder:
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    if prompt := st.chat_input("Escribe tu pregunta sobre el archivo subido..."):
        with mensaje_placeholder:
            with st.chat_message("user"):
                st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})
        chat_id = st.session_state.get("active_chat_id")
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
