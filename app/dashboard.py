import streamlit as st
import pandas as pd
from ia import analizar_datos
from graficas import generar_grafica
from chat import chat
from chats import (
    get_user_id, build_context, context_to_prompt,
    crear_chat, obtener_chats, obtener_chat, actualizar_chat,
    eliminar_chat, guardar_mensaje, obtener_mensajes,
)


def _cargar_chat(chat_id: int) -> None:
    """Carga un chat de la DB al session_state."""
    data = obtener_chat(chat_id)
    if not data:
        return

    st.session_state.active_chat_id = chat_id
    st.session_state.data_context = data["data_context"] or ""
    st.session_state.df = None  # el DataFrame solo vive en memoria; hay que re-subir

    # Reconstruir lista de mensajes: system (del contexto) + historial guardado
    messages = []
    if data["data_context"]:
        messages.append({
            "role": "system",
            "content": (
                "Eres un analista de negocios experto en ventas. "
                "Analiza los siguientes datos y responde consultas del usuario de forma concisa.\n\n"
                f"Datos:\n{context_to_prompt(data['data_context'])}"
            ),
        })
    for msg in obtener_mensajes(chat_id):
        messages.append(msg)

    st.session_state.messages = messages


def _mostrar_sidebar_chats() -> None:
    user_id = get_user_id(st.session_state.get("username"))
    if not user_id:
        return

    with st.sidebar:
        st.markdown("---")
        col_title, col_new = st.columns([3, 1])
        with col_title:
            st.markdown("**Chats**")
        with col_new:
            if st.button("+", help="Nuevo chat", use_container_width=True):
                new_id = crear_chat(user_id)
                if new_id:
                    _cargar_chat(new_id)
                    st.rerun()

        chats = obtener_chats(user_id)
        active_id = st.session_state.get("active_chat_id")

        for item in chats:
            is_active = item["id"] == active_id
            label = item["name"]
            if item.get("file_name"):
                label += f" · {item['file_name']}"

            col_btn, col_del = st.columns([5, 1])
            with col_btn:
                btn_type = "primary" if is_active else "secondary"
                if st.button(label, key=f"chat_{item['id']}", use_container_width=True, type=btn_type):
                    if not is_active:
                        _cargar_chat(item["id"])
                        st.rerun()
            with col_del:
                if st.button("x", key=f"del_{item['id']}", use_container_width=True):
                    eliminar_chat(item["id"])
                    if active_id == item["id"]:
                        for k in ("active_chat_id", "messages", "data_context", "df"):
                            st.session_state.pop(k, None)
                    st.rerun()


def mostrar_dashboard() -> None:
    _mostrar_sidebar_chats()

    for k, v in [("active_chat_id", None), ("messages", []), ("data_context", ""), ("df", None)]:
        if k not in st.session_state:
            st.session_state[k] = v

    active_chat_id = st.session_state.active_chat_id

    st.title("Asistente de Ventas con IA")

    if not active_chat_id:
        st.info("Crea un nuevo chat desde la barra lateral para comenzar.")
        return

    uploaded_file = st.file_uploader(
        "Sube tu archivo de ventas (CSV o Excel)",
        type=["csv", "xlsx"],
        key=f"uploader_{active_chat_id}",
    )

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            st.subheader("Vista previa de los datos")
            st.dataframe(df.head())
            st.session_state.df = df

            new_context = build_context(df, uploaded_file.name)

            if st.session_state.data_context != new_context:
                st.session_state.data_context = new_context
                actualizar_chat(active_chat_id, data_context=new_context, file_name=uploaded_file.name)

                # Auto-renombrar el chat con el nombre del archivo
                chat_data = obtener_chat(active_chat_id)
                if chat_data and chat_data["name"] == "Nuevo chat":
                    actualizar_chat(active_chat_id, name=uploaded_file.name.rsplit(".", 1)[0])

                st.session_state.messages = [
                    {
                        "role": "system",
                        "content": (
                            "Eres un analista de negocios experto en ventas. "
                            "Analiza los siguientes datos y responde consultas del usuario de forma concisa.\n\n"
                            f"Datos:\n{context_to_prompt(new_context)}"
                        ),
                    }
                ]

                with st.spinner("Realizando análisis inicial con IA..."):
                    resultado = analizar_datos(context_to_prompt(new_context))

                st.session_state.messages.append({"role": "assistant", "content": resultado})
                guardar_mensaje(active_chat_id, "assistant", resultado)
                st.success("Análisis inicial completado")
            else:
                st.success("Archivo cargado en memoria, listo para conversar.")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

    elif st.session_state.data_context:
        chat_data = obtener_chat(active_chat_id)
        if chat_data and chat_data["file_name"]:
            st.info(
                f"Contexto activo: **{chat_data['file_name']}** — "
                "puedes seguir conversando o subir un nuevo archivo."
            )

    if st.session_state.data_context:
        with st.container():
            chat()
        if st.session_state.df is not None:
            with st.sidebar:
                generar_grafica(st.session_state.df)
