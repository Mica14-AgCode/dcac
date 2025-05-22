import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import json
import io
from datetime import datetime, timedelta
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import geopandas as gpd
from shapely.geometry import Polygon
import zipfile

# ================================
# CONFIGURACIÓN DE PÁGINA
# ================================

st.set_page_config(
    page_title="OneClickLending - La Radiografía del Productor",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4478a7 0%, #7aa0c3 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: white;
        margin: 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4478a7;
    }
    .status-success {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #c3e6cb;
    }
    .status-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #ffeaa7;
    }
    .status-danger {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #f5c6cb;
    }
    .highlight-banner {
        background-color: #8aba5f;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# FUNCIONES DE GOOGLE DRIVE
# ================================

@st.cache_data
def authenticate_google_drive():
    """Autenticar con Google Drive usando Service Account"""
    # En producción, usar service account key
    # Por ahora simulamos la conexión
    return True

@st.cache_data
def load_analysis_from_drive(cuit):
    """Cargar análisis desde Google Drive basado en CUIT"""
    # Simulación de datos que vendrían de Google Drive
    # En producción, aquí iría la lógica real de Google Drive API
    
    if cuit == "30-12345678-9":
        return {
            'cuit': cuit,
            'razon_social': 'Agrícola Los Robles S.A.',
            'superficie_total': 2500,
            'superficie_agricola': 2000,
            'departamento': 'San Justo',
            'provincia': 'Santa Fe',
            'poligonos_geojson': {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"id": "P001", "tipo": "Agricola", "superficie": 1200},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[[-60.710, -31.569], [-60.710, -31.582], [-60.690, -31.582], [-60.690, -31.569], [-60.710, -31.569]]]
                        }
                    },
                    {
                        "type": "Feature", 
                        "properties": {"id": "P002", "tipo": "Agricola", "superficie": 800},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[[-60.710, -31.590], [-60.710, -31.600], [-60.690, -31.600], [-60.690, -31.590], [-60.710, -31.590]]]
                        }
                    }
                ]
            },
            'rotacion_cultivos': pd.DataFrame({
                'campania': ['19-20', '20-21', '21-22', '22-23', '23-24'],
                'soja': [45, 40, 35, 30, 25],
                'maiz': [30, 35, 40, 45, 50],
                'girasol': [10, 5, 5, 5, 5],
                'maiz_2da': [5, 10, 10, 10, 10],
                'no_agricola': [10, 10, 10, 10, 10]
            }),
            'rendimientos': {
                'propios': pd.DataFrame({
                    'cultivo': ['Maíz', 'Soja', 'Girasol'],
                    'rendimiento_5': [8500, 3800, 2200],
                    'rendimiento_10': [7200, 3500, 2000]
                }),
                'departamento': pd.DataFrame({
                    'cultivo': ['Maíz', 'Soja', 'Girasol'],
                    'rendimiento_5': [7800, 3500, 2000],
                    'rendimiento_10': [6900, 3200, 1800]
                })
            },
            'finanzas': {
                'ingresos_totales': 875000,
                'venta_cultivos': 850000,
                'otros_ingresos': 25000,
                'costos_produccion': 320000,
                'alquileres': 120000,
                'gastos_maquinaria': 85000,
                'fletes': 65000,
                'impuestos': 75000,
                'otros_gastos': 35000,
                'servicio_deuda_actual': 95000,
                'egresos_totales': 795000,
                'saldo_neto': 80000,
                'activos_totales': 2300000,
                'hacienda': 520000,
                'ratio_servicio_deuda': 1.84,
                'deuda_activos': 0.12,
                'deuda_hacienda': 0.18
            },
            'credito': {
                'score_nosis': 720,
                'cheques_rechazados': 0,
                'transacciones_dcac': 12,
                'pagos_realizados': 180000,
                'credito_pagos': 0.53,
                'consultas_nosis': 1.5,
                'creditos_bancos': 2,
                'garantias': {
                    'prenda_hacienda': True,
                    'garantia_personal': True,
                    'hipoteca': True
                }
            },
            'comparativa_mercado': {
                'percentil_apalancamiento': 35,
                'percentil_productividad': 78,
                'percentil_score_credito': 82
            }
        }
    else:
        return None

def get_available_producers():
    """Obtener lista de productores disponibles desde Google Drive"""
    # En producción, esto consultaría las carpetas en Google Drive
    return [
        {"cuit": "30-12345678-9", "razon_social": "Agrícola Los Robles S.A."},
        {"cuit": "30-98765432-1", "razon_social": "El Amanecer S.R.L."},
        {"cuit": "20-45678912-3", "razon_social": "Campos del Sur"},
        {"cuit": "30-56789012-3", "razon_social": "Agro Pampeano S.A."},
        {"cuit": "20-78901234-5", "razon_social": "Establecimiento La Loma"}
    ]

# ================================
# FUNCIONES DE GRÁFICOS
# ================================

def create_rotation_chart(df_rotacion):
    """Crear gráfico de rotación de cultivos"""
    fig = go.Figure()
    
    colors = {
        'soja': '#7aa0c3',
        'maiz': '#4478a7', 
        'girasol': '#FFD740',
        'maiz_2da': '#8aba5f',
        'no_agricola': '#e0e0e0'
    }
    
    for cultivo in ['soja', 'maiz', 'girasol', 'maiz_2da', 'no_agricola']:
        if cultivo in df_rotacion.columns:
            fig.add_trace(go.Bar(
                name=cultivo.replace('_', ' ').title(),
                x=df_rotacion['campania'],
                y=df_rotacion[cultivo],
                marker_color=colors[cultivo]
            ))
    
    fig.update_layout(
        title="Evolución de Cultivos por Campaña (%)",
        xaxis_title="Campaña",
        yaxis_title="Porcentaje (%)",
        barmode='stack',
        height=400,
        showlegend=True
    )
    
    return fig

