import os
import json
import faiss
import numpy as np
os.environ["USE_TF"] = "0"
os.environ["USE_JAX"] = "0"

from sentence_transformers import SentenceTransformer

def build_faiss_index(KB_PATH, index_file="./KB/faiss_index.index", docs_file="./KB/docs.json"):
    # Load embedding model
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    documents = []
    metadata = []

    # Load all JSON KB files
    for file in os.listdir(KB_PATH):
        if file.endswith(".json"):
            with open(os.path.join(KB_PATH, file), "r", encoding="utf-8") as f:
                data = json.load(f)

                # each crop JSON: {"crop": name, "diseases": [...]}
                for crop in data:
                    crop_name = crop["crop"]
                    for disease in crop["diseases"]:
                        text = (
                            f"Crop: {crop_name}\n"
                            f"Disease: {disease['name']}\n"
                            f"Symptoms: {disease.get('symptoms', [])}\n"
                            f"Management: {disease.get('management', {})}"
                        )

                        documents.append(text)
                        metadata.append({
                            "crop": crop_name,
                            "disease": disease["name"],
                            "url": disease.get("url", "")
                        })

    # Encode
    vectors = embedder.encode(documents, convert_to_numpy=True).astype("float32")

    # Build FAISS
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    # Save index + metadata
    faiss.write_index(index, index_file)
    with open(docs_file, "w", encoding="utf-8") as f:
        json.dump({"documents": documents, "metadata": metadata}, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(documents)} entries to {index_file} and {docs_file}")
    return index, documents, metadata

if __name__ == "__main__":
    KB_PATH = r"C:\Users\tarus\minor_project\Crop_Disease_Prediction\KB"
    build_faiss_index(KB_PATH)
