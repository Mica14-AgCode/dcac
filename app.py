import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import numpy as np
from datetime import datetime, timedelta
import json

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
    
    .positive { color: #2ecc71; }
    .warning { color: #f39c12; }
    .negative { color: #e74c3c; }
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
                {"id": "P001", "tipo": "Agricola", "superficie": 1200, 
                 "coordenadas": [[-31.569, -60.710], [-31.582, -60.710], [-31.582, -60.690], [-31.569, -60.690]]},
                {"id": "P002", "tipo": "Agricola", "superficie": 800,
                 "coordenadas": [[-31.590, -60.710], [-31.600, -60.710], [-31.600, -60.690], [-31.590, -60.690]]},
                {"id": "P003", "tipo": "No_Agricola", "superficie": 500,
                 "coordenadas": [[-31.610, -60.710], [-31.620, -60.710], [-31.620, -60.690], [-31.610, -60.690]]}
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
            # Gráfico de rotación de cultivos
            st.subheader("Rotación de Cultivos (Campañas 2019-2024)")
            
            rotacion_df = pd.DataFrame(productor_encontrado['rotacionCultivos'])
            
            fig_rotacion = go.Figure()
            
            colors = {
                'soja': '#7aa0c3',
                'maiz': '#4478a7',
                'girasol': '#FFD740',
                'maiz2da': '#8aba5f',
                'noAgricola': '#e0e0e0'
            }
            
            for cultivo in ['soja', 'maiz', 'girasol', 'maiz2da', 'noAgricola']:
                fig_rotacion.add_trace(go.Bar(
                    name=cultivo.replace('maiz2da', 'Maíz 2da').replace('noAgricola', 'No Agrícola').title(),
                    x=rotacion_df['campania'],
                    y=rotacion_df[cultivo],
                    marker_color=colors[cultivo]
                ))
            
            fig_rotacion.update_layout(
                barmode='stack',
                title="Evolución de Cultivos por Campaña (%)",
                xaxis_title="Campaña",
                yaxis_title="Porcentaje (%)",
                height=400
            )
            
            st.plotly_chart(fig_rotacion, use_container_width=True)
            
            # Mapa de polígonos
            st.subheader("Polígonos Productivos")
            
            # Crear mapa centrado en los datos
            center_lat = -31.585
            center_lon = -60.700
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
            
            for poligono in productor_encontrado['poligonos']:
                color = '#8aba5f' if poligono['tipo'] == 'Agricola' else '#e0e0e0'
                
                folium.Polygon(
                    locations=poligono['coordenadas'],
                    color='#4478a7',
                    weight=1,
                    fillColor=color,
                    fillOpacity=0.7,
                    popup=f"ID: {poligono['id']}<br>Tipo: {poligono['tipo']}<br>Superficie: {poligono['superficie']:,} ha"
                ).add_to(m)
            
            st_folium(m, width=700, height=400)
        
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
                        'Propio 5 años': rp['rendimiento5'],
                        'Departamento 5 años': rd['rendimiento5'],
                        'Propio 10 años': rp['rendimiento10'],
                        'Departamento 10 años': rd['rendimiento10']
                    })
            
            rendimientos_df = pd.DataFrame(rendimientos_data)
            
            # Gráfico de barras comparativo
            fig_rend = go.Figure()
            
            colors_rend = ['#4478a7', '#7aa0c3', '#8aba5f', '#a5d683']
            
            for i, col in enumerate(['Propio 5 años', 'Departamento 5 años', 'Propio 10 años', 'Departamento 10 años']):
                fig_rend.add_trace(go.Bar(
                    name=col,
                    x=rendimientos_df['Cultivo'],
                    y=rendimientos_df[col],
                    marker_color=colors_rend[i]
                ))
            
            fig_rend.update_layout(
                title="Comparativa de Rendimientos (kg/ha)",
                xaxis_title="Cultivo",
                yaxis_title="Rendimiento (kg/ha)",
                height=400
            )
            
            st.plotly_chart(fig_rend, use_container_width=True)
            
            # Tabla detallada
            st.subheader("Detalle de Rendimientos")
            
            # Calcular diferencias
            for i, row in rendimientos_df.iterrows():
                dif_5 = row['Propio 5 años'] - row['Departamento 5 años']
                pct_5 = (dif_5 / row['Departamento 5 años']) * 100
                rendimientos_df.loc[i, 'Diferencia 5 años'] = f"{dif_5:+,.0f} ({pct_5:+.1f}%)"
            
            st.dataframe(rendimientos_df, hide_index=True, use_container_width=True)
        
        # Tab 3: Flujo de Caja
        with tab3:
            finanzas = productor_encontrado['finanzas']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Resumen Financiero")
                
                # Gráfico de cash flow
                saldo_sin_deuda = finanzas['ingresosTotales'] - (finanzas['egresosTotales'] - finanzas['servicioDeudaActual'])
                
                fig_cash = go.Figure()
                
                fig_cash.add_trace(go.Bar(
                    name='Ingresos',
                    x=['Sin Deuda', 'Con Deuda Actual'],
                    y=[finanzas['ingresosTotales'], finanzas['ingresosTotales']],
                    marker_color='#8aba5f'
                ))
                
                fig_cash.add_trace(go.Bar(
                    name='Egresos sin deuda',
                    x=['Sin Deuda', 'Con Deuda Actual'],
                    y=[finanzas['egresosTotales'] - finanzas['servicioDeudaActual'], 0],
                    marker_color='#7aa0c3'
                ))
                
                fig_cash.add_trace(go.Bar(
                    name='Egresos con deuda',
                    x=['Sin Deuda', 'Con Deuda Actual'],
                    y=[0, finanzas['egresosTotales']],
                    marker_color='#4478a7'
                ))
                
                fig_cash.update_layout(
                    title="Comparativa de Flujo de Caja",
                    yaxis_title="USD",
                    height=400,
                    barmode='stack'
                )
                
                st.plotly_chart(fig_cash, use_container_width=True)
            
            with col2:
                st.subheader("Score Crediticio")
                
                score = productor_encontrado['credito']['scoreNosis']
                percentil = productor_encontrado['comparativaMercado']['percentilScoreCredito']
                
                # Gauge chart para score
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Score Nosis"},
                    gauge = {
                        'axis': {'range': [None, 1000]},
                        'bar': {'color': "#2ecc71"},
                        'steps': [
                            {'range': [0, 600], 'color': "#ffebee"},
                            {'range': [600, 800], 'color': "#fff3e0"},
                            {'range': [800, 1000], 'color': "#e8f5e8"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 900
                        }
                    }
                ))
                
                fig_gauge.update_layout(height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                st.markdown(f"""
                <div style="text-align: center; margin-top: 10px;">
                    <div class="metric-value">{percentil}°</div>
                    <div class="metric-label">Percentil</div>
                    <p style="font-size: 14px;">Mejor que el {percentil}% de productores</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Tabla de flujo de caja detallado
            st.subheader("Flujo de Caja Detallado")
            
            flujo_data = [
                ("INGRESOS", "", ""),
                ("Venta de Cultivos", f"${finanzas['ventaCultivos']:,}", f"{(finanzas['ventaCultivos']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Otros Ingresos", f"${finanzas['otrosIngresos']:,}", f"{(finanzas['otrosIngresos']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Total Ingresos", f"${finanzas['ingresosTotales']:,}", "100.0%"),
                ("", "", ""),
                ("EGRESOS", "", ""),
                ("Costos de Producción", f"${finanzas['costoProduccion']:,}", f"{(finanzas['costoProduccion']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Alquileres", f"${finanzas['alquileres']:,}", f"{(finanzas['alquileres']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Gastos de Maquinaria", f"${finanzas['gastosMaquinaria']:,}", f"{(finanzas['gastosMaquinaria']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Fletes", f"${finanzas['fletes']:,}", f"{(finanzas['fletes']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Impuestos", f"${finanzas['impuestos']:,}", f"{(finanzas['impuestos']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Otros Gastos", f"${finanzas['otrosGastos']:,}", f"{(finanzas['otrosGastos']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Servicio de Deuda Actual", f"${finanzas['servicioDeudaActual']:,}", f"{(finanzas['servicioDeudaActual']/finanzas['ingresosTotales']*100):.1f}%"),
                ("Total Egresos", f"${finanzas['egresosTotales']:,}", f"{(finanzas['egresosTotales']/finanzas['ingresosTotales']*100):.1f}%"),
                ("", "", ""),
                ("SALDO NETO", f"${finanzas['saldoNeto']:,}", f"{(finanzas['saldoNeto']/finanzas['ingresosTotales']*100):.1f}%")
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
                    ("Transacciones (Ventas o Compras) >= 3", credito['transaccionesDCAC'] >= 3, "CUMPLE"),
                    ("Crédito < Pagos realizados en DC", credito['creditoPagos'] < 1, "CUMPLE")
                ]
                
                for criterio, cumple, status in criterios_dcac:
                    color_class = "criteria-pass" if cumple else "criteria-fail"
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e0e0e0;">
                        <span>{criterio}</span>
                        <span class="{color_class}">{status}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("**Ratios Financieros**")
                criterios_ratios = [
                    ("Deuda/Activos <= 0.15", finanzas['deudaActivos'] <= 0.15, "CUMPLE"),
                    ("Deuda/Hacienda <= 0.25", finanzas['deudaHacienda'] <= 0.25, "CUMPLE"),
                    ("Ratio Servicio de Deuda >= 1.5", finanzas['ratioServicioDeuda'] >= 1.5, "CUMPLE")
                ]
                
                for criterio, cumple, status in criterios_ratios:
                    color_class = "criteria-pass" if cumple else "criteria-fail"
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e0e0e0;">
                        <span>{criterio}</span>
                        <span class="{color_class}">{status}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Calificación Crediticia**")
                criterios_credito = [
                    ("Score Nosis >= 600", credito['scoreNosis'] >= 600, "CUMPLE"),
                    ("Cheques Rechazados = 0", credito['chequesRechazados'] == 0, "CUMPLE"),
                    ("Créditos con Bancos <= 3", credito['creditosBancos'] <= 3, "CUMPLE"),
                    ("Consultas Nosis <= 1.5", credito['consultasNosis'] <= 1.5, "CUMPLE")
                ]
                
                for criterio, cumple, status in criterios_credito:
                    color_class = "criteria-pass" if cumple else "criteria-fail"
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e0e0e0;">
                        <span>{criterio}</span>
                        <span class="{color_class}">{status}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("**Garantías**")
                garantias = [
                    ("Prenda sobre hacienda", credito['garantias']['prendaHacienda'], "520,000 USD"),
                    ("Garantía personal", credito['garantias']['garantiaPersonal'], "-"),
                    ("Potencial de Hipoteca", credito['garantias']['hipoteca'], "1,800,000 USD")
                ]
                
                garantias_df = pd.DataFrame(garantias, columns=["Tipo", "Disponible", "Valor Estimado"])
                garantias_df["Disponible"] = garantias_df["Disponible"].map({True: "Sí", False: "No"})
                st.dataframe(garantias_df, hide_index=True, use_container_width=True)
            
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
                
                if st.button("Simular Crédito", type="primary"):
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
                    
                    st.session_state.simulacion = {
                        'monto': monto,
                        'tasa': tasa,
                        'plazo': plazo,
                        'cuota': cuota,
                        'interes_total': interes_total,
                        'monto_total': monto_total,
                        'cuota_anual': cuota_anual,
                        'numero_pagos': numero_pagos
                    }
            
            with col2:
                st.markdown("**Resultados de la Simulación**")
                
                if 'simulacion' in st.session_state:
                    sim = st.session_state.simulacion
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Monto</div>
                        <div class="metric-value">${sim['monto']:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Cuota {frecuencia}</div>
                        <div class="metric-value">${sim['cuota']:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Interés Total</div>
                        <div class="metric-value">${sim['interes_total']:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Monto Total a Pagar</div>
                        <div class="metric-value">${sim['monto_total']:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Análisis de impacto
                    st.markdown("**Impacto en Métricas Crediticias**")
                    
                    nueva_deuda = sim['monto']
                    nuevo_costo_anual = sim['cuota_anual']
                    
                    nuevo_deuda_activos = (finanzas['deudaActivos'] * finanzas['activosTotales'] + nueva_deuda) / finanzas['activosTotales']
                    nuevo_ratio_servicio = finanzas['saldoNeto'] / (finanzas['servicioDeudaActual'] + nuevo_costo_anual)
                    
                    porcentaje_flujo = (nuevo_costo_anual / finanzas['saldoNeto']) * 100
                    saldo_final = finanzas['saldoNeto'] - nuevo_costo_anual
                    
                    color_ratio = "positive" if nuevo_ratio_servicio >= 1.5 else "warning" if nuevo_ratio_servicio >= 1.2 else "negative"
                    
                    st.markdown(f"""
                    **Nuevo Ratio Servicio de Deuda:** <span class="{color_ratio}">{nuevo_ratio_servicio:.2f}</span><br>
                    **Cuota Anual:** ${nuevo_costo_anual:,.2f} ({porcentaje_flujo:.1f}% del flujo)<br>
                    **Saldo después de pagos:** ${saldo_final:,.2f}
                    """, unsafe_allow_html=True)
                    
                    if nuevo_ratio_servicio >= 1.5:
                        st.success("✅ El productor PUEDE afrontar el nuevo crédito")
                    elif nuevo_ratio_servicio >= 1.2:
                        st.warning("⚠️ El productor puede afrontar con PRECAUCIÓN el nuevo crédito")
                    else:
                        st.error("❌ El productor NO PUEDE afrontar el nuevo crédito")
        
        # Tab 6: Comparativa de Mercado
        with tab6:
            st.subheader("Posicionamiento en el Mercado")
            
            comparativa = productor_encontrado['comparativaMercado']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Apalancamiento**")
                percentil_apal = comparativa['percentilApalancamiento']
                
                fig_apal = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = percentil_apal,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"{percentil_apal}° Percentil"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#f39c12" if percentil_apal < 75 else "#2ecc71"},
                        'steps': [
                            {'range': [0, 25], 'color': "#ffebee"},
                            {'range': [25, 75], 'color': "#fff3e0"},
                            {'range': [75, 100], 'color': "#e8f5e8"}
                        ]
                    }
                ))
                fig_apal.update_layout(height=250)
                st.plotly_chart(fig_apal, use_container_width=True)
                
                st.markdown(f"<p style='text-align: center; font-size: 14px;'>{100-percentil_apal}% de productores tienen mayor apalancamiento</p>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Productividad**")
                percentil_prod = comparativa['percentilProductividad']
                
                fig_prod = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = percentil_prod,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"{percentil_prod}° Percentil"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#2ecc71"},
                        'steps': [
                            {'range': [0, 25], 'color': "#ffebee"},
                            {'range': [25, 75], 'color': "#fff3e0"},
                            {'range': [75, 100], 'color': "#e8f5e8"}
                        ]
                    }
                ))
                fig_prod.update_layout(height=250)
                st.plotly_chart(fig_prod, use_container_width=True)
                
                st.markdown(f"<p style='text-align: center; font-size: 14px;'>Mejor que el {percentil_prod}% de productores</p>", unsafe_allow_html=True)
            
            with col3:
                st.markdown("**Score Crediticio**")
                percentil_score = comparativa['percentilScoreCredito']
                
                fig_score = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = percentil_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"{percentil_score}° Percentil"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#2ecc71"},
                        'steps': [
                            {'range': [0, 25], 'color': "#ffebee"},
                            {'range': [25, 75], 'color': "#fff3e0"},
                            {'range': [75, 100], 'color': "#e8f5e8"}
                        ]
                    }
                ))
                fig_score.update_layout(height=250)
                st.plotly_chart(fig_score, use_container_width=True)
                
                st.markdown(f"<p style='text-align: center; font-size: 14px;'>Mejor que el {percentil_score}% de productores</p>", unsafe_allow_html=True)
            
            # Distribución del mercado
            st.subheader("Distribución del Mercado")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Distribución por Apalancamiento**")
                
                # Generar datos simulados de distribución
                np.random.seed(42)
                apalancamiento_data = np.random.normal(50, 20, 1000)
                apalancamiento_data = np.clip(apalancamiento_data, 0, 100)
                
                bins = range(0, 101, 10)
                hist, _ = np.histogram(apalancamiento_data, bins=bins)
                
                colors_hist = ['#4478a7' if i*10 <= percentil_apal < (i+1)*10 else '#7aa0c3' for i in range(len(hist))]
                
                fig_dist_apal = go.Figure(data=[go.Bar(
                    x=[f"{i*10}-{(i+1)*10}" for i in range(len(hist))],
                    y=hist,
                    marker_color=colors_hist
                )])
                
                fig_dist_apal.update_layout(
                    title="Distribución de Apalancamiento",
                    xaxis_title="Percentil",
                    yaxis_title="Cantidad de Productores",
                    height=300
                )
                
                st.plotly_chart(fig_dist_apal, use_container_width=True)
            
            with col2:
                st.markdown("**Distribución por Score Crediticio**")
                
                # Generar datos simulados de distribución
                score_data = np.random.normal(60, 25, 1000)
                score_data = np.clip(score_data, 0, 100)
                
                hist_score, _ = np.histogram(score_data, bins=bins)
                
                colors_hist_score = ['#4478a7' if i*10 <= percentil_score < (i+1)*10 else '#7aa0c3' for i in range(len(hist_score))]
                
                fig_dist_score = go.Figure(data=[go.Bar(
                    x=[f"{i*10}-{(i+1)*10}" for i in range(len(hist_score))],
                    y=hist_score,
                    marker_color=colors_hist_score
                )])
                
                fig_dist_score.update_layout(
                    title="Distribución de Score Crediticio",
                    xaxis_title="Percentil",
                    yaxis_title="Cantidad de Productores",
                    height=300
                )
                
                st.plotly_chart(fig_dist_score, use_container_width=True)

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
