import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import json
import base64
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import subprocess

# Configuration
VERSION = "2.1.0"
CACHE_TTL = 3600  # Cache time to live in seconds

@dataclass
class ProcessParameters:
    """Data class for storing process parameters"""
    temp_range: Tuple[float, float]
    ph_range: Tuple[float, float]
    do_setpoint: float
    agitation: int
    aeration: float
    duration: int

    def to_dict(self) -> dict:
        return {
            "temp_range": self.temp_range,
            "ph_range": self.ph_range,
            "do_setpoint": self.do_setpoint,
            "agitation": self.agitation,
            "aeration": self.aeration,
            "duration": self.duration
        }

class BioprocessApp:
    def __init__(self):
        """Initialize the application with configuration and state management"""
        self.configure_page()
        self.load_config()
        self.initialize_session_state()

    def configure_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Bioprocess Designer Pro",
            page_icon="🧬",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    @st.cache_data(ttl=CACHE_TTL)
    def load_config(self):
        """Load application configuration with caching"""
        self.config = {
            "process_types": ["Batch Culture", "Fed-batch Culture", "Continuous Culture", "Perfusion Culture"],
            "organisms": {
                "Mammalian": ["CHO Cells", "HEK293", "Hybridoma"],
                "Microbial": ["E. coli", "Pichia pastoris", "S. cerevisiae"]
            },
            "scales": ["Laboratory (1-10L)", "Pilot (10-100L)", "Production (>100L)"],
            "base_media": {
                "Mammalian": ["DMEM", "RPMI", "CD CHO"],
                "Microbial": ["LB", "TB", "YPD", "Minimal Media"],
                "Custom": ["Custom"]
            },
            "default_parameters": {
                "CHO Cells": {"temp": (37.0, 37.0), "ph": (7.0, 7.2), "do": 40},
                "E. coli": {"temp": (30.0, 37.0), "ph": (6.8, 7.2), "do": 30}
            }
        }

    def initialize_session_state(self):
        """Initialize or reset session state variables"""
        if 'process_history' not in st.session_state:
            st.session_state.process_history = []
        if 'current_parameters' not in st.session_state:
            st.session_state.current_parameters = None
        if 'warnings' not in st.session_state:
            st.session_state.warnings = []

    def render_header(self):
        """Render application header with version and description"""
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("🧬 Bioprocess Designer Pro")
            st.markdown("""
                Advanced bioprocess design and optimization tool for bioprocess engineers.
                Configure, simulate, and analyze your bioprocessing experiments.
                """)
        with col2:
            st.markdown(f"**Version:** {VERSION}")
            if st.button("Clear All"):
                self.initialize_session_state()
                st.experimental_rerun()

    def get_organism_category(self, organism: str) -> str:
        """Determine the category of the selected organism"""
        for category, organisms in self.config["organisms"].items():
            if organism in organisms:
                return category
        return "Custom"

    def render_sidebar(self) -> Dict:
        """Render sidebar with process configuration options"""
        with st.sidebar:
            st.header("Process Configuration")

            # Basic configuration
            process_type = st.selectbox("Select Process Type", self.config["process_types"])

            # Organism selection with categorization
            organism_category = st.selectbox("Organism Category", list(self.config["organisms"].keys()))
            organism_type = st.selectbox(
                "Select Organism Type",
                self.config["organisms"][organism_category]
            )

            # Scale selection
            scale = st.select_slider("Select Process Scale", options=self.config["scales"])

            # Save configuration to history
            config = {
                "process_type": process_type,
                "organism_type": organism_type,
                "scale": scale,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            if st.button("Save Configuration"):
                st.session_state.process_history.append(config)
                st.success("Configuration saved!")

            # Show configuration history
            if st.session_state.process_history:
                with st.expander("Previous Configurations"):
                    for i, conf in enumerate(st.session_state.process_history[-3:]):
                        st.markdown(f"**Configuration {i+1}**")
                        st.json(conf)

            return config

    def render_process_parameters(self, organism_type: str) -> ProcessParameters:
        """Render process parameters input section"""
        st.subheader("Process Parameters")

        # Get default parameters for organism
        default_params = self.config["default_parameters"].get(
            organism_type,
            {"temp": (30.0, 37.0), "ph": (6.8, 7.2), "do": 40}
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Basic Parameters")
            temp_range = st.slider(
                "Temperature Range (°C)",
                min_value=20.0,
                max_value=45.0,
                value=default_params["temp"],
                step=0.5
            )

            ph_range = st.slider(
                "pH Range",
                min_value=4.0,
                max_value=9.0,
                value=default_params["ph"],
                step=0.1
            )

            do_setpoint = st.slider(
                "Dissolved Oxygen Setpoint (%)",
                min_value=20,
                max_value=100,
                value=default_params["do"]
            )

        with col2:
            st.markdown("##### Advanced Parameters")
            agitation = st.number_input(
                "Agitation Speed (RPM)",
                min_value=50,
                max_value=1500,
                value=200,
                help="Impeller speed for mixing"
            )

            aeration = st.number_input(
                "Aeration Rate (vvm)",
                min_value=0.1,
                max_value=2.0,
                value=0.5,
                step=0.1,
                help="Volume of air per volume of medium per minute"
            )

            duration = st.number_input(
                "Process Duration (hours)",
                min_value=1,
                max_value=1000,
                value=168,
                help="Total process runtime"
            )

        return ProcessParameters(temp_range, ph_range, do_setpoint, agitation, aeration, duration)

    def render_media_design(self, organism_category: str):
        """Render media design section"""
        st.subheader("Media Design")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Carbon Sources")
            glucose_conc = st.number_input(
                "Glucose (g/L)",
                min_value=0.0,
                max_value=100.0,
                value=10.0
            )

            glutamine_conc = st.number_input(
                "Glutamine (g/L)",
