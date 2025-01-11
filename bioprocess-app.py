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
from Bio import SeqIO
import json
import graphviz

st.set_page_config(page_title="Bioprocess Designer Pro", layout="wide")

st.markdown("""
<style>
.draggable {
    position: absolute;
    cursor: move;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', (event) => {
    const element = document.querySelector('.element-container');
    let isMouseDown = false;
    let offset = [0, 0];
    
    element.addEventListener('mousedown', (event) => {
        isMouseDown = true;
        offset = [
            element.offsetLeft - event.clientX,
            element.offsetTop - event.clientY
        ];
    }, true);
    
    document.addEventListener('mouseup', () => {
        isMouseDown = false;
    }, true);
    
    document.addEventListener('mousemove', (event) => {
        event.preventDefault();
        if (isMouseDown) {
            element.style.left = (event.clientX + offset[0]) + 'px';
            element.style.top = (event.clientY + offset[1]) + 'px';
        }
    }, true);
});
</script>
""", unsafe_allow_html=True)

def ai_analyze_bioreactor(bioreactor, components):
    analysis = f"Analyzing {bioreactor} with components: {', '.join([k for k, v in components.items() if v])}."
    recommendations = []

    if "Stirrer" not in components or not components["Stirrer"]:
        recommendations.append("Consider adding a Stirrer for improved mixing.")
    if "Temperature Control" not in components or not components["Temperature Control"]:
        recommendations.append("Temperature Control is recommended for maintaining optimal conditions.")
    # Add more analysis based on bioreactor type and components

    return analysis, recommendations

def generate_bioreactor_diagram(selected_bioreactor, components):
    st.subheader("Bioreactor Flow Diagram")
    st.write(f"Generating flow diagram for {selected_bioreactor} with the following components:")

    dot = graphviz.Digraph(format='png')
    dot.attr(size='24,24')  # Increase the size of the diagram

    # Define main nodes
    main_components = components["Main Components"]
    sensing_components = components["Sensing and Control Components"]
    aeration_components = components["Aeration and Mixing Components"]
    feeding_components = components["Feeding and Harvesting Components"]
    support_components = components["Support Components"]
    optional_components = components["Optional Components"]

    # Add nodes and edges based on component selection
    for category, items in components.items():
        with dot.subgraph(name=f'cluster_{category}') as c:
            c.attr(label=category)
            for component, selected in items.items():
                if selected:
                    c.node(component)
                    st.write(f"- {component}")

    # Example of dynamic connections for a bioreactor
    if main_components["Vessel"]:
        dot.node("Vessel")
        if main_components["Lid/Headplate"]:
            dot.edge("Lid/Headplate", "Vessel")
        if main_components["Impeller/Agitator"]:
            dot.edge("Impeller/Agitator", "Vessel")
        if sensing_components["pH Sensor"]:
            dot.edge("pH Sensor", "Vessel")
        if sensing_components["Temperature Sensor"]:
            dot.edge("Temperature Sensor", "Vessel")
        if sensing_components["Dissolved Oxygen (DO) Sensor"]:
            dot.edge("Dissolved Oxygen (DO) Sensor", "Vessel")
        if sensing_components["Control Unit"]:
            dot.edge("Control Unit", "Vessel")
        if aeration_components["Sparger"]:
            dot.edge("Sparger", "Vessel")
        if aeration_components["Aeration System"]:
            dot.edge("Aeration System", "Sparger")
        if feeding_components["Feed Pump"]:
            dot.edge("Feed Pump", "Vessel")
        if feeding_components["Harvest Pump"]:
            dot.edge("Vessel", "Harvest Pump")
        if support_components["Base Plate"]:
            dot.edge("Vessel", "Base Plate")

    st.graphviz_chart(dot)

# Title and introduction
st.title("Bioprocess Designer Pro")
st.markdown("""
This advanced tool helps bioprocess engineers design and optimize bioprocessing experiments 
with comprehensive process controls and monitoring strategies.
""")

