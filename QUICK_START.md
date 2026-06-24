# Quick Start Guide

## 30 Second Setup

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Run Wikipedia Fetcher
```bash
python wikipedia_fetcher.py
```
This generates `data.json` with the knowledge graph.

### 3. Output
```
✓ Knowledge graph saved to data.json
Total Articles Processed: 5
Total Links Extracted: 1,200+
```

---

## What You Get

**`data.json`** - Wikipedia articles with:
- ✅ Article summaries
- ✅ All outbound links (ranked by health relevance)
- ✅ Article categories
- ✅ Wikipedia URLs
- ✅ Processing metadata

---

## Customization

### Change Starting Articles
Edit `wikipedia_fetcher.py`:
```python
seed_articles = [
    "Your Article 1",
    "Your Article 2",
]
```

### Adjust Search Depth
```python
fetcher.process_article(article_title, depth=1, max_depth=3)
#                                                      ↑
#                           Increase for deeper graph (slower)
```

### Run with Custom Keywords
Edit `score_relevance()` method in `wikipedia_fetcher.py`.

---

## Next: Pass to Ranking Pipeline

Once `data.json` is ready:
1. Your team creates ranking algorithm
2. Generates `origin_chain.json` with influence scores
3. `narrative.py` uses rankings to generate AI narrative

---

## Full Documentation

See `PIPELINE_GUIDE.md` for:
- Detailed API reference
- Advanced configuration
- Troubleshooting
- Team handoff checklist
