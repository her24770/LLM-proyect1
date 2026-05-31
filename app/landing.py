import base64
from pathlib import Path

import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
HERO_IMAGE = ASSETS_DIR / "landing-hero.png"


def _image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def render_landing_page() -> None:
    hero_image = _image_data_uri(HERO_IMAGE)

    st.markdown(
        f"""
        <style>
        #MainMenu, header, footer {{
            visibility: hidden;
        }}

        .block-container {{
            max-width: 1200px;
            padding-top: 1.25rem;
            padding-bottom: 3rem;
        }}

        .landing-hero {{
            min-height: min(720px, calc(100vh - 48px));
            border-radius: 20px;
            overflow: hidden;
            position: relative;
            padding: clamp(22px, 4vw, 44px);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background:
                linear-gradient(135deg, rgba(6,10,16,0.96) 0%, rgba(6,10,16,0.82) 38%, rgba(6,10,16,0.25) 72%),
                url("{hero_image}");
            background-size: cover;
            background-position: center right;
            box-shadow: 0 24px 64px rgba(0,0,0,0.4);
        }}

        .landing-nav {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            color: rgba(255,255,255,0.9);
            font-family: Inter, system-ui, sans-serif;
        }}

        .landing-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.98rem;
            font-weight: 800;
        }}

        .brand-mark {{
            width: 36px;
            height: 36px;
            display: inline-grid;
            place-items: center;
            border-radius: 10px;
            background: linear-gradient(135deg, #62d6c8, #3eb8ab);
            color: #0a1018;
            font-weight: 900;
            box-shadow: 0 4px 14px rgba(98,214,200,0.4);
        }}

        .landing-nav-actions {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}

        .landing-login-link {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 36px;
            padding: 0 14px;
            border-radius: 8px;
            color: rgba(255,255,255,0.85) !important;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.06);
            font-size: 0.88rem;
            font-weight: 700;
            text-decoration: none;
            white-space: nowrap;
            font-family: Inter, system-ui, sans-serif;
        }}

        .landing-register-link {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 36px;
            padding: 0 14px;
            border-radius: 8px;
            color: #0a1018 !important;
            background: linear-gradient(135deg, #62d6c8, #3eb8ab);
            font-size: 0.88rem;
            font-weight: 800;
            text-decoration: none;
            white-space: nowrap;
            font-family: Inter, system-ui, sans-serif;
            box-shadow: 0 4px 14px rgba(98,214,200,0.35);
        }}

        .landing-copy {{
            max-width: 650px;
            padding: 88px 0 44px;
            color: #ffffff;
            font-family: Inter, system-ui, sans-serif;
        }}

        .landing-eyebrow {{
            color: #62d6c8;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: .06em;
            text-transform: uppercase;
            margin-bottom: 14px;
        }}

        .landing-title {{
            font-size: clamp(2.8rem, 5.5vw, 5rem);
            line-height: 0.95;
            font-weight: 900;
            color: #ffffff;
            margin: 0 0 8px;
        }}

        .landing-copy p {{
            margin: 22px 0 0;
            max-width: 560px;
            color: rgba(255,255,255,0.75);
            font-size: 1.1rem;
            line-height: 1.65;
        }}

        .landing-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 32px;
        }}

        .landing-actions a {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 48px;
            padding: 0 24px;
            border-radius: 12px;
            text-decoration: none;
            font-weight: 800;
            font-family: Inter, system-ui, sans-serif;
            font-size: 0.95rem;
        }}

        .landing-primary {{
            color: #0a1018 !important;
            background: linear-gradient(135deg, #62d6c8, #3eb8ab);
            box-shadow: 0 6px 24px rgba(98,214,200,0.4);
        }}

        .landing-secondary {{
            color: #ffffff !important;
            border: 1px solid rgba(255,255,255,0.22);
            background: rgba(255,255,255,0.06);
        }}

        .landing-proof {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin: 18px 0 28px;
        }}

        .proof-item {{
            padding: 22px;
            border-radius: 14px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
        }}

        .proof-item strong {{
            display: block;
            color: #fff;
            font-family: Inter, system-ui, sans-serif;
            font-size: 0.96rem;
            font-weight: 700;
            margin-bottom: 6px;
        }}

        .proof-item span {{
            color: rgba(255,255,255,0.52);
            font-family: Inter, system-ui, sans-serif;
            line-height: 1.5;
            font-size: 0.9rem;
        }}

        @media (max-width: 760px) {{
            .block-container {{
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }}
            .landing-hero {{
                min-height: 680px;
                padding: 22px;
                background-position: center;
            }}
            .landing-copy {{
                padding: 72px 0 28px;
            }}
            .landing-title {{
                font-size: 2.6rem;
            }}
            .landing-copy p {{
                font-size: 1rem;
            }}
            .landing-actions a {{
                width: 100%;
            }}
            .landing-proof {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>

        <section class="landing-hero">
            <nav class="landing-nav" aria-label="Principal">
                <div class="landing-brand">
                    <span class="brand-mark">IA</span>
                    <span>SalesAI</span>
                </div>
                <div class="landing-nav-actions">
                    <a class="landing-login-link" href="./?login=1" target="_self">Iniciar sesion</a>
                    <a class="landing-register-link" href="./?register=1" target="_self">Registrarse</a>
                </div>
            </nav>
            <div class="landing-copy">
                <div class="landing-eyebrow">Analitica de ventas con IA</div>
                <div class="landing-title">Sistema de Gestion IA</div>
                <p>
                    Sube tu archivo CSV o Excel y obtén análisis automático,
                    respuestas en lenguaje natural y visualizaciones listas para decidir.
                </p>
                <div class="landing-actions">
                    <a class="landing-primary" href="./?register=1" target="_self">Empezar gratis</a>
                    <a class="landing-secondary" href="./?login=1" target="_self">Ya tengo cuenta</a>
                </div>
            </div>
        </section>

        <section class="landing-proof">
            <div class="proof-item">
                <strong>Analisis automatico</strong>
                <span>Carga CSV o Excel y recibe tendencias, alertas y métricas clave en segundos.</span>
            </div>
            <div class="proof-item">
                <strong>Chat con tus datos</strong>
                <span>Guarda multiples conversaciones y retomalas cuando quieras.</span>
            </div>
            <div class="proof-item">
                <strong>Graficas dinamicas</strong>
                <span>Genera barras, lineas y areas desde las columnas de tu archivo.</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
