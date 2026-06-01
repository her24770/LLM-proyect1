import streamlit as st
import pandas as pd
from ia import analizar_datos
from graficas import generar_grafica
from chat import chat
from chats import (
    get_user_id, build_context, context_to_prompt,
    crear_chat, obtener_chats, obtener_chat, actualizar_chat,
    eliminar_chat, guardar_mensaje, obtener_mensajes,
    obtener_master_chat, crear_master_chat, construir_contexto_historico,
)

_SYSTEM_BASE = (
    "Eres un asistente de negocios experto en ventas y análisis de datos. "
    "Responde de forma concisa y útil."
)

_SYSTEM_CON_DATOS = (
    "Eres un analista de negocios experto en ventas. "
    "Analiza los siguientes datos y responde consultas del usuario de forma concisa.\n\n"
    "Datos:\n{contexto}"
)

_SYSTEM_MAESTRO = (
    "Eres un analista de negocios con acceso al historial completo de análisis del usuario. "
    "Cada sección representa un chat distinto con su archivo y estadísticas. "
    "Puedes comparar periodos, identificar tendencias entre chats, analizar estacionalidad "
    "y responder cualquier consulta que cruce múltiples análisis. "
    "Cuando el usuario mencione un chat por nombre o fecha, úsalo como referencia.\n\n"
    "Historial de análisis disponible:\n\n{historial}"
)

_SYSTEM_MAESTRO_VACIO = (
    "Eres un analista de negocios con acceso al historial de análisis del usuario. "
    "Aún no hay chats con datos cargados. "
    "Indica al usuario que primero cree chats con archivos de ventas para poder hacer análisis histórico."
)


def _company_prefix() -> str:
    name = st.session_state.get("company_name", "")
    ctx = st.session_state.get("company_context", "")
    if name:
        return f"Empresa del usuario: {name}. {ctx}\n\n"
    return ""


def _system_message(data_context: str = "") -> dict:
    prefix = _company_prefix()
    if data_context:
        content = prefix + _SYSTEM_CON_DATOS.format(contexto=context_to_prompt(data_context))
    else:
        content = prefix + _SYSTEM_BASE
    return {"role": "system", "content": content}


def _system_message_maestro(user_id: int) -> dict:
    historial = construir_contexto_historico(user_id)
    if historial:
        return {"role": "system", "content": _SYSTEM_MAESTRO.format(historial=historial)}
    return {"role": "system", "content": _SYSTEM_MAESTRO_VACIO}


def _cargar_chat(chat_id: int) -> None:
    data = obtener_chat(chat_id)
    if not data:
        return

    st.session_state.active_chat_id = chat_id
    st.session_state.is_master = data.get("is_master", False)
    st.session_state.data_context = data["data_context"] or ""
    st.session_state.df = None

    if data.get("is_master"):
        user_id = get_user_id(st.session_state.get("username"))
        system_msg = _system_message_maestro(user_id)
    else:
        system_msg = _system_message(data["data_context"] or "")

    messages = [system_msg]
    for msg in obtener_mensajes(chat_id):
        messages.append(msg)

    st.session_state.messages = messages


def _mostrar_sidebar_chats() -> None:
    user_id = get_user_id(st.session_state.get("username"))
    if not user_id:
        return

    with st.sidebar:
        st.markdown("---")

        # Chat maestro (único, pinneado arriba)
        master = obtener_master_chat(user_id)
        if not master:
            if st.button("Crear Analisis Global", use_container_width=True):
                mid = crear_master_chat(user_id)
                if mid:
                    _cargar_chat(mid)
                    st.rerun()
        else:
            is_active = st.session_state.get("active_chat_id") == master["id"]
            btn_type = "primary" if is_active else "secondary"
            if st.button(
                f"[Global] {master['name']}",
                key="master_chat_btn",
                use_container_width=True,
                type=btn_type,
            ):
                if not is_active:
                    _cargar_chat(master["id"])
                    st.rerun()

        st.markdown("---")
        st.markdown("**Chats**")
        if st.button("+ Nuevo chat", use_container_width=True):
            new_id = crear_chat(user_id)
            if new_id:
                _cargar_chat(new_id)
                st.rerun()

        chats = obtener_chats(user_id)
        active_id = st.session_state.get("active_chat_id")

        if "renaming_chat_id" not in st.session_state:
            st.session_state.renaming_chat_id = None

        for item in chats:
            is_active = item["id"] == active_id
            is_renaming = st.session_state.renaming_chat_id == item["id"]

            if is_renaming:
                nuevo_nombre = st.text_input(
                    "Nuevo nombre",
                    value=item["name"],
                    key=f"rename_input_{item['id']}",
                    label_visibility="collapsed",
                )
                col_ok, col_cancel = st.columns(2)
                with col_ok:
                    if st.button("Guardar", key=f"rename_ok_{item['id']}", use_container_width=True):
                        if nuevo_nombre.strip():
                            actualizar_chat(item["id"], name=nuevo_nombre.strip())
                        st.session_state.renaming_chat_id = None
                        st.rerun()
                with col_cancel:
                    if st.button("Cancelar", key=f"rename_cancel_{item['id']}", use_container_width=True):
                        st.session_state.renaming_chat_id = None
                        st.rerun()
            else:
                label = item["name"]
                if item.get("file_name"):
                    label += f" · {item['file_name']}"

                col_btn, col_rename, col_del = st.columns([4, 1, 1])
                with col_btn:
                    btn_type = "primary" if is_active else "secondary"
                    if st.button(label, key=f"chat_{item['id']}", use_container_width=True, type=btn_type):
                        if not is_active:
                            _cargar_chat(item["id"])
                        st.rerun()
                with col_rename:
                    if st.button("✏", key=f"ren_{item['id']}", use_container_width=True, help="Renombrar"):
                        st.session_state.renaming_chat_id = item["id"]
                        st.rerun()
                with col_del:
                    if st.button("✕", key=f"del_{item['id']}", use_container_width=True, help="Eliminar"):
                        eliminar_chat(item["id"])
                        if active_id == item["id"]:
                            for k in ("active_chat_id", "messages", "data_context", "df", "is_master"):
                                st.session_state.pop(k, None)
                        st.rerun()


