import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

import os
from langchain_groq import ChatGroq

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

llm = ChatGroq(
    model="gemma2-9b-it",
    temperature=0.5,
)

def remedy(disease_name, location):
    prompt = [
        (
            "system",
            "You are an agricultural advisor. Given a crop disease and a location in India, provide farmer-friendly guidance. Write in bullet points, covering treatment, prevention, and locally suitable practices. Use simple Hindi. Do not include any introduction or conclusion."
        ),
        ("human", f"Disease is {disease_name} and location is {location}.")
    ]

    response = llm.invoke(prompt)
    return response.content
