# Sistema de Gestión

Aplicación web construida con Streamlit y Python, con integración a OpenAI. Corre completamente en Docker.

## Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.11
- **IA:** OpenAI API
- **Contenedor:** Docker + Docker Compose

## Requisitos

- Docker
- Docker Compose

## Instalación y uso

1. Clona el repositorio y entra al directorio:

   ```bash
   git clone <repo-url>
   cd LLM-proyect1
   ```

2. Crea el archivo de variables de entorno:

   ```bash
   cp .env.example .env
   ```

3. Abre `.env` y agrega tu clave de OpenAI:

   ```
   OPENAI_API_KEY=sk-...
   ```

4. Levanta la aplicación:

   ```bash
   docker-compose up --build
   ```

5. Abre el navegador en [http://localhost:8501](http://localhost:8501)

## Estructura del proyecto

```
.
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── app/
    ├── main.py         # Entry point Streamlit
    ├── auth.py         # Autenticación
    ├── movimientos.py  # CRUD de movimientos
    ├── dashboard.py    # Dashboard principal
    ├── ia.py           # Cliente OpenAI
    └── reportes.py     # Generación de reportes
```

## Variables de entorno

| Variable | Descripción |
|---|---|
| `OPENAI_API_KEY` | Clave de API de OpenAI |
