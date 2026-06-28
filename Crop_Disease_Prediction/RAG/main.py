from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
from typing import List
import asyncio
from markdown import markdown

from prediction import predict
from rag_utils1 import generate_answer, retrieve_docs

app = FastAPI(title="Crop Disease Detector + Cure API")

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple cache to avoid recomputation
cache = {}

@app.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    try:
        image = Image.open(io.BytesIO(await file.read()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    # Step 1: Predict disease
    disease_name, confidence = predict(image)

    # Cache prediction
    cache['last_prediction'] = {"disease_name": disease_name, "confidence": float(confidence)}

    return {"disease_name": disease_name, "confidence": float(confidence)}


@app.get("/get_advice/{disease_name}")
async def get_advice(disease_name: str):
    disease_name = disease_name.strip()
    if not disease_name:
        raise HTTPException(status_code=400, detail="Disease name is required")

    # Default fallback for healthy crops
    if disease_name.lower().endswith("healthy"):
        return {"advice": "🌿 The crop is healthy. No treatment needed. ✅", "retrieved_docs": []}

    # Check cache first
    if disease_name in cache:
        return cache[disease_name]

    # Step 2: Retrieve docs and generate answer
    retrieved_docs, meta, dist, indices = await asyncio.to_thread(retrieve_docs, disease_name, 3)
    threshold = 1.2

    if dist[0][0] < threshold:
        # Relevant docs → use as context
        answer = await asyncio.to_thread(generate_answer, disease_name, retrieved_docs)
    else:
        # LLM fallback
        answer = await asyncio.to_thread(generate_answer, disease_name, [])
    answer_html = answer.replace("\n", "<br>")

    response = {
        "advice": answer_html,
        "retrieved_docs": [
            {"crop": m["crop"], "disease": m["disease"], "url": m["url"], "distance": float(dist[0][i])}
            for i, m in enumerate(meta)
        ]
    }

    # Cache response
    cache[disease_name] = response
    return response
