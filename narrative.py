import json
import os
import sys
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

TOPICS = ["Type 2 Diabetes", "Maternal Mortality", "Childhood Obesity"]

# Change this to switch topics, or pass one as a command-line argument.
topic = sys.argv[1] if len(sys.argv) > 1 else "Type 2 Diabetes"

if topic not in TOPICS:
    raise ValueError(f"Unknown topic: {topic!r}. Choose from {TOPICS}")

# Load origin chain
with open("origin_chain.json", "r") as f:
    chain = json.load(f)

nodes = [item["node"] for item in chain]

prompt = f"""
You are OriginZero, an AI that traces the historical root causes of health disparities.

Based on these Wikipedia knowledge graph nodes ranked by influence:
{", ".join(nodes)}

Write a powerful 150-word origin story explaining why {topic}
disproportionately affects African American and underrepresented communities.

Focus on the historical, social, and economic root causes — not biology or genetics.
Make it clear, compelling, and suitable for a general audience.
"""

print("Generating narrative with Groq...\n")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=300
)

narrative = response.choices[0].message.content

print("--- ORIGIN ZERO NARRATIVE ---")
print(narrative)

with open("narrative.txt", "w") as f:
    f.write(narrative)

print("\nNarrative saved to narrative.txt")