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