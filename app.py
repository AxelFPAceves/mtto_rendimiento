import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Dashboard Eficiencia Mtto", layout="wide")
st.title("🛠️ Análisis de Eficiencia de Mantenimiento")

@st.cache_data
def load_data():
    # Leer el archivo original directo de tu repositorio
    df = pd.read_csv('reportes_de_manto.csv')
    
    # Convertir fechas asegurando el formato correcto
    date_cols = ['FECHA DEL REPORTE', 'FECHA DE REALIZACIÓN DEL TRABAJO', 'FECHA DE CIERRE TICKET FORMS', 'FECHA PAGO']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
        
    # Cálculos de tiempo (en días)
    # Dilación de mtto (Realización - Reporte)
    df['Tiempo_Operacion_Dias'] = (df['FECHA DE REALIZACIÓN DEL TRABAJO'] - df['FECHA DEL REPORTE']).dt.total_seconds() / (24*3600)
    # Brecha administrativa
    df['Brecha_Admin_Dias'] = (df['FECHA DE CIERRE TICKET FORMS'] - df['FECHA DE REALIZACIÓN DEL TRABAJO']).dt.total_seconds() / (24*3600)
    # Vida total del ticket
    df['Tiempo_Total_Dias'] = (df['FECHA DE CIERRE TICKET FORMS'] - df['FECHA DEL REPORTE']).dt.total_seconds() / (24*3600)
    # Tiempo de pago (Pago - Realización)
    df['Tiempo_Pago_Dias'] = (df['FECHA PAGO'] - df['FECHA DE REALIZACIÓN DEL TRABAJO']).dt.total_seconds() / (24*3600)
    
    # Extraer mes y año para la gráfica de tendencia de pagos
    df['Mes_Realizacion'] = df['FECHA DE REALIZACIÓN DEL TRABAJO'].dt.to_period('M').astype(str)
    
    # Rango de costo (para agrupar barras de cobro)
    bins = [-1, 0, 1000, 5000, 10000, 1000000]
    labels = ['Gratis (0)', 'Bajo (<1k)', 'Medio (1k-5k)', 'Alto (5k-10k)', 'Muy Alto (>10k)']
    df['Rango_Costo'] = pd.cut(df['COSTO DE MANTENIMIENTO'].fillna(0), bins=bins, labels=labels)
    
    return df

df = load_data()

# Paleta corporativa (sin Triage: sin rojo, verde o amarillo)
colores_corp = ['#1f77b4', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#17becf', '#000080']

# ==========================================
# NUEVAS GRÁFICAS PRINCIPALES
# ==========================================
st.header("Nuevos Indicadores")

c1, c2 = st.columns(2)

with c1:
    st.subheader("1. Dilación Promedio de Mantenimiento por Sucursal")
    # Promedio del tiempo de operación, agrupado por sucursal
    df_suc_dil = df.groupby('SUCURSAL')['Tiempo_Operacion_Dias'].mean().reset_index().sort_values('Tiempo_Operacion_Dias', ascending=False)
    
    fig_suc_dil = px.bar(
        df_suc_dil, 
        x='SUCURSAL', 
        y='Tiempo_Operacion_Dias',
        color='SUCURSAL',
        color_discrete_sequence=colores_corp,
        labels={'Tiempo_Operacion_Dias': 'Días Promedio (Reporte a Realización)'}
    )
    fig_suc_dil.update_layout(showlegend=False)
    st.plotly_chart(fig_suc_dil, use_container_width=True)

with c2:
    st.subheader("2. Tiempo Promedio de Pago Global por Mes")
    # Filtrar solo los tickets que sí tienen fecha de pago
    df_pagos = df.dropna(subset=['Tiempo_Pago_Dias', 'Mes_Realizacion'])
    df_pagos_mes = df_pagos.groupby('Mes_Realizacion')['Tiempo_Pago_Dias'].mean().reset_index().sort_values('Mes_Realizacion')
    
    fig_pagos = px.line(
        df_pagos_mes, 
        x='Mes_Realizacion', 
        y='Tiempo_Pago_Dias', 
        markers=True,
        labels={'Mes_Realizacion': 'Mes del Mantenimiento', 'Tiempo_Pago_Dias': 'Días Promedio (Realización a Pago)'},
        color_discrete_sequence=['#1f77b4'] # Azul corporativo
    )
    st.plotly_chart(fig_pagos, use_container_width=True)

st.markdown("---")

# ==========================================
# GRÁFICOS ANTERIORES
# ==========================================
st.header("Gráficos Generales Detallados")

# Métricas Principales
col1, col2, col3 = st.columns(3)
col1.metric("Tiempo Total Promedio (Días)", f"{df['Tiempo_Total_Dias'].mean():.1f}")
col2.metric("Tiempo de Operación Promedio", f"{df['Tiempo_Operacion_Dias'].mean():.1f}")
col3.metric("Brecha Admin Promedio", f"{df['Brecha_Admin_Dias'].mean():.1f}")

st.markdown("---")

# Fila 1
c3, c4 = st.columns(2)

with c3:
    st.subheader("Tiempo de Operación vs Prioridad")
    fig_prio = px.box(df, x="PRIORIDAD", y="Tiempo_Operacion_Dias", color="PRIORIDAD",
                      color_discrete_sequence=colores_corp,
                      labels={"Tiempo_Operacion_Dias": "Días de Operación"})
    st.plotly_chart(fig_prio, use_container_width=True)

with c4:
    st.subheader("Brecha Administrativa vs Costo")
    df_costo = df.groupby('Rango_Costo', observed=False)['Brecha_Admin_Dias'].mean().reset_index()
    fig_costo = px.bar(df_costo, x="Rango_Costo", y="Brecha_Admin_Dias", 
                       color_discrete_sequence=['#9467bd'], # Morado corporativo
                       labels={"Brecha_Admin_Dias": "Días hasta Cierre de Ticket", "Rango_Costo": "Rango de Costo"})
    st.plotly_chart(fig_costo, use_container_width=True)

# Fila 2
st.markdown("---")
c5, c6 = st.columns(2)

with c5:
    st.subheader("Tiempo Total por Sucursal")
    df_suc = df.groupby('SUCURSAL')['Tiempo_Total_Dias'].mean().reset_index().sort_values('Tiempo_Total_Dias', ascending=False)
    fig_suc = px.bar(df_suc, x='SUCURSAL', y='Tiempo_Total_Dias', color='SUCURSAL',
                     color_discrete_sequence=colores_corp)
    fig_suc.update_layout(showlegend=False)
    st.plotly_chart(fig_suc, use_container_width=True)

with c6:
    st.subheader("Tiempo Total por Categoría")
    df_cat = df.groupby('CATEGORÍA')['Tiempo_Total_Dias'].mean().reset_index().sort_values('Tiempo_Total_Dias', ascending=True)
    fig_cat = px.bar(df_cat, y='CATEGORÍA', x='Tiempo_Total_Dias', orientation='h',
                     color_discrete_sequence=['#7f7f7f']) # Gris corporativo
    st.plotly_chart(fig_cat, use_container_width=True)
