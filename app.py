import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from streamlit_folium import folium_static
import folium

# Configuración de la página
st.set_page_config(
    page_title="Análisis Agrícola Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para cargar datos de un CUIT
def load_cuit_data(cuit_folder):
    """Carga los datos del Super CSV y otros archivos relevantes para un CUIT."""
    try:
        # Cargar Super CSV
        csv_path = os.path.join(cuit_folder, "Super_CSV", f"Super_CSV_Insights_{os.path.basename(cuit_folder).split('_')[1]}.csv")
        data = pd.read_csv(csv_path)
        return data
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return None

def create_rendimientos_chart(data):
    """Crea un gráfico de barras comparativo de rendimientos."""
    cultivos = ['Maíz', 'Soja 1ra', 'Trigo Total']
    fig = go.Figure()
    
    # Agregar barras para rendimientos de 10 años
    fig.add_trace(go.Bar(
        name='Rendimiento 10 años',
        x=cultivos,
        y=[data[f'Rendimiento_10_Anos_{c}'].values[0] for c in cultivos],
        text=[f"{data[f'Rendimiento_10_Anos_{c}'].values[0]:,.0f}" for c in cultivos],
        textposition='auto',
    ))
    
    # Agregar barras para rendimientos de 5 años
    fig.add_trace(go.Bar(
        name='Rendimiento 5 años',
        x=cultivos,
        y=[data[f'Rendimiento_5_Anos_{c}'].values[0] for c in cultivos],
        text=[f"{data[f'Rendimiento_5_Anos_{c}'].values[0]:,.0f}" for c in cultivos],
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Comparativa de Rendimientos por Cultivo',
        xaxis_title='Cultivo',
        yaxis_title='Rendimiento (kg/ha)',
        barmode='group'
    )
    
    return fig

def main():
    # Sidebar
    st.sidebar.title("🌾 Análisis Agrícola")
    
    # Selector de método de entrada
    input_method = st.sidebar.radio(
        "Seleccione método de entrada",
        ["Cargar archivo", "Seleccionar de carpeta"]
    )
    
    if input_method == "Cargar archivo":
        uploaded_file = st.sidebar.file_uploader("Cargar Super CSV", type=['csv'])
        if uploaded_file:
            data = pd.read_csv(uploaded_file)
            st.session_state['current_data'] = data
    else:
        # Buscar carpetas de análisis en Downloads
        analysis_folders = [d for d in os.listdir("/Users/mica14/Downloads") 
                          if d.startswith("Analisis_") and 
                          os.path.isdir(os.path.join("/Users/mica14/Downloads", d))]
        
        if analysis_folders:
            selected_folder = st.sidebar.selectbox(
                "Seleccionar análisis",
                analysis_folders,
                format_func=lambda x: x.split('_')[1]  # Mostrar solo el CUIT
            )
            
            if selected_folder:
                data = load_cuit_data(os.path.join("/Users/mica14/Downloads", selected_folder))
                if data is not None:
                    st.session_state['current_data'] = data
        else:
            st.sidebar.warning("No se encontraron carpetas de análisis")
    
    # Main content
    if 'current_data' in st.session_state:
        data = st.session_state['current_data']
        
        # Header con información principal
        st.title(f"Dashboard Análisis Agrícola - CUIT {data['Identificador'].values[0]}")
        st.caption(f"Fecha de análisis: {data['Fecha_Analisis'].values[0]}")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Área Total", f"{data['Area_Total_Ha'].values[0]:,.2f} Ha")
        with col2:
            st.metric("Área Agrícola", f"{data['Area_Agricola_Ha'].values[0]:,.2f} Ha")
        with col3:
            st.metric("% Agrícola", f"{data['Porcentaje_Agricola'].values[0]:.1f}%")
        with col4:
            st.metric("Distancia a Puerto", f"{data['Distancia_Puerto_Ponderada_Km'].values[0]:.1f} km")
        
        # Tabs para diferentes análisis
        tab1, tab2, tab3 = st.tabs(["📊 Rendimientos", "🗺️ Ubicación", "📈 Cultivos"])
        
        with tab1:
            # Gráfico de rendimientos
            st.plotly_chart(create_rendimientos_chart(data), use_container_width=True)
            
            # Tabla de mejores y peores rendimientos
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Mejores Rendimientos")
                mejores = pd.DataFrame({
                    'Cultivo': ['Maíz', 'Soja 1ra', 'Trigo Total'],
                    'Rendimiento (kg/ha)': [
                        data['Mejor_Rendimiento_Maíz'].values[0],
                        data['Mejor_Rendimiento_Soja 1ra'].values[0],
                        data['Mejor_Rendimiento_Trigo Total'].values[0]
                    ]
                })
                st.dataframe(mejores)
            
            with col2:
                st.subheader("Peores Rendimientos")
                peores = pd.DataFrame({
                    'Cultivo': ['Maíz', 'Soja 1ra', 'Trigo Total'],
                    'Rendimiento (kg/ha)': [
                        data['Peor_Rendimiento_Maíz'].values[0],
                        data['Peor_Rendimiento_Soja 1ra'].values[0],
                        data['Peor_Rendimiento_Trigo Total'].values[0]
                    ]
                })
                st.dataframe(peores)
        
        with tab2:
            st.subheader("Información Geográfica")
            col1, col2 = st.columns([2,1])
            
            with col1:
                # Aquí iría el mapa con folium si tuviéramos las coordenadas
                st.info("Mapa no disponible - Se requieren coordenadas")
            
            with col2:
                st.metric("Departamentos", data['Cantidad_Departamentos'].values[0])
                st.write(f"**Departamentos:** {data['Departamentos'].values[0]}")
                st.write(f"**Puertos cercanos:** {data['Puertos_Cercanos'].values[0]}")
                st.metric("Distancia promedio a puertos", 
                         f"{data['Distancia_Promedio_Puertos_Km'].values[0]:.1f} km")
        
        with tab3:
            st.subheader("Distribución de Cultivos")
            # Crear gráfico de distribución de cultivos
            cultivos_data = pd.DataFrame({
                'Cultivo': ['Principal 16', 'Principal 32', 'Principal 64'],
                'Área (Ha)': [
                    data['Area_Cultivo_16_Ha'].values[0],
                    data['Area_Cultivo_32_Ha'].values[0],
                    data['Area_Cultivo_64_Ha'].values[0]
                ],
                'Porcentaje': [
                    data['Porcentaje_Cultivo_16'].values[0],
                    data['Porcentaje_Cultivo_32'].values[0],
                    data['Porcentaje_Cultivo_64'].values[0]
                ]
            })
            
            fig = px.bar(cultivos_data, 
                        x='Cultivo', 
                        y='Área (Ha)',
                        text='Porcentaje',
                        title="Distribución de Cultivos Principales")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 
