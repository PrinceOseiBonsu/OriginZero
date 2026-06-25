import os
import json
import time
import dotenv
import networkx as nx
from typing import Dict, List
from groq import Groq

import dotenv


dotenv.load_dotenv()



def clean_and_normalize_links(links: List[str]) -> List[str]:
    """
    Filters out Wikipedia meta-links, templates, categories, and internal help strings
    to keep only clean content nodes.
    """
    cleaned = []
    exclude_prefixes = (
        "Wikipedia:", "Template:", "Template talk:", "Help:", 
        "Category:", "Talk:", "Portal:", "Special:", "File:"
    )
    for link in links:
        if not link or any(link.startswith(prefix) for prefix in exclude_prefixes):
            continue
        cleaned.append(link.strip())
    return cleaned

def generate_teacher_narrative(client: Groq, instruction: str, context: str, target_links: List[str]) -> str:
    """
    Calls the teacher model (Groq Llama 3.1) to synthesize a high-quality 
    origin story, passing priority target links as hard-anchored context.
    """
    target_links_str = ", ".join([f"'{link}'" for link in target_links]) if target_links else "None detected"
    
    prompt = f"""You are the core intelligence of OriginZero, an expert system specializing in tracing systemic root causes of health disparities.
    
Your task is to generate a powerful, hard-hitting narrative based on the provided instruction, graph connectivity facts, and source text summary.

{instruction}

### CRITICAL CORE TARGET LINKING ENTITIES:
The network topology dictates that the following target nodes are your high-priority causal anchors. You MUST explicitly trace, integrate, or reference these key vectors in your response:
👉 [ {target_links_str} ]

### CONTEXT DATA PROVIDED:
{context}

### OUTPUT GUIDELINES:
1. Synthesize the raw text with the primary Causal Anchor target links identified in the Knowledge Graph.
2. Maintain an authoritative, analytical, and highly impactful tone.
3. Keep the output concise, dense with information, and under 300 words.
4. Output only the final narrative. Do not include introductory phrases like "Here is the narrative:".
"""

    try:
        # UPDATED MODEL STRING TO AN ACTIVE GENERATION ENDPOINT
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "You are a research distillation agent specialized in health disparities and complex system narratives."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"  ⚠ Error generating teacher narrative: {e}")
        return "Generation error. Baseline text extraction failed."
    
def prepare_finetuning_dataset(input_json_path: str, output_jsonl_path: str):
    """
    Ingests data.json, extracts network dimensions, computes PageRank, 
    and passes unified context blocks + target links to Groq for teacher distillation.
    """
    if not os.environ.get("GROQ_API_KEY"):
        raise ValueError("CRITICAL: GROQ_API_KEY environment variable is not set.")
    
    client = Groq()

    # 1. Load the crawled data
    with open(input_json_path, 'r', encoding='utf-8') as f:
        graph_data = json.load(f)
        
    print(f"Loaded {len(graph_data)} articles from {input_json_path}")
    
    # 2. Extract title mapping
    title_to_key_map = {}
    for key, article in graph_data.items():
        if "title" in article:
            title_to_key_map[article["title"]] = key
            title_to_key_map[key] = key

    # 3. Build the Network Graph
    G = nx.DiGraph()
    for key in graph_data.keys():
        G.add_node(key)
        
    for key, article in graph_data.items():
        raw_links = article.get('links', [])
        cleaned_links = clean_and_normalize_links(raw_links)
        
        for target_link in cleaned_links:
            resolved_key = None
            if target_link in graph_data:
                resolved_key = target_link
            elif target_link in title_to_key_map:
                resolved_key = title_to_key_map[target_link]
                
            if resolved_key and resolved_key != key:
                G.add_edge(key, resolved_key)
                
    # Calculate PageRank
    try:
        pagerank_scores = nx.pagerank(G)
    except Exception as e:
        print(f"PageRank fallback: {e}")
        pagerank_scores = {node: 1.0 / len(G) for node in G.nodes()}
    
    # 4. Open Output File and Loop Through Data
    print("\n--- Starting Target-Linked Distillation Pipeline ---")
    
    with open(output_jsonl_path, 'w', encoding='utf-8') as out_f:
        for idx, (key, article) in enumerate(graph_data.items(), 1):
            title = article.get('title', key)
            raw_summary = article.get('summary', '').strip()
            
            # Pull outbound active neighbors from graph topology
            neighbors = [edge[1] for edge in G.out_edges(key)]
            # Sort targets by their overarching calculated PageRank value
            ranked_neighbors = sorted(neighbors, key=lambda x: pagerank_scores.get(x, 0), reverse=True)
            
            # Isolate the top 3 highest-priority destination node identities for explicit instruction targeting
            top_target_links = ranked_neighbors[:3]
            
            print(f"[{idx}/{len(graph_data)}] Distilling Node: '{title}' -> Priority Anchors: {top_target_links}")
            
            graph_context_facts = []
            for rank_idx, target in enumerate(ranked_neighbors[:10], 1):
                score = pagerank_scores[target]
                graph_context_facts.append(
                    f"Fact #{rank_idx}: '{title}' features a systemic link to high-impact node '{target}' (Network Weight Score: {score:.4f})."
                )
                
            graph_context_str = "\n".join(graph_context_facts) if graph_context_facts else "No immediate high-impact cluster links mapped."
                
            # Construct unified context block
            full_context = (
                f"KNOWLEDGE GRAPH CONNECTIONS:\n{graph_context_str}\n\n"
                f"RAW ARTICLE EXTRACT:\n{raw_summary}"
            )
            
            instruction = f"Analyze the underlying social, institutional, and root causes linking to '{title}' using the extracted knowledge graph relationships and source text."
            
            # CALL TEACHER MODEL: Generate target response passing the top_target_links list
            teacher_response = generate_teacher_narrative(client, instruction, full_context, top_target_links)
            
            # Form clean instruction tuning dataset row
            record = {
                "instruction": instruction,
                "context": full_context,
                "response": teacher_response
            }
            
            # Write immediately to file
            out_f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            # Short sleep for rate limiting
            time.sleep(1.5)
            
    print(f"\n> Knowledge Distillation complete! Saved training file to: {output_jsonl_path}")

if __name__ == '__main__':
    prepare_finetuning_dataset('data.json', 'originzero_gemma4_dataset.jsonl')