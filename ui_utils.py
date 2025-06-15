import streamlit as st

# Page header rendering
def render_page_header(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.markdown(subtitle)
    st.markdown("---")

# Instruction helper block
def render_instructions_block(instructions):
    st.info(instructions)

# KPI card rendering
def render_kpi_cards(kpi_list):
    cols = st.columns(len(kpi_list))
    for col, (label, value, delta) in zip(cols, kpi_list):
        col.metric(label, value, delta if delta is not None else "")
