import shutil
import subprocess
import sys

TOPICS = {
    "Type 2 Diabetes": "narrative_diabetes.txt",
    "Maternal Mortality": "narrative_maternal.txt",
    "Childhood Obesity": "narrative_obesity.txt",
}

for topic, output_file in TOPICS.items():
    print(f"Running narrative.py for topic: {topic}")
    subprocess.run([sys.executable, "narrative.py", topic], check=True)
    shutil.copyfile("narrative.txt", output_file)
    print(f"Saved to {output_file}\n")

print("All narratives generated.")
