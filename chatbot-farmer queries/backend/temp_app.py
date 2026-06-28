
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os

# Load .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Flask session secret key
app.secret_key = os.getenv("SECRET_KEY", "default_secret")

# Load OpenAI API Key and model
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# ---------------------------
# Initialize conversation
# ---------------------------
def init_conversation():
    if "messages" not in session:
        session["messages"] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant for farmers. "
                    "Answer in simple language and give practical solutions."
                    "Always respond in simple, plain text only. "
                    "Do not use markdown, bullet points, numbering, or formatting. "
                    "Keep answers short and easy to understand."
                ),
            }
        ]


# ---------------------------
# Home Route
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------
# Chat API Route
# ---------------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    init_conversation()
    data = request.get_json() or {}
    user_text = data.get("message", "").strip()

    if not user_text:
        return jsonify({"error": "Empty message"}), 400

    # Add user message to session
    messages = session["messages"]
    messages.append({"role": "user", "content": user_text})

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0.4
        )
        

        # Correct way to extract content
        assistant_reply = response.choices[0].message.content

        # Save assistant message
        messages.append({"role": "assistant", "content": assistant_reply})
        session["messages"] = messages

        return jsonify({"reply": assistant_reply})

    except Exception as e:
        print("------ OPENAI ERROR ------")
        print(e)
        print("---------------------------")
        return jsonify({"error": "LLM request failed."}), 500


# ---------------------------
# Run Flask
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)