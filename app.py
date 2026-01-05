import streamlit as st
from main import run


st.set_page_config(page_title="Docstring Generator", layout="centered")

st.title("Automated Python Docstring Generator")
st.write("Upload a Python file to generate docstrings and coverage report")

uploaded_file = st.file_uploader("Upload Python file", type=["py"])

if uploaded_file is not None:
    source_code = uploaded_file.read().decode("utf-8")

    with open("temp.py", "w", encoding="utf-8") as f:
        f.write(source_code)

    if st.button("Generate Docstrings"):
        docs, report = run("temp.py")

        st.subheader("Generated Docstrings")
        for d in docs:
            st.code(d, language="python")

        st.subheader("Docstring Coverage Report")
        st.write(f"Total functions/methods : {report['total']}")
        st.write(f"With docstrings        : {report['with_doc']}")
        st.write(f"Missing docstrings     : {report['missing']}")
