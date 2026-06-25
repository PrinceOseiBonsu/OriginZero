import json
import os
import networkx as nx

# 1. Load the crawled data
data_path = os.path.join(os.path.dirname(__file__), "../data.json")
with open(data_path, "r") as f:
    data = json.load(f)

# 2. Build the graph
G = nx.DiGraph()
for article, content in data.items():
    G.add_node(article)
    for link in content.get("links", []):
        if link in data:
            G.add_edge(article, link)

print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# 3. Create an Personalization Vector
# Define the core "seed" topics that define what maternal mortality is.
# This guides the algorithm structurally rather than artificially boosting final scores.
SEED_TOPICS = [
    "maternal mortality", "maternal health", "pregnancy", 
    "obstetrics", "postpartum period", "underrepresented communities"
]

# Find which seed topics actually exist in your crawled graph
valid_seeds = [node for node in SEED_TOPICS if G.has_node(node)]

if not valid_seeds:
    print("\n[Warning]: None of the core seed topics were found in the graph dataset.")
    print("Defaulting to standard, un-personalized PageRank.")
    personalization_dict = None
else:
    # Distribute probability evenly among the seed nodes found in your data
    personalization_dict = {node: 0.0 for node in G.nodes()}
    weight = 1.0 / len(valid_seeds)
    for node in valid_seeds:
        personalization_dict[node] = weight
    print(f"Personalizing PageRank using seeds: {valid_seeds}")

# 4. Run Personalized PageRank
# Alpha=0.85 means 85% following structural links, 15% jumping back to our seed topics
pagerank_scores = nx.pagerank(G, alpha=0.85, personalization=personalization_dict)

# 5. Sort by mathematically accurate scores (No manual multiplication!)
ranked = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)

# 6. Print the top results
print("\n--- TOP 10 STRUCTURALLY RELEVANT MATERNAL HEALTH NODES ---")
for i, (node, score) in enumerate(ranked[:10]):
    print(f"{i+1}. {node} (score: {round(score, 6)})")

# 7. Save to JSON
output = [
    {"rank": i+1, "node": node, "score": round(score, 6)} 
    for i, (node, score) in enumerate(ranked[:10])
]

output_path = os.path.join(os.path.dirname(__file__), "../data_chains/maternal_mortality_chain.json")
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {os.path.basename(output_path)}")