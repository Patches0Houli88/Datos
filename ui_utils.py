import streamlit as st

# Set global Streamlit config early for all pages
st.set_page_config(page_title="Datos 3.0 PRO", layout="wide")

# ------------------------
# Global Color Theme
PRIMARY_COLOR = "#1f77b4"  # Streamlit SaaS blue
SECONDARY_COLOR = "#ff7f0e"
ACCENT_COLOR = "#2ca02c"

# ------------------------
# Universal Page Header

def render_page_header(title, subtitle=None, icon=None):
    st.markdown(f"""
    <h1 style='font-size: 42px; color: {PRIMARY_COLOR}; margin-bottom: 0px;'>{icon or ''} {title}</h1>
    """, unsafe_allow_html=True)
    
    if subtitle:
        st.markdown(f"""<p style='font-size: 18px; color: #aaa;'>{subtitle}</p>""", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 0 0 25px 0;'>", unsafe_allow_html=True)

# ------------------------
# Expandable instructions

def render_instructions_block(instructions_text):
    with st.expander("ℹ️ How To Use This Page"):
        st.markdown(instructions_text)

# ------------------------
# Universal KPI Cards

def render_kpi_cards(metrics: list):
    cols = st.columns(len(metrics))
    for col, (label, value, delta) in zip(cols, metrics):
        col.metric(label, value, delta=delta if delta else None)
