import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import subprocess
subprocess.run(["pip", "install", "scikit-learn"])
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Set page config
st.set_page_config(page_title="Bioprocess Designer Pro", layout="wide")

# Title and introduction
st.title("🧬 Bioprocess Designer Pro")
st.markdown("""
This advanced tool helps bioprocess engineers design and optimize bioprocessing experiments 
with comprehensive process controls and monitoring strategies.
""")

# Sidebar for process configuration
with st.sidebar:
    st.header("Process Configuration")
    
    # Process type selection
    process_type = st.selectbox(
        "Select Process Type",
        ["Batch Culture", "Fed-batch Culture", "Continuous Culture", "Perfusion Culture"]
    )
    
    # Organism type
    organism_type = st.selectbox(
        "Select Organism Type",
        ["CHO Cells", "E. coli", "Pichia pastoris", "S. cerevisiae", "HEK293", "Hybridoma"]
    )
    
    # Scale selection
    scale = st.select_slider(
        "Select Process Scale",
        options=["Laboratory (1-10L)", "Pilot (10-100L)", "Production (>100L)"]
    )

# Main content in tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Process Parameters", 
    "Media Design", 
    "Process Controls",
    "PAT Strategy",
    "Safety Controls"
])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Parameters")
        
        # Temperature settings
        temp_range = st.slider(
            "Temperature Range (°C)",
            min_value=20.0,
            max_value=45.0,
            value=(30.0, 37.0),
            step=0.5
        )
        
        # pH settings
        ph_range = st.slider(
            "pH Range",
            min_value=4.0,
            max_value=9.0,
            value=(6.8, 7.2),
            step=0.1
        )
        
        # Dissolved oxygen
        do_setpoint = st.slider(
            "Dissolved Oxygen Setpoint (%)",
            min_value=20,
            max_value=100,
            value=40
        )
    
    with col2:
        st.subheader("Advanced Parameters")
        
        # Agitation settings
        agitation = st.number_input(
            "Agitation Speed (RPM)",
            min_value=50,
            max_value=1500,
            value=200
        )
        
        # Aeration rate
        aeration = st.number_input(
            "Aeration Rate (vvm)",
            min_value=0.1,
            max_value=2.0,
            value=0.5,
            step=0.1
        )
        
        # Process duration
        duration = st.number_input(
            "Process Duration (hours)",
            min_value=1,
            max_value=1000,
            value=168
        )

with tab2:
    st.subheader("Media Components")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Carbon sources
        st.write("Carbon Sources (g/L)")
        glucose_conc = st.number_input("Glucose", 0.0, 100.0, 10.0)
        glutamine_conc = st.number_input("Glutamine", 0.0, 10.0, 2.0)
        
        # Base media selection
        base_media = st.selectbox(
            "Select Base Media",
            ["DMEM", "RPMI", "CD CHO", "LB", "TB", "YPD", "Minimal Media", "Custom"]
        )
    
    with col4:
        # Additional components
        st.write("Additional Components")
        components = {
            "Yeast Extract": st.checkbox("Yeast Extract", True),
            "Peptone": st.checkbox("Peptone", True),
            "Trace Elements": st.checkbox("Trace Elements", True),
            "Vitamins": st.checkbox("Vitamins", True),
            "Antifoam": st.checkbox("Antifoam", True)
        }

with tab3:
    st.subheader("Advanced Process Controls")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.write("PID Control Parameters")
        
        # Temperature PID
        st.write("Temperature Control")
        temp_kp = st.number_input("Temperature Kp", 0.0, 100.0, 2.0)
        temp_ki = st.number_input("Temperature Ki", 0.0, 100.0, 0.5)
        temp_kd = st.number_input("Temperature Kd", 0.0, 100.0, 0.1)
        
        # pH PID
        st.write("pH Control")
        ph_kp = st.number_input("pH Kp", 0.0, 100.0, 1.0)
        ph_ki = st.number_input("pH Ki", 0.0, 100.0, 0.2)
        ph_kd = st.number_input("pH Kd", 0.0, 100.0, 0.05)
    
    with col6:
        st.write("Feed Control Strategy")
        
        if process_type in ["Fed-batch Culture", "Perfusion Culture"]:
            feed_control = st.selectbox(
                "Feed Control Method",
                ["Time-based", "pH-stat", "DO-stat", "Glucose-stat", "Exponential", "Specific Growth Rate"]
            )
            
            if feed_control == "Exponential":
                mu_setpoint = st.number_input("Target Specific Growth Rate (h⁻¹)", 0.01, 1.0, 0.1)
                y_xs = st.number_input("Biomass Yield on Substrate (g/g)", 0.1, 1.0, 0.5)
            
            elif feed_control == "Specific Growth Rate":
                st.write("Growth Rate Control")
                mu_control = st.checkbox("Enable μ-stat Control", True)
                if mu_control:
                    mu_target = st.number_input("Target μ (h⁻¹)", 0.01, 1.0, 0.1)

