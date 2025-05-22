import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math

# Configuración de la página
st.set_page_config(
    page_title="OneClickLending - La Radiografía del Productor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado inspirado en deCampoaCampo
st.markdown("""
<style>
    /* Reset y configuración base */
    .main > div {
        padding-top: 0rem;
    }
    
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    /* Variables de colores inspiradas en deCampoaCampo */
    :root {
        --dcac-green-primary: #2C7A2C;
        --dcac-green-secondary: #4A934A;
        --dcac-green-light: #7DB87D;
        --dcac-brown-primary: #8B4513;
        --dcac-brown-light: #D2B48C;
        --dcac-cream: #F5F5DC;
        --dcac-white: #FFFFFF;
        --dcac-gray-light: #F8F8F8;
        --dcac-gray-medium: #E5E5E5;
        --dcac-gray-dark: #666666;
        --dcac-text-dark: #333333;
    }
    
    /* Header principal con gradiente verde */
    .dcac-header {
        background: linear-gradient(135deg, var(--dcac-green-primary) 0%, var(--dcac-green-secondary) 100%);
        padding: 20px 0;
        margin-bottom: 0;
        box-shadow: 0 4px 12px rgba(44, 122, 44, 0.2);
    }
    
    .dcac-logo-container {
        text-align: center;
        margin-bottom: 15px;
    }
    
    .dcac-logo {
        font-size: 48px;
        font-weight: 700;
        color: var(--dcac-white);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 10px;
        letter-spacing: -1px;
    }
    
    .dcac-title {
        font-size: 32px;
        font-weight: 600;
        color: var(--dcac-white);
        margin: 15px 0 10px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .dcac-subtitle {
        font-size: 18px;
        color: var(--dcac-cream);
        margin: 0 0 20px 0;
        font-weight: 400;
        opacity: 0.9;
    }
    
    /* Banner de búsqueda */
    .dcac-search-banner {
        background: var(--dcac-cream);
        padding: 25px;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    
    .dcac-search-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--dcac-green-primary);
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Estilos para selectbox y inputs */
    .stSelectbox > div > div > div {
        background-color: var(--dcac-white);
        border: 2px solid var(--dcac-green-light);
        border-radius: 8px;
        font-size: 16px;
    }
    
    .stSelectbox > div > div > div:focus-within {
        border-color: var(--dcac-green-primary);
        box-shadow: 0 0 0 3px rgba(44, 122, 44, 0.1);
    }
    
    /* Botón de búsqueda */
    .stButton > button {
        background: linear-gradient(135deg, var(--dcac-green-primary) 0%, var(--dcac-green-secondary) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 4px 12px rgba(44, 122, 44, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(44, 122, 44, 0.4);
    }
    
    /* Visor principal */
    .dcac-viewer {
        background: var(--dcac-white);
        border-radius: 15px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid var(--dcac-gray-medium);
    }
    
    .dcac-viewer-title {
        font-size: 28px;
        font-weight: 700;
        color: var(--dcac-green-primary);
        margin-bottom: 20px;
        text-align: center;
        border-bottom: 3px solid var(--dcac-green-light);
        padding-bottom: 15px;
    }
    
    /* Dashboard de métricas */
    .dcac-dashboard {
        background: linear-gradient(135deg, var(--dcac-gray-light) 0%, var(--dcac-white) 100%);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        border: 1px solid var(--dcac-gray-medium);
    }
    
    .dcac-dashboard-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--dcac-green-primary);
        margin-bottom: 20px;
        text-align: center;
        border-bottom: 2px solid var(--dcac-green-light);
        padding-bottom: 10px;
    }
    
    /* Métricas individuales */
    .dcac-metric {
        background: var(--dcac-white);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid var(--dcac-green-primary);
        transition: all 0.3s ease;
    }
    
    .dcac-metric:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    .dcac-metric-label {
        font-size: 14px;
        font-weight: 600;
        color: var(--dcac-gray-dark);
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .dcac-metric-value {
        font-size: 32px;
        font-weight: 700;
        color: var(--dcac-green-primary);
        margin: 8px 0;
        line-height: 1;
    }
    
    .dcac-metric-subvalue {
        font-size: 13px;
        color: var(--dcac-gray-dark);
        font-weight: 500;
        opacity: 0.8;
    }
    
    /* Tabs mejoradas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--dcac-gray-light);
        border-radius: 12px;
        padding: 8px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--dcac-gray-dark);
        font-weight: 600;
        padding: 12px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--dcac-green-primary) 0%, var(--dcac-green-secondary) 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(44, 122, 44, 0.3);
    }
    
    /* Mapa/Polígonos placeholder */
    .dcac-map-placeholder {
        background: linear-gradient(135deg, var(--dcac-cream) 0%, var(--dcac-white) 100%);
        border: 2px dashed var(--dcac-green-light);
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        margin: 20px 0;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .dcac-map-icon {
        font-size: 64px;
        color: var(--dcac-green-light);
        margin-bottom: 20px;
    }
    
    .dcac-map-text {
        font-size: 18px;
        color: var(--dcac-gray-dark);
        font-weight: 500;
    }
    
    /* Tabla de polígonos */
    .dcac-polygon-table {
        background: var(--dcac-white);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    
    /* Progreso visual */
    .dcac-progress {
        background: var(--dcac-gray-medium);
        border-radius: 20px;
        height: 24px;
        margin: 10px 0;
        overflow: hidden;
        position: relative;
    }
    
    .dcac-progress-fill {
        height: 100%;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 12px;
        transition: width 0.8s ease;
        background: linear-gradient(90deg, var(--dcac-green-primary) 0%, var(--dcac-green-secondary) 100%);
    }
    
    /* Estados de progreso */
    .dcac-progress-excellent {
        background: linear-gradient(90deg, #2C7A2C 0%, #4A934A 100%);
    }
    
    .dcac-progress-good {
        background: linear-gradient(90deg, #7DB87D 0%, #9BC59B 100%);
    }
    
    .dcac-progress-warning {
        background: linear-gradient(90deg, #FF8C00 0%, #FFB347 100%);
    }
    
    .dcac-progress-danger {
        background: linear-gradient(90deg, #DC143C 0%, #FF6B6B 100%);
    }
    
    /* Mensaje inicial */
    .dcac-initial-message {
        background: linear-gradient(135deg, var(--dcac-cream) 0%, var(--dcac-white) 100%);
        border-radius: 20px;
        padding: 60px 40px;
        text-align: center;
        margin: 40px 0;
        border: 2px solid var(--dcac-green-light);
    }
    
    .dcac-initial-icon {
        font-size: 80px;
        color: var(--dcac-green-light);
        margin-bottom: 20px;
    }
    
    .dcac-initial-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--dcac-green-primary);
        margin-bottom: 10px;
    }
    
    .dcac-initial-subtitle {
        font-size: 16px;
        color: var(--dcac-gray-dark);
        opacity: 0.8;
    }
    
    /* Footer */
    .dcac-footer {
        background: linear-gradient(135deg, var(--dcac-green-primary) 0%, var(--dcac-brown-primary) 100%);
        color: var(--dcac-white);
        padding: 40px 0;
        margin-top: 50px;
        border-radius: 15px 15px 0 0;
    }
    
    .dcac-footer-content {
        text-align: center;
    }
    
    .dcac-footer-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .dcac-footer-text {
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 5px;
    }
    
    /* Efectos hover y transiciones */
    .dcac-card {
        transition: all 0.3s ease;
    }
    
    .dcac-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.15);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .dcac-logo {
            font-size: 36px;
        }
        
        .dcac-title {
            font-size: 24px;
        }
        
        .dcac-subtitle {
            font-size: 16px;
        }
        
        .dcac-metric-value {
            font-size: 24px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Datos de ejemplo
@st.cache_data
def load_data():
    productores_data = [
        {"cuit": "30-12345678-9", "razonSocial": "Agrícola Los Robles S.A."},
        {"cuit": "30-98765432-1", "razonSocial": "El Amanecer S.R.L."},
        {"cuit": "20-45678912-3", "razonSocial": "Campos del Sur"},
        {"cuit": "30-56789012-3", "razonSocial": "Agro Pampeano S.A."},
        {"cuit": "20-78901234-5", "razonSocial": "Establecimiento La Loma"}
    ]
    
    datos_analisis = {
        "30-12345678-9": {
            "cuit": "30-12345678-9",
            "razonSocial": "Agrícola Los Robles S.A.",
            "superficieTotal": 2500,
            "superficieAgricola": 2000,
            "superficieNoAgricola": 500,
            "porcentajeAgricola": 80,
            "departamento": "San Justo",
            "provincia": "Santa Fe",
            "poligonos": [
                {"id": "P001", "tipo": "Agrícola", "superficie": 1200, "cultivo": "Soja/Maíz"},
                {"id": "P002", "tipo": "Agrícola", "superficie": 800, "cultivo": "Girasol"},
                {"id": "P003", "tipo": "No Agrícola", "superficie": 500, "cultivo": "Pasturas"}
            ],
            "rotacionCultivos": [
                {"campania": "19-20", "soja": 45, "maiz": 30, "girasol": 10, "maiz2da": 5, "noAgricola": 10},
                {"campania": "20-21", "soja": 40, "maiz": 35, "girasol": 5, "maiz2da": 10, "noAgricola": 10},
                {"campania": "21-22", "soja": 35, "maiz": 40, "girasol": 5, "maiz2da": 10, "noAgricola": 10},
                {"campania": "22-23", "soja": 30, "maiz": 45, "girasol": 5, "maiz2da": 10, "noAgricola": 10},
                {"campania": "23-24", "soja": 25, "maiz": 50, "girasol": 5, "maiz2da": 10, "noAgricola": 10}
            ],
            "rendimientos": [
                {"cultivo": "Maíz", "rendimiento": 8500, "benchmark": 7800},
                {"cultivo": "Soja", "rendimiento": 3800, "benchmark": 3500},
                {"cultivo": "Girasol", "rendimiento": 2200, "benchmark": 2000}
            ],
            "finanzas": {
                "ingresosTotales": 875000,
                "egresosTotales": 795000,
                "saldoNeto": 80000,
                "ratioServicioDeuda": 1.84,
                "deudaActivos": 0.12,
                "scoreCredito": 720
            },
            "comparativaMercado": {
                "percentilProductividad": 78,
                "percentilScoreCredito": 82,
                "clasificacion": "PREMIUM"
            }
        }
    }
    
    return productores_data, datos_analisis

def crear_metric_visual(label, value, subvalue, icon="📊"):
    return f"""
    <div class="dcac-metric">
        <div style="font-size: 24px; margin-bottom: 10px;">{icon}</div>
        <div class="dcac-metric-label">{label}</div>
        <div class="dcac-metric-value">{value}</div>
        <div class="dcac-metric-subvalue">{subvalue}</div>
    </div>
    """

def crear_progress_bar(valor, maximo, tipo="excellent"):
    porcentaje = min((valor / maximo) * 100, 100)
    return f"""
    <div class="dcac-progress">
        <div class="dcac-progress-fill dcac-progress-{tipo}" style="width: {porcentaje}%;">
            {porcentaje:.1f}%
        </div>
    </div>
    """

def crear_mapa_placeholder():
    return """
    <div class="dcac-map-placeholder">
        <div class="dcac-map-icon">🗺️</div>
        <div class="dcac-map-text">Visualización de Polígonos Productivos</div>
        <div style="font-size: 14px; color: #999; margin-top: 10px;">
            Vista satelital con límites de campos y tipos de cultivos
        </div>
    </div>
    """

# Cargar datos
productores_data, datos_analisis = load_data()

# Header principal con logo
st.markdown("""
<div class="dcac-header">
    <div class="dcac-logo-container">
        <div class="dcac-logo">🌾 deCampoaCampo</div>
        <div style="font-size: 16px; color: var(--dcac-cream); opacity: 0.8; margin-bottom: 20px;">
            Mercado Ganadero Digital
        </div>
        <div class="dcac-title">OneClickLending</div>
        <div class="dcac-subtitle">La Radiografía del Productor</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Banner de búsqueda
st.markdown("""
<div class="dcac-search-banner">
    <div class="dcac-search-title">🔍 Consultar Productor</div>
</div>
""", unsafe_allow_html=True)

# Formulario de búsqueda en el centro
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    search_type = st.selectbox(
        "Buscar por:",
        ["CUIT", "Razón Social"],
        help="Seleccione el tipo de búsqueda"
    )
    
    if search_type == "CUIT":
        search_value = st.selectbox(
            "Seleccione un CUIT:",
            options=[""] + [p["cuit"] for p in productores_data],
            format_func=lambda x: x if x else "-- Seleccione un CUIT --"
        )
    else:
        search_value = st.selectbox(
            "Seleccione una Razón Social:",
            options=[""] + [p["razonSocial"] for p in productores_data],
            format_func=lambda x: x if x else "-- Seleccione una Razón Social --"
        )
    
    search_button = st.button("🔍 Consultar Productor", type="primary", use_container_width=True)

# Lógica principal: mostrar visor cuando se selecciona un productor
if search_value or search_button:
    # Buscar datos del productor
    productor_encontrado = None
    if search_type == "CUIT" and search_value:
        cuit_buscar = search_value
        productor_encontrado = datos_analisis.get(cuit_buscar)
    elif search_type == "Razón Social" and search_value:
        # Buscar por razón social
        for p in productores_data:
            if p["razonSocial"] == search_value:
                cuit_buscar = p["cuit"]
                productor_encontrado = datos_analisis.get(cuit_buscar)
                break
    
    if productor_encontrado:
        # VISOR PRINCIPAL
        st.markdown(f"""
        <div class="dcac-viewer">
            <div class="dcac-viewer-title">
                🏢 {productor_encontrado['razonSocial']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Layout principal: Mapa + Dashboard
        col_map, col_dashboard = st.columns([2, 1])
        
        with col_map:
            # Visor de mapa/polígonos
            st.markdown("### 🗺️ Visualización de Campos")
            st.markdown(crear_mapa_placeholder(), unsafe_allow_html=True)
            
            # Tabla de polígonos debajo del mapa
            st.markdown("### 📋 Detalle de Polígonos")
            
            poligonos_df = pd.DataFrame([
                {
                    'ID': p['id'],
                    'Tipo': p['tipo'],
                    'Superficie (ha)': f"{p['superficie']:,}",
                    'Cultivo/Uso': p['cultivo']
                } for p in productor_encontrado['poligonos']
            ])
            
            st.dataframe(
                poligonos_df, 
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "ID": st.column_config.TextColumn("ID", width="small"),
                    "Tipo": st.column_config.TextColumn("Tipo", width="medium"),
                    "Superficie (ha)": st.column_config.TextColumn("Superficie", width="medium"),
                    "Cultivo/Uso": st.column_config.TextColumn("Cultivo/Uso", width="medium")
                }
            )
        
        with col_dashboard:
            # Dashboard de métricas
            st.markdown("""
            <div class="dcac-dashboard">
                <div class="dcac-dashboard-title">📊 Dashboard Productivo</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Métricas principales
            st.markdown(crear_metric_visual(
                "Superficie Total", 
                f"{productor_encontrado['superficieTotal']:,}", 
                "hectáreas",
                "🌾"
            ), unsafe_allow_html=True)
            
            st.markdown(crear_metric_visual(
                "Superficie Agrícola", 
                f"{productor_encontrado['superficieAgricola']:,}", 
                f"{productor_encontrado['porcentajeAgricola']}% del total",
                "🚜"
            ), unsafe_allow_html=True)
            
            st.markdown(crear_metric_visual(
                "Superficie No Agrícola", 
                f"{productor_encontrado['superficieNoAgricola']:,}", 
                f"{100-productor_encontrado['porcentajeAgricola']}% del total",
                "🌿"
            ), unsafe_allow_html=True)
            
            st.markdown(crear_metric_visual(
                "Ubicación", 
                productor_encontrado['departamento'], 
                productor_encontrado['provincia'],
                "📍"
            ), unsafe_allow_html=True)
            
            # Barra de progreso para uso de tierra
            st.markdown("**Distribución de Superficie:**")
            st.markdown(crear_progress_bar(
                productor_encontrado['porcentajeAgricola'], 
                100, 
                "excellent"
            ), unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; font-size: 14px; color: #666; margin-top: 5px;'>{productor_encontrado['porcentajeAgricola']}% Uso Agrícola</div>", unsafe_allow_html=True)
        
        # Tabs adicionales
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Productividad", "💰 Análisis Financiero", "🎯 Score Crediticio", "🔄 Simulador"
        ])
        
        with tab1:
            st.subheader("🌾 Rendimientos por Cultivo")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Tabla de rendimientos
                rendimientos_df = pd.DataFrame([
                    {
                        'Cultivo': r['cultivo'],
                        'Rendimiento Propio': f"{r['rendimiento']:,} kg/ha",
                        'Benchmark Zona': f"{r['benchmark']:,} kg/ha",
                        'Diferencia': f"{r['rendimiento'] - r['benchmark']:+,} kg/ha"
                    } for r in productor_encontrado['rendimientos']
                ])
                
                st.dataframe(rendimientos_df, hide_index=True, use_container_width=True)
            
            with col2:
                # Gráfico usando st.bar_chart
                chart_data = pd.DataFrame({
                    'Propio': [r['rendimiento'] for r in productor_encontrado['rendimientos']],
                    'Benchmark': [r['benchmark'] for r in productor_encontrado['rendimientos']]
                }, index=[r['cultivo'] for r in productor_encontrado['rendimientos']])
                
                st.bar_chart(chart_data, height=300)
            
            # Clasificación de productividad
            percentil = productor_encontrado['comparativaMercado']['percentilProductividad']
            st.markdown(f"""
            <div class="dcac-metric">
                <div style="font-size: 24px; margin-bottom: 10px;">🏆</div>
                <div class="dcac-metric-label">Percentil de Productividad</div>
                <div class="dcac-metric-value">{percentil}°</div>
                <div class="dcac-metric-subvalue">Mejor que el {percentil}% de productores</div>
            </div>
            """, unsafe_allow_html=True)
        
        with tab2:
            st.subheader("💰 Situación Financiera")
            
            finanzas = productor_encontrado['finanzas']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(crear_metric_visual(
                    "Ingresos Totales", 
                    f"${finanzas['ingresosTotales']:,}", 
                    "USD anuales",
                    "💰"
                ), unsafe_allow_html=True)
            
            with col2:
                st.markdown(crear_metric_visual(
                    "Egresos Totales", 
                    f"${finanzas['egresosTotales']:,}", 
                    "USD anuales",
                    "💸"
                ), unsafe_allow_html=True)
            
            with col3:
                st.markdown(crear_metric_visual(
                    "Saldo Neto", 
                    f"${finanzas['saldoNeto']:,}", 
                    "USD anuales",
                    "📈"
                ), unsafe_allow_html=True)
            
            # Ratios financieros
            st.markdown("**Ratios Financieros:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Ratio Servicio de Deuda:**")
                tipo_ratio = "excellent" if finanzas['ratioServicioDeuda'] >= 1.5 else "good" if finanzas['ratioServicioDeuda'] >= 1.2 else "warning"
                st.markdown(crear_progress_bar(finanzas['ratioServicioDeuda'], 3, tipo_ratio), unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 14px; color: #666;'>{finanzas['ratioServicioDeuda']:.2f}</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Deuda / Activos:**")
                tipo_deuda = "excellent" if finanzas['deudaActivos'] <= 0.1 else "good" if finanzas['deudaActivos'] <= 0.15 else "warning"
                st.markdown(crear_progress_bar(finanzas['deudaActivos'], 0.3, tipo_deuda), unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 14px; color: #666;'>{finanzas['deudaActivos']:.2%}</div>", unsafe_allow_html=True)
        
        with tab3:
            st.subheader("🎯 Evaluación Crediticia")
            
            col1, col2 = st.columns(2)
            
            with col1:
                score = finanzas['scoreCredito']
                percentil_score = productor_encontrado['comparativaMercado']['percentilScoreCredito']
                
                st.markdown(f"""
                <div class="dcac-metric">
                    <div style="font-size: 48px; margin-bottom: 15px;">🏅</div>
                    <div class="dcac-metric-label">Score Crediticio</div>
                    <div class="dcac-metric-value">{score}</div>
                    <div class="dcac-metric-subvalue">Percentil {percentil_score}° - Excelente</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Progreso del score
                st.markdown("**Calificación del Score:**")
                tipo_score = "excellent" if score >= 700 else "good" if score >= 600 else "warning"
                st.markdown(crear_progress_bar(score, 1000, tipo_score), unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Criterios de Aprobación:**")
                
                criterios = [
                    ("✅ Score Nosis ≥ 600", True),
                    ("✅ Ratio Servicio ≥ 1.5", finanzas['ratioServicioDeuda'] >= 1.5),
                    ("✅ Deuda/Activos ≤ 15%", finanzas['deudaActivos'] <= 0.15),
                    ("✅ Sin cheques rechazados", True),
                    ("✅ Garantías disponibles", True)
                ]
                
                for criterio, cumple in criterios:
                    color = "#2C7A2C" if cumple else "#DC143C"
                    st.markdown(f"<div style='color: {color}; font-weight: 600; margin: 8px 0;'>{criterio}</div>", unsafe_allow_html=True)
                
                # Recomendación final
                clasificacion = productor_encontrado['comparativaMercado']['clasificacion']
                st.markdown(f"""
                <div class="dcac-metric">
                    <div style="font-size: 32px; margin-bottom: 10px;">🎯</div>
                    <div class="dcac-metric-label">Recomendación</div>
                    <div class="dcac-metric-value">{clasificacion}</div>
                    <div class="dcac-metric-subvalue">Aprobar con condiciones preferenciales</div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab4:
            st.subheader("🔄 Simulador de Créditos")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Parámetros del Crédito:**")
                
                monto = st.number_input("Monto (USD):", min_value=1000, max_value=500000, value=100000, step=5000)
                tasa = st.number_input("Tasa Anual (%):", min_value=5.0, max_value=25.0, value=12.0, step=0.5)
                plazo = st.number_input("Plazo (meses):", min_value=6, max_value=60, value=24, step=6)
                
                simular = st.button("🔄 Simular Crédito", type="primary", use_container_width=True)
            
            with col2:
                if simular:
                    # Cálculos básicos
                    tasa_mensual = tasa / 100 / 12
                    cuota_mensual = monto * (tasa_mensual * (1 + tasa_mensual)**plazo) / ((1 + tasa_mensual)**plazo - 1)
                    total_intereses = (cuota_mensual * plazo) - monto
                    total_pagar = monto + total_intereses
                    
                    st.markdown("**Resultados de la Simulación:**")
                    
                    st.markdown(crear_metric_visual(
                        "Cuota Mensual", 
                        f"${cuota_mensual:,.0f}", 
                        "USD",
                        "💳"
                    ), unsafe_allow_html=True)
                    
                    st.markdown(crear_metric_visual(
                        "Total a Pagar", 
                        f"${total_pagar:,.0f}", 
                        f"Intereses: ${total_intereses:,.0f}",
                        "💰"
                    ), unsafe_allow_html=True)
                    
                    # Evaluación de capacidad
                    cuota_anual = cuota_mensual * 12
                    saldo_disponible = finanzas['saldoNeto']
                    porcentaje_comprometido = (cuota_anual / saldo_disponible) * 100
                    
                    if porcentaje_comprometido <= 30:
                        st.success(f"✅ Capacidad de pago EXCELENTE ({porcentaje_comprometido:.1f}% del flujo)")
                    elif porcentaje_comprometido <= 50:
                        st.warning(f"⚠️ Capacidad de pago BUENA ({porcentaje_comprometido:.1f}% del flujo)")
                    else:
                        st.error(f"❌ Capacidad de pago COMPROMETIDA ({porcentaje_comprometido:.1f}% del flujo)")
                else:
                    st.info("Complete los parámetros y simule el crédito para ver los resultados")

else:
    # Mensaje inicial cuando no hay búsqueda
    st.markdown("""
    <div class="dcac-initial-message">
        <div class="dcac-initial-icon">🔍</div>
        <div class="dcac-initial-title">Seleccione un Productor para Consultar</div>
        <div class="dcac-initial-subtitle">
            Obtenga una radiografía completa con análisis de superficie, productividad y capacidad crediticia
        </div>
        <div style="margin-top: 30px; font-size: 18px; color: var(--dcac-green-primary); font-weight: 600;">
            🌾 Sistema integrado con datos de SENASA/RENSPA
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Características del sistema
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(crear_metric_visual(
            "Análisis Satelital", 
            "Google Earth", 
            "Engine Integration",
            "🛰️"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(crear_metric_visual(
            "Datos SENASA", 
            "Tiempo Real", 
            "RENSPA Actualizado",
            "📊"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(crear_metric_visual(
            "Score Crediticio", 
            "Automático", 
            "Decisión Inmediata",
            "⚡"
        ), unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="dcac-footer">
    <div class="dcac-footer-content">
        <div class="dcac-footer-title">OneClickLending</div>
        <div class="dcac-footer-text">Powered by deCampoaCampo</div>
        <div class="dcac-footer-text">Sistema Integrado de Análisis Agrícola</div>
        <div style="margin-top: 20px; font-size: 14px; opacity: 0.8;">
            © 2025 OneClickLending - Todos los derechos reservados
        </div>
        <div style="margin-top: 15px; font-size: 14px;">
            📧 pepo@riverwoodag.com | micaias@riverwoodag.com
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
