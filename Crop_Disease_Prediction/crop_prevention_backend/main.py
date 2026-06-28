from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from rag_utils import generate_answer, retrieve_docs

app = FastAPI(title="Crop Disease Cure API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "rag-backend-running"}

@app.get("/get_advice/{disease}")
async def get_advice(disease: str):

    retrieved_docs, meta, dist, idx = await asyncio.to_thread(retrieve_docs, disease, 3)

    if dist[0][0] < 1.0:
        answer = await asyncio.to_thread(generate_answer, disease, retrieved_docs)
    else:
        answer = await asyncio.to_thread(generate_answer, disease, [])

    return {
        "advice": answer.replace("\n", "<br>"),
        "retrieved_docs": meta
    }
