import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Dashboard Eficiencia Mtto", layout="wide")
st.title("🛠️ Análisis de Eficiencia de Mantenimiento")

# Cargar el archivo procesado que generamos
@st.cache_data
def load_data():
    df = pd.read_csv('reportes_procesados_para_streamlit.csv')
    # Definir orden de categorías de costo
    df['Rango_Costo'] = pd.Categorical(df['Rango_Costo'], 
        categories=['Gratis (0)', 'Bajo (<1k)', 'Medio (1k-5k)', 'Alto (5k-10k)', 'Muy Alto (>10k)'], 
        ordered=True)
    return df

df = load_data()

# Métricas Principales
col1, col2, col3 = st.columns(3)
col1.metric("Tiempo Total Promedio (Días)", f"{df['Tiempo_Total_Dias'].mean():.1f}")
col2.metric("Tiempo de Operación Promedio", f"{df['Tiempo_Operacion_Dias'].mean():.1f}")
col3.metric("Brecha Admin Promedio", f"{df['Brecha_Admin_Dias'].mean():.1f}")

st.markdown("---")

# Fila 1 de Gráficos
c1, c2 = st.columns(2)

with c1:
    st.subheader("Tiempo de Operación vs Prioridad")
    fig_prio = px.box(df, x="PRIORIDAD", y="Tiempo_Operacion_Dias", color="PRIORIDAD",
                      labels={"Tiempo_Operacion_Dias": "Días de Operación"})
    st.plotly_chart(fig_prio, use_container_width=True)

with c2:
    st.subheader("Brecha Administrativa vs Costo")
    # Agrupamos promedios
    df_costo = df.groupby('Rango_Costo', observed=False)['Brecha_Admin_Dias'].mean().reset_index()
    fig_costo = px.bar(df_costo, x="Rango_Costo", y="Brecha_Admin_Dias", 
                       labels={"Brecha_Admin_Dias": "Días hasta Cierre de Ticket", "Rango_Costo": "Rango de Costo"})
    st.plotly_chart(fig_costo, use_container_width=True)

# Fila 2 de Gráficos
st.markdown("---")
c3, c4 = st.columns(2)

with c3:
    st.subheader("Tiempo Total por Sucursal")
    df_suc = df.groupby('SUCURSAL')['Tiempo_Total_Dias'].mean().reset_index().sort_values('Tiempo_Total_Dias', ascending=False)
    fig_suc = px.bar(df_suc, x='SUCURSAL', y='Tiempo_Total_Dias', color='Tiempo_Total_Dias',
                     color_continuous_scale='Reds')
    st.plotly_chart(fig_suc, use_container_width=True)

with c4:
    st.subheader("Tiempo Total por Categoría")
    df_cat = df.groupby('CATEGORÍA')['Tiempo_Total_Dias'].mean().reset_index().sort_values('Tiempo_Total_Dias', ascending=True)
    fig_cat = px.bar(df_cat, y='CATEGORÍA', x='Tiempo_Total_Dias', orientation='h',
                     color='Tiempo_Total_Dias', color_continuous_scale='Reds')
    st.plotly_chart(fig_cat, use_container_width=True)
