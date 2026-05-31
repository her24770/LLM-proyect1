# SalesAI — Asistente de Ventas con IA

Aplicación web construida con Streamlit y Python que permite analizar archivos de ventas usando IA. Los usuarios se registran, crean múltiples chats, suben archivos CSV/Excel y conversan con sus datos en lenguaje natural.

## Stack

- **Frontend/Backend:** Python 3.11 + Streamlit
- **IA:** OpenAI API (gpt-4o-mini)
- **Base de datos:** SQLite
- **Contenedor:** Docker + Docker Compose

## Funcionalidades

- Registro e inicio de sesión de usuarios (bcrypt + sesión con timeout de 8h)
- Múltiples chats por usuario, cada uno con su propio contexto y historial persistente
- Subida de archivos CSV y Excel — la IA analiza automáticamente al cargar
- Chat en lenguaje natural sobre los datos del archivo
- Generador de gráficas dinámicas (barras, líneas, área) en la sidebar
- Auto-renombrado del chat con IA al enviar el primer mensaje
- Renombrar y eliminar chats desde la sidebar
- **Análisis Global** — chat maestro único por usuario que accede al contexto estadístico de todos los chats para análisis histórico y comparativo entre periodos
- Contexto comprimido: se guardan estadísticas del archivo (no el archivo completo) para mantener el uso de tokens constante sin importar el tamaño del CSV

## Estructura del proyecto

```
.
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── app/
    ├── main.py         # Entry point
    ├── auth.py         # Registro, login, sesión, tablas DB
    ├── landing.py      # Landing page pública
    ├── dashboard.py    # Dashboard principal y sidebar de chats
    ├── chat.py         # Componente de chat con persistencia
    ├── chats.py        # CRUD de chats, contexto histórico
    ├── ia.py           # Cliente OpenAI (análisis, chat, nombres)
    ├── graficas.py     # Generador de visualizaciones
    ├── movimientos.py  # (pendiente)
    ├── reportes.py     # (pendiente)
    └── assets/
        └── landing-hero.png
```

## Base de datos

SQLite en `app/data/users.db`. Se crea automáticamente al iniciar.

| Tabla | Descripción |
|-------|-------------|
| `users` | Usuarios registrados con contraseña hasheada (bcrypt) |
| `chats` | Chats por usuario con nombre, contexto comprimido e indicador de chat maestro |
| `messages` | Historial de mensajes por chat (roles: user, assistant, system) |

## Requisitos

- Docker y Docker Compose

## Instalación local

```bash
git clone <repo-url>
cd LLM-proyect1

cp .env.example .env
# Editar .env y agregar OPENAI_API_KEY

docker compose up --build
```

Acceder en [http://localhost:8501](http://localhost:8501)

## Despliegue en servidor (producción)

El `docker-compose.yml` está configurado para producción: el puerto solo escucha en `127.0.0.1` y Nginx hace el proxy.

```bash
# En el servidor
git clone <repo-url> salesai
cd salesai
cp .env.example .env && nano .env  # agregar OPENAI_API_KEY
docker compose up -d
```

Config de Nginx necesaria (incluir headers de WebSocket para Streamlit):

```nginx
server {
    listen 80;
    server_name sales.jhgo.online;

    location / {
        proxy_pass http://127.0.0.1:8502;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `OPENAI_API_KEY` | Clave de API de OpenAI (requerida) |
