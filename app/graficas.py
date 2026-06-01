import streamlit as st
import pandas as pd
import plotly.express as px


def generar_grafica(df: pd.DataFrame) -> None:
    st.markdown(
        '<div id="graficas-section" style="scroll-margin-top: 5rem;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.subheader("Generador de Graficas")

    columnas = df.columns.tolist()
    columnas_numericas = df.select_dtypes(include=["number"]).columns.tolist()
    columnas_categoricas = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if not columnas_numericas:
        st.warning("No hay columnas numéricas para generar gráficas.")
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        default_x = columnas_categoricas[0] if columnas_categoricas else columnas[0]
        col_x = st.selectbox("Eje X", columnas, index=columnas.index(default_x), key="graf_x")
    with col2:
        col_y = st.selectbox("Eje Y", columnas_numericas, key="graf_y")
    with col3:
        tipo = st.selectbox("Tipo", ["Barras", "Líneas", "Área"], key="graf_tipo")
    with col4:
        agregacion = st.selectbox("Agregación", ["Suma", "Promedio", "Conteo"], key="graf_agr")

    if st.button("Generar Visualización", key="graf_btn"):
        try:
            if agregacion == "Suma":
                df_grouped = df.groupby(col_x)[col_y].sum().reset_index()
            elif agregacion == "Promedio":
                df_grouped = df.groupby(col_x)[col_y].mean().reset_index()
            else:
                df_grouped = df.groupby(col_x)[col_y].count().reset_index()

            titulo = f"{agregacion} de {col_y} por {col_x}"

            if tipo == "Barras":
                fig = px.bar(df_grouped, x=col_x, y=col_y, title=titulo)
            elif tipo == "Líneas":
                fig = px.line(df_grouped, x=col_x, y=col_y, title=titulo, markers=True)
            else:
                fig = px.area(df_grouped, x=col_x, y=col_y, title=titulo)

            fig.update_layout(
                xaxis_title=col_x,
                yaxis_title=col_y,
                height=420,
            )

            st.plotly_chart(fig, use_container_width=True)
            st.caption("LAS GRAFICAS NO SE GUARDARN EN EL CHAT. Usa el ícono de la cámara en la esquina del gráfico para descargarlo como PNG.")

            with st.expander("Ver tabla de datos agrupados"):
                st.dataframe(df_grouped, use_container_width=True)

        except Exception as e:
            st.error(f"Error al generar gráfica: {e}")
