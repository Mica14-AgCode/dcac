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

# CSS personalizado para mantener el estilo original
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f0f0;
        border-radius: 8px 8px 0 0;
        color: #666666;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4478a7;
        color: white;
    }
    
    .metric-card {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 14px;
        font-weight: 600;
        color: #666666;
        margin-bottom: 5px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #4478a7;
        margin: 0;
    }
    
    .metric-subvalue {
        font-size: 12px;
        color: #666666;
        margin-top: 3px;
    }
    
    .header-container {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    
    .search-container {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    
    .positive { color: #2ecc71; font-weight: bold; }
    .warning { color: #f39c12; font-weight: bold; }
    .negative { color: #e74c3c; font-weight: bold; }
    .neutral { color: #666666; }
    
    .criteria-pass { 
        background-color: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    
    .criteria-warning {
        background-color: rgba(243, 156, 18, 0.2);
        color: #f39c12;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    
    .criteria-fail {
        background-color: rgba(231, 76, 60, 0.2);
        color: #e74c3c;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    
    .progress-bar {
        background-color: #f0f0f0;
        border-radius: 10px;
        overflow: hidden;
        height: 20px;
        margin: 5px 0;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-size: 12px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .progress-good { background-color: #2ecc71; }
    .progress-warning { background-color: #f39c12; }
    .progress-bad { background-color: #e74c3c; }
    
    /* Estilos específicos para ganadería */
    .ganaderia-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .animal-category {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #e9ecef;
    }
    
    .animal-category:last-child {
        border-bottom: none;
    }
    
    .animal-name {
        font-weight: 600;
        color: #495057;
    }
    
    .animal-count {
        font-weight: 700;
        color: #6f5499;
        font-size: 18px;
    }
    
    .section-title {
        color: #4478a7;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 15px;
        border-bottom: 2px solid #4478a7;
        padding-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Datos de ejemplo expandidos con ganadería
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
            "superficieTotal": 10500,  # Ahora incluye superficie ganadera
            "superficieAgricola": 5300,  # 800 propias + 4500 arrendadas
            "superficieGanadera": 5200,  # Según Excel
            "porcentajeAgricola": 50.5,
            "porcentajeGanadero": 49.5,
            "departamento": "San Justo",
            "provincia": "Santa Fe",
            "poligonos": [
                {"id": "P001", "tipo": "Agrícola", "superficie": 1200},
                {"id": "P002", "tipo": "Agrícola", "superficie": 800},
                {"id": "P003", "tipo": "Ganadero", "superficie": 2500},
                {"id": "P004", "tipo": "Ganadero", "superficie": 2700},
                {"id": "P005", "tipo": "No Productivo", "superficie": 300}
            ],
            "rotacionCultivos": [
                {"campania": "19-20", "soja": 45, "maiz": 30, "girasol": 10, "maiz2da": 5, "noAgricola": 10},
                {"campania": "20-21", "soja": 40, "maiz": 35, "girasol": 5, "maiz2da": 10, "noAgricola": 10},
                {"campania": "21-22", "soja": 35, "maiz": 40, "girasol": 5, "maiz2da": 10, "noAgricola": 10},
                {"campania": "22-23", "soja": 30, "maiz": 45, "girasol": 5, "maiz2da": 10, "noAgricola": 10},
                {"campania": "23-24", "soja": 25, "maiz": 50, "girasol": 5, "maiz2da": 10, "noAgricola": 10}
            ],
            "rendimientos": {
                "propios": [
                    {"cultivo": "Maíz", "rendimiento5": 8500, "rendimiento10": 7200},
                    {"cultivo": "Soja", "rendimiento5": 3800, "rendimiento10": 3500},
                    {"cultivo": "Girasol", "rendimiento5": 2200, "rendimiento10": 2000}
                ],
                "departamento": [
                    {"cultivo": "Maíz", "rendimiento5": 7800, "rendimiento10": 6900},
                    {"cultivo": "Soja", "rendimiento5": 3500, "rendimiento10": 3200},
                    {"cultivo": "Girasol", "rendimiento5": 2000, "rendimiento10": 1800}
                ]
            },
            # DATOS GANADEROS basados en el Excel
            "ganaderia": {
                "stockTotal": {
                    "Vaca": 10000,
                    "Vaquillonas": 5000,
                    "Novillo": 3000,
                    "Novillito": 3000,
                    "Ternero": 5000,
                    "Ternera": 5000,
                    "Toro": 6000,
                    "Torito/MEJ": 5000,
                    "total": 42000
                },
                "stockCria": {
                    "Vaca": 5000,
                    "Vaquillonas": 1000,
                    "Novillo": 0,
                    "Novillito": 0,
                    "Ternero": 1500,
                    "Ternera": 1500,
                    "Toro": 200,
                    "Torito/MEJ": 0,
                    "total": 9200
                },
                "stockEngorde": {
                    "Vaca": 5000,
                    "Vaquillonas": 4000,
                    "Novillo": 3000,
                    "Novillito": 3000,
                    "Ternero": 3500,
                    "Ternera": 3500,
                    "Toro": 5800,
                    "Torito/MEJ": 5000,
                    "total": 32800
                },
                "valorStock": {
                    "stockBruto": 26604699.19,
                    "stockNeto": 24210276.27,
                    "mortandad": 0.02,
                    "gastosComercializacion": 0.07
                },
                "parametrosCria": {
                    "mortandadRodeo": 0.02,
                    "destete": 0.60,
                    "gastosComercializacion": 0.07,
                    "torosEnRodeo": 0.04,
                    "reposicion": 0.20,
                    "proporcionTerneroTernera": 0.50,
                    "hectareasGanaderas": 5200,
                    "hectareasArrendadas": 5000,
                    "cabezasPorPeon": 400
                },
                "finanzasCria": {
                    "ingresosPorVentas": 1724345.97,
                    "costoManoObra": 388723,
                    "costoSanidad": 71100,
                    "costoAlimentacion": 0,
                    "costoArrendamiento": 710214.59,
                    "costoReposicionToros": 58369.10,
                    "gastosComercializacion": 120704.22,
                    "margenAnual": 314882.96,
                    "margenPorcentual": 18.26
                },
                "densidad": {
                    "cabezasPorHectarea": 8.08,  # 42000 / 5200
                    "eqVacaPorHectarea": 7.50,
                    "cargaAnimal": "Alta"
                }
            },
            "finanzas": {
                "ingresosTotales": 875000,
                "ventaCultivos": 850000,
                "otrosIngresos": 25000,
                "costoProduccion": 320000,
                "alquileres": 120000,
                "gastosMaquinaria": 85000,
                "fletes": 65000,
                "impuestos": 75000,
                "otrosGastos": 35000,
                "servicioDeudaActual": 95000,
                "egresosTotales": 795000,
                "saldoNeto": 80000,
                "activosTotales": 2300000,
                "haciendia": 520000,
                "ratioServicioDeuda": 1.84,
                "deudaActivos": 0.12,
                "deudaHacienda": 0.18
            },
            "credito": {
                "scoreNosis": 720,
                "chequesRechazados": 0,
                "transaccionesDCAC": 12,
                "pagosRealizados": 180000,
                "creditoPagos": 0.53,
                "consultasNosis": 1.5,
                "creditosBancos": 2,
                "garantias": {
                    "prendaHacienda": True,
                    "garantiaPersonal": True,
                    "hipoteca": True
                }
            },
            "comparativaMercado": {
                "percentilApalancamiento": 35,
                "percentilProductividad": 78,
                "percentilScoreCredito": 82
            }
        }
    }
    
    return productores_data, datos_analisis

def crear_progress_bar(valor, maximo, tipo="good"):
    porcentaje = (valor / maximo) * 100
    return f"""
    <div class="progress-bar">
        <div class="progress-fill progress-{tipo}" style="width: {porcentaje}%;">
            {porcentaje:.1f}%
        </div>
    </div>
    """

def crear_gauge_simple(valor, maximo, titulo, subtitulo=""):
    porcentaje = (valor / maximo) * 100
    color = "#2ecc71" if porcentaje >= 75 else "#f39c12" if porcentaje >= 50 else "#e74c3c"
    
    return f"""
    <div style="text-align: center; padding: 20px; background-color: #f5f5f5; border-radius: 8px; margin: 10px 0;">
        <div style="font-size: 36px; font-weight: bold; color: {color};">
            {valor}
        </div>
        <div style="font-size: 14px; color: #666; margin: 5px 0;">
            {titulo}
        </div>
        <div style="font-size: 12px; color: #666;">
            {subtitulo}
        </div>
        <div style="background-color: #e0e0e0; height: 8px; border-radius: 4px; margin: 10px 0; overflow: hidden;">
            <div style="background-color: {color}; height: 100%; width: {porcentaje}%; border-radius: 4px;"></div>
        </div>
    </div>
    """

def crear_categoria_animal(nombre, cantidad, total, icon="🐄"):
    porcentaje = (cantidad / total) * 100 if total > 0 else 0
    return f"""
    <div class="animal-category">
        <div style="display: flex; align-items: center;">
            <span style="margin-right: 8px; font-size: 16px;">{icon}</span>
            <span class="animal-name">{nombre}</span>
        </div>
        <div style="text-align: right;">
            <div class="animal-count">{cantidad:,}</div>
            <div style="font-size: 11px; color: #6c757d;">{porcentaje:.1f}%</div>
        </div>
    </div>
    """

# Cargar datos
productores_data, datos_analisis = load_data()

# Header
st.markdown("""
<div class="header-container">
    <h1 style="margin: 0; font-weight: 600; font-size: 28px;">
        <span style="color: #4478a7;">OneClick</span><span style="color: #7aa0c3;">Lending</span>
    </h1>
    <p style="font-size: 15px; color: #666666; margin: 5px 0 0 0; font-weight: 400;">
        La Radiografía del Productor
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #8aba5f; color: white; padding: 10px 0; text-align: center; 
font-weight: 600; margin-bottom: 20px; border-radius: 4px;">
    Dar créditos nunca fue tan fácil
</div>
""", unsafe_allow_html=True)

# Formulario de búsqueda
st.markdown("""
<div class="search-container">
    <h2 style="font-size: 18px; font-weight: 600; color: #4478a7; margin-top: 0; margin-bottom: 15px;">
        Buscar Productor
    </h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    search_type = st.selectbox("Buscar por:", ["CUIT", "Razón Social"])

with col2:
    if search_type == "CUIT":
        search_value = st.selectbox(
            "CUIT:",
            options=[""] + [p["cuit"] for p in productores_data],
            format_func=lambda x: x if x else "Seleccione un CUIT"
        )
    else:
        search_value = st.selectbox(
            "Razón Social:",
            options=[""] + [p["razonSocial"] for p in productores_data],
            format_func=lambda x: x if x else "Seleccione una razón social"
        )

with col3:
    search_button = st.button("Buscar", type="primary", use_container_width=True)

# Lógica de búsqueda
if search_button or search_value:
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
        # Mostrar datos del productor
        st.markdown(f"""
        <h2 style="color: #4478a7; margin-bottom: 5px;">
            Datos del Productor: {productor_encontrado['razonSocial']}
        </h2>
        """, unsafe_allow_html=True)
        
        # Métricas principales expandidas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Superficie Total</div>
                <div class="metric-value">{productor_encontrado['superficieTotal']:,}</div>
                <div class="metric-subvalue">hectáreas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Superficie Agrícola</div>
                <div class="metric-value">{productor_encontrado['superficieAgricola']:,}</div>
                <div class="metric-subvalue">{productor_encontrado['porcentajeAgricola']:.1f}% del total</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Superficie Ganadera</div>
                <div class="metric-value">{productor_encontrado['superficieGanadera']:,}</div>
                <div class="metric-subvalue">{productor_encontrado['porcentajeGanadero']:.1f}% del total</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Stock Ganadero</div>
                <div class="metric-value">{productor_encontrado['ganaderia']['stockTotal']['total']:,}</div>
                <div class="metric-subvalue">cabezas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Ubicación</div>
                <div class="metric-value">{productor_encontrado['departamento']}</div>
                <div class="metric-subvalue">{productor_encontrado['provincia']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Tabs principales - AGRICULTURA Y GANADERÍA
        tab_agri, tab_gana, tab_finanzas, tab_credito, tab_simulador, tab_comparativa = st.tabs([
            "🌾 Agricultura", "🐄 Ganadería", "💰 Finanzas", 
            "🎯 Crédito", "🔄 Simulador", "📊 Comparativa"
        ])
        
        # TAB AGRICULTURA (código existente)
        with tab_agri:
            tab_info, tab_rend = st.tabs(["Información General", "Rendimientos"])
            
            with tab_info:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Rotación de Cultivos (Campañas 2019-2024)")
                    
                    # Preparar datos para gráfico
                    rotacion_df = pd.DataFrame(productor_encontrado['rotacionCultivos'])
                    rotacion_df = rotacion_df.set_index('campania')
                    
                    # Renombrar columnas para mejor presentación
                    rotacion_df.columns = [col.replace('maiz2da', 'Maíz 2da').replace('noAgricola', 'No Agrícola').title() for col in rotacion_df.columns]
                    
                    st.bar_chart(rotacion_df, height=400)
                    
                    st.info("📊 Gráfico de barras apiladas mostrando la evolución de cultivos por campaña")
                
                with col2:
                    st.subheader("Polígonos Agrícolas")
                    
                    # Filtrar solo polígonos agrícolas
                    poligonos_agricolas = [p for p in productor_encontrado['poligonos'] if p['tipo'] == 'Agrícola']
                    
                    if poligonos_agricolas:
                        poligonos_df = pd.DataFrame([
                            {
                                'ID': p['id'],
                                'Superficie (ha)': f"{p['superficie']:,}"
                            } for p in poligonos_agricolas
                        ])
                        st.dataframe(poligonos_df, hide_index=True, use_container_width=True)
                        
                        total_agricola = sum(p['superficie'] for p in poligonos_agricolas)
                        st.metric("Total Agrícola", f"{total_agricola:,} ha")
                    else:
                        st.info("No hay polígonos agrícolas registrados")
            
            with tab_rend:
                st.subheader("Comparativa de Rendimientos")
                
                # Preparar datos de rendimientos
                rendimientos_data = []
                for rp in productor_encontrado['rendimientos']['propios']:
                    rd = next((r for r in productor_encontrado['rendimientos']['departamento'] 
                             if r['cultivo'] == rp['cultivo']), None)
                    if rd:
                        rendimientos_data.append({
                            'Cultivo': rp['cultivo'],
                            'Propio_5': rp['rendimiento5'],
                            'Depto_5': rd['rendimiento5'],
                            'Propio_10': rp['rendimiento10'],
                            'Depto_10': rd['rendimiento10']
                        })
                
                rendimientos_df = pd.DataFrame(rendimientos_data)
                rendimientos_df = rendimientos_df.set_index('Cultivo')
                
                # Gráfico de barras comparativo
                st.bar_chart(rendimientos_df, height=400)
                
                # Tabla detallada
                st.subheader("Detalle de Rendimientos")
                
                tabla_rendimientos = []
                for rp in productor_encontrado['rendimientos']['propios']:
                    rd = next((r for r in productor_encontrado['rendimientos']['departamento'] 
                             if r['cultivo'] == rp['cultivo']), None)
                    if rd:
                        dif_5 = rp['rendimiento5'] - rd['rendimiento5']
                        pct_5 = (dif_5 / rd['rendimiento5']) * 100
                        
                        tabla_rendimientos.append({
                            'Cultivo': rp['cultivo'],
                            'Propio 5 años': f"{rp['rendimiento5']:,}",
                            'Departamento 5 años': f"{rd['rendimiento5']:,}",
                            'Propio 10 años': f"{rp['rendimiento10']:,}",
                            'Departamento 10 años': f"{rd['rendimiento10']:,}",
                            'Diferencia 5 años': f"{dif_5:+,} ({pct_5:+.1f}%)"
                        })
                
                st.dataframe(pd.DataFrame(tabla_rendimientos), hide_index=True, use_container_width=True)
        
        # TAB GANADERÍA (NUEVO)
        with tab_gana:
            ganaderia = productor_encontrado['ganaderia']
            
            tab_cria, tab_engorde, tab_general = st.tabs(["🐄 Cría", "🥩 Engorde", "📊 General"])
            
            with tab_cria:
                st.markdown('<div class="section-title">📊 Stock de Cría</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Stock de cría
                    st.markdown('<div class="ganaderia-card">', unsafe_allow_html=True)
                    
                    icons = {
                        "Vaca": "🐄", "Vaquillonas": "🐮", "Ternero": "🐄", 
                        "Ternera": "🐄", "Toro": "🐂", "Torito/MEJ": "🐂"
                    }
                    
                    total_cria = ganaderia['stockCria']['total']
                    
                    for categoria, cantidad in ganaderia['stockCria'].items():
                        if categoria != 'total' and cantidad > 0:
                            icon = icons.get(categoria, "🐄")
                            st.markdown(crear_categoria_animal(categoria, cantidad, total_cria, icon), unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Métricas de cría
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Cría</div>
                        <div class="metric-value">{total_cria:,}</div>
                        <div class="metric-subvalue">cabezas</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Parámetros técnicos
                    st.markdown('<div class="section-title">🔧 Parámetros Técnicos</div>', unsafe_allow_html=True)
                    
                    params = ganaderia['parametrosCria']
                    
                    col2_1, col2_2 = st.columns(2)
                    
                    with col2_1:
                        st.metric("% Destete", f"{params['destete']:.0%}")
                        st.metric("% Mortandad", f"{params['mortandadRodeo']:.1%}")
                        st.metric("% Reposición", f"{params['reposicion']:.0%}")
                    
                    with col2_2:
                        st.metric("Toros en Rodeo", f"{params['torosEnRodeo']:.1%}")
                        st.metric("Cabezas/Peón", f"{params['cabezasPorPeon']:.0f}")
                        st.metric("Ha Ganaderas", f"{params['hectareasGanaderas']:,}")
                
                # Análisis financiero de cría
                st.markdown('<div class="section-title">💰 Análisis Financiero - Cría</div>', unsafe_allow_html=True)
                
                finanzas_cria = ganaderia['finanzasCria']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Ingresos por Ventas</div>
                        <div class="metric-value">${finanzas_cria['ingresosPorVentas']:,.0f}</div>
                        <div class="metric-subvalue">USD anuales</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Costos Totales</div>
                        <div class="metric-value">${finanzas_cria['ingresosPorVentas'] - finanzas_cria['margenAnual']:,.0f}</div>
                        <div class="metric-subvalue">USD anuales</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Margen Bruto</div>
                        <div class="metric-value">${finanzas_cria['margenAnual']:,.0f}</div>
                        <div class="metric-subvalue">USD anuales</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Margen %</div>
                        <div class="metric-value">{finanzas_cria['margenPorcentual']:.1f}%</div>
                        <div class="metric-subvalue">sobre ventas</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Desglose de costos
                st.subheader("Desglose de Costos - Cría")
                
                costos_data = {
                    'Concepto': ['Mano de Obra', 'Sanidad', 'Arrendamiento', 'Reposición Toros', 'Gastos Comercialización'],
                    'Monto (USD)': [
                        finanzas_cria['costoManoObra'],
                        finanzas_cria['costoSanidad'],
                        finanzas_cria['costoArrendamiento'],
                        finanzas_cria['costoReposicionToros'],
                        finanzas_cria['gastosComercializacion']
                    ]
                }
                
                costos_df = pd.DataFrame(costos_data)
                costos_df = costos_df.set_index('Concepto')
                st.bar_chart(costos_df, height=300)
            
            with tab_engorde:
                st.markdown('<div class="section-title">🥩 Stock de Engorde</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Stock de engorde
                    st.markdown('<div class="ganaderia-card">', unsafe_allow_html=True)
                    
                    total_engorde = ganaderia['stockEngorde']['total']
                    
                    for categoria, cantidad in ganaderia['stockEngorde'].items():
                        if categoria != 'total' and cantidad > 0:
                            icon = icons.get(categoria, "🐄")
                            st.markdown(crear_categoria_animal(categoria, cantidad, total_engorde, icon), unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Engorde</div>
                        <div class="metric-value">{total_engorde:,}</div>
                        <div class="metric-subvalue">cabezas</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Métricas de engorde
                    st.markdown('<div class="section-title">📈 Métricas de Engorde</div>', unsafe_allow_html=True)
                    
                    # Calcular densidad para engorde
                    densidad_engorde = total_engorde / ganaderia['parametrosCria']['hectareasGanaderas']
                    
                    st.metric("Densidad", f"{densidad_engorde:.1f} cab/ha")
                    
                    # Distribución por categoría para engorde
                    principales_engorde = ['Novillo', 'Novillito', 'Vaquillonas']
                    for cat in principales_engorde:
                        if cat in ganaderia['stockEngorde']:
                            cantidad = ganaderia['stockEngorde'][cat]
                            porcentaje = (cantidad / total_engorde) * 100
                            st.metric(f"{cat}", f"{cantidad:,} ({porcentaje:.1f}%)")
                
                # Análisis de capacidad de engorde
                st.markdown('<div class="section-title">⚖️ Análisis de Capacidad</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    capacidad_optima = ganaderia['parametrosCria']['hectareasGanaderas'] * 1.5  # Ejemplo: 1.5 EV/ha
                    utilizacion = (total_engorde / capacidad_optima) * 100
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Utilización de Capacidad</div>
                        <div class="metric-value">{utilizacion:.0f}%</div>
                        <div class="metric-subvalue">vs capacidad óptima</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    ganancia_peso_estimada = 0.8  # kg/día promedio
                    kilos_anuales = total_engorde * ganancia_peso_estimada * 365
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Producción Estimada</div>
                        <div class="metric-value">{kilos_anuales/1000:.0f}</div>
                        <div class="metric-subvalue">ton/año de carne</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    rotacion_estimada = 1.5  # veces por año
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Rotación Anual</div>
                        <div class="metric-value">{rotacion_estimada:.1f}</div>
                        <div class="metric-subvalue">veces/año</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with tab_general:
                st.markdown('<div class="section-title">📊 Vista General del Rodeo</div>', unsafe_allow_html=True)
                
                # Comparación stock total vs cría vs engorde
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("Distribución del Stock Total")
                    
                    # Crear dataframe para el gráfico
                    distribucion_data = pd.DataFrame({
                        'Cría': [ganaderia['stockCria']['total']],
                        'Engorde': [ganaderia['stockEngorde']['total']]
                    })
                    
                    st.bar_chart(distribucion_data, height=300)
                    
                    # Porcentajes
                    total_general = ganaderia['stockTotal']['total']
                    pct_cria = (ganaderia['stockCria']['total'] / total_general) * 100
                    pct_engorde = (ganaderia['stockEngorde']['total'] / total_general) * 100
                    
                    st.markdown(f"""
                    **Distribución:**
                    - Cría: {pct_cria:.1f}% ({ganaderia['stockCria']['total']:,} cabezas)
                    - Engorde: {pct_engorde:.1f}% ({ganaderia['stockEngorde']['total']:,} cabezas)
                    """)
                
                with col2:
                    st.subheader("Valor del Stock Ganadero")
                    
                    valor_stock = ganaderia['valorStock']
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Valor Stock Bruto</div>
                        <div class="metric-value">${valor_stock['stockBruto']:,.0f}</div>
                        <div class="metric-subvalue">USD</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Valor Stock Neto</div>
                        <div class="metric-value">${valor_stock['stockNeto']:,.0f}</div>
                        <div class="metric-subvalue">Descontando mortandad y gastos</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Densidad general
                    densidad_general = ganaderia['densidad']
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Carga Animal</div>
                        <div class="metric-value">{densidad_general['cabezasPorHectarea']:.1f}</div>
                        <div class="metric-subvalue">cab/ha - {densidad_general['cargaAnimal']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Tabla resumen por categorías
                st.subheader("Resumen por Categorías")
                
                resumen_categorias = []
                for categoria in ganaderia['stockTotal'].keys():
                    if categoria != 'total':
                        total = ganaderia['stockTotal'][categoria]
                        cria = ganaderia['stockCria'].get(categoria, 0)
                        engorde = ganaderia['stockEngorde'].get(categoria, 0)
                        
                        resumen_categorias.append({
                            'Categoría': categoria,
                            'Total': f"{total:,}",
                            'Cría': f"{cria:,}",
                            'Engorde': f"{engorde:,}",
                            '% Cría': f"{(cria/total*100):.1f}%" if total > 0 else "0%",
                            '% Engorde': f"{(engorde/total*100):.1f}%" if total > 0 else "0%"
                        })
                
                resumen_df = pd.DataFrame(resumen_categorias)
                st.dataframe(resumen_df, hide_index=True, use_container_width=True)
        
        # TAB FINANZAS (código existente adaptado)
        with tab_finanzas:
            finanzas = productor_encontrado['finanzas']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Indicadores Principales")
                
                saldo_sin_deuda = finanzas['ingresosTotales'] - (finanzas['egresosTotales'] - finanzas['servicioDeudaActual'])
                
                st.metric("Saldo sin deuda", f"${saldo_sin_deuda:,}")
                st.metric("Saldo con deuda actual", f"${finanzas['saldoNeto']:,}")
                st.metric("Ratio Servicio de Deuda", f"{finanzas['ratioServicioDeuda']:.2f}")
                st.metric("Deuda / Activos", f"{finanzas['deudaActivos']:.2f}")
                
                st.subheader("Análisis de Flujo de Caja")
                
                # Gráfico simple de ingresos vs egresos
                flujo_data = pd.DataFrame({
                    'Concepto': ['Ingresos Totales', 'Egresos Totales', 'Saldo Neto'],
                    'Monto': [finanzas['ingresosTotales'], finanzas['egresosTotales'], finanzas['saldoNeto']]
                })
                flujo_data = flujo_data.set_index('Concepto')
                st.bar_chart(flujo_data, height=300)
            
            with col2:
                st.subheader("Score Crediticio")
                
                score = productor_encontrado['credito']['scoreNosis']
                percentil = productor_encontrado['comparativaMercado']['percentilScoreCredito']
                
                # Mostrar score como gauge simple
                st.markdown(crear_gauge_simple(score, 1000, "Score Nosis", f"Percentil {percentil}°"), unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center; margin-top: 10px;">
                    <p style="font-size: 14px;">Mejor que el {percentil}% de productores</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Tabla de flujo de caja detallado
            st.subheader("Flujo de Caja Detallado")
            
            flujo_data = [
                ("**INGRESOS**", "", ""),
                ("Venta de Cultivos", f"${finanzas['ventaCultivos']:,}", f"{(finanzas['ventaCultivos']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Otros Ingresos", f"${finanzas['otrosIngresos']:,}", f"{(finanzas['otrosIngresos']/finanzas['ingresosTotales']*100):.1f}%"),
                ("**Total Ingresos**", f"**${finanzas['ingresosTotales']:,}**", "**100.0%**"),
                ("", "", ""),
                ("**EGRESOS**", "", ""),
                ("Costos de Producción", f"${finanzas['costoProduccion']:,}", f"{(finanzas['costoProduccion']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Alquileres", f"${finanzas['alquileres']:,}", f"{(finanzas['alquileres']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Gastos de Maquinaria", f"${finanzas['gastosMaquinaria']:,}", f"{(finanzas['gastosMaquinaria']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Fletes", f"${finanzas['fletes']:,}", f"{(finanzas['fletes']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Impuestos", f"${finanzas['impuestos']:,}", f"{(finanzas['impuestos']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Otros Gastos", f"${finanzas['otrosGastos']:,}", f"{(finanzas['otrosGastos']/finanzas['ingresosTotales']*100):.1f}%"),
                ("🔴 Servicio de Deuda Actual", f"${finanzas['servicioDeudaActual']:,}", f"{(finanzas['servicioDeudaActual']/finanzas['ingresosTotales']*100):.1f}%"),
                ("**Total Egresos**", f"**${finanzas['egresosTotales']:,}**", f"**{(finanzas['egresosTotales']/finanzas['ingresosTotales']*100):.1f}%**"),
                ("", "", ""),
                ("**🟢 SALDO NETO**", f"**${finanzas['saldoNeto']:,}**", f"**{(finanzas['saldoNeto']/finanzas['ingresosTotales']*100):.1f}%**")
            ]
            
            flujo_df = pd.DataFrame(flujo_data, columns=["Concepto", "Monto (USD)", "% del Total"])
            st.dataframe(flujo_df, hide_index=True, use_container_width=True)
        
        # Resto de tabs (Crédito, Simulador, Comparativa) - código existente
        with tab_credito:
            credito = productor_encontrado['credito']
            
            st.subheader("Criterios de Aprobación de Crédito")
            
            # Criterios en columnas
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Historial con DCAC**")
                criterios_dcac = [
                    ("Transacciones >= 3", credito['transaccionesDCAC'] >= 3, f"✅ {credito['transaccionesDCAC']} transacciones"),
                    ("Crédito < Pagos", credito['creditoPagos'] < 1, f"✅ Ratio {credito['creditoPagos']:.2f}")
                ]
                
                for criterio, cumple, detalle in criterios_dcac:
                    st.markdown(f"• **{criterio}:** {detalle}")
                
                st.markdown("**Ratios Financieros**")
                criterios_ratios = [
                    ("Deuda/Activos <= 0.15", finanzas['deudaActivos'] <= 0.15, f"✅ {finanzas['deudaActivos']:.2f}"),
                    ("Deuda/Hacienda <= 0.25", finanzas['deudaHacienda'] <= 0.25, f"✅ {finanzas['deudaHacienda']:.2f}"),
                    ("Ratio Servicio >= 1.5", finanzas['ratioServicioDeuda'] >= 1.5, f"✅ {finanzas['ratioServicioDeuda']:.2f}")
                ]
                
                for criterio, cumple, detalle in criterios_ratios:
                    st.markdown(f"• **{criterio}:** {detalle}")
            
            with col2:
                st.markdown("**Calificación Crediticia**")
                criterios_credito = [
                    ("Score Nosis >= 600", credito['scoreNosis'] >= 600, f"✅ {credito['scoreNosis']} puntos"),
                    ("Cheques Rechazados = 0", credito['chequesRechazados'] == 0, f"✅ {credito['chequesRechazados']} rechazos"),
                    ("Créditos Bancos <= 3", credito['creditosBancos'] <= 3, f"✅ {credito['creditosBancos']} créditos"),
                    ("Consultas Nosis <= 1.5", credito['consultasNosis'] <= 1.5, f"✅ {credito['consultasNosis']:.1f} ratio")
                ]
                
                for criterio, cumple, detalle in criterios_credito:
                    st.markdown(f"• **{criterio}:** {detalle}")
                
                st.markdown("**Garantías Disponibles**")
                garantias = [
                    ("Prenda sobre hacienda", credito['garantias']['prendaHacienda'], "520,000 USD"),
                    ("Garantía personal", credito['garantias']['garantiaPersonal'], "-"),
                    ("Potencial de Hipoteca", credito['garantias']['hipoteca'], "1,800,000 USD")
                ]
                
                for tipo, disponible, valor in garantias:
                    status = "✅ Disponible" if disponible else "❌ No disponible"
                    st.markdown(f"• **{tipo}:** {status} ({valor})")
            
            # Resumen de recomendación
            st.subheader("Resumen Comparativo")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">Clasificación General</div>
                    <div class="metric-value">PREMIUM</div>
                    <div class="metric-subvalue">Top 20% del mercado</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">Riesgo Crediticio</div>
                    <div class="metric-value">BAJO</div>
                    <div class="metric-subvalue">Score 720/1000</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">Capacidad de Pago</div>
                    <div class="metric-value">ALTA</div>
                    <div class="metric-subvalue">Ratio 1.84</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">Recomendación</div>
                    <div class="metric-value">APROBAR</div>
                    <div class="metric-subvalue">Cliente objetivo</div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab_simulador:
            st.subheader("Simulador de Créditos")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Parámetros del Crédito**")
                
                monto = st.number_input("Monto del Préstamo (USD):", min_value=1000, max_value=1000000, value=50000, step=1000)
                tasa = st.number_input("Tasa de Interés Anual (%):", min_value=1.0, max_value=20.0, value=7.5, step=0.1)
                plazo = st.number_input("Plazo (meses):", min_value=1, max_value=60, value=12, step=1)
                
                tipo_pago = st.selectbox("Tipo de Pago:", [
                    "Cuota Fija (Principal + Interés)",
                    "Cuota Variable (Interés + Principal fijo)",
                    "Bullet (Interés periódico, Principal al final)"
                ])
                
                frecuencia = st.selectbox("Frecuencia de Pago:", ["Mensual", "Trimestral", "Semestral", "Anual"])
                
                calcular = st.button("Simular Crédito", type="primary")
            
            with col2:
                st.markdown("**Resultados de la Simulación**")
                
                if calcular:
                    # Cálculos de simulación
                    pagos_por_anio = {"Mensual": 12, "Trimestral": 4, "Semestral": 2, "Anual": 1}[frecuencia]
                    tasa_periodo = tasa / 100 / pagos_por_anio
                    numero_pagos = int(plazo / (12 / pagos_por_anio))
                    
                    if "Cuota Fija" in tipo_pago:
                        # Sistema francés
                        cuota = monto * (tasa_periodo * (1 + tasa_periodo)**numero_pagos) / ((1 + tasa_periodo)**numero_pagos - 1)
                        interes_total = (cuota * numero_pagos) - monto
                    elif "Cuota Variable" in tipo_pago:
                        # Sistema alemán
                        capital_fijo = monto / numero_pagos
                        cuota = capital_fijo + (monto * tasa_periodo)  # Primera cuota
                        interes_total = monto * tasa_periodo * (numero_pagos + 1) / 2
                    else:  # Bullet
                        cuota = monto * tasa_periodo  # Solo interés
                        interes_total = cuota * numero_pagos
                    
                    monto_total = monto + interes_total
                    cuota_anual = cuota * pagos_por_anio
                    
                    # Mostrar resultados
                    st.metric("Monto", f"${monto:,.0f}")
                    st.metric(f"Cuota {frecuencia}", f"${cuota:,.2f}")
                    st.metric("Interés Total", f"${interes_total:,.2f}")
                    st.metric("Monto Total a Pagar", f"${monto_total:,.2f}")
                    
                    # Análisis de impacto
                    st.markdown("**Impacto en Métricas Crediticias**")
                    
                    nueva_deuda = monto
                    nuevo_costo_anual = cuota_anual
                    
                    nuevo_deuda_activos = (finanzas['deudaActivos'] * finanzas['activosTotales'] + nueva_deuda) / finanzas['activosTotales']
                    nuevo_ratio_servicio = finanzas['saldoNeto'] / (finanzas['servicioDeudaActual'] + nuevo_costo_anual)
                    
                    porcentaje_flujo = (nuevo_costo_anual / finanzas['saldoNeto']) * 100
                    saldo_final = finanzas['saldoNeto'] - nuevo_costo_anual
                    
                    st.metric("Nuevo Ratio Servicio", f"{nuevo_ratio_servicio:.2f}")
                    st.metric("% del Flujo de Caja", f"{porcentaje_flujo:.1f}%")
                    st.metric("Saldo Final", f"${saldo_final:,.2f}")
                    
                    if nuevo_ratio_servicio >= 1.5:
                        st.success("✅ El productor PUEDE afrontar el nuevo crédito")
                    elif nuevo_ratio_servicio >= 1.2:
                        st.warning("⚠️ El productor puede afrontar con PRECAUCIÓN el nuevo crédito")
                    else:
                        st.error("❌ El productor NO PUEDE afrontar el nuevo crédito")
                else:
                    st.info("Complete los parámetros y haga clic en 'Simular Crédito' para ver los resultados")
        
        with tab_comparativa:
            st.subheader("Posicionamiento en el Mercado")
            
            comparativa = productor_encontrado['comparativaMercado']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Apalancamiento**")
                percentil_apal = comparativa['percentilApalancamiento']
                st.markdown(crear_gauge_simple(percentil_apal, 100, f"{percentil_apal}° Percentil", 
                           f"{100-percentil_apal}% tienen mayor apalancamiento"), unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Productividad**")
                percentil_prod = comparativa['percentilProductividad']
                st.markdown(crear_gauge_simple(percentil_prod, 100, f"{percentil_prod}° Percentil", 
                           f"Mejor que el {percentil_prod}% de productores"), unsafe_allow_html=True)
            
            with col3:
                st.markdown("**Score Crediticio**")
                percentil_score = comparativa['percentilScoreCredito']
                st.markdown(crear_gauge_simple(percentil_score, 100, f"{percentil_score}° Percentil", 
                           f"Mejor que el {percentil_score}% de productores"), unsafe_allow_html=True)
            
            # Resumen comparativo
            st.subheader("Resumen del Análisis")
            
            resumen_data = {
                'Métrica': ['Apalancamiento', 'Productividad', 'Score Crediticio'],
                'Percentil': [f"{comparativa['percentilApalancamiento']}°", 
                             f"{comparativa['percentilProductividad']}°", 
                             f"{comparativa['percentilScoreCredito']}°"],
                'Clasificación': ['Conservador', 'Alto', 'Excelente'],
                'Status': ['✅ Bajo riesgo', '✅ Alta productividad', '✅ Excelente historial']
            }
            
            st.dataframe(pd.DataFrame(resumen_data), hide_index=True, use_container_width=True)
            
            st.success("🎯 **Recomendación Final:** Cliente PREMIUM - Aprobar crédito con condiciones preferenciales")
            
            # Análisis específico de ganadería
            st.subheader("Análisis Ganadero Específico")
            
            ganaderia = productor_encontrado['ganaderia']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                densidad = ganaderia['densidad']['cabezasPorHectarea']
                if densidad > 1.0:
                    clasificacion_densidad = "Alta densidad - Intensivo"
                    color_densidad = "success"
                elif densidad > 0.7:
                    clasificacion_densidad = "Densidad media - Eficiente"
                    color_densidad = "info"
                else:
                    clasificacion_densidad = "Baja densidad - Extensivo"
                    color_densidad = "warning"
                
                if color_densidad == "success":
                    st.success(f"🐄 **Carga Animal:** {densidad:.1f} cab/ha - {clasificacion_densidad}")
                elif color_densidad == "info":
                    st.info(f"🐄 **Carga Animal:** {densidad:.1f} cab/ha - {clasificacion_densidad}")
                else:
                    st.warning(f"🐄 **Carga Animal:** {densidad:.1f} cab/ha - {clasificacion_densidad}")
            
            with col2:
                margen_cria = ganaderia['finanzasCria']['margenPorcentual']
                if margen_cria > 15:
                    st.success(f"💰 **Margen Cría:** {margen_cria:.1f}% - Excelente")
                elif margen_cria > 10:
                    st.info(f"💰 **Margen Cría:** {margen_cria:.1f}% - Bueno")
                else:
                    st.warning(f"💰 **Margen Cría:** {margen_cria:.1f}% - Mejorable")
            
            with col3:
                valor_stock_por_ha = ganaderia['valorStock']['stockNeto'] / ganaderia['parametrosCria']['hectareasGanaderas']
                st.info(f"📊 **Valor por Hectárea:** ${valor_stock_por_ha:,.0f}/ha")

else:
    # Mostrar mensaje inicial
    st.markdown("""
    <div style="text-align: center; padding: 50px; color: #666666;">
        <div style="font-size: 48px; margin-bottom: 15px;">🔍</div>
        <div style="font-size: 18px; margin-bottom: 5px;">Ingrese un CUIT o Razón Social para consultar</div>
        <div style="font-size: 14px;">La radiografía completa del productor en un solo lugar</div>
        <div style="margin-top: 30px;">
            <div style="font-size: 16px; color: #4478a7; font-weight: 600;">
                🌾 Análisis Agrícola + 🐄 Análisis Ganadero
            </div>
            <div style="font-size: 14px; color: #666; margin-top: 10px;">
                Sistema integrado con datos de SENASA/RENSPA y análisis satelital
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
---
<div style="background-color: #4478a7; color: white; padding: 30px; border-radius: 8px; margin-top: 40px;">
    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px; margin-bottom: 20px;">
            <div style="font-size: 16px; font-weight: 600; margin-bottom: 15px;">OneClickLending</div>
            <div style="font-size: 14px; margin-bottom: 10px;">La Radiografía del Productor</div>
            <div style="font-size: 14px;">Sistema Integrado de Análisis Agrícola y Ganadero</div>
        </div>
        <div style="flex: 1; min-width: 200px; margin-bottom: 20px;">
            <div style="font-size: 16px; font-weight: 600; margin-bottom: 15px;">Contacto</div>
            <div style="font-size: 14px; margin-bottom: 10px;">pepo@riverwoodag.com</div>
            <div style="font-size: 14px;">micaias@riverwoodag.com</div>
        </div>
    </div>
    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.2); text-align: center; font-size: 14px;">
        © 2025 OneClickLending - Todos los derechos reservados
    </div>
</div>
""", unsafe_allow_html=True)