# Sidebar for process configuration
with st.sidebar:
    st.header("Process Configuration")
    
    # Process selection
    process_stage = st.selectbox(
        "Select Process Stage",
        ["Upstream", "Downstream"]
    )
    
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
    
    # Approval checkbox
    approve_settings = st.checkbox("Approve Settings")

    if approve_settings:
        st.info("You have approved the settings.")
        
        if st.button("Confirm Settings"):
            st.success("Settings confirmed!")

# Main content in tabs
tabs = st.tabs(["Bioreactor Selector", "Media Creator", "Bioprocess Simulator", "Integration"])

with tabs[0]:
    st.subheader("Bioreactor Selector")
    bioreactors = {
        "Stirred Tank Bioreactors": [
            "Glass bioreactors: Suitable for small-scale applications, often used in research and development.",
            "Stainless steel bioreactors: Robust and corrosion-resistant, commonly used in industrial-scale applications.",
            "Single-use bioreactors: Disposable bioreactors made from plastic or other materials, often used in biopharmaceutical applications."
        ],
        "Packed Bed Bioreactors": [
            "Fixed bed bioreactors: Used for solid-phase catalysis and enzymatic reactions.",
            "Fluidized bed bioreactors: Used for applications requiring high mass transfer rates."
        ],
        "Membrane Bioreactors": [
            "Microfiltration/Ultrafiltration (MF/UF) bioreactors: Used for cell culture, protein separation, and wastewater treatment.",
            "Dialysis bioreactors: Used for cell culture, protein separation, and medical applications."
        ],
        "Photo-Bioreactors": [
            "Flat panel photobioreactors: Used for algae cultivation and photosynthetic bioprocesses.",
            "Tubular photobioreactors: Used for large-scale algae cultivation and photosynthetic bioprocesses."
        ],
        "Wave-Induced Motion Bioreactors": [
            "Wave bioreactors: Used for cell culture, tissue engineering, and bioprocess development."
        ],
        "Other Bioreactors": [
            "Airlift bioreactors: Used for cell culture, bioremediation, and wastewater treatment.",
            "Perfusion bioreactors: Used for cell culture, tissue engineering, and bioprocess development.",
            "Rotating wall vessel bioreactors: Used for cell culture, tissue engineering, and bioprocess development."
        ]
    }

    selected_bioreactor_type = st.selectbox("Select Bioreactor Type", list(bioreactors.keys()))
    selected_bioreactor = st.selectbox("Select Bioreactor", bioreactors[selected_bioreactor_type])

    components = {
        "Main Components": {
            "Vessel": st.checkbox("Vessel: The main container of the bioreactor, made from materials like glass, stainless steel, or plastic.", True),
            "Lid/Headplate": st.checkbox("Lid/Headplate: The top part of the bioreactor, providing access for sampling, feeding, and monitoring.", True),
            "Impeller/Agitator": st.checkbox("Impeller/Agitator: Mixes the culture medium, ensuring uniform distribution of nutrients and temperature.", True)
        },
        "Sensing and Control Components": {
            "pH Sensor": st.checkbox("pH Sensor: Monitors the acidity/basicity of the culture medium.", True),
            "Temperature Sensor": st.checkbox("Temperature Sensor: Monitors the temperature of the culture medium.", True),
            "Dissolved Oxygen (DO) Sensor": st.checkbox("Dissolved Oxygen (DO) Sensor: Monitors the oxygen levels in the culture medium.", True),
            "Conductivity Sensor": st.checkbox("Conductivity Sensor: Monitors the conductivity of the culture medium.", True),
            "Control Unit": st.checkbox("Control Unit: Regulates parameters like pH, temperature, and DO to maintain optimal conditions.", True)
        },
        "Aeration and Mixing Components": {
            "Sparger": st.checkbox("Sparger: Introduces air or gas into the culture medium.", True),
            "Aeration System": st.checkbox("Aeration System: Provides a consistent supply of air or gas to the bioreactor.", True),
            "Baffles": st.checkbox("Baffles: Enhances mixing and reduces vortex formation.", True),
            "Impeller Blades": st.checkbox("Impeller Blades: Mixes the culture medium, ensuring uniform distribution of nutrients and temperature.", True),
            "Impeller Stirrers": st.checkbox("Impeller stirrer: Uses an impeller (a rotating blade or paddle) to mix the culture medium.", False),
            "Anchor Stirrers": st.checkbox("Anchor stirrer: Uses a large, anchor-shaped blade to mix the culture medium.", False),
            "Helical Stirrers": st.checkbox("Helical stirrer: Uses a helical-shaped blade to mix the culture medium.", False),
            "Turbine Stirrers": st.checkbox("Turbine stirrer: Uses a turbine-shaped blade to mix the culture medium.", False)
        },
        "Feeding and Harvesting Components": {
            "Feed Pump": st.checkbox("Feed Pump: Delivers nutrients or other substances to the bioreactor.", True),
            "Harvest Pump": st.checkbox("Harvest Pump: Removes the biomass or product from the bioreactor.", True),
            "Sampling Port": st.checkbox("Sampling Port: Allows for aseptic sampling of the culture medium.", True),
            "Exhaust System": st.checkbox("Exhaust System: Removes waste gases and vapors from the bioreactor.", True)
        },
        "Support Components": {
            "Base Plate": st.checkbox("Base Plate: Provides a stable foundation for the bioreactor.", True),
            "Support Legs": st.checkbox("Support Legs: Elevates the bioreactor, ensuring easy access and maintenance.", True),
            "Cable Management": st.checkbox("Cable Management: Organizes cables and tubing, reducing clutter and improving safety.", True)
        },
        "Optional Components": {
            "Biomass Sensor": st.checkbox("Biomass Sensor: Monitors the biomass concentration in the culture medium.", False),
            "Nutrient Sensors": st.checkbox("Nutrient Sensors: Monitors the levels of specific nutrients in the culture medium.", False),
            "Gas Analyzer": st.checkbox("Gas Analyzer: Analyzes the composition of gases in the bioreactor.", False),
            "Automated Sampling System": st.checkbox("Automated Sampling System: Enables automated sampling and analysis of the culture medium.", False)
        }
    }

    if "selected_bioreactor" in st.session_state and "components" in st.session_state:
        analysis, recommendations = ai_analyze_bioreactor(st.session_state["selected_bioreactor"], st.session_state["components"])
        st.subheader("AI Analysis")
        st.write(analysis)
        st.write("Recommendations:")
        for rec in recommendations:
            st.write(f"- {rec}")

    if st.button("Confirm Bioreactor"):
        st.success(f"Bioreactor {selected_bioreactor} confirmed with components: {', '.join([k for k, v in components.items() if v])}")
        st.session_state["selected_bioreactor"] = selected_bioreactor
        st.session_state["components"] = components

    if st.button("Generate Bioreactor"):
        if "selected_bioreactor" in st.session_state and "components" in st.session_state:
            generate_bioreactor_diagram(st.session_state["selected_bioreactor"], st.session_state["components"])
        else:
            st.error("Please confirm the bioreactor settings first.")

