import streamlit as st
import os
from main import run

st.set_page_config(page_title="Docstring Generator & Validator", layout="wide")

st.title("🚀 Automated Python Docstring Generator & Validator")
st.markdown("Docstring Synthesis & Validation")
st.write("Upload a Python file to generate styled docstrings and check PEP 257 compliance.")

# Sidebar for options
st.sidebar.header("Configuration")
style = st.sidebar.selectbox("Select Docstring Style", ["google", "numpy", "rest"])
validate = st.sidebar.checkbox("Enable PEP 257 Validation", value=True)

uploaded_file = st.file_uploader("Choose a Python file", type=["py"])

if uploaded_file is not None:
    source_code = uploaded_file.read().decode("utf-8")
    
    # Save to a temporary file for analysis
    temp_filename = "temp_upload.py"
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write(source_code)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Source Code")
        st.code(source_code, language="python")

    if st.button("Generate & Validate"):
        docs, report = run(temp_filename, style=style, validate=validate)

        with col2:
            st.subheader("Generated Docstrings")
            if not docs:
                st.info("No missing docstrings detected!")
            else:
                for d in docs:
                    with st.expander(f"{d['type'].capitalize()}: {d['name']}", expanded=True):
                        st.code(d['docstring'], language="python")

            st.subheader("Coverage & Compliance Report")
            
            # Display metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Coverage", f"{report['coverage_percentage']:.1f}%")
            m2.metric("Total Items", report['total'])
            m3.metric("Compliance", report['compliance'])

            st.write(f"- **Functions:** {report['documented_functions']} / {report['total_functions']} documented")
            st.write(f"- **Classes:** {report['documented_classes']} / {report['total_classes']} documented")

            if validate:
                st.subheader("Validation Results (PEP 257)")
                if not report['violations']:
                    st.success("All existing docstrings are PEP 257 compliant!")
                else:
                    st.error(f"Found {len(report['violations'])} violations")
                    for v in report['violations']:
                        st.warning(f"**Line {v['line']}**: {v['message']} ({v['code']})")

    # Cleanup (optional, but keep for now if needed for next runs)
    # os.remove(temp_filename)
