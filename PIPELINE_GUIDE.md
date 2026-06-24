# OriginZero Pipeline Guide

## Overview

The OriginZero pipeline traces the **root causes of health disparities in underrepresented communities** through Wikipedia's knowledge graph.

### Pipeline Flow

```
Seed Articles 
    ↓
wikipedia_fetcher.py (Fetch & Process)
    ↓
data.json (Clean Knowledge Graph)
    ↓
origin_chain.json (Ranked Nodes)
    ↓
narrative.py (AI-Generated Narrative)
    ↓
narrative.txt (Final Output)
```

---

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required Packages:**
- `requests` - Wikipedia API calls
- `python-dotenv` - Environment variable management
- `groq` - AI narrative generation

---

## Step 2: Run the Wikipedia Fetcher

The `wikipedia_fetcher.py` script:
- ✅ Fetches Wikipedia articles via MediaWiki API
- ✅ Extracts all outbound links (wikilinks)
- ✅ Scores links by relevance to health disparities
- ✅ Recursively builds a knowledge graph (configurable depth)
- ✅ Outputs clean JSON to `data.json`

### Command

```bash
python wikipedia_fetcher.py
```

### What It Does

```
Processing: Type 2 diabetes (depth: 1/2)
  ✓ Fetched article with 312 links
  ✓ Scored links by health relevance
  ✓ Found top links: African Americans, Diet, Obesity, etc.
  
Processing: African Americans (depth: 2/2)
  ✓ Fetched article with 456 links
  ✓ Scored links by health relevance
  ✓ Recursive depth limit reached

✓ Knowledge graph saved to data.json
```

### Output: `data.json`

```json
{
  "Type 2 diabetes": {
    "title": "Type 2 diabetes",
    "pageid": 12345,
    "url": "https://en.wikipedia.org/wiki/Type_2_diabetes",
    "summary": "Type 2 diabetes (T2D)...",
    "links": [
      {
        "title": "African Americans",
        "relevance_score": 0.45,
        "type": "wikilink"
      },
      {
        "title": "Diet (nutrition)",
        "relevance_score": 0.38,
        "type": "wikilink"
      }
    ],
    "categories": ["Health", "Endocrine disorders"],
    "processed_at": "2026-06-24T12:00:00",
    "depth": 1
  },
  "African Americans": {
    "title": "African Americans",
    "pageid": 54321,
    "url": "https://en.wikipedia.org/wiki/African_Americans",
    "summary": "African Americans or Black Americans...",
    "links": [...],
    "categories": ["Race and ethnicity"],
    "processed_at": "2026-06-24T12:05:00",
    "depth": 2
  }
}
```

---

## Step 3: Configure Seed Articles

Edit the seed articles in `wikipedia_fetcher.py`:

```python
seed_articles = [
    "Type 2 diabetes",
    "Health disparities",
    "African Americans",
    "Poverty and health",
    "Healthcare in the United States"
]
```

**Example Topics:**
- Health conditions: `Type 2 diabetes`, `Hypertension`, `Obesity`
- Communities: `African Americans`, `Latinos`, `Native Americans`, `Appalachian people`
- Social factors: `Poverty`, `Healthcare access`, `Food deserts`, `Environmental racism`

---

## Step 4: Customize Relevance Scoring

Health-related keywords are automatically used to score links:

```python
health_keywords = [
    'health', 'disease', 'diabetes', 'disparities', 'race', 'ethnicity',
    'African American', 'Black', 'underrepresented', 'community', 'socioeconomic',
    'poverty', 'discrimination', 'inequality', 'access', 'healthcare',
    ...
]
```

**To customize:**

```python
# In wikipedia_fetcher.py, modify score_relevance()
custom_keywords = [
    'your_keyword_1',
    'your_keyword_2',
    'your_keyword_3'
]
fetcher.process_article("Your Article", depth=1, max_depth=2)
```

---

## Step 5: Adjust Recursion Depth

The `max_depth` parameter controls how deep the knowledge graph goes:

