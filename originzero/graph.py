import json
import os
import networkx as nx
import matplotlib.pyplot as plt

# Load the crawled data
with open(os.path.join(os.path.dirname(__file__), "../data.json"), "r") as f:
    data = json.load(f)

# Build the graph
G = nx.DiGraph()

for article, content in data.items():
    G.add_node(article)
    for link in content["links"]:
        if link in data:
            G.add_edge(article, link)

print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# Run PageRank
pagerank = nx.pagerank(G, alpha=0.85)

# Sort by score — highest first
ranked = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)

# Filter out irrelevant nodes
IRRELEVANT = [
    "hinduism", "jews", "jewish", "france", "ghana", "israel",
    "australia", "chinese", "sikhism", "christian", "atlantic",
    "cardiac", "cotton", "climatarian", "low-fat", "low-carb",
    "diet food", "diabetic diet"
]

# Boost historical and social nodes
BOOST_KEYWORDS = [
    "history", "african", "poverty", "racism", "segregation",
    "inequality", "community", "disparity", "housing", "income",
    "slavery", "redlining", "discrimination", "obesity", "nutrition"
]

def is_origin_node(node):
    node_lower = node.lower()
    return not any(word in node_lower for word in IRRELEVANT)

def boost_score(node, score):
    node_lower = node.lower()
    if any(keyword in node_lower for keyword in BOOST_KEYWORDS):
        return score * 1.5
    return score

filtered = [
    (node, boost_score(node, score))
    for node, score in ranked
    if is_origin_node(node)
]

# Re-sort after boosting
filtered = sorted(filtered, key=lambda x: x[1], reverse=True)

print("\n--- TOP 10 ORIGIN CAUSE NODES ---")
for i, (node, score) in enumerate(filtered[:10]):
    print(f"{i+1}. {node} (score: {round(score, 4)})")

# Save ranked chain to JSON for Person 4
output = [{"rank": i+1, "node": node, "score": round(score, 4)} 
          for i, (node, score) in enumerate(filtered[:10])]

with open(os.path.join(os.path.dirname(__file__), "../data_chains/diabetes_chain.json"), "w") as f:
    json.dump(output, f, indent=2)

print("\nDiabetes chain saved to data_chains/diabetes_chain.json")