import streamlit as st
import pandas as pd

st.set_page_config(page_title="Plataforma de Créditos - deCampoaCampo", layout="wide")

# Estilos CSS simples
st.markdown("""
    <style>
        .main {
            font-family: "Georgia", serif;
            color: #336699;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 18px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Plataforma de Créditos - deCampoaCampo")

# Tabs principales
tabs = st.tabs(["👤 Usuario", "🛠️ Administrador"])

# ==== TAB 1: USUARIO ====
with tabs[0]:
    st.subheader("Resumen Financiero del Productor")
    st.info("Aquí se mostrará la información cargada por el administrador.")
    st.warning("🔧 En construcción - se completará cuando haya datos cargados.")

# ==== TAB 2: ADMINISTRADOR ====
with tabs[1]:
    st.subheader("Carga de Datos del Productor")
    
    with st.form("carga_productor"):
        cuit = st.text_input("CUIT")
        razon_social = st.text_input("Razón Social")
        ha_agricolas = st.number_input("Hectáreas Agrícolas", min_value=0.0)
        ha_ganaderas = st.number_input("Hectáreas Ganaderas", min_value=0.0)
        ha_totales = ha_agricolas + ha_ganaderas
        st.markdown(f"**Hectáreas Totales:** {ha_totales:.2f}")

        submitted = st.form_submit_button("Guardar Datos")
        
        if submitted:
            st.success("✅ Datos guardados correctamente (simulado)")
            # Aquí después guardaremos en GSheet o base de datos