```python
fetcher.process_article(article_title, depth=1, max_depth=2)
#                                                  ↑
#                              1 = only seed articles
#                              2 = seed + first neighbors
#                              3 = seed + first + second neighbors
```

**Memory/Time Trade-offs:**
- `max_depth=1`: Fast (~30 sec), shallow insights
- `max_depth=2`: Moderate (~5 min), good balance
- `max_depth=3`: Slow (~30+ min), comprehensive graph

---

## Step 6: Run the Ranking Algorithm

After `data.json` is created, the next step would be:

```bash
python rank_nodes.py  # (to be created)
```

This generates `origin_chain.json` with influence scores.

---

## Step 7: Generate AI Narrative

Set your Groq API key:

```bash
export GROQ_API_KEY="your_api_key_here"
```

Run the narrative generator:

```bash
python narrative.py
```

Output: `narrative.txt` - AI-generated explanation of health disparities root causes.

---

## API Reference: `WikipediaFetcher` Class

### Methods

#### `fetch_article(title: str) → Dict`
Fetch article content, summary, and metadata.

```python
article = fetcher.fetch_article("Type 2 diabetes")
# Returns: {title, pageid, url, summary, thumbnail}
```

#### `fetch_links(title: str, limit: int = 500) → List[Dict]`
Extract all outbound Wikipedia links.

```python
links = fetcher.fetch_links("Type 2 diabetes")
# Returns: [{"title": "...", "type": "wikilink"}, ...]
```

#### `fetch_categories(title: str) → List[str]`
Get article categories.

```python
categories = fetcher.fetch_categories("Type 2 diabetes")
# Returns: ["Health", "Endocrine disorders", ...]
```

#### `score_relevance(title: str, article_context: str, health_keywords: List[str]) → float`
Score link relevance to health disparities (0.0-1.0).

```python
score = fetcher.score_relevance("African Americans", article_context)
# Returns: 0.45
```

#### `process_article(title: str, depth: int, max_depth: int) → Dict`
Recursively process articles and build knowledge graph.

```python
fetcher.process_article("Type 2 diabetes", depth=1, max_depth=2)
```

#### `save_to_json(filename: str) → None`
Save knowledge graph to JSON file.

```python
fetcher.save_to_json('data.json')
```

#### `get_summary() → Dict`
Get statistics about processed articles.

```python
summary = fetcher.get_summary()
# Returns: {total_articles, total_links, articles: [...]}
```

---

## Troubleshooting

### Error: "Article not found"
- Check Wikipedia article title spelling
- Wikipedia titles are case-sensitive for redirects
- Try the exact URL slug (e.g., "African_Americans")

### Error: "Rate limit exceeded"
- The fetcher includes `time.sleep(0.5)` between requests
- Reduce `max_depth` or use fewer seed articles
- Run during off-peak hours

### Empty links in output
- Article may not have relevant health-related links
- Adjust `health_keywords` in `score_relevance()`
- Try a different seed article

### Large file size
- Limit top links: change `scored_links[:100]` to `scored_links[:50]`
- Reduce recursion depth: `max_depth=1`
- Filter by relevance score threshold

---

## Next Steps

1. ✅ Run `wikipedia_fetcher.py` → generates `data.json`
2. 📊 Create ranking algorithm → generates `origin_chain.json`
3. 🤖 Run `narrative.py` with Groq API → generates `narrative.txt`
4. 📈 Visualize in `index.html` (already exists)

---

## For Your Team

**Hand-off Checklist:**
- ✅ `wikipedia_fetcher.py` - Fetches and processes Wikipedia data
- ✅ `requirements.txt` - Dependencies
- ✅ `PIPELINE_GUIDE.md` - This documentation
- 📝 `data.json` - Output (to be generated)
- ⏳ `origin_chain.json` - Ranking algorithm (to be created)
- ⏳ Ranking script - To score and rank nodes

---

## Questions?

For issues or custom configurations:
1. Check `WikipediaFetcher` class docstrings
2. Modify `score_relevance()` for custom scoring
3. Edit `seed_articles` for different starting points
4. Adjust `max_depth` for graph scope

**Happy researching! 🔬📊**
