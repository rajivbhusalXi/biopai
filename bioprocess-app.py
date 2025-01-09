import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass
class ProcessParameters:
    temp_range: Tuple[float, float]
    ph_range: Tuple[float, float]
    do_setpoint: float
    agitation: int
    aeration: float
    duration: int

class BioprocessApp:
    def __init__(self):
        st.set_page_config(page_title="Bioprocess Designer Pro", layout="wide")
        self.initialize_config()
        self.initialize_session_state()
        
    def initialize_config(self):
        self.config = {
            "process_types": ["Batch Culture", "Fed-batch Culture", "Continuous Culture", "Perfusion Culture"],
            "organisms": ["CHO Cells", "E. coli", "Pichia pastoris", "S. cerevisiae", "HEK293", "Hybridoma"],
            "scales": ["Laboratory (1-10L)", "Pilot (10-100L)", "Production (>100L)"],
            "base_media": ["DMEM", "RPMI", "CD CHO", "LB", "TB", "YPD", "Minimal Media", "Custom"]
        }
        
    def initialize_session_state(self):
        if 'process_history' not in st.session_state:
            st.session_state.process_history = []
        if 'current_parameters' not in st.session_state:
            st.session_state.current_parameters = None

    def render_header(self):
        st.title("🧬 Bioprocess Designer Pro")
        st.markdown("""
        This advanced tool helps bioprocess engineers design and optimize bioprocessing experiments 
        with comprehensive process controls and monitoring strategies.
        """)

    def render_sidebar(self) -> Dict:
        with st.sidebar:
            st.header("Process Configuration")
            
            config = {
                "process_type": st.selectbox("Select Process Type", self.config["process_types"]),
                "organism_type": st.selectbox("Select Organism Type", self.config["organisms"]),
                "scale": st.select_slider("Select Process Scale", options=self.config["scales"])
            }
            
            return config

    def render_process_parameters(self) -> ProcessParameters:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Basic Parameters")
            temp_range = st.slider(
                "Temperature Range (°C)",
                min_value=20.0,
                max_value=45.0,
                value=(30.0, 37.0),
                step=0.5
            )
            ph_range = st.slider(
                "pH Range",
                min_value=4.0,
                max_value=9.0,
                value=(6.8, 7.2),
                step=0.1
            )
            do_setpoint = st.slider(
                "Dissolved Oxygen Setpoint (%)",
                min_value=20,
                max_value=100,
                value=40
            )
        
        with col2:
            st.subheader("Advanced Parameters")
            agitation = st.number_input(
                "Agitation Speed (RPM)",
                min_value=50,
                max_value=1500,
                value=200
            )
            aeration = st.number_input(
                "Aeration Rate (vvm)",
                min_value=0.1,
                max_value=2.0,
                value=0.5,
                step=0.1
            )
            duration = st.number_input(
                "Process Duration (hours)",
                min_value=1,
                max_value=1000,
                value=168
            )
        
        return ProcessParameters(temp_range, ph_range, do_setpoint, agitation, aeration, duration)

    def render_media_design(self):
        st.subheader("Media Components")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Carbon Sources (g/L)")
            glucose_conc = st.number_input("Glucose", 0.0, 100.0, 10.0)
            glutamine_conc = st.number_input("Glutamine", 0.0, 10.0, 2.0)
            
            base_media = st.selectbox(
                "Select Base Media",
                self.config["base_media"]
            )
        
        with col2:
            st.write("Additional Components")
            components = {
                "Yeast Extract": st.checkbox("Yeast Extract", True),
                "Peptone": st.checkbox("Peptone", True),
                "Trace Elements": st.checkbox("Trace Elements", True),
                "Vitamins": st.checkbox("Vitamins", True),
                "Antifoam": st.checkbox("Antifoam", True)
            }
            
        return {
            "glucose": glucose_conc,
            "glutamine": glutamine_conc,
            "base_media": base_media,
            "components": components
        }

    def render_process_controls(self, process_type: str):
        st.subheader("Advanced Process Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("PID Control Parameters")
            
            st.write("Temperature Control")
            temp_pid = {
                "kp": st.number_input("Temperature Kp", 0.0, 100.0, 2.0),
                "ki": st.number_input("Temperature Ki", 0.0, 100.0, 0.5),
                "kd": st.number_input("Temperature Kd", 0.0, 100.0, 0.1)
            }
            
            st.write("pH Control")
            ph_pid = {
                "kp": st.number_input("pH Kp", 0.0, 100.0, 1.0),
                "ki": st.number_input("pH Ki", 0.0, 100.0, 0.2),
                "kd": st.number_input("pH Kd", 0.0, 100.0, 0.05)
            }
        
        with col2:
            if process_type in ["Fed-batch Culture", "Perfusion Culture"]:
                st.write("Feed Control Strategy")
                feed_control = st.selectbox(
                    "Feed Control Method",
                    ["Time-based", "pH-stat", "DO-stat", "Glucose-stat", "Exponential", "Specific Growth Rate"]
                )
                
                if feed_control == "Exponential":
                    mu_setpoint = st.number_input("Target Specific Growth Rate (h⁻¹)", 0.01, 1.0, 0.1)
                    y_xs = st.number_input("Biomass Yield on Substrate (g/g)", 0.1, 1.0, 0.5)
                
                elif feed_control == "Specific Growth Rate":
                    mu_control = st.checkbox("Enable μ-stat Control", True)
                    if mu_control:
                        mu_target = st.number_input("Target μ (h⁻¹)", 0.01, 1.0, 0.1)

    def render_pat_strategy(self):
        st.subheader("Process Analytical Technology (PAT)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Online Measurements")
            online_measurements = {
                "Biomass": st.checkbox("Biomass Probe", True),
                "Glucose": st.checkbox("Glucose Analyzer", True),
                "Oxygen Uptake": st.checkbox("Off-gas Analysis", True),
                "Capacitance": st.checkbox("Capacitance Probe", False),
                "Fluorescence": st.checkbox("Fluorescence Sensor", False)
            }
            
            sampling_interval = st.number_input(
                "Sampling Interval (hours)",
                min_value=0.5,
                max_value=24.0,
                value=12.0
            )
        
        with col2:
            st.write("Data Analysis")
            data_analysis = {
                "Real-time OUR": st.checkbox("Calculate OUR/CER", True),
                "Mass Balance": st.checkbox("Component Mass Balance", True),
                "Metabolic Rates": st.checkbox("Metabolic Rates", True),
                "Yield Coefficients": st.checkbox("Yield Coefficients", True)
            }
        
        return {"measurements": online_measurements, "sampling": sampling_interval, "analysis": data_analysis}

    def render_safety_controls(self, params: ProcessParameters):
        st.subheader("Safety Controls and Alarms")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Critical Alarms")
            temp_low = st.number_input("Temperature Low Alarm (°C)", 0.0, 50.0, params.temp_range[0]-2)
            temp_high = st.number_input("Temperature High Alarm (°C)", 0.0, 50.0, params.temp_range[1]+2)
            ph_low = st.number_input("pH Low Alarm", 0.0, 14.0, params.ph_range[0]-0.5)
            ph_high = st.number_input("pH High Alarm", 0.0, 14.0, params.ph_range[1]+0.5)
            do_low = st.number_input("DO Low Alarm (%)", 0.0, 100.0, 20.0)
        
        with col2:
            st.write("Safety Interlocks")
            safety_features = {
                "Pressure Relief": st.checkbox("Pressure Relief Valve", True),
                "Emergency Stop": st.checkbox("Emergency Stop Button", True),
                "Power Backup": st.checkbox("UPS System", True),
                "Sterile Filter": st.checkbox("Sterile Filter on Gas Line", True),
                "Foam Control": st.checkbox("Automatic Foam Control", True)
            }
        
        # Add warnings for critical settings
        if abs(temp_low - params.temp_range[0]) < 1:
            st.warning("⚠️ Temperature low alarm is very close to setpoint!")
        if abs(temp_high - params.temp_range[1]) < 1:
            st.warning("⚠️ Temperature high alarm is very close to setpoint!")

        return {
            "alarms": {
                "temp_low": temp_low,
                "temp_high": temp_high,
                "ph_low": ph_low,
                "ph_high": ph_high,
                "do_low": do_low
            },
            "safety_features": safety_features
        }

    def create_process_visualization(self, params: ProcessParameters):
        time_points = np.linspace(0, params.duration, 100)
        
        # Calculate growth curves
        initial_biomass = 0.1
        growth_rate = 0.1
        carrying_capacity = 10
        
        biomass = carrying_capacity / (1 + ((carrying_capacity - initial_biomass) / initial_biomass) * 
                                     np.exp(-growth_rate * time_points))
        substrate = 10 * np.exp(-0.05 * time_points)  # Substrate consumption
        product = carrying_capacity * (1 - np.exp(-0.03 * time_points))  # Product formation
        
        fig = go.Figure()
        
        # Add traces
        fig.add_trace(go.Scatter(x=time_points, y=biomass, name="Biomass", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=time_points, y=substrate, name="Substrate", line=dict(color="red")))
        fig.add_trace(go.Scatter(x=time_points, y=product, name="Product", line=dict(color="green")))
        
        fig.update_layout(
            title="Process Profile Prediction",
            xaxis_title="Time (hours)",
            yaxis_title="Concentration (g/L)",
            hovermode="x unified",
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig

    def generate_experimental_design(self, config: Dict, params: ProcessParameters, 
                                   media_data: Dict, pat_data: Dict, safety_data: Dict):
        st.subheader("Experimental Design Summary")
        
        # Create summary DataFrame
        summary_data = {
            "Parameter": [
                "Process Type", "Organism", "Scale", 
                "Temperature Range", "pH Range", "DO Setpoint",
                "Agitation Speed", "Aeration Rate", "Duration",
                "Base Media", "Glucose Concentration", "Sampling Interval"
            ],
            "Value": [
                config["process_type"],
                config["organism_type"],
                config["scale"],
                f"{params.temp_range[0]}-{params.temp_range[1]}°C",
                f"{params.ph_range[0]}-{params.ph_range[1]}",
                f"{params.do_setpoint}%",
                f"{params.agitation} RPM",
                f"{params.aeration} vvm",
                f"{params.duration} hours",
                media_data["base_media"],
                f"{media_data['glucose']} g/L",
                f"{pat_data['sampling']} hours"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Process visualization
        st.subheader("Process Visualization")
        fig = self.create_process_visualization(params)
        st.plotly_chart(fig, use_container_width=True)
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Process Summary",
                data=summary_df.to_csv(index=False),
                file_name=f"bioprocess_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            media_df = pd.DataFrame({
                "Component": ["Glucose", "Glutamine"] + list(media_data["components"].keys()),
                "Value": [media_data["glucose"], media_data["glutamine"]] + 
                        [str(v) for v in media_data["components"].values()]
            })
            st.download_button(
                label="Download Media Composition",
                data=media_df.to_csv(index=False),
                file_name=f"media_composition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    def run(self):
        self.render_header()
        config = self.render_sidebar()
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Process Parameters",
            "Media Design",
            "Process Controls",
            "PAT Strategy",
            "Safety Controls"
        ])
        
        with tab1:
            params = self.render_process_parameters()
        
        with tab2:
