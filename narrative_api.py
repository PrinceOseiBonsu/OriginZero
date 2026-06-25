import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
app = Flask(__name__)
CORS(app)

TOPICS = ["Type 2 Diabetes", "Maternal Mortality", "Childhood Obesity"]

TONE_INSTRUCTIONS = {
    "academic": (
        "Write in a formal, research-style tone suitable for scholars and public health "
        "researchers. Use precise, analytical language and frame the explanation as if "
        "introducing a peer-reviewed paper."
    ),
    "emotional": (
        "Write in a powerful, personal, and moving tone suitable for the general public. "
        "Make it compelling and emotionally resonant while staying factual."
    ),
    "simple": (
        "Write in simple, easy-to-understand language suitable for kids and students. "
        "Avoid jargon, use short sentences, and explain ideas plainly."
    ),
}

# app = Flask(__name__)

with open("./data_chains/diabetes_chain.json", "r") as f:
    chain = json.load(f)

nodes_type_2_diabetes = [item["node"] for item in chain]

with open("./data_chains/maternal_mortality_chain.json", "r") as f:
    chain = json.load(f)

nodes_maternal_mortality = [item["node"] for item in chain]

with open("./data_chains/childhood_obesity_chain.json", "r") as f:
    chain = json.load(f)

nodes_childhood_obesity = [item["node"] for item in chain]

def generate_narrative(topic, tone="emotional"):
    if topic == "Type 2 Diabetes":
        nodes = nodes_type_2_diabetes
    elif topic == "Maternal Mortality":
        nodes = nodes_maternal_mortality
    elif topic == "Childhood Obesity":
        nodes = nodes_childhood_obesity
    else:
        raise ValueError(f"Unknown topic: {topic}")
    prompt = f"""
You are OriginZero, an AI that traces the historical root causes of health disparities.

Based on these Wikipedia knowledge graph nodes ranked by influence:
{", ".join(nodes)}

Write a powerful 150-word origin story explaining why {topic}
disproportionately affects underrepresented communities.

Focus on the historical, social, and economic root causes — not biology or genetics.
Make it clear, compelling, and suitable for a general audience.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )

    return response.choices[0].message.content


@app.route("/narrative", methods=["GET"])
def narrative():
    topic = request.args.get("topic", "Type 2 Diabetes")
    tone = request.args.get("tone", "emotional")

    if topic not in TOPICS:
        return jsonify({"error": f"Unknown topic: {topic!r}. Choose from {TOPICS}"}), 400

    if tone not in TONE_INSTRUCTIONS:
        return jsonify({"error": f"Unknown tone: {tone!r}. Choose from {list(TONE_INSTRUCTIONS)}"}), 400

    text = generate_narrative(topic, tone)
    return jsonify({"topic": topic, "tone": tone, "narrative": text})


if __name__ == "__main__":
    app.run(debug=True)