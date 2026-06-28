import streamlit as st
from PIL import Image
from prediction import predict
from llm_helper import remedy
from rag_utils1 import generate_answer, retrieve_docs

st.set_page_config(page_title="Crop Disease Detector + Cure", layout="wide")

st.title("🌱 Crop Disease Prediction + Cure Assistant")

# File uploader
uploaded_file = st.file_uploader("Upload a crop leaf image", type=["jpg","jpeg","png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", width='content')

    # Predict button
    if st.button("🔍 Predict Disease"):
        with st.spinner("Analyzing image..."):
            disease_name, confidence = predict(image)
            st.session_state["disease_name"] = disease_name
            st.session_state["confidence"] = confidence
        st.success(f"**Prediction:** {disease_name} ({confidence:.2f}% confidence)")

# Show disease info if available
if "disease_name" in st.session_state:

    if st.button("Get Advice"):
        query = st.session_state["disease_name"]

        if query.lower().endswith("healthy"):
            # Skip retrieval for healthy leaves
            st.subheader("💡 Farmer-Friendly Answer")
            st.success("🌿 The crop is healthy. No treatment needed. ✅")
        
        else:
            with st.spinner("Fetching advice..."):
                retrieved_docs, meta, dist, indices = retrieve_docs(query, top_k=3)

                threshold = 1.5  # tune based on embedding similarity

                if dist[0][0] < threshold:
                    # Relevant documents found → use them as context
                    answer = generate_answer(query, retrieved_docs)
                else:
                    # No reliable match → ask LLM to generate fallback response
                    answer = generate_answer(query, retrieved_docs=[])

            st.subheader("💡 Farmer-Friendly Answer")
            st.write(answer)

            with st.expander("Retrieved Knowledge Base Entries"):
                i = 0
                for m in meta:
                    st.markdown(f"- **Crop**: {m['crop']}, **Disease**: {m['disease']}, **URL**: {m['url']}, **Distance**: {dist[0][i]}")
                    i += 1
