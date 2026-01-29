"""Streamlit Web Interface for the Docstring Generator tool."""
import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from main import run, load_config

# Load config for initial state
config = load_config()

# Page Configuration
st.set_page_config(
    page_title="Docstring Intelligence Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #e94560;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
    }
    .css-1offfwp {
        background-color: transparent !important;
    }
    .report-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3 {
        color: #00d2ff !important;
        font-family: 'Outfit', sans-serif;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00d2ff !important;
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("🚀 Docstring Intelligence Pro")
st.markdown("### Next-Gen Automated Python Documentation & Quality Assurance")
st.write("Leverage AI-driven docstring synthesis and automated PEP 257 validation.")

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.header("⚡ Control Center")
    # Map config style to index
    style_options = ["google", "numpy", "rest"]
    default_style_idx = style_options.index(config["default_style"]) if config["default_style"] in style_options else 0
    
    style = st.selectbox("🎯 Target Style", style_options, index=default_style_idx)
    validate = st.checkbox("🔍 Enable Compliance Check", value=config["validation_enabled"])
    
    st.divider()
    st.write(f"**Current Threshold:** {config['min_coverage']}%")
    st.info("Upload your Python script to begin the intelligence audit.")

# File Upload Section
uploaded_file = st.file_uploader("📂 Select Python Source File", type=["py"])

if uploaded_file is not None:
    source_code = uploaded_file.read().decode("utf-8")
    
    # Save to a temporary file
    temp_filename = "temp_upload.py"
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write(source_code)

    if st.button("🔥 Run Analysis & Generation"):
        docs, report = run(temp_filename, style=style, validate=validate)

        # Create Tabs for Separated Reports
        tab_code, tab_coverage, tab_compliance = st.tabs([
            "📝 Code & Generation", 
            "📊 Coverage Intelligence", 
            "⚖️ Compliance Audit"
        ])

        with tab_code:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("Original Source")
                st.code(source_code, language="python")

            with col2:
                st.subheader("Synthesized Docstrings")
                if not docs:
                    st.success("✅ Full Documentation Coverage Detected!")
                else:
                    for d in docs:
                        with st.expander(f"{d['type'].capitalize()}: {d['name']}", expanded=False):
                            st.code(d['docstring'], language="python")

        with tab_coverage:
            st.subheader("Documentation Coverage Audit")
            
            # Key Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Overall Coverage", f"{report['coverage_percentage']:.1f}%")
            m2.metric("Total Entities", report['total'])
            m3.metric("Documented", report['with_doc'])
            m4.metric("Missing", report['missing'])

            col_chart, col_details = st.columns([2, 1])
            
            with col_chart:
                # Pie Chart for Coverage
                labels = ['Documented', 'Missing']
                values = [report['with_doc'], report['missing']]
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels, 
                    values=values, 
                    hole=.6,
                    marker=dict(colors=['#00d2ff', '#e94560']),
                    textinfo='percent+label'
                )])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="white"),
                    margin=dict(t=0, b=0, l=0, r=0),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_details:
                st.write("#### 📌 Breakdown")
                st.write(f"**Functions:** {report['documented_functions']} / {report['total_functions']}")
                st.progress(report['documented_functions'] / report['total_functions'] if report['total_functions'] > 0 else 1.0)
                
                st.write(f"**Classes:** {report['documented_classes']} / {report['total_classes']}")
                st.progress(report['documented_classes'] / report['total_classes'] if report['total_classes'] > 0 else 1.0)

                mod_status = "✅ Present" if report.get("has_module_doc") else "❌ Missing"
                st.write(f"**Module Docstring:** {mod_status}")

        with tab_compliance:
            st.subheader("PEP 257 Compliance Report")
            
            if not validate:
                st.warning("⚠️ Compliance checks were disabled for this run.")
            else:
                comp_status = report['compliance']
                comp_percentage = report.get('compliance_percentage', 100.0)
                color = "#00ff88" if comp_status == "PASS" else "#ff4444"
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Compliance Score", f"{comp_percentage:.1f}%")
                    st.metric("Total Violations", len(report['violations']), delta=len(report['violations']), delta_color="inverse")
                    
                    if comp_status == "PASS":
                        st.success("✅ **STATUS: PASS**")
                    else:
                        st.error("❌ **STATUS: FAIL**")
                
                with col2:
                    # Simple Compliance Gauge/Progress
                    fig_comp = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = comp_percentage,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Compliance Detail"},
                        gauge = {
                            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                            'bar': {'color': color},
                            'bgcolor': "rgba(0,0,0,0)",
                            'borderwidth': 2,
                            'bordercolor': "white",
                            'steps': [
                                {'range': [0, 70], 'color': 'rgba(255, 68, 68, 0.1)'},
                                {'range': [70, 90], 'color': 'rgba(255, 187, 51, 0.1)'},
                                {'range': [90, 100], 'color': 'rgba(0, 255, 136, 0.1)'}
                            ],
                        }
                    ))
                    fig_comp.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color="white"),
                        margin=dict(t=30, b=0, l=30, r=30),
                        height=250
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)

                if not report['violations']:
                    st.balloons()
                    st.success("🌟 Perfect Compliance! This codebase adheres to PEP 257 standards.")
                else:
                    # Bar Chart for Violations by Code
                    violation_codes = [v['code'] for v in report['violations']]
                    code_counts = pd.Series(violation_codes).value_counts().reset_index()
                    code_counts.columns = ['Code', 'Count']
                    
                    fig_violations = px.bar(
                        code_counts, 
                        x='Code', 
                        y='Count',
                        title="Violation Frequency by Code",
                        color='Count',
                        color_continuous_scale='Reds'
                    )
                    fig_violations.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color="white"),
                    )
                    st.plotly_chart(fig_violations, use_container_width=True)

                    st.markdown("#### 🚩 Identified Violations")
                    for v in report['violations']:
                        with st.container():
                            st.error(f"**[{v['code']}]** Line {v['line']}: {v['message']}")
                            st.write(f"_{v['short_desc']}_")
                            st.divider()

    # Cleanup
    if os.path.exists("temp_upload.py"):
        try:
            pass # Keep it for debugging or let streamlit handle session state
        except:
            pass
