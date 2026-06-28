import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama

# Load index + docs
embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("KB/faiss_index.index")

with open("KB/docs.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    docs = data["documents"]
    metadata = data["metadata"]

def retrieve_docs(query, top_k=3):
    q_vec = embedder.encode([query], convert_to_numpy=True).astype("float32")
    dist, indices = index.search(q_vec, top_k)
    retrieved = [docs[i] for i in indices[0] if i < len(docs)]
    meta = [metadata[i] for i in indices[0] if i < len(metadata)]
    return retrieved, meta, dist, indices

def generate_answer(disease_or_pest_name, retrieved_docs, model_name="llama3"):
    """
    Generate a farmer-friendly answer in pure Hindi using Ollama (LLaMA 3),
    for a pest or disease.
    """
    context = "\n\n---\n\n".join(retrieved_docs)

    prompt = f"""
You are an agricultural advisor. A farmer asked about: "{disease_or_pest_name}" (pest or disease).  
Use this context if relevant: {context}.  

Provide the answer in the following structured format.  
**Important:** Use <br> for line breaks instead of newlines.

English Version:<br>
Disease: <disease name><br>
Symptoms: <describe all symptoms in one or more lines, using <br> for breaks><br>
Management: <describe all management practices in one or more lines, using <br> for breaks><br>

Hindi Version:<br>
Disease: <disease name><br>
Symptoms: <describe all symptoms in Hindi, using <br> for breaks><br>
Management: <describe all management practices in Hindi, using <br> for breaks><br>

Requirements:
1. Use farmer-friendly, easy-to-understand language.
2. Keep chemical names, tools, and numbers in English even in the Hindi version.
3. If exact info is not available, generate the best possible symptoms & management in the same format.
4. Do not include any "Note" or extra sections.
"""


    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])

    hindi_answer = response['message']['content']
    return hindi_answer
