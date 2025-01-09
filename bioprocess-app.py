import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from scipy.stats import norm

# Set page config
st.set_page_config(page_title="Bioprocess Designer Pro", layout="wide")

# Title and introduction
st.title(" Bioprocess Designer Pro")
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Process Parameters", 
    "Media Design", 
    "Process Controls",
    "PAT Strategy",
    "Safety Controls",
    "Data Analysis",
    "Machine Learning"
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

        # Alarm notification settings
        alarm_notification = st.selectbox(
            "Alarm Notification Method",
            ["Email", "SMS", "Audible Alert", "Visual Alert"]
        )

    with col10:
        st.write("Safety Interlocks")

        safety_features = {
            "Pressure Relief": st.checkbox("Pressure Relief Valve", True),
            "Emergency Stop": st.checkbox("Emergency Stop Button", True),
            "Power Backup": st.checkbox("UPS System", True),
            "Sterile Filter": st.checkbox("Sterile Filter", True),
            "Biocontainment": st.checkbox("Biocontainment System", True)
        }

        # Safety protocol settings
        safety_protocol = st.selectbox(
            "Safety Protocol",
            ["Biosafety Level 1", "Biosafety Level 2", "Biosafety Level 3", "Custom"]
        )

with tab6:
    st.subheader("Data Analysis")
    
    col11, col12 = st.columns(2)
    
    with col11:
        st.write("Process Data Visualization")
        
        # Data visualization options
        data_vis = st.selectbox(
            "Select Data Visualization",
            ["Time-series Plot", "Scatter Plot", "Bar Chart", "Heatmap"]
        )
        
        # Data export options
        data_export = st.selectbox(
            "Select Data Export Format",
            ["CSV", "Excel", "JSON", "PDF"]
        )
        
        # Plotly figure for data visualization
        fig = go.Figure()
        
        if data_vis == "Time-series Plot":
            fig.add_trace(go.Scatter(x=[1, 2, 3], y=[10, 20, 30]))
        
        elif data_vis == "Scatter Plot":
            fig.add_trace(go.Scatter(x=[1, 2, 3], y=[10, 20, 30], mode='markers'))
        
        elif data_vis == "Bar Chart":
            fig.add_trace(go.Bar(x=[1, 2, 3], y=[10, 20, 30]))
        
        elif data_vis == "Heatmap":
            fig.add_trace(go.Heatmap(z=[[10, 20], [30, 40]]))
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col12:
        st.write("Statistical Analysis")
        
        # Statistical analysis options
        stats_analysis = st.selectbox(
            "Select Statistical Analysis",
            ["Descriptive Statistics", "Inferential Statistics", "Regression Analysis", "Time-series Analysis"],
            key="stats_analysis"
        )
        
        # Confidence interval settings
        ci_level = st.number_input("Confidence Interval Level (%)", 50, 100, 95)
        
        # Statistical analysis output
        if stats_analysis == "Descriptive Statistics":
            st.write("Mean: 20.5")
            st.write("Median: 20.0")
            st.write("Standard Deviation: 5.2")
        
        elif stats_analysis == "Inferential Statistics":
            st.write("p-value: 0.01")
            st.write("t-statistic: 2.5")
        
        elif stats_analysis == "Regression Analysis":
            st.write("R-squared: 0.8")
            st.write("Coefficient of Determination: 0.7")
        
        elif stats_analysis == "Time-series Analysis":
            st.write("ARIMA Order: (1,1,1)")
            st.write("Seasonal Decomposition: Additive")

with tab6:
    st.subheader("Data Analysis")
    
    col11, col12 = st.columns(2)
    
    with col11:
        st.write("Process Data Visualization")
        data_vis = st.selectbox(
            "Select Data Visualization",
            ["Time-series Plot", "Scatter Plot", "Bar Chart", "Heatmap"],
            key="data_vis"
        )
               # Data export options
        data_export = st.selectbox(
            "Select Data Export Format",
            ["CSV", "Excel", "JSON", "PDF"]
        )
    
    with col12:
        st.write("Statistical Analysis")
        stats_analysis = st.selectbox(
            "Select Statistical Analysis",
            ["Descriptive Statistics", "Inferential Statistics", "Regression Analysis", "Time-series Analysis"],
            key="stats_analysis"
        )
        
        # Confidence interval settings
        ci_level = st.number_input("Confidence Interval Level (%)", 50, 100, 95)

with tab7:
    st.subheader("Machine Learning")
    
    col13, col14 = st.columns(2)
    
    with col13:
        st.write("Model Selection")
        
        # Machine learning model options
       ml_model = st.selectbox(
    "Select Machine Learning Model",
    ["Linear Regression", "Random Forest", "Support Vector Machine", "Neural Network"],
    key="ml_model"
)
        
        # Feature selection options
        feature_selection = st.selectbox(
            "Select Feature Selection Method",
            ["All Features", "Recursive Feature Elimination", "Lasso Regression", "Random Forest Feature Importance"]
        )
    
    with col14:
        st.write("Model Evaluation")
        
        # Model evaluation metrics
        evaluation_metrics = st.selectbox(
            "Select Model Evaluation Metric",
            ["Mean Squared Error", "Mean Absolute Error", "R-squared", "Mean Absolute Percentage Error"]
        )
        
        # Hyperparameter tuning options
        hyperparam_tuning = st.selectbox(
            "Select Hyperparameter Tuning Method",
            ["Grid Search", "Random Search", "Bayesian Optimization"]
        )

# Download configuration as JSON file
if st.button("Download Configuration"):
    config_data = {
        "process_type": process_type,
        "organism_type": organism_type,
        "scale": scale,
        "temp_range": temp_range,
        "ph_range": ph_range,
        "do_setpoint": do_setpoint,
        "agitation": agitation,
        "aeration": aeration,
        "duration": duration,
        "feed_control": feed_control,
        "online_measurements": online_measurements,
        "sampling_interval": sampling_interval,
        "data_analysis": data_analysis,
        "safety_features": safety_features
    }
    
    config_json = json.dumps(config_data, indent=4)
    
    st.download_button(
        label="Download Configuration",
        data=config_json,
        file_name="bioprocess_config.json",
        mime="application/json"
    )
