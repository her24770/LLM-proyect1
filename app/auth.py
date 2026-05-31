import os
import re
import time
import sqlite3
import bcrypt
import streamlit as st
from datetime import datetime, timedelta
from landing import render_landing_page

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "users.db")

TIMEOUT_HOURS = 8

_LOGIN_STYLES = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}

.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    padding: 40px;
    border-radius: 16px;
    background: rgba(28, 30, 38, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);
    margin: 40px auto;
    max-width: 450px;
}

@media (prefers-color-scheme: light) {
    .login-container {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.15);
    }
}

.login-title {
    font-family: 'Outfit', 'Inter', sans-serif;
    font-size: 28px;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(135deg, #FF4B4B, #FF7676);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.login-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    text-align: center;
    color: #8A8D9F;
    margin-bottom: 24px;
}

.login-back-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin: 24px 0 0;
    color: #8A8D9F;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
}

.login-back-link:hover {
    color: #FF4B4B;
    text-decoration: none;
}

.login-switch-link {
    display: block;
    text-align: center;
    margin-top: 16px;
    color: #8A8D9F;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
}

.login-switch-link a {
    color: #62d6c8;
    font-weight: 600;
    text-decoration: none;
}
</style>
"""


def init_auth() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL DEFAULT 'Nuevo chat',
                file_name TEXT,
                data_context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error al inicializar la base de datos: {e}")
        raise
    finally:
        if conn:
            conn.close()


def registrar_usuario(username: str, password: str, full_name: str, email: str) -> tuple[bool, str]:
    if len(username) < 3:
        return False, "El usuario debe tener al menos 3 caracteres."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "El usuario solo puede contener letras, números y guiones bajos."
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "El email no tiene un formato válido."
    if len(full_name.strip()) < 2:
        return False, "El nombre completo es requerido."

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Ese nombre de usuario ya está en uso."

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return False, "Ese email ya está registrado."

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, email) VALUES (?, ?, ?, ?)",
            (username, hashed, full_name.strip(), email.strip()),
        )
        conn.commit()
        return True, ""
    except sqlite3.Error as e:
        return False, f"Error al crear el usuario: {e}"
    finally:
        if conn:
            conn.close()


def check_credentials(username: str, password: str) -> tuple[bool, dict | None]:
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, password_hash, full_name, email, is_active FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()
        if row:
            db_username, db_pwd_hash, db_full_name, db_email, is_active = row
            if is_active and bcrypt.checkpw(password.encode("utf-8"), db_pwd_hash.encode("utf-8")):
                return True, {"username": db_username, "full_name": db_full_name, "email": db_email}
        return False, None
    except sqlite3.Error:
        return False, None
    finally:
        if conn:
            conn.close()


def check_timeout() -> None:
    if st.session_state.get("authenticated", False):
        last_activity_str = st.session_state.get("last_activity")
        if last_activity_str:
            try:
                last_activity = datetime.fromisoformat(last_activity_str)
                if datetime.now() - last_activity > timedelta(hours=TIMEOUT_HOURS):
                    logout()
                    st.warning("Sesión expirada por inactividad. Inicia sesión de nuevo.")
                    st.rerun()
            except ValueError:
                logout()
                st.rerun()
        st.session_state["last_activity"] = datetime.now().isoformat()


def _render_login_form() -> None:
    st.markdown(_LOGIN_STYLES, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<a class="login-back-link" href="./" target="_self">← Volver al inicio</a>', unsafe_allow_html=True)
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Bienvenido</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Ingresa tus credenciales para acceder</div>', unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Usuario", placeholder="Nombre de usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Contraseña")
            submit = st.form_submit_button("Iniciar sesión", use_container_width=True)

            if submit:
                if not username.strip() or not password.strip():
                    st.error("Completa todos los campos.")
                else:
                    if "failed_attempts" not in st.session_state:
                        st.session_state["failed_attempts"] = 0
                    if st.session_state["failed_attempts"] >= 3:
                        st.warning("Demasiados intentos fallidos. Espera 5 segundos...")
                        time.sleep(5)

                    success, user_info = check_credentials(username.strip(), password.strip())
                    if success and user_info:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user_info["username"]
                        st.session_state["full_name"] = user_info["full_name"]
                        st.session_state["email"] = user_info["email"]
                        st.session_state["last_activity"] = datetime.now().isoformat()
                        st.session_state["failed_attempts"] = 0
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.session_state["failed_attempts"] = st.session_state.get("failed_attempts", 0) + 1
                        st.error("Usuario o contraseña incorrectos.")

        st.markdown(
            '<div class="login-switch-link">¿No tienes cuenta? '
            '<a href="./?register=1" target="_self">Regístrate</a></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def _render_register_form() -> None:
    st.markdown(_LOGIN_STYLES, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<a class="login-back-link" href="./" target="_self">← Volver al inicio</a>', unsafe_allow_html=True)
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Crear cuenta</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Completa los datos para registrarte</div>', unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            full_name = st.text_input("Nombre completo", placeholder="Tu nombre")
            email = st.text_input("Email", placeholder="tu@email.com")
            username = st.text_input("Usuario", placeholder="Sin espacios ni caracteres especiales")
            password = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            password2 = st.text_input("Confirmar contraseña", type="password", placeholder="Repite la contraseña")
            submit = st.form_submit_button("Crear cuenta", use_container_width=True)

            if submit:
                if not all([full_name, email, username, password, password2]):
                    st.error("Completa todos los campos.")
                elif password != password2:
                    st.error("Las contraseñas no coinciden.")
                else:
                    ok, msg = registrar_usuario(username.strip(), password, full_name, email.strip())
                    if ok:
                        st.success("Cuenta creada. Ya puedes iniciar sesión.")
                        st.query_params["login"] = "1"
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown(
            '<div class="login-switch-link">¿Ya tienes cuenta? '
            '<a href="./?login=1" target="_self">Inicia sesión</a></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def login() -> None:
    param = st.query_params.get("login")
    reg_param = st.query_params.get("register")

    if reg_param == "1":
        _render_register_form()
        return

    if param != "1":
        render_landing_page()
        return

    _render_login_form()


def logout() -> None:
    for key in ["authenticated", "username", "full_name", "email", "last_activity", "failed_attempts"]:
        st.session_state.pop(key, None)
    st.query_params.clear()


def protect_page() -> bool:
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    check_timeout()

    if not st.session_state["authenticated"]:
        login()
        return False

    _mostrar_sidebar_usuario()
    return True


def _mostrar_sidebar_usuario() -> None:
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**{st.session_state.get('full_name', '')}**")
        st.caption(f"@{st.session_state.get('username', '')}")
        if st.button("Cerrar sesión", use_container_width=True):
            logout()
            st.rerun()


def get_current_user() -> dict | None:
    if st.session_state.get("authenticated", False):
        return {
            "username": st.session_state.get("username"),
            "full_name": st.session_state.get("full_name"),
            "email": st.session_state.get("email"),
        }
    return None
