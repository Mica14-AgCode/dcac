import streamlit as st
import json
import os
from datetime import datetime
import hashlib

# Configuración de la página
st.set_page_config(
    page_title="deCampoaCampo - Mercado Ganadero",
    page_icon="🐄",
    layout="wide"
)

# CSS personalizado basado en el diseño de referencia
st.markdown("""
<style>
    .main {
        background-color: white;
    }
    .stButton > button {
        background-color: #1f2937;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #374151;
    }
    .logo-text {
        font-size: 3rem;
        font-weight: 400;
        line-height: 1.2;
    }
    .logo-blue {
        color: #4682B4;
    }
    .logo-gray {
        color: #666666;
    }
    .subtitle {
        color: #666666;
        font-size: 1.5rem;
        font-weight: 300;
        margin-top: -10px;
    }
    .metric-card {
        background-color: #f9fafb;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Inicialización del estado de la sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Archivo de datos
DATA_FILE = "ganadero_data.json"

# Credenciales predefinidas
USERS = {
    'user': {'password': 'dcac2025', 'type': 'usuario'},
    'dcac': {'password': '2025', 'type': 'admin'}
}

# Funciones de utilidad
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def verify_login(username, password):
    if username in USERS and USERS[username]['password'] == password:
        return True, USERS[username]['type']
    return False, None

# Cargar datos
st.session_state.data = load_data()

# Logo y título
def show_logo():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div class="logo-text">
            <span class="logo-blue">deCampo</span><span class="logo-gray">a</span><span class="logo-blue">Campo</span>
        </div>
        <div class="subtitle">Mercado Ganadero</div>
    </div>
    """, unsafe_allow_html=True)

# Página de login
if not st.session_state.logged_in:
    show_logo()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Iniciar Sesión")
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            submitted = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submitted:
                valid, user_type = verify_login(username, password)
                if valid:
                    st.session_state.logged_in = True
                    st.session_state.user_type = user_type
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown("---")
        st.info("**Usuarios de prueba:**\n- Usuario: user / Contraseña: dcac2025\n- Admin: dcac / Contraseña: 2025")