with tabs[1]:
    st.subheader("Media Creator")
    st.write("Configure your media components and adjust for volume")

    with st.form("media_form"):
        volume = st.number_input("Total Volume (L)", min_value=0.1, step=0.1)

        # Basal Media
        st.write("Basal Media")
        basal_media = st.selectbox("Select Basal Media", [
            "DMEM", "RPMI 1640", "MEM", "Ham's F-12", "M199", "IMDM", "Alpha-MEM", "Beta-MEM"
        ])

        # Serum-Free Media
        st.write("Serum-Free Media")
        serum_free_media = st.selectbox("Select Serum-Free Media", [
            "PFHM-II", "CDM-HD", "X-VIVO", "AIM-V", "SFM4Mega", "Sf-900 II SFM", "ExCell"
        ])

        # Specialty Media
        st.write("Specialty Media")
        specialty_media = st.selectbox("Select Specialty Media", [
            "Neurobasal Medium", "STEMCELL Technologies' Media", "MesenCult", "Osteoblast Growth Medium",
            "Chondrocyte Growth Medium", "Adipocyte Growth Medium", "Hepatocyte Growth Medium"
        ])

        # Biomass Production Media
        st.write("Biomass Production Media")
        biomass_production_media = st.selectbox("Select Biomass Production Media", [
            "LB", "TB", "YPD", "PDA", "MRS", "TSA", "BHI"
        ])

        # Biotherapeutics Production Media
        st.write("Biotherapeutics Production Media")
        biotherapeutics_production_media = st.selectbox("Select Biotherapeutics Production Media", [
            "CHO Cell Culture Medium", "HEK Cell Culture Medium", "Insect Cell Culture Medium",
            "Hybridoma Cell Culture Medium", "PER.C6 Cell Culture Medium", "Vero Cell Culture Medium",
            "MDCK Cell Culture Medium"
        ])

        # Additional Supplements
        st.write("Additional Supplements")
        fbs = st.number_input("Fetal Bovine Serum (FBS) (mL/L)", 0.0, 100.0, 10.0)
        penicillin_streptomycin = st.number_input("Penicillin-Streptomycin (mL/L)", 0.0, 100.0, 10.0)
        l_glutamine = st.number_input("L-Glutamine (mM)", 0.0, 100.0, 2.0)
        neaa = st.number_input("Non-Essential Amino Acids (NEAA) (mM)", 0.0, 100.0, 1.0)
        sodium_pyruvate = st.number_input("Sodium Pyruvate (mM)", 0.0, 100.0, 1.0)
        hepes_buffer = st.number_input("Hepes Buffer (mM)", 0.0, 100.0, 25.0)
        growth_factors = st.text_area("Growth Factors", "EGF, FGF, IGF")

        # Submit button
        submitted = st.form_submit_button("Generate Media Recipe")

        if submitted:
            st.success(f"Media recipe generated for {volume} L")
            st.write(f"Basal Media: {basal_media}")
            st.write(f"Serum-Free Media: {serum_free_media}")
            st.write(f"Specialty Media: {specialty_media}")
            st.write(f"Biomass Production Media: {biomass_production_media}")
            st.write(f"Biotherapeutics Production Media: {biotherapeutics_production_media}")
            st.write(f"Fetal Bovine Serum (FBS): {fbs * volume} mL")
            st.write(f"Penicillin-Streptomycin: {penicillin_streptomycin * volume} mL")
            st.write(f"L-Glutamine: {l_glutamine * volume} mM")
            st.write(f"Non-Essential Amino Acids (NEAA): {neaa * volume} mM")
            st.write(f"Sodium Pyruvate: {sodium_pyruvate * volume} mM")
            st.write(f"Hepes Buffer: {hepes_buffer * volume} mM")
            st.write(f"Growth Factors: {growth_factors}")

