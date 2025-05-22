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
            "porcentajeAgricola": 80,
            "departamento": "San Justo",
            "provincia": "Santa Fe",
            "poligonos": [
                {"id": "P001", "tipo": "Agrícola", "superficie": 1200},
                {"id": "P002", "tipo": "Agrícola", "superficie": 800},
                {"id": "P003", "tipo": "No Agrícola", "superficie": 500}
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
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
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
                <div class="metric-subvalue">hectáreas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Porcentaje Agrícola</div>
                <div class="metric-value">{productor_encontrado['porcentajeAgricola']}%</div>
                <div class="metric-subvalue">del total</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Ubicación</div>
                <div class="metric-value">{productor_encontrado['departamento']}</div>
                <div class="metric-subvalue">{productor_encontrado['provincia']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Tabs principales
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Información General", "Rendimientos", "Flujo de Caja", 
            "Métricas de Crédito", "Simulador", "Comparativa de Mercado"
        ])
        
        # Tab 1: Información General
        with tab1:
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
                st.subheader("Polígonos Productivos")
                
                # Mostrar información de polígonos en tabla
                poligonos_df = pd.DataFrame([
                    {
                        'ID': p['id'],
                        'Tipo': p['tipo'],
                        'Superficie (ha)': f"{p['superficie']:,}"
                    } for p in productor_encontrado['poligonos']
                ])
                st.dataframe(poligonos_df, hide_index=True, use_container_width=True)
                
                # Resumen de polígonos
                total_agricola = sum(p['superficie'] for p in productor_encontrado['poligonos'] if p['tipo'] == 'Agrícola')
                total_no_agricola = sum(p['superficie'] for p in productor_encontrado['poligonos'] if p['tipo'] == 'No Agrícola')
                
                st.metric("Total Agrícola", f"{total_agricola:,} ha")
                st.metric("Total No Agrícola", f"{total_no_agricola:,} ha")
        
        # Tab 2: Rendimientos
        with tab2:
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
        
        # Tab 3: Flujo de Caja
        with tab3:
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
        
        # Tab 4: Métricas de Crédito
        with tab4:
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
        
        # Tab 5: Simulador
        with tab5:
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
        
        # Tab 6: Comparativa de Mercado
        with tab6:
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

else:
    # Mostrar mensaje inicial
    st.markdown("""
    <div style="text-align: center; padding: 50px; color: #666666;">
        <div style="font-size: 48px; margin-bottom: 15px;">🔍</div>
        <div style="font-size: 18px; margin-bottom: 5px;">Ingrese un CUIT o Razón Social para consultar</div>
        <div style="font-size: 14px;">La radiografía completa del productor en un solo lugar</div>
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
            <div style="font-size: 14px;">Sistema Integrado de Análisis Agrícola con Google Earth Engine</div>
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