# Interfaz principal
else:
    # Header con información de sesión
    col1, col2 = st.columns([3, 1])
    with col1:
        show_logo()
    with col2:
        st.markdown(f"**Usuario:** {st.session_state.username}")
        st.markdown(f"**Tipo:** {st.session_state.user_type.capitalize()}")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.username = None
            st.rerun()
    
    st.markdown("---")
    
    # Interfaz de Usuario
    if st.session_state.user_type == 'usuario':
        tab1, tab2, tab3 = st.tabs(["🔍 Buscar Ganado", "📊 Mercado", "📈 Estadísticas"])
        
        with tab1:
            st.subheader("🔍 Buscar Información de Ganado")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input("Buscar por productor, CUIT o categoría", placeholder="Ej: Angus, 30-12345678-9")
            with col2:
                st.write("")
                search_btn = st.button("Buscar", use_container_width=True)
            
            if search_btn and search_term:
                # Buscar en los datos
                results = []
                for key, value in st.session_state.data.items():
                    if (search_term.lower() in value.get('productor', '').lower() or
                        search_term.lower() in value.get('cuit', '').lower() or
                        search_term.lower() in value.get('categoria', '').lower()):
                        results.append(value)
                
                if results:
                    st.success(f"✅ Se encontraron {len(results)} resultados")
                    for result in results:
                        with st.expander(f"{result['productor']} - {result['categoria']}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Categoría", result['categoria'])
                                st.metric("Cantidad", f"{result['cantidad']} cabezas")
                            with col2:
                                st.metric("Peso Promedio", f"{result['peso_promedio']} kg")
                                st.metric("Ubicación", result['ubicacion'])
                            with col3:
                                st.metric("Precio por kg", f"${result['precio_kg']}")
                                precio_total = result['cantidad'] * result['peso_promedio'] * result['precio_kg']
                                st.metric("Valor Total", f"${precio_total:,.0f}")
                else:
                    st.warning("No se encontraron resultados")
        
        with tab2:
            st.subheader("📊 Estado del Mercado")
            
            if st.session_state.data:
                # Calcular estadísticas
                total_cabezas = sum(item.get('cantidad', 0) for item in st.session_state.data.values())
                precio_promedio = sum(item.get('precio_kg', 0) for item in st.session_state.data.values()) / len(st.session_state.data) if st.session_state.data else 0
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Cabezas", f"{total_cabezas:,}")
                col2.metric("Productores Activos", len(st.session_state.data))
                col3.metric("Precio Promedio/kg", f"${precio_promedio:.2f}")
                col4.metric("Actualización", datetime.now().strftime("%d/%m/%Y"))
                
                st.markdown("---")
                
                # Mostrar categorías disponibles
                st.markdown("### Categorías Disponibles")
                categorias = {}
                for item in st.session_state.data.values():
                    cat = item.get('categoria', 'Sin categoría')
                    if cat not in categorias:
                        categorias[cat] = {'cantidad': 0, 'productores': 0}
                    categorias[cat]['cantidad'] += item.get('cantidad', 0)
                    categorias[cat]['productores'] += 1
                
                for cat, data in categorias.items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{cat}**")
                        st.caption(f"{data['cantidad']} cabezas • {data['productores']} productores")
                    with col2:
                        if st.button(f"Ver detalles", key=f"cat_{cat}"):
                            st.session_state.selected_category = cat
            else:
                st.info("No hay datos disponibles en el mercado")
        
        with tab3:
            st.subheader("📈 Estadísticas del Mercado")
            
            if st.session_state.data:
                # Resumen por ubicación
                st.markdown("### Distribución por Ubicación")
                ubicaciones = {}
                for item in st.session_state.data.values():
                    ub = item.get('ubicacion', 'Sin ubicación')
                    if ub not in ubicaciones:
                        ubicaciones[ub] = 0
                    ubicaciones[ub] += item.get('cantidad', 0)
                
                for ub, cantidad in sorted(ubicaciones.items(), key=lambda x: x[1], reverse=True):
                    st.markdown(f"**{ub}**: {cantidad:,} cabezas")
                
                st.markdown("---")
                
                # Top productores
                st.markdown("### Top Productores por Volumen")
                productores = sorted(st.session_state.data.values(), 
                                   key=lambda x: x.get('cantidad', 0), 
                                   reverse=True)[:5]
                
                for i, prod in enumerate(productores, 1):
                    st.markdown(f"{i}. **{prod['productor']}** - {prod['cantidad']:,} cabezas")
            else:
                st.info("No hay datos para mostrar estadísticas")
    
    # Interfaz de Administrador
    elif st.session_state.user_type == 'admin':
        tab1, tab2, tab3, tab4 = st.tabs(["➕ Agregar", "📋 Ver Todos", "✏️ Editar", "📊 Dashboard"])
        
        with tab1:
            st.subheader("➕ Agregar Nuevo Registro")
            
            with st.form("nuevo_registro"):
                col1, col2 = st.columns(2)
                
                with col1:
                    productor = st.text_input("Nombre del Productor *")
                    cuit = st.text_input("CUIT *", placeholder="30-12345678-9")
                    categoria = st.selectbox("Categoría *", 
                        ["Terneros", "Novillos", "Vaquillonas", "Vacas", "Toros", "Angus", "Hereford", "Braford"])
                    ubicacion = st.text_input("Ubicación *", placeholder="Provincia, Departamento")
                
                with col2:
                    cantidad = st.number_input("Cantidad de Cabezas *", min_value=1, value=1)
                    peso_promedio = st.number_input("Peso Promedio (kg) *", min_value=1.0, value=300.0)
                    precio_kg = st.number_input("Precio por kg ($) *", min_value=0.01, value=1000.0)
                    observaciones = st.text_area("Observaciones")
                
                submitted = st.form_submit_button("💾 Guardar Registro", use_container_width=True)
                
                if submitted and all([productor, cuit, categoria, ubicacion]):
                    # Crear ID único
                    registro_id = f"{cuit}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    nuevo_registro = {
                        'id': registro_id,
                        'productor': productor,
                        'cuit': cuit,
                        'categoria': categoria,
                        'ubicacion': ubicacion,
                        'cantidad': cantidad,
                        'peso_promedio': peso_promedio,
                        'precio_kg': precio_kg,
                        'observaciones': observaciones,
                        'fecha_carga': datetime.now().isoformat(),
                        'usuario_carga': st.session_state.username
                    }
                    
                    st.session_state.data[registro_id] = nuevo_registro
                    save_data(st.session_state.data)
                    st.success(f"✅ Registro guardado exitosamente!")
                    st.balloons()
        
        with tab2:
            st.subheader("📋 Todos los Registros")
            
            if st.session_state.data:
                # Filtros
                col1, col2, col3 = st.columns(3)
                with col1:
                    filter_cat = st.selectbox("Filtrar por categoría", 
                        ["Todas"] + list(set(item.get('categoria', '') for item in st.session_state.data.values())))
                with col2:
                    filter_ub = st.selectbox("Filtrar por ubicación",
                        ["Todas"] + list(set(item.get('ubicacion', '') for item in st.session_state.data.values())))
                
                # Mostrar registros
                for key, registro in st.session_state.data.items():
                    if (filter_cat == "Todas" or registro.get('categoria') == filter_cat) and \
                       (filter_ub == "Todas" or registro.get('ubicacion') == filter_ub):
                        
                        with st.expander(f"{registro['productor']} - {registro['categoria']} ({registro['cuit']})"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown("**📋 Información Básica**")
                                st.write(f"CUIT: {registro['cuit']}")
                                st.write(f"Categoría: {registro['categoria']}")
                                st.write(f"Ubicación: {registro['ubicacion']}")
                            
                            with col2:
                                st.markdown("**🐄 Detalles del Ganado**")
                                st.write(f"Cantidad: {registro['cantidad']} cabezas")
                                st.write(f"Peso Promedio: {registro['peso_promedio']} kg")
                                st.write(f"Precio/kg: ${registro['precio_kg']}")
                            
                            with col3:
                                st.markdown("**💰 Valores**")
                                total = registro['cantidad'] * registro['peso_promedio'] * registro['precio_kg']
                                st.write(f"Valor Total: ${total:,.0f}")
                                st.write(f"Cargado: {registro.get('fecha_carga', 'N/A')[:10]}")
                                st.write(f"Por: {registro.get('usuario_carga', 'N/A')}")
                            
                            if registro.get('observaciones'):
                                st.markdown("**Observaciones:**")
                                st.write(registro['observaciones'])
                            
                            # Botón eliminar
                            if st.button(f"🗑️ Eliminar", key=f"del_{key}"):
                                del st.session_state.data[key]
                                save_data(st.session_state.data)
                                st.rerun()
            else:
                st.info("No hay registros cargados")
        
        with tab3:
            st.subheader("✏️ Editar Registro")
            
            if st.session_state.data:
                # Selector de registro
                registro_seleccionado = st.selectbox(
                    "Seleccione un registro para editar",
                    options=list(st.session_state.data.keys()),
                    format_func=lambda x: f"{st.session_state.data[x]['productor']} - {st.session_state.data[x]['categoria']}"
                )
                
                if registro_seleccionado:
                    registro = st.session_state.data[registro_seleccionado]
                    
                    with st.form("editar_registro"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            productor = st.text_input("Nombre del Productor", value=registro['productor'])
                            cuit = st.text_input("CUIT", value=registro['cuit'])
                            categoria = st.selectbox("Categoría", 
                                ["Terneros", "Novillos", "Vaquillonas", "Vacas", "Toros", "Angus", "Hereford", "Braford"],
                                index=["Terneros", "Novillos", "Vaquillonas", "Vacas", "Toros", "Angus", "Hereford", "Braford"].index(registro['categoria']))
                            ubicacion = st.text_input("Ubicación", value=registro['ubicacion'])
                        
                        with col2:
                            cantidad = st.number_input("Cantidad de Cabezas", min_value=1, value=registro['cantidad'])
                            peso_promedio = st.number_input("Peso Promedio (kg)", min_value=1.0, value=registro['peso_promedio'])
                            precio_kg = st.number_input("Precio por kg ($)", min_value=0.01, value=registro['precio_kg'])
                            observaciones = st.text_area("Observaciones", value=registro.get('observaciones', ''))
                        
                        submitted = st.form_submit_button("💾 Actualizar Registro", use_container_width=True)
                        
                        if submitted:
                            # Actualizar registro
                            st.session_state.data[registro_seleccionado].update({
                                'productor': productor,
                                'cuit': cuit,
                                'categoria': categoria,
                                'ubicacion': ubicacion,
                                'cantidad': cantidad,
                                'peso_promedio': peso_promedio,
                                'precio_kg': precio_kg,
                                'observaciones': observaciones,
                                'fecha_modificacion': datetime.now().isoformat(),
                                'usuario_modificacion': st.session_state.username
                            })
                            
                            save_data(st.session_state.data)
                            st.success("✅ Registro actualizado exitosamente!")
            else:
                st.info("No hay registros para editar")
        
        with tab4:
            st.subheader("📊 Dashboard Administrativo")
            
            if st.session_state.data:
                # Métricas generales
                col1, col2, col3, col4 = st.columns(4)
                
                total_registros = len(st.session_state.data)
                total_cabezas = sum(item.get('cantidad', 0) for item in st.session_state.data.values())
                valor_total = sum(item.get('cantidad', 0) * item.get('peso_promedio', 0) * item.get('precio_kg', 0) 
                                for item in st.session_state.data.values())
                precio_promedio = sum(item.get('precio_kg', 0) for item in st.session_state.data.values()) / total_registros
                
                col1.metric("Total Registros", total_registros)
                col2.metric("Total Cabezas", f"{total_cabezas:,}")
                col3.metric("Valor Total", f"${valor_total:,.0f}")
                col4.metric("Precio Promedio/kg", f"${precio_promedio:.2f}")
                
                st.markdown("---")
                
                # Resumen por categoría
                st.markdown("### Resumen por Categoría")
                categorias_resumen = {}
                for item in st.session_state.data.values():
                    cat = item.get('categoria', 'Sin categoría')
                    if cat not in categorias_resumen:
                        categorias_resumen[cat] = {'cantidad': 0, 'valor': 0, 'registros': 0}
                    categorias_resumen[cat]['cantidad'] += item.get('cantidad', 0)
                    categorias_resumen[cat]['valor'] += (item.get('cantidad', 0) * 
                                                         item.get('peso_promedio', 0) * 
                                                         item.get('precio_kg', 0))
                    categorias_resumen[cat]['registros'] += 1
                
                for cat, data in sorted(categorias_resumen.items(), key=lambda x: x[1]['valor'], reverse=True):
                    with st.container():
                        col1, col2, col3 = st.columns(3)
                        col1.metric(cat, f"{data['cantidad']:,} cabezas")
                        col2.metric("Valor", f"${data['valor']:,.0f}")
                        col3.metric("Registros", data['registros'])
                
                st.markdown("---")
                
                # Exportar datos
                st.markdown("### 📥 Exportar Datos")
                
                col1, col2 = st.columns(2)
                with col1:
                    json_str = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="📥 Descargar JSON",
                        data=json_str,
                        file_name=f"ganadero_data_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )
                
                with col2:
                    # Crear CSV
                    import csv
                    import io
                    
                    output = io.StringIO()
                    writer = csv.writer(output)
                    
                    # Header
                    writer.writerow(['ID', 'Productor', 'CUIT', 'Categoría', 'Ubicación', 
                                   'Cantidad', 'Peso Promedio', 'Precio/kg', 'Valor Total', 
                                   'Fecha Carga', 'Observaciones'])
                    
                    # Datos
                    for key, item in st.session_state.data.items():
                        valor_total = item['cantidad'] * item['peso_promedio'] * item['precio_kg']
                        writer.writerow([
                            key,
                            item['productor'],
                            item['cuit'],
                            item['categoria'],
                            item['ubicacion'],
                            item['cantidad'],
                            item['peso_promedio'],
                            item['precio_kg'],
                            valor_total,
                            item.get('fecha_carga', '')[:10],
                            item.get('observaciones', '')
                        ])
                    
                    csv_str = output.getvalue()
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv_str,
                        file_name=f"ganadero_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No hay datos para mostrar en el dashboard")

# Footer
st.markdown("---")
st.markdown(
    "<center><small>deCampoaCampo - Mercado Ganadero © 2024</small></center>", 
    unsafe_allow_html=True
)
