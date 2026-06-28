import streamlit as st
from PIL import Image
import numpy as np

# import your modules EXACTLY as written
from prediction import predict
from rag_utils import retrieve_docs, generate_answer

st.set_page_config(page_title="AgroCast AI", layout="centered")
st.title("🌱 AgroCast AI – Crop Disease Detection & Prevention")

st.write("Upload a leaf image to detect disease and get prevention advice.")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", width=300)

    # --- Disease Prediction ---
    with st.spinner("🔍 Predicting disease..."):
        disease_name, confidence = predict(img)

    st.success(f"🌿 **Predicted Disease:** {disease_name}")
    st.write(f"**Confidence:** {confidence}%")

    # --- RAG Advice ---
    st.header("🛠 Prevention Advice")

    with st.spinner("📚 Fetching relevant documents..."):
        retrieved_docs, meta, dist, idx = retrieve_docs(disease_name, top_k=3)

    with st.spinner("🤖 Generating final answer..."):
        final_answer = generate_answer(disease_name, retrieved_docs)

    # HTML available because your RAG uses <br>
    st.markdown(final_answer, unsafe_allow_html=True)

    # --- Retrieved Documents (Optional Debug UI) ---
    with st.expander("🔎 Retrieved Source Documents"):
        for i, doc in enumerate(retrieved_docs):
            st.markdown(f"**Doc {i+1}:**<br>{doc}", unsafe_allow_html=True)
