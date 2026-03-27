import streamlit as st
import pandas as pd

def generar_grafica(df) -> None:
    st.markdown("📊 Generador de Gráficas")
    
    # Identificar los tipos de columnas
    columnas = df.columns.tolist()
    columnas_numericas = df.select_dtypes(include=['number']).columns.tolist()
    columnas_categoricas = df.select_dtypes(include=['object', 'category']).columns.tolist()

    if not columnas_numericas:
        st.warning("⚠️ No hay columnas numéricas para generar gráficas.")
        return
    
    # Interfaz para la configuración de gráficas
    col1, col2 = st.columns(2)
    with col1:
        # Seleccion de columna para eje x
        default_x = columnas_categoricas[0] if columnas_categoricas else columnas[0]
        col_x = st.selectbox("Eje X (Categoría)", columnas, index=columnas.index(default_x))
    
    with col2:
        # Seleccion de columna para eje y (Solo datos numericos)
        col_y = st.selectbox("Eje Y (Valor)", columnas_numericas)

    tipo_grafica = st.selectbox("Tipo de Gráfica", ["Barras", "Líneas", "Área"])
    agregacion = st.radio("Agregación", ["Suma", "Promedio", "Conteo"], horizontal=True)

    if st.button("🚀 Generar Visualización"):
        try:
            # Usando pandas para agrupar los datos
            df_plot = df.copy()
            
            if agregacion == "Suma":
                df_grouped = df_plot.groupby(col_x)[col_y].sum().reset_index()
            elif agregacion == "Promedio":
                df_grouped = df_plot.groupby(col_x)[col_y].mean().reset_index()
            else: # Conteo
                df_grouped = df_plot.groupby(col_x)[col_y].count().reset_index()

            # Establecer X como indice para las graficas de Streamlit
            df_grouped = df_grouped.set_index(col_x)

            # Mostrar la grafica
            st.write(f"**{agregacion} de {col_y} por {col_x}**")
            
            if tipo_grafica == "Barras":
                st.bar_chart(df_grouped)
            elif tipo_grafica == "Líneas":
                st.line_chart(df_grouped)
            elif tipo_grafica == "Área":
                st.area_chart(df_grouped)
                
            # Mostrar la tabla
            with st.expander("Ver tabla de datos agrupados"):
                st.dataframe(df_grouped)

        except Exception as e:
            st.error(f"Error al generar gráfica: {e}")
            st.info("Asegúrate de que las columnas seleccionadas sean compatibles.")
