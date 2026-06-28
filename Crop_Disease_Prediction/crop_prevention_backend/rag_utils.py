print("DEBUG X: rag_utils loading...")

import faiss
import json
import numpy as np
from groq import Groq
import os
from sentence_transformers import SentenceTransformer

print("DEBUG Y: Basic libraries imported")

# -------------------------
# GLOBAL VARIABLES
# -------------------------

# Load embedder once
print("DEBUG Z1: Loading embedder...")
embedder = SentenceTransformer("paraphrase-MiniLM-L3-v2")
print("DEBUG Z2: Embedder loaded")

# Load FAISS index once
print("DEBUG Z3: Loading FAISS index...")
index = faiss.read_index("KB/faiss_index.index")
print("DEBUG Z4: FAISS index loaded")

# Load docs and metadata once
print("DEBUG Z5: Loading docs.json...")
with open("KB/docs.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    docs = data["documents"]
    metadata = data["metadata"]
print("DEBUG Z6: docs.json loaded")

# Initialize Groq client once
print("DEBUG G0: Initializing Groq client...")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("DEBUG G0.1: Groq client ready")

# -------------------------
# MAIN FUNCTIONS
# -------------------------

def retrieve_docs(query, top_k=3):
    print(f"DEBUG R1: retrieve_docs called -> {query}")

    q_vec = embedder.encode([query], convert_to_numpy=True).astype("float32")
    print("DEBUG R2: Query encoded")

    dist, indices = index.search(q_vec, top_k)
    print("DEBUG R3: FAISS search done")

    retrieved = [docs[i] for i in indices[0] if i < len(docs)]
    meta = [metadata[i] for i in indices[0] if i < len(metadata)]
    print("DEBUG R4: Docs + metadata extracted")

    return retrieved, meta, dist, indices


def generate_answer(disease_or_pest_name, retrieved_docs):
    print(f"DEBUG G1: generate_answer called -> {disease_or_pest_name}")

    context = "\n\n---\n\n".join(retrieved_docs)
    print("DEBUG G2: Context prepared")

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""
You are an agricultural advisor. A farmer asked about: "{disease_or_pest_name}".  
Use this context if relevant: {context}.

Provide structured answer with <br>.
"""}],
        temperature=0.3,
    )

    print("DEBUG G3: Groq response received")
    return response.choices[0].message.content