with tab4:
    st.subheader("Process Analytical Technology (PAT)")
    
    col7, col8 = st.columns(2)
    
    with col7:
        st.write("Online Measurements")
        online_measurements = {
            "Biomass": st.checkbox("Biomass Probe", True),
            "Glucose": st.checkbox("Glucose Analyzer", True),
            "Oxygen Uptake": st.checkbox("Off-gas Analysis", True),
            "Capacitance": st.checkbox("Capacitance Probe", False),
            "Fluorescence": st.checkbox("Fluorescence Sensor", False)
        }
        
        st.write("Sampling Configuration")
        sampling_interval = st.number_input(
            "Sampling Interval (hours)",
            min_value=0.5,
            max_value=24.0,
            value=12.0
        )
    
    with col8:
        st.write("Data Analysis")
        data_analysis = {
            "Real-time OUR": st.checkbox("Calculate OUR/CER", True),
            "Mass Balance": st.checkbox("Component Mass Balance", True),
            "Metabolic Rates": st.checkbox("Metabolic Rates", True),
            "Yield Coefficients": st.checkbox("Yield Coefficients", True)
        }

with tab5:
    st.subheader("Safety Controls and Alarms")
    
    col9, col10 = st.columns(2)
    
    with col9:
        st.write("Critical Alarms")
        
        # Temperature alarms
        temp_low = st.number_input("Temperature Low Alarm (°C)", 0.0, 50.0, temp_range[0]-2)
        temp_high = st.number_input("Temperature High Alarm (°C)", 0.0, 50.0, temp_range[1]+2)
        
        # pH alarms
        ph_low = st.number_input("pH Low Alarm", 0.0, 14.0, ph_range[0]-0.5)
        ph_high = st.number_input("pH High Alarm", 0.0, 14.0, ph_range[1]+0.5)
        
        # DO alarm
        do_low = st.number_input("DO Low Alarm (%)", 0.0, 100.0, 20.0)
    
    with col10:
        st.write("Safety Interlocks")
        
        safety_features = {
            "Pressure Relief": st.checkbox("Pressure Relief Valve", True),
            "Emergency Stop": st.checkbox("Emergency Stop Button", True),
            "Power Backup": st.checkbox("UPS System", True),
            "Sterile Filter": st.checkbox("Sterile Filter on Gas Line", True),
            "Foam Control": st.checkbox("Automatic Foam Control", True)
        }

# Generate experimental design
if st.button("Generate Experimental Design"):
    st.subheader("Experimental Design Summary")
    
    # Create summary DataFrame
    summary_data = {
        "Parameter": ["Process Type", "Organism", "Scale", "Temperature Range", "pH Range",
                     "DO Setpoint", "Agitation Speed", "Aeration Rate", "Duration"],
        "Value": [
            process_type,
            organism_type,
            scale,
            f"{temp_range[0]}-{temp_range[1]}°C",
            f"{ph_range[0]}-{ph_range[1]}",
            f"{do_setpoint}%",
            f"{agitation} RPM",
            f"{aeration} vvm",
            f"{duration} hours"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
    
    # Generate process visualization
    st.subheader("Process Visualization")
    
    # Time points for visualization
    time_points = np.linspace(0, duration, 100)
    
    # Create mock growth curve
    def growth_curve(t):
        initial_biomass = 0.1
        growth_rate = 0.1
        carrying_capacity = 10
        return carrying_capacity / (1 + ((carrying_capacity - initial_biomass) / initial_biomass) * np.exp(-growth_rate * t))
    
    biomass = growth_curve(time_points)
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add biomass curve
    fig.add_trace(
        go.Scatter(x=time_points, y=biomass, name="Biomass", line=dict(color="blue"))
    )
    
    # Add temperature profile
    fig.add_trace(
        go.Scatter(
            x=time_points,
            y=[np.mean(temp_range)] * len(time_points),
            name="Temperature",
            line=dict(color="red", dash="dash"),
            yaxis="y2"
        )
    )
    
    fig.update_layout(
        title="Process Profile Prediction",
        xaxis_title="Time (hours)",
        yaxis_title="Biomass (g/L)",
        yaxis2=dict(
            title="Temperature (°C)",
            overlaying="y",
            side="right"
        ),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create CSV download options
    process_csv = summary_df.to_csv(index=False)
    media_df = pd.DataFrame({
        "Component": ["Glucose", "Glutamine"] + list(components.keys()),
        "Value": [glucose_conc, glutamine_conc] + list(components.values())
    })
    media_csv = media_df.to_csv(index=False)
    
    # Download buttons
    col11, col12 = st.columns(2)
    with col11:
        st.download_button(
            label="Download Process Summary",
            data=process_csv,
            file_name=f"bioprocess_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    with col12:
        st.download_button(
            label="Download Media Composition",
            data=media_csv,
            file_name=f"media_composition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
### Important Notes:
- All parameters should be validated according to your specific organism and process requirements
- Consider regulatory requirements and GMP guidelines for your scale of operation
- Implement appropriate safety measures and containment levels
- Monitor and document any deviations from the planned process
- Ensure proper calibration of all PAT instruments
- Maintain sterility throughout the process
- Follow standard operating procedures (SOPs)
""")