def create_rendimientos_chart(rendimientos):
    """Crear gráfico comparativo de rendimientos"""
    propios = rendimientos['propios']
    departamento = rendimientos['departamento']
    
    fig = go.Figure()
    
    # Rendimientos propios 5 años
    fig.add_trace(go.Bar(
        name='Propio 5 años',
        x=propios['cultivo'],
        y=propios['rendimiento_5'],
        marker_color='#4478a7'
    ))
    
    # Rendimientos departamento 5 años
    fig.add_trace(go.Bar(
        name='Departamento 5 años',
        x=departamento['cultivo'],
        y=departamento['rendimiento_5'],
        marker_color='#7aa0c3'
    ))
    
    # Rendimientos propios 10 años
    fig.add_trace(go.Bar(
        name='Propio 10 años',
        x=propios['cultivo'],
        y=propios['rendimiento_10'],
        marker_color='#8aba5f'
    ))
    
    # Rendimientos departamento 10 años
    fig.add_trace(go.Bar(
        name='Departamento 10 años',
        x=departamento['cultivo'],
        y=departamento['rendimiento_10'],
        marker_color='#a5d683'
    ))
    
    fig.update_layout(
        title="Comparativa de Rendimientos (kg/ha)",
        xaxis_title="Cultivo",
        yaxis_title="Rendimiento (kg/ha)",
        barmode='group',
        height=400
    )
    
    return fig

