import os
import json
import time
import sqlite3
import bcrypt
import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path

# Determinar la ruta absoluta del archivo de base de datos dentro del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
DB_PATH = os.path.join(DATA_DIR, "users.db")
USERS_CONFIG_PATH = os.path.join(CONFIG_DIR, "users_config.json")

TIMEOUT_HOURS = 8

def cargar_usuarios_desde_config() -> list[tuple]:
    """
    Carga los usuarios desde el archivo JSON de configuración.
    Si el archivo no existe, muestra error y permite ejecución con usuarios de demostración.
    Retorna lista de tuplas (username, password, full_name, email)
    """
    try:
        if not os.path.exists(USERS_CONFIG_PATH):
            st.error(
                f"Archivo de configuración no encontrado: {USERS_CONFIG_PATH}\n\n"
                "Por favor, crea el archivo `config/users_config.json` basándote en "
                "`config/users_config.example.json` con tus credenciales reales."
            )
            # Opcional: cargar usuarios de demostración SOLO para desarrollo
            if os.getenv("STREAMLIT_ENV") == "development":
                st.warning("Modo desarrollo: Cargando usuarios de demostración")
                return [
                    ("demo", "demo123", "Usuario Demo", "demo@ejemplo.com")
                ]
            return []
        
        with open(USERS_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        usuarios = []
        for user in config.get("users", []):
            usuarios.append((
                user["username"],
                user["password"],
                user["full_name"],
                user["email"]
            ))
        
        return usuarios
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Error al leer el archivo de configuración JSON: {e}")
        return []
    except Exception as e:
        st.error(f"❌ Error inesperado al cargar configuración: {e}")
        return []

def init_auth() -> None:
    """
    Inicializa la base de datos SQLite y la tabla de usuarios.
    Carga los usuarios desde el archivo JSON externo (ignorado por Git).
    """
    # Crear carpetas necesarias
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Crear la tabla de usuarios
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
        conn.commit()
        
        # Cargar usuarios desde archivo de configuración
        usuarios_base = cargar_usuarios_desde_config()
        
        if not usuarios_base:
            st.warning("No se cargaron usuarios. El sistema no tendrá cuentas disponibles.")
            return
        
        for username, password, full_name, email in usuarios_base:
            # Verificar si el usuario ya existe (por username o email)
            cursor.execute(
                "SELECT id FROM users WHERE username = ? OR email = ?",
                (username, email)
            )
            
            if not cursor.fetchone():
                # Generar hash con bcrypt (costo 12)
                password_bytes = password.encode('utf-8')
                salt = bcrypt.gensalt(rounds=12)
                hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
                
                cursor.execute(
                    """INSERT INTO users (username, password_hash, full_name, email) 
                       VALUES (?, ?, ?, ?)""",
                    (username, hashed, full_name, email)
                )
                print(f"Usuario '{username}' creado exitosamente")
        
        conn.commit()
        print(f"Base de datos inicializada en: {DB_PATH}")
        
    except sqlite3.Error as e:
        st.error(f"Error de base de datos durante la inicialización: {e}")
        raise
    finally:
        if conn:
            conn.close()

def check_credentials(username, password) -> tuple[bool, dict | None]:
    """
    Verifica las credenciales ingresadas contra la base de datos usando bcrypt.checkpw.
    Retorna (True, datos_usuario) si es válido, de lo contrario (False, None).
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar usuario activo
        cursor.execute(
            "SELECT username, password_hash, full_name, email, is_active FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        
        if row:
            db_username, db_pwd_hash, db_full_name, db_email, is_active = row
            if is_active:
                # Comprobar contraseña
                if bcrypt.checkpw(password.encode('utf-8'), db_pwd_hash.encode('utf-8')):
                    return True, {
                        "username": db_username,
                        "full_name": db_full_name,
                        "email": db_email
                    }
        return False, None
    except sqlite3.Error:
        # No mostrar detalles del error técnico por seguridad
        return False, None
    finally:
        if conn:
            conn.close()

def check_timeout() -> None:
    """
    Verifica la inactividad de la sesión de usuario (8 horas).
    Cierra la sesión de forma automática si se supera el tiempo límite.
    """
    if st.session_state.get("authenticated", False):
        last_activity_str = st.session_state.get("last_activity")
        if last_activity_str:
            try:
                last_activity = datetime.fromisoformat(last_activity_str)
                # Si pasaron más de 8 horas
                if datetime.now() - last_activity > timedelta(hours=TIMEOUT_HOURS):
                    logout()
                    st.warning("Sesión expirada por inactividad. Inicie sesión de nuevo.")
                    st.rerun()
            except ValueError:
                logout()
                st.rerun()
        
        # Actualizar timestamp de última actividad
        st.session_state["last_activity"] = datetime.now().isoformat()

def login() -> None:
    """
    Controla el formulario y los intentos de inicio de sesión.
    """
    # Inyectar estilos personalizados para centrar y dar diseño premium
    st.markdown("""
    <style>
    /* Ocultar elementos predeterminados de Streamlit */
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
    </style>
    """, unsafe_allow_html=True)
    
    # Centrado vertical/horizontal mediante columnas de Streamlit
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Sistema de Gestión</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Introduce tus credenciales para acceder</div>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Usuario", placeholder="Nombre de usuario", key="username_field")
            password = st.text_input("Contraseña", type="password", placeholder="Contraseña", key="password_field")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit:
                if not username.strip() or not password.strip():
                    st.error("Por favor, completa todos los campos.")
                else:
                    if "failed_attempts" not in st.session_state:
                        st.session_state["failed_attempts"] = 0
                        
                    # Penalización por más de 3 intentos erróneos
                    if st.session_state["failed_attempts"] >= 3:
                        st.warning("Demasiados intentos fallidos. Esperando 5 segundos antes de validar...")
                        time.sleep(5)
                    
                    success, user_info = check_credentials(username.strip(), password.strip())
                    
                    if success and user_info:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user_info["username"]
                        st.session_state["full_name"] = user_info["full_name"]
                        st.session_state["email"] = user_info["email"]
                        st.session_state["last_activity"] = datetime.now().isoformat()
                        st.session_state["failed_attempts"] = 0
                        st.success("Acceso concedido.")
                        st.rerun()
                    else:
                        st.session_state["failed_attempts"] = st.session_state.get("failed_attempts", 0) + 1
                        st.error("Credenciales inválidas.")
                        
        st.markdown('</div>', unsafe_allow_html=True)

def logout() -> None:
    """
    Cierra la sesión limpiando el st.session_state.
    """
    keys_to_clear = ["authenticated", "username", "full_name", "email", "last_activity", "failed_attempts"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def protect_page() -> bool:
    """
    Protege la página actual de Streamlit.
    Retorna True si el usuario está autenticado, False en caso contrario.
    Dibuja el login en caso de no estar autenticado.
    """
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        
    check_timeout()
    
    if not st.session_state["authenticated"]:
        login()
        return False
    
    # Mostrar barra lateral con información del usuario y botón de salida
    mostrar_sidebar_usuario()
    return True

def mostrar_sidebar_usuario() -> None:
    """
    Agrega información del usuario logueado y botón de logout en la barra lateral.
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**Bienvenido, {st.session_state.get('full_name', '')}**")
        st.caption(f"Usuario: {st.session_state.get('username', '')}")
        st.caption(f"Email: {st.session_state.get('email', '')}")
        
        if st.button("Cerrar Sesión", use_container_width=True):
            logout()
            st.rerun()

def get_current_user() -> dict | None:
    """
    Retorna información estructurada del usuario logueado en la sesión activa.
    """
    if st.session_state.get("authenticated", False):
        return {
            "username": st.session_state.get("username"),
            "full_name": st.session_state.get("full_name"),
            "email": st.session_state.get("email")
        }
    return None