def _mostrar_chat_maestro() -> None:
    st.title("Analisis Global")
    st.caption(
        "Este chat tiene acceso al contexto estadistico de todos tus chats. "
        "Puedes pedirle comparar periodos, analizar tendencias o cruzar datos entre archivos."
    )

    user_id = get_user_id(st.session_state.get("username"))
    historial = construir_contexto_historico(user_id)

    if not historial:
        st.info("Aun no tienes chats con archivos cargados. Crea chats con datos de ventas para activar el analisis historico.")
        return

    # Mostrar resumen de chats disponibles
    chats_con_datos = [c for c in obtener_chats(user_id) if c.get("file_name")]
    if chats_con_datos:
        with st.expander(f"{len(chats_con_datos)} analisis disponibles", expanded=False):
            for c in chats_con_datos:
                fecha = c.get("updated_at", "")[:10]
                st.caption(f"- **{c['name']}** — {c.get('file_name', '?')} ({fecha})")

    # Actualizar system message con el historial más reciente
    if st.session_state.messages:
        st.session_state.messages[0] = _system_message_maestro(user_id)

    with st.container():
        chat()


def mostrar_dashboard() -> None:
    _mostrar_sidebar_chats()

    for k, v in [("active_chat_id", None), ("messages", []), ("data_context", ""), ("df", None), ("is_master", False)]:
        if k not in st.session_state:
            st.session_state[k] = v

    active_chat_id = st.session_state.active_chat_id

    if not active_chat_id:
        st.title("Asistente de Ventas con IA")
        st.info("Crea un nuevo chat o abre el Analisis Global desde la barra lateral.")
        return

    # Chat maestro
    if st.session_state.get("is_master"):
        _mostrar_chat_maestro()
        return

    # Chat regular
    st.title("Asistente de Ventas con IA")

    if not st.session_state.messages:
        st.session_state.messages = [_system_message()]

    with st.expander("Subir archivo de ventas (opcional)", expanded=not st.session_state.data_context):
        uploaded_file = st.file_uploader(
            "CSV o Excel",
            type=["csv", "xlsx"],
            key=f"uploader_{active_chat_id}",
            label_visibility="collapsed",
        )
        st.caption("Por tu seguridad no guardamos el archivo — solo estadisticas del mismo para el contexto de la IA.")

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                st.subheader("Vista previa")
                st.dataframe(df.head())
                st.session_state.df = df

                new_context = build_context(df, uploaded_file.name)

                if st.session_state.data_context != new_context:
                    st.session_state.data_context = new_context
                    actualizar_chat(active_chat_id, data_context=new_context, file_name=uploaded_file.name)

                    chat_data = obtener_chat(active_chat_id)
                    if chat_data and chat_data["name"] == "Nuevo chat":
                        actualizar_chat(active_chat_id, name=uploaded_file.name.rsplit(".", 1)[0])

                    st.session_state.messages[0] = _system_message(new_context)

                    with st.spinner("Analizando datos..."):
                        resultado = analizar_datos(context_to_prompt(new_context))

                    st.session_state.messages.append({"role": "assistant", "content": resultado})
                    guardar_mensaje(active_chat_id, "assistant", resultado)
                    st.success("Analisis completado.")
                else:
                    st.success("Archivo en memoria, listo para conversar.")

            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

        elif st.session_state.data_context:
            chat_data = obtener_chat(active_chat_id)
            if chat_data and chat_data["file_name"]:
                st.caption(f"Contexto activo: {chat_data['file_name']} — sube un nuevo archivo para reemplazarlo.")

    with st.container():
        chat()

    if st.session_state.df is not None:
        with st.sidebar:
            generar_grafica(st.session_state.df)
