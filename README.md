# OriginZero: Tracing the Root Causes of Health Disparities

**OriginZero** is an expert pipeline designed to trace, map, and analyze the complex, historical, institutional, and socioeconomic root causes behind public health disparities (such as Type 2 Diabetes, Childhood Obesity, and Maternal Mortality).

By combining automated Wikipedia network crawling, PageRank topology analysis, and fine-tuned Large Language Models (LLMs), OriginZero synthesizes dense, highly accurate structural narratives instead of relying purely on biomedical explanations.



## Goals
* Identify the historical and institutional 
chains that drive health disparities, going 
past correlated risk factors to the decisions 
that created them.
* Build a graph based method for ranking 
causal significance that is reproducible and 
does not depend on a researcher's prior 
assumptions about what matters.
* Turn that graph structure into a narrative 
that a non specialist, a journalist, a 
policymaker, a student, can read once and 
actually understand.
* Prove the approach works across more 
than one disparity, so the method is 
judged on its design, not on luck with a 
single dataset.


## Core Features

* **Contextual Knowledge Crawling (`wikipedia_fetcher.py`):** Deep-crawls Wikipedia layers targeted at tracking historical and environmental vectors (e.g., redlining, food deserts, poverty).
* **Graph-Topology Anchoring (`graph.py`, `*_origin.py`):** Leverages NetworkX to build Directed Graphs. Uses **Personalized PageRank** across balanced pillars to find mathematically significant structural nodes without algorithmic bias.
* **Narrative Generation (`generate_narrative.py`):** Client script that queries the inference engine to produce a plain-English narrative of the root causes of health disparities.
* **Visualization & Reporting:** Generates interactive visualizations of the knowledge graph, PageRank scores, and evolution of the structural network.
* **Web Interface (`index.html`):** Provides a user-friendly interface to explore the knowledge graph, timelines, and key statistics.
* **Teacher-Model Distillation (`data_generator.py`):** Automatically passes knowledge graph data and text fragments to Groq (`llama-3.3-70b-versatile`) to compile instruction-tuning training datasets (`.jsonl`).
* **Hardware-Accelerated Inference Engine (`inference.py`):** A production-ready FastAPI service backed by Unsloth for ultra-fast, 4-bit quantized narrative generation using fine-tuned models.
* **Supervised Fine-Tuning:** Supports fine-tuning of LLMs with domain-specific datasets for improved narrative accuracy.




## Setup & Installation

### 1. Initialize a Virtual Environment

Isolate your dependencies using Python's native virtual environment wizardry:

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

```

### 2. Install Core Dependencies

Install the required packages:

```bash
pip install -r requirements.txt

```

### 3. GPU/LLM Inference Acceleration (Optional)

If you are running the `inference.py` backend locally or in a cloud container (like Google Colab), install the dedicated optimization packages:

```bash
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps xformers trl peft loralib torch

```

---

## Environment Variables (`.env`)

Create a `.env` file in the root directory and populate it with your cloud endpoints:

```bash
# Groq API Key for Teacher-Model Dataset Generation or narrative inference
GROQ_API_KEY=gsk_your_secret_key_here

```

---

## Step-by-Step Pipeline Execution

1. **Crawl Data:** Run `python crawler.py` to scrape localized ecosystem context files.
2. **Process Topology:** Run `python childhood_obesity_origin.py` (or other target analytics) to generate ranked metadata indices.
3. **Build Datasets / Generate Narratives:** Execute `python data_generator.py` to leverage the Groq cloud dataset engine, or spin up `uvicorn inference:app --reload` to host your own local generation engine!
4. **Generate Narrative:** Run `python generate_narrative.py` to produce the final narrative output.
5. **Visualize & Report:** Open `index.html` in a browser to explore the knowledge graph, PageRank scores, and evolution of the structural network.

---

## Model Training Report

### Configuration & Hardware

* **Model:** Gemma-4-E2B (Instruction-Tuned LLM)
* **Total Gradient Tokens:** 983,040 tokens
* **Training Steps:** 60
* **Batch Size:** 2
* **Average Tokens per Sample:** 735.3 tokens
* **Total Corpus Data Tokens:** 44,119 tokens
* **Training Duration:** < 30 minutes
* **Hardware:** 1x L4 GPU

## Model Performance & Loss Curves

* **Training Objective:** Cross-Entropy Loss with LoRA (Low-Rank Adaptation) targets on `q_proj`, `k_proj`, `v_proj`, and `o_proj` layers.
* **Precision:** 4-bit Base Model Quantization (QLoRA) with Float16/Bfloat16 gradient accumulation.
* **Loss Convergence:**

| Step | Training Loss |
| --- | --- |
| 1 | 1.057599 |
| 19 | 0.209967 |
| 39 | 0.123117 |
| 59 | 0.118483 |

---

## Dataset Schema & Distillation Format

The `data_generator.py` script distills raw graph contexts into a structural instruction-tuning format. Example `.jsonl` training sample:

```json
{
  "instruction": "Analyze the structural root causes of Type 2 Diabetes disparities in historical urban centers.",
  "context": "Node: Food Desert (PageRank: 0.042), Node: 1930s Redlining (PageRank: 0.038). Edge: Redlining -> Reduced Supermarket Investment.",
  "response": "The disparity in Type 2 Diabetes prevalence is heavily anchored in historical 1930s redlining policies. Graph topology highlights that redlining directly influenced a lack of commercial supermarket investment, creating modern food deserts..."
}

```

---

## Inference API Reference

The `inference.py` script spins up a high-performance **FastAPI** server optimized with **Unsloth 4-bit quantization**.

### `POST /v1/generate-narrative`

Generates a plain-English structural narrative from a given graph state or context.

**Request Body:**

```json
{
  "topic": "childhood_obesity",
  "top_k_nodes": 5,
  "temperature": 0.3
}

```

**Response (200 OK):**

```json
{
  "status": "success",
  "model": "Gemma-4-E2B-OriginZero-4bit",
  "narrative": "Childhood obesity disparities are strongly tied to zip-code level infrastructure..."
}

```