with tabs[2]:
    st.subheader("Bioprocess Simulator")

    # Existing content moved to Bioprocess Simulator tab
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
            
            # Additional advanced parameters
            temperature_control = st.slider("Temperature Control (°C)", min_value=20.0, max_value=45.0, value=37.0, step=0.5)
            pH_control = st.slider("pH Control", min_value=4.0, max_value=9.0, value=7.2, step=0.1)

        # Function to simulate bioprocess
        def simulate_bioprocess(config):
            # Simulate process based on configuration (for demonstration purposes, using random data)
            time = np.arange(0, config['duration'])
            biomass = np.random.rand(config['duration']) * 100
            glucose = np.random.rand(config['duration']) * 10
            oxygen = np.random.rand(config['duration']) * 100
            lactate = np.random.rand(config['duration']) * 5
            ammonia = np.random.rand(config['duration']) * 2
            return time, biomass, glucose, oxygen, lactate, ammonia

        # AI feature to explain simulation results and provide recommendations
        def ai_analysis(biomass, glucose, oxygen, lactate, ammonia):
            explanation = "The simulation shows the dynamic behavior of biomass, glucose, oxygen, lactate, and ammonia over time."
            recommendations = []

            if np.mean(biomass) < 50:
                recommendations.append("Consider optimizing the media composition or feed strategy to improve biomass growth.")
            if np.mean(glucose) < 5:
                recommendations.append("Glucose levels are low. Increase the glucose concentration in the feed.")
            if np.mean(oxygen) < 50:
                recommendations.append("Oxygen levels are low. Increase the aeration rate or agitation speed.")
            if np.mean(lactate) > 2:
                recommendations.append("High lactate levels detected. Check for possible anaerobic conditions and adjust pH or oxygen levels.")
            if np.mean(ammonia) > 1:
                recommendations.append("High ammonia levels detected. Optimize the nitrogen source or control the pH better.")

            return explanation, recommendations

        if st.button("Simulate Bioprocess"):
            config_data = {
                "temp_range": temp_range,
                "ph_range": ph_range,
                "do_setpoint": do_setpoint,
                "agitation": agitation,
                "aeration": aeration,
                "duration": duration,
                "temperature_control": temperature_control,
                "pH_control": pH_control
            }
            time, biomass, glucose, oxygen, lactate, ammonia = simulate_bioprocess(config_data)

            st.subheader("Bioprocess Simulation Results")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=time, y=biomass, mode='lines', name='Biomass'))
            fig.add_trace(go.Scatter(x=time, y=glucose, mode='lines', name='Glucose'))
            fig.add_trace(go.Scatter(x=time, y=oxygen, mode='lines', name='Oxygen'))
            fig.add_trace(go.Scatter(x=time, y=lactate, mode='lines', name='Lactate'))
            fig.add_trace(go.Scatter(x=time, y=ammonia, mode='lines', name='Ammonia'))
            fig.update_layout(title='Bioprocess Simulation Results', xaxis_title='Time (hours)', yaxis_title='Concentration')
            st.plotly_chart(fig, use_container_width=True)

            charts = [
                ("Biomass vs Glucose", biomass, glucose),
                ("Biomass vs Oxygen", biomass, oxygen),
                ("Biomass vs Lactate", biomass, lactate),
                ("Biomass vs Ammonia", biomass, ammonia),
                ("Glucose vs Oxygen", glucose, oxygen),
                ("Glucose vs Lactate", glucose, lactate),
                ("Glucose vs Ammonia", glucose, ammonia),
                ("Oxygen vs Lactate", oxygen, lactate),
                ("Oxygen vs Ammonia", oxygen, ammonia),
                ("Lactate vs Ammonia", lactate, ammonia)
            ]

            for title, y1, y2 in charts:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=time, y=y1, mode='lines', name=title.split(' vs ')[0]))
                fig.add_trace(go.Scatter(x=time, y=y2, mode='lines', name=title.split(' vs ')[1]))
                fig.update_layout(title=title, xaxis_title='Time (hours)', yaxis_title='Concentration')
                st.plotly_chart(fig, use_container_width=True)

            explanation, recommendations = ai_analysis(biomass, glucose, oxygen, lactate, ammonia)
            st.subheader("AI Analysis")
            st.write(explanation)
            st.write("Recommendations:")
            for rec in recommendations:
                st.write(f"- {rec}")

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
            data_vis = st.selectbox(
                "Select Data Visualization",
                ["Time-series Plot", "Scatter Plot", "Bar Chart", "Heatmap"],
                key="data_vis"
            )
            data_export = st.selectbox(
                "Select Data Export Format",
                ["CSV", "Excel", "JSON", "PDF"],
                key="data_export_unique"
            )

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

    with tab7:
        st.subheader("Machine Learning")
        
        col13, col14 = st.columns(2)
        
        with col13:
            st.write("Model Selection")
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
            evaluation_metrics = st.selectbox(
                "Select Model Evaluation Metric",
                ["Mean Squared Error", "Mean Absolute Error", "R-squared", "Mean Absolute Percentage Error"],
                key="evaluation_metrics"
            )
            
            hyperparam_tuning = st.selectbox(
                "Select Hyperparameter Tuning Method",
                ["Grid Search", "Random Search", "Bayesian Optimization"]
            )

            
