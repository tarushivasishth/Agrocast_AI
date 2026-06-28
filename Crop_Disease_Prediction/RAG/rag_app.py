import streamlit as st
from rag_utils1 import retrieve_docs, generate_answer

st.title("🌾 Crop Disease & Pest Advisor (Hindi + English)")
st.write("Ask about any crop disease or pest. The system fetches knowledge and replies in farmer-friendly Hindi + English.")

query = st.text_input("Enter disease or pest name (e.g., Wheat Aphid, Rice Blast):")

if st.button("Get Advice"):
    if query.strip():
        with st.spinner("Fetching advice..."):
            retrieved_docs, meta, dist, indices = retrieve_docs(query, top_k=3)
            # answer = generate_answer(query, retrieved_docs)
            threshold = 1.0  # tune based on embedding similarity

            if dist[0][0] < threshold:
                # Relevant documents found → use them as context
                answer = generate_answer(query, retrieved_docs)
                relevant_found = True
            else:
                # No reliable match → ask LLM to generate own response
                answer = generate_answer(query, retrieved_docs=[])
                relevant_found = False


        st.subheader("💡 Farmer-Friendly Answer")
        st.write(answer)

        if relevant_found:
            with st.expander("Retrieved Knowledge Base Entries"):
                for m in meta:
                    st.markdown(f"- **Crop**: {m['crop']}, **Disease**: {m['disease']}, [More Info]({m['url']})")

    else:
        st.warning("Please enter a disease or pest name.")
