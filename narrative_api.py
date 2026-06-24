import json
import os
from flask import Flask, jsonify, request
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

TOPICS = ["Type 2 Diabetes", "Maternal Mortality", "Childhood Obesity"]

app = Flask(__name__)

with open("origin_chain.json", "r") as f:
    chain = json.load(f)

nodes = [item["node"] for item in chain]


def generate_narrative(topic):
    prompt = f"""
You are OriginZero, an AI that traces the historical root causes of health disparities.

Based on these Wikipedia knowledge graph nodes ranked by influence:
{", ".join(nodes)}

Write a powerful 150-word origin story explaining why {topic}
disproportionately affects African American and underrepresented communities.

Focus on the historical, social, and economic root causes — not biology or genetics.
Make it clear, compelling, and suitable for a general audience.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    return response.choices[0].message.content


@app.route("/narrative", methods=["GET"])
def narrative():
    topic = request.args.get("topic", "Type 2 Diabetes")

    if topic not in TOPICS:
        return jsonify({"error": f"Unknown topic: {topic!r}. Choose from {TOPICS}"}), 400

    text = generate_narrative(topic)
    return jsonify({"topic": topic, "narrative": text})


if __name__ == "__main__":
    app.run(debug=True)