def create_cashflow_chart(finanzas):
    """Crear gráfico de flujo de caja"""
    saldo_sin_deuda = finanzas['ingresos_totales'] - (finanzas['egresos_totales'] - finanzas['servicio_deuda_actual'])
    
    fig = go.Figure()
    
    # Ingresos
    fig.add_trace(go.Bar(
        name='Ingresos',
        x=['Sin Deuda', 'Con Deuda Actual'],
        y=[finanzas['ingresos_totales'], finanzas['ingresos_totales']],
        marker_color='#8aba5f'
    ))
    
    # Egresos sin deuda
    fig.add_trace(go.Bar(
        name='Egresos sin deuda',
        x=['Sin Deuda', 'Con Deuda Actual'],
        y=[finanzas['egresos_totales'] - finanzas['servicio_deuda_actual'], 0],
        marker_color='#7aa0c3'
    ))
    
    # Egresos con deuda
    fig.add_trace(go.Bar(
        name='Egresos con deuda',
        x=['Sin Deuda', 'Con Deuda Actual'],
        y=[0, finanzas['egresos_totales']],
        marker_color='#4478a7'
    ))
    
    # Saldo como línea
    fig.add_trace(go.Scatter(
        name='Saldo',
        x=['Sin Deuda', 'Con Deuda Actual'],
        y=[saldo_sin_deuda, finanzas['saldo_neto']],
        mode='lines+markers',
        line=dict(color='#ffa000', width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="Comparativa de Flujo de Caja",
        xaxis_title="Escenario",
        yaxis_title="USD",
        yaxis2=dict(title="Saldo (USD)", overlaying='y', side='right'),
        barmode='stack',
        height=400
    )
    
    return fig

def create_score_gauge(score):
    """Crear gauge del score crediticio"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Score Nosis"},
        delta = {'reference': 600},
        gauge = {
            'axis': {'range': [None, 1000]},
            'bar': {'color': "#2ecc71"},
            'steps': [
                {'range': [0, 600], 'color': "#f8d7da"},
                {'range': [600, 750], 'color': "#fff3cd"},
                {'range': [750, 1000], 'color': "#d4edda"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 600
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_map(geojson_data):
    """Crear mapa con polígonos"""
    # Calcular centro del mapa
    coords = []
    for feature in geojson_data['features']:
        for coord_pair in feature['geometry']['coordinates'][0]:
            coords.append(coord_pair)
    
    center_lat = sum(coord[1] for coord in coords) / len(coords)
    center_lon = sum(coord[0] for coord in coords) / len(coords)
    
    # Crear mapa
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    # Añadir polígonos
    for feature in geojson_data['features']:
        color = '#8aba5f' if feature['properties']['tipo'] == 'Agricola' else '#e0e0e0'
        
        folium.GeoJson(
            feature,
            style_function=lambda x, color=color: {
                'fillColor': color,
                'color': '#4478a7',
                'weight': 2,
                'fillOpacity': 0.7
            },
            popup=folium.Popup(
                f"<b>ID:</b> {feature['properties']['id']}<br>"
                f"<b>Tipo:</b> {feature['properties']['tipo']}<br>"
                f"<b>Superficie:</b> {feature['properties']['superficie']:,} ha",
                max_width=300
            )
        ).add_to(m)
    
    return m

def create_percentile_chart(percentil, title):
    """Crear gráfico de percentil"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = percentil,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#4478a7"},
            'steps': [
                {'range': [0, 25], 'color': "#f8d7da"},
                {'range': [25, 50], 'color': "#fff3cd"},
                {'range': [50, 75], 'color': "#d1ecf1"},
                {'range': [75, 100], 'color': "#d4edda"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig

# ================================
# SIMULADOR DE CRÉDITOS
# ================================

def calculate_loan_simulation(monto, tasa_anual, plazo_meses, tipo_pago, frecuencia):
    """Calcular simulación de crédito"""
    pagos_por_anio = {'mensual': 12, 'trimestral': 4, 'semestral': 2, 'anual': 1}[frecuencia]
    tasa_periodo = tasa_anual / 100 / pagos_por_anio
    numero_pagos = int(plazo_meses / (12 / pagos_por_anio))
    
    if tipo_pago == 'cuota_fija':
        # Sistema francés
        cuota = monto * (tasa_periodo * (1 + tasa_periodo)**numero_pagos) / ((1 + tasa_periodo)**numero_pagos - 1)
        interes_total = (cuota * numero_pagos) - monto
    elif tipo_pago == 'cuota_variable':
        # Sistema alemán
        capital_fijo = monto / numero_pagos
        cuota_primera = capital_fijo + (monto * tasa_periodo)
        interes_total = monto * tasa_periodo * (numero_pagos + 1) / 2
        cuota = cuota_primera  # Para mostrar
    else:  # bullet
        cuota = monto * tasa_periodo
        interes_total = cuota * numero_pagos
    
    return {
        'monto': monto,
        'tasa_anual': tasa_anual,
        'plazo_meses': plazo_meses,
        'tipo_pago': tipo_pago,
        'frecuencia': frecuencia,
        'cuota': cuota,
        'numero_pagos': numero_pagos,
        'interes_total': interes_total,
        'monto_total': monto + interes_total,
        'cuota_anual': cuota * pagos_por_anio
    }

def create_amortization_table(simulacion):
    """Crear tabla de amortización"""
    rows = []
    saldo_capital = simulacion['monto']
    tasa_periodo = simulacion['tasa_anual'] / 100 / 12  # Mensual para simplicidad
    
    for i in range(1, min(simulacion['numero_pagos'] + 1, 13)):  # Mostrar máximo 12 cuotas
        interes = saldo_capital * tasa_periodo
        
        if simulacion['tipo_pago'] == 'cuota_fija':
            cuota = simulacion['cuota']
            capital = cuota - interes
        elif simulacion['tipo_pago'] == 'cuota_variable':
            capital = simulacion['monto'] / simulacion['numero_pagos']
            cuota = capital + interes
        else:  # bullet
            capital = simulacion['monto'] if i == simulacion['numero_pagos'] else 0
            cuota = interes + capital
        
        saldo_capital -= capital
        fecha = datetime.now() + timedelta(days=30 * i)
        
        rows.append({
            'Nº Pago': i,
            'Fecha': fecha.strftime('%d/%m/%Y'),
            'Cuota': f"${cuota:,.2f}",
            'Interés': f"${interes:,.2f}",
            'Capital': f"${capital:,.2f}",
            'Saldo': f"${max(0, saldo_capital):,.2f}"
        })
    
    return pd.DataFrame(rows)

# ================================
# HEADER PRINCIPAL
# ================================

st.markdown("""
<div class="main-header">
    <h1>🚜 OneClickLending</h1>
    <p>La Radiografía del Productor - Sistema Integrado de Análisis Agrícola</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="highlight-banner">
    🎯 Dar créditos nunca fue tan fácil
</div>
""", unsafe_allow_html=True)

# ================================
# SIDEBAR - BÚSQUEDA
# ================================

with st.sidebar:
    st.title("🔍 Buscar Productor")
    
    # Tipo de búsqueda
    tipo_busqueda = st.selectbox(
        "Buscar por:",
        ["CUIT", "Razón Social"],
        help="Seleccione el tipo de búsqueda que desea realizar"
    )
    
    # Obtener productores disponibles
    productores = get_available_producers()
    
    if tipo_busqueda == "CUIT":
        cuit_options = [p["cuit"] for p in productores]
        cuit_selected = st.selectbox(
            "Seleccione CUIT:",
            [""] + cuit_options,
            help="Seleccione un CUIT de la lista de productores disponibles"
        )
        
        if cuit_selected:
            # Buscar datos del productor
            with st.spinner("Cargando análisis desde Google Drive..."):
                datos_productor = load_analysis_from_drive(cuit_selected)
    else:
        razon_options = [p["razon_social"] for p in productores]
        razon_selected = st.selectbox(
            "Seleccione Razón Social:",
            [""] + razon_options,
            help="Seleccione una razón social de la lista"
        )
        
        if razon_selected:
            # Encontrar CUIT correspondiente
            cuit_selected = next(p["cuit"] for p in productores if p["razon_social"] == razon_selected)
            with st.spinner("Cargando análisis desde Google Drive..."):
                datos_productor = load_analysis_from_drive(cuit_selected)
    
    # Información adicional en sidebar
    st.markdown("---")
    st.markdown("### 📊 Datos Disponibles")
    st.info(f"**{len(productores)}** productores en base de datos")
    
    st.markdown("### 🔧 Funcionalidades")
    st.markdown("""
    - ✅ Análisis de polígonos RENSPA
    - ✅ Comparativa de rendimientos
    - ✅ Evaluación crediticia
    - ✅ Simulador de préstamos
    - ✅ Mapas interactivos
    - ✅ Descarga de archivos
    """)

# ================================
# CONTENIDO PRINCIPAL
# ================================

# Verificar si hay datos cargados
if 'datos_productor' in locals() and datos_productor:
    
    # ================================
    # TABS PRINCIPALES
    # ================================
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Información General", 
        "🌾 Rendimientos", 
        "💰 Flujo de Caja",
        "📈 Métricas de Crédito",
        "🏦 Simulador",
        "📊 Comparativa"
    ])
    
    # ================================
    # TAB 1: INFORMACIÓN GENERAL
    # ================================
    
    with tab1:
        st.header(f"📊 Datos del Productor: {datos_productor['razon_social']}")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Superficie Total",
                f"{datos_productor['superficie_total']:,} ha",
                help="Superficie total del establecimiento"
            )
        
        with col2:
            st.metric(
                "Superficie Agrícola", 
                f"{datos_productor['superficie_agricola']:,} ha",
                help="Superficie destinada a agricultura"
            )
        
        with col3:
            porcentaje_agricola = (datos_productor['superficie_agricola'] / datos_productor['superficie_total']) * 100
            st.metric(
                "% Agrícola",
                f"{porcentaje_agricola:.1f}%",
                help="Porcentaje de superficie destinada a agricultura"
            )
        
        with col4:
            st.metric(
                "Ubicación",
                f"{datos_productor['departamento']}, {datos_productor['provincia']}",
                help="Ubicación del establecimiento"
            )
        
        st.markdown("---")
        
        # Gráfico de rotación y mapa
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🌱 Rotación de Cultivos (2019-2024)")
            fig_rotacion = create_rotation_chart(datos_productor['rotacion_cultivos'])
            st.plotly_chart(fig_rotacion, use_container_width=True)
        
        with col2:
            st.subheader("🗺️ Polígonos Productivos")
            mapa = create_map(datos_productor['poligonos_geojson'])
            st_folium(mapa, height=400, width=None)
        
        # Botones de descarga
        st.markdown("---")
        st.subheader("📥 Descargar Archivos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Botón descarga GeoJSON
            geojson_str = json.dumps(datos_productor['poligonos_geojson'], indent=2)
            st.download_button(
                label="📄 Descargar GeoJSON",
                data=geojson_str,
                file_name=f"{datos_productor['cuit']}_poligonos.geojson",
                mime="application/json"
            )
        
        with col2:
            # Botón descarga CSV de rotación
            csv = datos_productor['rotacion_cultivos'].to_csv(index=False)
            st.download_button(
                label="📊 Descargar Rotación CSV",
                data=csv,
                file_name=f"{datos_productor['cuit']}_rotacion.csv",
                mime="text/csv"
            )
    
    # ================================
    # TAB 2: RENDIMIENTOS
    # ================================
    
    with tab2:
        st.header("🌾 Análisis de Rendimientos")
        
        # Gráfico comparativo
        fig_rendimientos = create_rendimientos_chart(datos_productor['rendimientos'])
        st.plotly_chart(fig_rendimientos, use_container_width=True)
        
        st.markdown("---")
        
        # Tabla comparativa detallada
        st.subheader("📋 Detalle de Rendimientos (kg/ha)")
        
        propios = datos_productor['rendimientos']['propios']
        departamento = datos_productor['rendimientos']['departamento']
        
        # Crear tabla comparativa
        tabla_rendimientos = []
        for i, row in propios.iterrows():
            cultivo = row['cultivo']
            depto_row = departamento[departamento['cultivo'] == cultivo].iloc[0]
            
            diferencia_5 = row['rendimiento_5'] - depto_row['rendimiento_5']
            diferencia_10 = row['rendimiento_10'] - depto_row['rendimiento_10']
            
            tabla_rendimientos.append({
                'Cultivo': cultivo,
                'Propio 5 años': f"{row['rendimiento_5']:,}",
                'Departamento 5 años': f"{depto_row['rendimiento_5']:,}",
                'Diferencia 5 años': f"{diferencia_5:+,} ({(diferencia_5/depto_row['rendimiento_5']*100):+.1f}%)",
                'Propio 10 años': f"{row['rendimiento_10']:,}",
                'Departamento 10 años': f"{depto_row['rendimiento_10']:,}",
                'Diferencia 10 años': f"{diferencia_10:+,} ({(diferencia_10/depto_row['rendimiento_10']*100):+.1f}%)"
            })
        
        df_tabla = pd.DataFrame(tabla_rendimientos)
        st.dataframe(df_tabla, use_container_width=True)
        
        # Insights automáticos
        st.markdown("---")
        st.subheader("🎯 Insights Automáticos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cultivo con mejor performance
            mejor_cultivo = None
            mejor_diferencia = -float('inf')
            
            for i, row in propios.iterrows():
                cultivo = row['cultivo']
                depto_row = departamento[departamento['cultivo'] == cultivo].iloc[0]
                diferencia_pct = (row['rendimiento_5'] - depto_row['rendimiento_5']) / depto_row['rendimiento_5'] * 100
                
                if diferencia_pct > mejor_diferencia:
                    mejor_diferencia = diferencia_pct
                    mejor_cultivo = cultivo
            
            if mejor_diferencia > 0:
                st.markdown(f"""
                <div class="status-success">
                    <strong>🏆 Mejor Performance:</strong><br>
                    {mejor_cultivo} supera al promedio departamental en {mejor_diferencia:.1f}%
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-warning">
                    <strong>⚠️ Área de Mejora:</strong><br>
                    Todos los cultivos están por debajo del promedio departamental
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Consistencia temporal
            consistente = True
            for i, row in propios.iterrows():
                if row['rendimiento_5'] < row['rendimiento_10'] * 0.9:  # Si cayó más del 10%
                    consistente = False
                    break
            
            if consistente:
                st.markdown("""
                <div class="status-success">
                    <strong>📈 Tendencia Positiva:</strong><br>
                    Los rendimientos se mantienen estables o mejoran en el tiempo
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="status-warning">
                    <strong>📉 Tendencia Descendente:</strong><br>
                    Algunos rendimientos han disminuido en los últimos 5 años
                </div>
                """, unsafe_allow_html=True)
    
    # ================================
    # TAB 3: FLUJO DE CAJA
    # ================================
    
    with tab3:
        st.header("💰 Análisis de Flujo de Caja")
        
        finanzas = datos_productor['finanzas']
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            saldo_sin_deuda = finanzas['ingresos_totales'] - (finanzas['egresos_totales'] - finanzas['servicio_deuda_actual'])
            st.metric(
                "Saldo sin deuda",
                f"${saldo_sin_deuda:,}",
                help="Flujo de caja sin considerar servicio de deuda actual"
            )
        
        with col2:
            st.metric(
                "Saldo con deuda actual",
                f"${finanzas['saldo_neto']:,}",
                help="Flujo de caja actual considerando todas las obligaciones"
            )
        
        with col3:
            st.metric(
                "Ratio Servicio de Deuda",
                f"{finanzas['ratio_servicio_deuda']:.2f}",
                help="Capacidad de pago de deuda (>1.5 recomendado)"
            )
        
        with col4:
            st.metric(
                "Deuda/Activos",
                f"{finanzas['deuda_activos']:.2f}",
                help="Nivel de apalancamiento (<0.15 recomendado)"
            )
        
        # Gráfico de flujo de caja
        fig_cashflow = create_cashflow_chart(finanzas)
        st.plotly_chart(fig_cashflow, use_container_width=True)
        
        st.markdown("---")
        
        # Tabla detallada de flujo de caja
        st.subheader("📊 Flujo de Caja Detallado")
        
        cashflow_data = [
            {"Concepto": "INGRESOS", "Monto (USD)": "", "% del Total": "", "Tipo": "header"},
            {"Concepto": "Venta de Cultivos", "Monto (USD)": finanzas['venta_cultivos'], "% del Total": f"{finanzas['venta_cultivos']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "normal"},
            {"Concepto": "Otros Ingresos", "Monto (USD)": finanzas['otros_ingresos'], "% del Total": f"{finanzas['otros_ingresos']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "normal"},
            {"Concepto": "Total Ingresos", "Monto (USD)": finanzas['ingresos_totales'], "% del Total": "100.0%", "Tipo": "subtotal"},
            {"Concepto": "EGRESOS", "Monto (USD)": "", "% del Total": "", "Tipo": "header"},
            {"Concepto": "Costos de Producción", "Monto (USD)": finanzas['costos_produccion'], "% del Total": f"{finanzas['costos_produccion']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "normal"},
            {"Concepto": "Alquileres", "Monto (USD)": finanzas['alquileres'], "% del Total": f"{finanzas['alquileres']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "normal"},
            {"Concepto": "Gastos de Maquinaria", "Monto (USD)": finanzas['gastos_maquinaria'], "% del Total": f"{finanzas['gastos_maquinaria']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "normal"},
            {"Concepto": "Fletes", "Monto (USD)": finanzas['fletes'], "% del Total": f"{finanzas['fletes']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "normal"},
            {"Concepto": "Impuestos", "Monto (USD)": finanzas['impuestos'], "% del Total": f"{finanzas['impuestos']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "normal"},
            {"Concepto": "Otros Gastos", "Monto (USD)": finanzas['otros_gastos'], "% del Total": f"{finanzas['otros_gastos']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "normal"},
            {"Concepto": "Servicio de Deuda Actual", "Monto (USD)": finanzas['servicio_deuda_actual'], "% del Total": f"{finanzas['servicio_deuda_actual']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "highlight"},
            {"Concepto": "Total Egresos", "Monto (USD)": finanzas['egresos_totales'], "% del Total": f"{finanzas['egresos_totales']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "subtotal"},
            {"Concepto": "SALDO NETO", "Monto (USD)": finanzas['saldo_neto'], "% del Total": f"{finanzas['saldo_neto']/finanzas['ingresos_totales']*100:.1f}%", "Tipo": "total"}
        ]
        
        # Mostrar tabla con formato
        for item in cashflow_data:
            if item["Tipo"] == "header":
                st.markdown(f"**{item['Concepto']}**")
            elif item["Tipo"] == "normal":
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(item["Concepto"])
                with col2:
                    st.write(f"${item['Monto (USD)']:,}")
                with col3:
                    st.write(item["% del Total"])
            elif item["Tipo"] == "highlight":
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{item['Concepto']}**")
                with col2:
                    st.markdown(f"**${item['Monto (USD)']:,}**")
                with col3:
                    st.markdown(f"**{item['% del Total']}**")
            elif item["Tipo"] in ["subtotal", "total"]:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{item['Concepto']}**")
                with col2:
                    st.markdown(f"**${item['Monto (USD)']:,}**")
                with col3:
                    st.markdown(f"**{item['% del Total']}**")
                if item["Tipo"] == "subtotal":
                    st.markdown("---")
    
    # ================================
    # TAB 4: MÉTRICAS DE CRÉDITO
    # ================================
    
    with tab4:
        st.header("📈 Evaluación Crediticia")
        
        credito = datos_productor['credito']
        
        # Score crediticio destacado
        col1, col2 = st.columns([1, 2])
        
        with col1:
            fig_score = create_score_gauge(credito['score_nosis'])
            st.plotly_chart(fig_score, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Calificación Crediticia")
            
            if credito['score_nosis'] >= 750:
                status_class = "status-success"
                status_text = "EXCELENTE"
            elif credito['score_nosis'] >= 600:
                status_class = "status-warning" 
                status_text = "BUENO"
            else:
                status_class = "status-danger"
                status_text = "RIESGO"
            
            st.markdown(f"""
            <div class="{status_class}">
                <strong>Score Nosis:</strong> {credito['score_nosis']}/1000<br>
                <strong>Calificación:</strong> {status_text}<br>
                <strong>Cheques Rechazados:</strong> {credito['cheques_rechazados']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Métricas adicionales
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric("Transacciones DCAC", credito['transacciones_dcac'], help="Últimos 12 meses")
                st.metric("Crédito/Pagos", f"{credito['credito_pagos']:.2f}", help="Ratio de utilización")
            
            with col_b:
                st.metric("Pagos Realizados", f"${credito['pagos_realizados']:,}", help="Total en DCAC")
                st.metric("Consultas Nosis", f"{credito['consultas_nosis']:.1f}", help="Últimos 3 meses")
        
        st.markdown("---")
        
        # Criterios de aprobación
        st.subheader("✅ Criterios de Aprobación")
        
        criterios = [
            {"categoria": "Historial DCAC", "criterios": [
                ("Transacciones >= 3", credito['transacciones_dcac'] >= 3),
                ("Crédito < Pagos realizados", credito['credito_pagos'] < 1.0)
            ]},
            {"categoria": "Ratios Financieros", "criterios": [
                ("Deuda/Activos <= 0.15", datos_productor['finanzas']['deuda_activos'] <= 0.15),
                ("Deuda/Hacienda <= 0.25", datos_productor['finanzas']['deuda_hacienda'] <= 0.25),
                ("Ratio Servicio Deuda >= 1.5", datos_productor['finanzas']['ratio_servicio_deuda'] >= 1.5)
            ]},
            {"categoria": "Calificación Crediticia", "criterios": [
                ("Score Nosis >= 600", credito['score_nosis'] >= 600),
                ("Cheques Rechazados = 0", credito['cheques_rechazados'] == 0),
                ("Créditos con Bancos <= 3", credito['creditos_bancos'] <= 3),
                ("Consultas Nosis <= 1.5", credito['consultas_nosis'] <= 1.5)
            ]},
            {"categoria": "Garantías", "criterios": [
                ("Prenda sobre hacienda", credito['garantias']['prenda_hacienda']),
                ("Garantía personal", credito['garantias']['garantia_personal']),
                ("Potencial de Hipoteca", credito['garantias']['hipoteca'])
            ]}
        ]
        
        for categoria_info in criterios:
            st.markdown(f"**{categoria_info['categoria']}**")
            
            for criterio, cumple in categoria_info['criterios']:
                if cumple:
                    st.markdown(f"✅ {criterio} - **CUMPLE**")
                else:
                    st.markdown(f"❌ {criterio} - **NO CUMPLE**")
            
            st.markdown("")
        
        # Resumen de aprobación
        total_criterios = sum(len(cat['criterios']) for cat in criterios)
        criterios_cumplidos = sum(sum(1 for _, cumple in cat['criterios'] if cumple) for cat in criterios)
        porcentaje_aprobacion = (criterios_cumplidos / total_criterios) * 100
        
        st.markdown("---")
        st.subheader("📊 Resumen de Evaluación")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Criterios Cumplidos", f"{criterios_cumplidos}/{total_criterios}")
        
        with col2:
            st.metric("% de Aprobación", f"{porcentaje_aprobacion:.1f}%")
        
        with col3:
            if porcentaje_aprobacion >= 80:
                recomendacion = "APROBAR"
                color_class = "status-success"
            elif porcentaje_aprobacion >= 60:
                recomendacion = "APROBAR CON CONDICIONES"
                color_class = "status-warning"
            else:
                recomendacion = "RECHAZAR"
                color_class = "status-danger"
            
            st.markdown(f"""
            <div class="{color_class}">
                <strong>Recomendación:</strong><br>{recomendacion}
            </div>
            """, unsafe_allow_html=True)
    
    # ================================
    # TAB 5: SIMULADOR
    # ================================
    
    with tab5:
        st.header("🏦 Simulador de Créditos")
        
        # Formulario de simulación
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 Parámetros del Crédito")
            
            monto_credito = st.number_input(
                "Monto del Préstamo (USD)",
                min_value=1000,
                max_value=1000000,
                value=50000,
                step=1000,
                help="Monto total del préstamo solicitado"
            )
            
            tasa_interes = st.number_input(
                "Tasa de Interés Anual (%)",
                min_value=1.0,
                max_value=30.0,
                value=7.5,
                step=0.1,
                help="Tasa de interés anual del préstamo"
            )
            
            plazo_credito = st.number_input(
                "Plazo (meses)",
                min_value=1,
                max_value=60,
                value=12,
                help="Plazo del préstamo en meses"
            )
            
            tipo_pago = st.selectbox(
                "Tipo de Pago",
                ["cuota_fija", "cuota_variable", "bullet"],
                format_func=lambda x: {
                    "cuota_fija": "Cuota Fija (Sistema Francés)",
                    "cuota_variable": "Cuota Variable (Sistema Alemán)", 
                    "bullet": "Bullet (Interés + Capital al final)"
                }[x],
                help="Sistema de amortización del préstamo"
            )
            
            frecuencia_pago = st.selectbox(
                "Frecuencia de Pago",
                ["mensual", "trimestral", "semestral", "anual"],
                format_func=str.title,
                help="Frecuencia de pago de las cuotas"
            )
            
            if st.button("🔄 Simular Crédito", type="primary"):
                # Realizar simulación
                simulacion = calculate_loan_simulation(
                    monto_credito, tasa_interes, plazo_credito, tipo_pago, frecuencia_pago
                )
                
                # Guardar en session state
                st.session_state['simulacion'] = simulacion
        
        with col2:
            if 'simulacion' in st.session_state:
                simulacion = st.session_state['simulacion']
                
                st.subheader("📊 Resultados de la Simulación")
                
                # Métricas de la simulación
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric("Monto", f"${simulacion['monto']:,.0f}")
                    st.metric("Plazo", f"{simulacion['plazo_meses']} meses")
                
                with col_b:
                    st.metric("Tasa Anual", f"{simulacion['tasa_anual']:.1f}%")
                    st.metric("Cuota", f"${simulacion['cuota']:,.2f}")
                
                with col_c:
                    st.metric("Interés Total", f"${simulacion['interes_total']:,.2f}")
                    st.metric("Monto Total", f"${simulacion['monto_total']:,.2f}")
                
                # Evaluación de capacidad de pago
                st.markdown("---")
                st.subheader("⚖️ Evaluación de Capacidad de Pago")
                
                finanzas = datos_productor['finanzas']
                cuota_anual_nueva = simulacion['cuota_anual']
                porcentaje_flujo = (cuota_anual_nueva / finanzas['saldo_neto']) * 100
                nuevo_ratio_servicio = finanzas['saldo_neto'] / (finanzas['servicio_deuda_actual'] + cuota_anual_nueva)
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric(
                        "% del Flujo de Caja",
                        f"{porcentaje_flujo:.1f}%",
                        help="Porcentaje del flujo de caja que representa la nueva cuota"
                    )
                
                with col_b:
                    delta_ratio = nuevo_ratio_servicio - finanzas['ratio_servicio_deuda']
                    st.metric(
                        "Nuevo Ratio Servicio Deuda",
                        f"{nuevo_ratio_servicio:.2f}",
                        delta=f"{delta_ratio:+.2f}",
                        help="Nuevo ratio de servicio de deuda con el crédito"
                    )
                
                # Evaluación
                if nuevo_ratio_servicio >= 1.5:
                    st.markdown("""
                    <div class="status-success">
                        <strong>✅ CAPACIDAD DE PAGO ADECUADA</strong><br>
                        El productor puede afrontar el nuevo crédito sin problemas.
                    </div>
                    """, unsafe_allow_html=True)
                elif nuevo_ratio_servicio >= 1.2:
                    st.markdown("""
                    <div class="status-warning">
                        <strong>⚠️ CAPACIDAD DE PAGO AJUSTADA</strong><br>
                        El productor puede afrontar el crédito con precaución.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="status-danger">
                        <strong>❌ CAPACIDAD DE PAGO INSUFICIENTE</strong><br>
                        El productor no puede afrontar el nuevo crédito.
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("👆 Configure los parámetros y haga clic en 'Simular Crédito' para ver los resultados")
        
        # Tabla de amortización
        if 'simulacion' in st.session_state:
            st.markdown("---")
            st.subheader("📋 Tabla de Amortización")
            
            df_amortizacion = create_amortization_table(st.session_state['simulacion'])
            st.dataframe(df_amortizacion, use_container_width=True)
            
            # Botón de descarga
            csv_amortizacion = df_amortizacion.to_csv(index=False)
            st.download_button(
                "📥 Descargar Tabla de Amortización",
                csv_amortizacion,
                f"amortizacion_{datos_productor['cuit']}.csv",
                "text/csv"
            )
    
    # ================================
    # TAB 6: COMPARATIVA DE MERCADO
    # ================================
    
    with tab6:
        st.header("📊 Posicionamiento en el Mercado")
        
        comparativa = datos_productor['comparativa_mercado']
        
        # Gráficos de percentiles
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_apal = create_percentile_chart(comparativa['percentil_apalancamiento'], "Apalancamiento")
            st.plotly_chart(fig_apal, use_container_width=True)
            st.markdown(f"**{100-comparativa['percentil_apalancamiento']}%** de productores tienen mayor apalancamiento")
        
        with col2:
            fig_prod = create_percentile_chart(comparativa['percentil_productividad'], "Productividad")
            st.plotly_chart(fig_prod, use_container_width=True)
            st.markdown(f"Mejor que el **{comparativa['percentil_productividad']}%** de productores")
        
        with col3:
            fig_score = create_percentile_chart(comparativa['percentil_score_credito'], "Score Crediticio")
            st.plotly_chart(fig_score, use_container_width=True)
            st.markdown(f"Mejor que el **{comparativa['percentil_score_credito']}%** de productores")
        
        st.markdown("---")
        
        # Distribución del mercado simulada
        st.subheader("📈 Distribución del Mercado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de distribución de apalancamiento
            np.random.seed(42)
            distribucion_apal = np.random.beta(2, 5, 1000) * 100
            
            fig_dist_apal = px.histogram(
                x=distribucion_apal,
                nbins=20,
                title="Distribución de Apalancamiento en el Mercado"
            )
            fig_dist_apal.add_vline(
                x=comparativa['percentil_apalancamiento'],
                line_dash="dash",
                line_color="red",
                annotation_text="Su posición"
            )
            fig_dist_apal.update_layout(height=300)
            st.plotly_chart(fig_dist_apal, use_container_width=True)
        
        with col2:
            # Gráfico de distribución de score crediticio
            distribucion_score = np.random.beta(3, 2, 1000) * 100
            
            fig_dist_score = px.histogram(
                x=distribucion_score,
                nbins=20,
                title="Distribución de Score Crediticio en el Mercado"
            )
            fig_dist_score.add_vline(
                x=comparativa['percentil_score_credito'],
                line_dash="dash",
                line_color="red",
                annotation_text="Su posición"
            )
            fig_dist_score.update_layout(height=300)
            st.plotly_chart(fig_dist_score, use_container_width=True)
        
        st.markdown("---")
        
        # Resumen comparativo
        st.subheader("🎯 Resumen Comparativo")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Clasificación general
            percentil_promedio = np.mean([
                comparativa['percentil_apalancamiento'],
                comparativa['percentil_productividad'],
                comparativa['percentil_score_credito']
            ])
            
            if percentil_promedio >= 80:
                clasificacion = "PREMIUM"
                desc_clasif = "Top 20% del mercado"
                color_clasif = "status-success"
            elif percentil_promedio >= 60:
                clasificacion = "ALTO"
                desc_clasif = "Top 40% del mercado"
                color_clasif = "status-success"
            elif percentil_promedio >= 40:
                clasificacion = "MEDIO"
                desc_clasif = "Promedio del mercado"
                color_clasif = "status-warning"
            else:
                clasificacion = "BÁSICO"
                desc_clasif = "Por debajo del promedio"
                color_clasif = "status-danger"
            
            st.markdown(f"""
            <div class="{color_clasif}">
                <strong>Clasificación General:</strong><br>
                {clasificacion}<br>
                <small>{desc_clasif}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Riesgo crediticio
            score = datos_productor['credito']['score_nosis']
            if score >= 750:
                riesgo = "MUY BAJO"
                color_riesgo = "status-success"
            elif score >= 600:
                riesgo = "BAJO"
                color_riesgo = "status-success"
            elif score >= 500:
                riesgo = "MEDIO"
                color_riesgo = "status-warning"
            else:
                riesgo = "ALTO"
                color_riesgo = "status-danger"
            
            st.markdown(f"""
            <div class="{color_riesgo}">
                <strong>Riesgo Crediticio:</strong><br>
                {riesgo}<br>
                <small>Score {score}/1000</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Capacidad de pago
            ratio = datos_productor['finanzas']['ratio_servicio_deuda']
            if ratio >= 2.0:
                capacidad = "MUY ALTA"
                color_cap = "status-success"
            elif ratio >= 1.5:
                capacidad = "ALTA"
                color_cap = "status-success"
            elif ratio >= 1.2:
                capacidad = "MEDIA"
                color_cap = "status-warning"
            else:
                capacidad = "BAJA"
                color_cap = "status-danger"
            
            st.markdown(f"""
            <div class="{color_cap}">
                <strong>Capacidad de Pago:</strong><br>
                {capacidad}<br>
                <small>Ratio {ratio:.2f}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Recomendación final
            if percentil_promedio >= 70 and score >= 600 and ratio >= 1.5:
                recomendacion = "APROBAR"
                desc_rec = "Cliente objetivo"
                color_rec = "status-success"
            elif percentil_promedio >= 50 and score >= 500 and ratio >= 1.2:
                recomendacion = "APROBAR CON CONDICIONES"
                desc_rec = "Revisar términos"
                color_rec = "status-warning"
            else:
                recomendacion = "EVALUAR DETALLADAMENTE"
                desc_rec = "Requiere análisis adicional"
                color_rec = "status-danger"
            
            st.markdown(f"""
            <div class="{color_rec}">
                <strong>Recomendación:</strong><br>
                {recomendacion}<br>
                <small>{desc_rec}</small>
            </div>
            """, unsafe_allow_html=True)

else:
    # ================================
    # MENSAJE INICIAL
    # ================================
    
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2>🔍 Seleccione un Productor para Analizar</h2>
        <p style="font-size: 1.2rem; color: #666;">
            Utilice el panel lateral para buscar por CUIT o Razón Social.<br>
            Los análisis se cargan automáticamente desde Google Drive.
        </p>
        
        <div style="margin: 2rem 0;">
            <h3>🚀 Funcionalidades Disponibles:</h3>
            <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 1rem; margin-top: 1rem;">
                <div style="background: #f8f0ff; padding: 1rem; border-radius: 8px; min-width: 200px;">
                    <strong>📈 Métricas de Crédito</strong><br>
                    <small>Evaluación crediticia, criterios de aprobación</small>
                </div>
                <div style="background: #f0f8f8; padding: 1rem; border-radius: 8px; min-width: 200px;">
                    <strong>🏦 Simulador</strong><br>
                    <small>Simulación de créditos, tabla de amortización</small>
                </div>
                <div style="background: #f8f8f0; padding: 1rem; border-radius: 8px; min-width: 200px;">
                    <strong>📊 Comparativa</strong><br>
                    <small>Posicionamiento en el mercado, percentiles</small>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 2rem; padding: 1rem; background: #f0f8ff; border-radius: 8px;">
            <h4>🔧 Integración con Google Drive</h4>
            <p>El sistema está configurado para cargar automáticamente los análisis desde las carpetas de Google Drive organizadas por CUIT.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================================
# FOOTER
# ================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; background: #4478a7; color: white; border-radius: 8px; margin-top: 2rem;">
    <h3>🚜 OneClickLending</h3>
    <p>La Radiografía del Productor - Sistema Integrado de Análisis Agrícola con Google Earth Engine</p>
    <p><strong>Contacto:</strong> pepo@riverwoodag.com | micaias@riverwoodag.com</p>
    <p><small>© 2025 OneClickLending - Todos los derechos reservados</small></p>
</div>
""", unsafe_allow_html=True)1rem;">
                <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; min-width: 200px;">
                    <strong>📊 Información General</strong><br>
                    <small>Polígonos, rotación de cultivos, mapas interactivos</small>
                </div>
                <div style="background: #f0fff0; padding: 1rem; border-radius: 8px; min-width: 200px;">
                    <strong>🌾 Rendimientos</strong><br>
                    <small>Comparativas vs departamento, análisis temporal</small>
                </div>
                <div style="background: #fff8f0; padding: 1rem; border-radius: 8px; min-width: 200px;">
                    <strong>💰 Flujo de Caja</strong><br>
                    <small>Análisis financiero detallado, ratios clave</small>
                </div>
            </div>
            <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 1rem; margin-top: 
