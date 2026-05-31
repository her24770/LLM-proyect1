import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analizar_datos(data: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Eres un analista de negocios experto en ventas."
            },
            {
                "role": "user",
                "content": f"""
                Analiza estos datos:

                {data}

                Dame:
                1. Insights clave
                2. Problemas detectados
                3. Recomendaciones para aumentar ingresos
                """
            }
        ]
    )

    return response.choices[0].message.content


def chat_con_datos(messages: list) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content


def generar_nombre_chat(primer_mensaje: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Genera un título muy corto (máximo 4 palabras) para una conversación "
                    "basándote en el primer mensaje del usuario. "
                    "Solo responde el título, sin comillas ni puntuación."
                ),
            },
            {"role": "user", "content": primer_mensaje},
        ],
        max_tokens=20,
    )
    return response.choices[0].message.content.strip()