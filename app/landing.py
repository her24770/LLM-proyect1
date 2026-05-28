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
            border-radius: 0;
            overflow: hidden;
            position: relative;
            padding: clamp(22px, 4vw, 44px);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background:
                linear-gradient(90deg, rgba(9, 13, 18, 0.92) 0%, rgba(9, 13, 18, 0.78) 38%, rgba(9, 13, 18, 0.2) 72%),
                linear-gradient(180deg, rgba(9, 13, 18, 0.1), rgba(9, 13, 18, 0.78)),
                url("{hero_image}");
            background-size: cover;
            background-position: center right;
            box-shadow: 0 18px 48px rgba(10, 18, 28, 0.22);
        }}

        .landing-nav {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            color: rgba(255, 255, 255, 0.9);
            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        .landing-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.98rem;
            font-weight: 750;
        }}

        .brand-mark {{
            width: 34px;
            height: 34px;
            display: inline-grid;
            place-items: center;
            border-radius: 8px;
            background: #f15b5b;
            color: #10151c;
            font-weight: 900;
        }}

        .landing-tag {{
            color: rgba(255, 255, 255, 0.78);
            font-size: 0.85rem;
            white-space: nowrap;
        }}

        .landing-login-link {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 36px;
            padding: 0 12px;
            border-radius: 8px;
            color: #10151c !important;
            background: #62d6c8;
            font-size: 0.9rem;
            font-weight: 800;
            text-decoration: none;
            white-space: nowrap;
        }}

        .landing-copy {{
            max-width: 650px;
            padding: 88px 0 44px;
            color: #ffffff;
            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        .landing-eyebrow {{
            color: #62d6c8;
            font-size: 0.85rem;
            font-weight: 800;
            letter-spacing: 0;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}

        .landing-copy h1 {{
            margin: 0;
            font-size: 5.4rem;
            line-height: 0.95;
            letter-spacing: 0;
            font-weight: 850;
            color: #ffffff;
        }}

        .landing-copy p {{
            margin: 24px 0 0;
            max-width: 580px;
            color: rgba(255, 255, 255, 0.82);
            font-size: 1.16rem;
            line-height: 1.62;
        }}

        .landing-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 30px;
        }}

        .landing-actions a {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 44px;
            padding: 0 18px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 800;
        }}

        .landing-primary {{
            color: #10151c !important;
            background: #62d6c8;
        }}

        .landing-secondary {{
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.26);
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
        }}

        .landing-proof {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin: 18px 0 28px;
        }}

        .proof-item {{
            padding: 20px;
            border: 1px solid rgba(20, 32, 42, 0.1);
            background: rgba(255, 255, 255, 0.82);
            border-radius: 8px;
            box-shadow: 0 12px 28px rgba(20, 32, 42, 0.08);
        }}

        .proof-item strong {{
            display: block;
            color: #17212b;
            font-size: 1.02rem;
            margin-bottom: 6px;
        }}

        .proof-item span {{
            color: #5d6975;
            line-height: 1.5;
            font-size: 0.94rem;
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

            .landing-tag {{
                display: none;
            }}

            .landing-login-link {{
                min-height: 34px;
                padding: 0 10px;
                font-size: 0.86rem;
            }}

            .landing-copy {{
                padding: 72px 0 28px;
            }}

            .landing-copy h1 {{
                font-size: 3.1rem;
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
                    <span>Sistema de Gestión</span>
                </div>
                <a class="landing-login-link" href="./?login=1" target="_self">Iniciar sesión</a>
            </nav>
            <div class="landing-copy">
                <div class="landing-eyebrow">Analítica de ventas con IA</div>
                <h1>Sistema de Gestión IA</h1>
                <p>
                    Convierte archivos de ventas en análisis claro, conversaciones con tus datos
                    y visualizaciones listas para decidir con más confianza.
                </p>
                <div class="landing-actions">
                    <a class="landing-primary" href="./?login=1" target="_self">Iniciar sesión</a>
                </div>
            </div>
        </section>

        <section id="capabilities" class="landing-proof">
            <div class="proof-item">
                <strong>Análisis inmediato</strong>
                <span>Carga CSV o Excel y recibe una primera lectura de tendencias, hallazgos y alertas.</span>
            </div>
            <div class="proof-item">
                <strong>Chat con datos</strong>
                <span>Consulta ventas, segmentos y métricas usando lenguaje natural.</span>
            </div>
            <div class="proof-item">
                <strong>Gráficas dinámicas</strong>
                <span>Genera barras, líneas y áreas desde las columnas de tu archivo.</span>
            </div>
        </section>

        """,
        unsafe_allow_html=True,
    )
