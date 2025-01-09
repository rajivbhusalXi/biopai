import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(page_title="Bioprocess Designer Pro", layout="wide")

# Title and introduction
st.title("🧬 Bioprocess Designer Pro")
st.markdown("""
This advanced tool helps bioprocess engineers design and optimize bioprocessing experiments 
with comprehensive process controls and monitoring strategies.
""")

# Sidebar for process configuration
def configure_process():
    st.header("Process Configuration")
    
    process_type = st.selectbox(
        "Select Process Type",
        ["Batch Culture", "Fed-batch Culture", "Continuous Culture", "Perfusion Culture"]
    )
    
    organism_type = st.selectbox(
        "Select Organism Type",
        ["CHO Cells", "E. coli", "Pichia pastoris", "S. cerevisiae", "HEK293", "Hybridoma"]
    )
    
    scale = st.select_slider(
        "Select Process Scale",
        options=["Laboratory (1-10L)", "Pilot (10-100L)", "Production (>100L)"]
    )
    
    return process_type, organism_type, scale

process_type, organism_type, scale = configure_process()

# Main content in tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Process Parameters", 
    "Media Design", 
    "Process Controls",
    "PAT Strategy",
    "Safety Controls"
])

# Function to configure process parameters
def configure_process_parameters():
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Parameters")
        temp_range = st.slider("Temperature Range (°C)", 20.0, 45.0, (30.0, 37.0), 0.5)
        ph_range = st.slider("pH Range", 4.0, 9.0, (6.8, 7.2), 0.1)
        do_setpoint = st.slider("Dissolved Oxygen Setpoint (%)", 20, 100, 40)
    
    with col2:
        st.subheader("Advanced Parameters")
        agitation = st.number_input("Agitation Speed (RPM)", 50, 1500, 200)
        aeration = st.number_input("Aeration Rate (vvm)", 0.1, 2.0, 0.5, 0.1)
        duration = st.number_input("Process Duration (hours)", 1, 1000, 168)
    
    return temp_range, ph_range, do_setpoint, agitation, aeration, duration

temp_range, ph_range, do_setpoint, agitation, aeration, duration = configure_process_parameters()

# Function to configure media components
def configure_media():
    st.subheader("Media Components")
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("Carbon Sources (g/L)")
        glucose_conc = st.number_input("Glucose", 0.0, 100.0, 10.0)
        glutamine_conc = st.number_input("Glutamine", 0.0, 10.0, 2.0)
        base_media = st.selectbox("Select Base Media", ["DMEM", "RPMI", "CD CHO", "LB", "TB", "YPD", "Minimal Media", "Custom"])
    
    with col4:
        st.write("Additional Components")
        components = {
            "Yeast Extract": st.checkbox("Yeast Extract", True),
            "Peptone": st.checkbox("Peptone", True),
            "Trace Elements": st.checkbox("Trace Elements", True),
            "Vitamins": st.checkbox("Vitamins", True),
            "Antifoam": st.checkbox("Antifoam", True)
        }
    
    return glucose_conc, glutamine_conc, base_media, components

glucose_conc, glutamine_conc, base_media, components = configure_media()

# Function to configure process controls
def configure_process_controls():
    st.subheader("Advanced Process Controls")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.write("PID Control Parameters")
        temp_kp = st.number_input("Temperature Kp", 0.0, 100.0, 2.0)
        temp_ki = st.number_input("Temperature Ki", 0.0, 100.0, 0.5)
        temp_kd = st.number_input("Temperature Kd", 0.0, 
