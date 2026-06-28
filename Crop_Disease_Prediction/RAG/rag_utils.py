import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
import os

# ---------- Load embeddings ----------
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ---------- Load FAISS index + docs ----------
index = faiss.read_index("KB/faiss_index.index")

with open("KB/docs.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    docs = data["documents"]
    metadata = data["metadata"]

# ---------- Groq Client ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)  
# IMPORTANT: Set GROQ_API_KEY=xxxx in environment


def retrieve_docs(query, top_k=3):
    """Retrieve top-k similar documents using FAISS."""
    q_vec = embedder.encode([query], convert_to_numpy=True).astype("float32")
    dist, indices = index.search(q_vec, top_k)

    retrieved = [docs[i] for i in indices[0] if i < len(docs)]
    meta = [metadata[i] for i in indices[0] if i < len(metadata)]
    return retrieved, meta, dist, indices


def generate_answer(disease_or_pest_name, retrieved_docs, model_name="llama3-70b-8192"):
    """
    Generate an agricultural advisory answer using Groq LLaMA-3.
    Output includes <br> formatted English + Hindi sections.
    """

    context = "\n\n---\n\n".join(retrieved_docs)

    prompt = f"""
You are an agricultural expert. A farmer asked about: "{disease_or_pest_name}" (pest or disease).
Use the context below ONLY if relevant:

Context:
{context}

Provide the answer in this EXACT format using <br> tags instead of newlines:

English Version:<br>
Disease: <disease name><br>
Symptoms: <symptoms with <br> breaks><br>
Management: <management steps with <br> breaks><br>

Hindi Version:<br>
Disease: <disease name><br>
Symptoms: <symptoms in Hindi with <br> breaks><br>
Management: <management in Hindi with <br> breaks><br>

Rules:
1. Keep farmer-friendly language.
2. Keep chemical names, tools, numbers in English even in Hindi.
3. If context has missing information, generate reasonable content.
4. DO NOT add any extra sections.
5. DO NOT use markdown headings (#). Just plain text with <br>.
    """

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=1000
    )

    final_answer = response.choices[0].message.content
    return final_answer
