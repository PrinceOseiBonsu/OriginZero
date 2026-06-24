from narrative_api import generate_narrative

TOPIC_SLUGS = {
    "Type 2 Diabetes": "diabetes",
    "Maternal Mortality": "maternal",
    "Childhood Obesity": "obesity",
}

TONES = ["academic", "emotional", "simple"]

for topic, topic_slug in TOPIC_SLUGS.items():
    for tone in TONES:
        print(f"Generating narrative for topic: {topic} | tone: {tone}")
        narrative = generate_narrative(topic, tone)

        output_file = f"narrative_{topic_slug}_{tone}.txt"
        with open(output_file, "w") as f:
            f.write(narrative)

        print(f"Saved to {output_file}\n")

print("All narratives generated.")
