import spacy
import subprocess

# Auto-download if not available
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

import streamlit as st
import os
import tempfile
from document_metadata_pipeline import process_document

st.set_page_config(page_title="Document Metadata Extractor", layout="centered")

st.title("📄 Automated Metadata Generator")
st.write("Upload a document (PDF, DOCX, or TXT) and get auto-generated metadata.")

uploaded_file = st.file_uploader("Choose a document file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    with st.spinner("Extracting metadata..."):
        metadata = process_document(tmp_path)

    if "Error" in metadata:
        st.error(metadata["Error"])
    else:
        st.success("Metadata extracted successfully!")
        st.subheader("📌 Title")
        st.write(metadata["Title"])

        st.subheader("📝 Summary")
        st.write(metadata["Summary"])

        st.subheader("🔑 Keywords")
        st.write(", ".join(metadata["Keywords"]))

        st.subheader("🧠 Named Entities")
        for label, ents in metadata["Named Entities"].items():
            st.markdown(f"**{label}:** {', '.join(ents)}")

    os.remove(tmp_path)
