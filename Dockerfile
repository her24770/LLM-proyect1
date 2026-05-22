FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# Crear el directorio de datos y configurar permisos de escritura
RUN mkdir -p /app/data && chmod 777 /app/data

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501"]
