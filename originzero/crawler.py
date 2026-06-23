import wikipediaapi
import json

wiki = wikipediaapi.Wikipedia(
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent='OriginZero/1.0'
)

# Keywords that point toward origin/historical causes
ORIGIN_KEYWORDS = [
    "poverty", "food", "race", "racism", "history", "inequality",
    "segregation", "redlining", "slavery", "discrimination", "social",
    "economic", "community", "disparity", "access", "income", "housing",
    "nutrition", "obesity", "diet", "african", "minority", "urban"
]

def get_article(topic):
    page = wiki.page(topic)
    if not page.exists():
        print(f"Article '{topic}' not found.")
        return None
    return page

def extract_links(page):
    links = list(page.links.keys())
    return links

def crawl(topic):
    page = get_article(topic)
    if not page:
        return None

    data = {
        "title": page.title,
        "summary": page.summary[0:500],
        "links": extract_links(page)
    }
    return data

def is_relevant(link):
    link_lower = link.lower()
    return any(keyword in link_lower for keyword in ORIGIN_KEYWORDS)

def deep_crawl(topic, depth=2, max_links=15):
    visited = {}

    def crawl_recursive(current_topic, current_depth):
        if current_depth == 0 or current_topic in visited:
            return
        print(f"  Crawling (depth {current_depth}): {current_topic}")
        result = crawl(current_topic)
        if not result:
            return
        visited[current_topic] = result
        relevant_links = [l for l in result["links"] if is_relevant(l)]
        for link in relevant_links[:max_links]:
            crawl_recursive(link, current_depth - 1)

    crawl_recursive(topic, depth)
    return visited

if __name__ == "__main__":
    topic = "Type 2 diabetes"
    print(f"Starting deep crawl: {topic}\n")
    result = deep_crawl(topic, depth=3, max_links=10)
    with open("data.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nDone! Crawled {len(result)} articles.")
    print(f"Data saved to data.json")