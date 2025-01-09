import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import json

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
        self.load_config()
        self.initialize_session_state()
        
    def load_config(self):
        # Load configuration from JSON (could be external file)
        self.config = {
            "process_types": ["Batch Culture", "Fed-batch Culture", "Continuous Culture", "Perfusion Culture"],
            "organisms": ["CHO Cells", "E. coli", "Pichia pastoris", "S. cerevisiae", "HEK293", "Hybridoma"],
            "scales": ["Laboratory (1-10L)", "Pilot (10-100L)", "Production (>100L)"],
            "base_media": ["DMEM", "RPMI", "CD CHO", "LB", "TB", "YPD", "Minimal Media", "Custom"]
        }
        
    def initialize_session_state(self):
        if 'process_history' not in st.session_state:
            st.session_state.process_history = []

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
            
            if st.button("Save Configuration"):
                st.session_state.process_history.append(config)
                st.success("Configuration saved!")
            
            if st.session_state.process_history:
                st.write("Previous Configurations:")
                for i, conf in enumerate(st.session_state.process_history[-3:]):
                    st.json(conf)
                    
            return config

    def render_process_parameters(self) -> ProcessParameters:
        st.subheader("Basic Parameters")
        col1, col2 = st.columns(2)
        
        with col1:
            temp_range = st.slider("Temperature Range (°C)", 20.0, 45.0, (30.0, 37.0), 0.5)
            ph_range = st.slider("pH Range", 4.0, 9.0, (6.8, 7.2), 0.1)
            do_setpoint = st.slider("Dissolved Oxygen Setpoint (%)", 20, 100, 40)
        
        with col2:
            agitation = st.number_input("Agitation Speed (RPM)", 50, 1500, 200)
            aeration = st.number_input("Aeration Rate (vvm)", 0.1, 2.0, 0.5, 0.1)
            duration = st.number_input("Process Duration (hours)", 1, 1000, 168)
        
        return ProcessParameters(temp_range, ph_range, do_setpoint, agitation, aeration, duration)

    def calculate_growth_profile(self, time_points: np.ndarray, params: ProcessParameters) -> Dict[str, np.ndarray]:
        """Calculate theoretical growth and metabolite profiles"""
        initial_biomass = 0.1
        growth_rate = 0.1
        carrying_capacity = 10
        
        biomass = carrying_capacity / (1 + ((carrying_capacity - initial_biomass) / initial_biomass) * 
                                     np.exp(-growth_rate * time_points))
        
        # Add substrate and product profiles
        substrate = 10 * np.exp(-0.05 * time_points)
        product = carrying_capacity * (1 - np.exp(-0.03 * time_points))
        
        return {
            "biomass": biomass,
            "substrate": substrate,
            "product": product
        }

    def create_process_visualization(self, params: ProcessParameters):
        time_points = np.linspace(0, params.duration, 100)
        profiles = self.calculate_growth_profile(time_points, params)
        
        fig = go.Figure()
        
        # Add traces
        fig.add_trace(go.Scatter(x=time_points, y=profiles["biomass"], 
                               name="Biomass", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=time_points, y=profiles["substrate"], 
                               name="Substrate", line=dict(color="red")))
        fig.add_trace(go.Scatter(x=time_points, y=profiles["product"], 
                               name="Product", line=dict(color="green")))
        
        fig.update_layout(
            title="Process Profile Prediction",
            xaxis_title="Time (hours)",
            yaxis_title="Concentration (g/L)",
            hovermode="x unified",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig

    def render_safety_controls(self, params: ProcessParameters):
        st.subheader("Safety Controls and Alarms")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Critical Alarms")
            temp_low = st.number_input("Temperature Low Alarm (°C)", 
                                     0.0, 50.0, params.temp_range[0]-2)
            temp_high = st.number_input("Temperature High Alarm (°C)", 
                                      0.0, 50.0, params.temp_range[1]+2)
            
            # Add warning if alarms are too close to setpoints
            if abs(temp_low - params.temp_range[0]) < 1:
                st.warning("Temperature low alarm is very close to setpoint!")
            if abs(temp_high - params.temp_range[1]) < 1:
                st.warning("Temperature high alarm is very close to setpoint!")

    def export_data(self, params: ProcessParameters, config: Dict):
        # Create summary DataFrame
        summary_data = {
            "Parameter": ["Process Type", "Organism", "Scale", "Temperature Range", "pH Range",
                         "DO Setpoint", "Agitation Speed", "Aeration Rate", "Duration"],
            "Value": [
                config["process_type"],
                config["organism_type"],
                config["scale"],
                f"{params.temp_range[0]}-{params.temp_range[1]}°C",
                f"{params.ph_range[0]}-{params.ph_range[1]}",
                f"{params.do_setpoint}%",
                f"{params.agitation} RPM",
                f"{params.aeration} vvm",
                f"{params.duration} hours"
            ]
        }
        
        return pd.DataFrame(summary_data)

    def run(self):
        self.render_header()
        config = self.render_sidebar()
        
        # Create tabs
        tabs = st.tabs(["Process Parameters", "Media Design", "Process Controls", 
                       "PAT Strategy", "Safety Controls"])
        
        with tabs[0]:
            params = self.render_process_parameters()
            
            if st.button("Generate Process Profile"):
                fig = self.create_process_visualization(params)
                st.plotly_chart(fig, use_container_width=True)
                
                summary_df = self.export_data(params, config)
                st.dataframe(summary_df, use_container_width=True)
                
                # Export options
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download Process Summary",
                        summary_df.to_csv(index=False),
                        f"bioprocess_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        with tabs[4]:
            self.render_safety_controls(params)

if __name__ == "__main__":
    app = BioprocessApp()
    app.run()
