import requests
import json
import time
from typing import Dict, List, Optional
from datetime import datetime

class WikipediaFetcher:
    """
    Fetches Wikipedia articles and builds a knowledge graph for health disparities research.
    Uses MediaWiki API to extract articles, links, and categories.
    """
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OriginZero/1.0 (Health Disparities Research)'
        })
        self.processed_articles = set()
        self.knowledge_graph = {}
        
    def fetch_article(self, title: str) -> Optional[Dict]:
        """
        Fetch article content, summary, and metadata from Wikipedia.
        
        Args:
            title: Wikipedia article title
            
        Returns:
            Dictionary with article data or None if not found
        """
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'extracts|pageimages|info',
            'explaintext': True,
            'exintro': True,
            'inprop': 'url',
            'format': 'json'
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            page = list(pages.values())[0] if pages else None
            
            if page and 'extract' in page:
                return {
                    'title': page.get('title', title),
                    'pageid': page.get('pageid'),
                    'url': page.get('canonicalurl', f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"),
                    'summary': page.get('extract', ''),
                    'thumbnail': page.get('thumbnail', {}).get('source')
                }
            return None
            
        except requests.RequestException as e:
            print(f"Error fetching article '{title}': {e}")
            return None
    
    def fetch_links(self, title: str, limit: int = 500) -> List[Dict]:
        """
        Fetch all outbound links (wikilinks) from an article.
        
        Args:
            title: Wikipedia article title
            limit: Maximum number of links to fetch
            
        Returns:
            List of dictionaries with link information
        """
        links = []
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'links',
            'pllimit': limit,
            'plnamespace': 0,  # Main namespace only (excludes Talk, User, etc.)
            'format': 'json'
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            page_links = list(pages.values())[0].get('links', []) if pages else []
            
            for link in page_links:
                links.append({
                    'title': link['title'],
                    'type': 'wikilink'
                })
            
            return links
            
        except requests.RequestException as e:
            print(f"Error fetching links for '{title}': {e}")
            return []
    
    def fetch_categories(self, title: str) -> List[str]:
        """
        Fetch all categories an article belongs to.
        
        Args:
            title: Wikipedia article title
            
        Returns:
            List of category names
        """
        categories = []
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'categories',
            'cllimit': 'max',
            'clshow': '!hidden',  # Exclude hidden categories
            'format': 'json'
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            page_cats = list(pages.values())[0].get('categories', []) if pages else []
            
            for cat in page_cats:
                categories.append(cat['title'].replace('Category:', ''))
            
            return categories
            
        except requests.RequestException as e:
            print(f"Error fetching categories for '{title}': {e}")
            return []
    
    def score_relevance(self, title: str, article_context: str, health_keywords: List[str] = None) -> float:
        """
        Score how relevant a link is to health disparities research.
        
        Args:
            title: Link title
            article_context: Summary or content of the source article
            health_keywords: Keywords related to health disparities
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        if health_keywords is None:
            health_keywords = [
                'health', 'disease', 'diabetes', 'disparities', 'race', 'ethnicity',
                'African American', 'Black', 'underrepresented', 'community', 'socioeconomic',
                'poverty', 'discrimination', 'inequality', 'access', 'healthcare',
                'diet', 'nutrition', 'obesity', 'mortality', 'cardiovascular',
                'kidney', 'complication', 'treatment', 'prevention', 'risk'
            ]
        
        score = 0.0
        title_lower = title.lower()
        
        # Exact keyword matches (high weight)
        for keyword in health_keywords:
            if keyword.lower() in title_lower:
                score += 0.15
        
        # Partial matches (medium weight)
        for keyword in health_keywords:
            if keyword.lower()[:4] in title_lower:
                score += 0.05
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def process_article(self, title: str, depth: int = 1, max_depth: int = 2) -> Dict:
        """
        Process a Wikipedia article and recursively fetch related articles.
        
        Args:
            title: Article title to process
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            
        Returns:
            Dictionary with article data and knowledge graph
        """
        if title in self.processed_articles:
            return {}
        
        self.processed_articles.add(title)
        print(f"Processing: {title} (depth: {depth}/{max_depth})")
        
        # Fetch article data
        article = self.fetch_article(title)
        if not article:
            print(f"  ⚠ Article not found: {title}")
            return {}
        
        # Fetch links and categories
        raw_links = self.fetch_links(title)
        categories = self.fetch_categories(title)
        
        # Score and filter links by relevance
        scored_links = []
        for link in raw_links:
            score = self.score_relevance(link['title'], article.get('summary', ''))
            if score > 0.0:  # Only include relevant links
                scored_links.append({
                    'title': link['title'],
                    'relevance_score': round(score, 4),
                    'type': 'wikilink'
                })
        
        # Sort by relevance score
        scored_links = sorted(scored_links, key=lambda x: x['relevance_score'], reverse=True)
        
        # Build node entry
        node_entry = {
            'title': article['title'],
            'pageid': article['pageid'],
            'url': article['url'],
            'summary': article['summary'][:500] + '...' if len(article['summary']) > 500 else article['summary'],
            'links': scored_links[:100],  # Top 100 relevant links
            'categories': categories,
            'thumbnail': article.get('thumbnail'),
            'processed_at': datetime.now().isoformat(),
            'depth': depth
        }
        
        self.knowledge_graph[title] = node_entry
        
        # Recursively process top relevant links
        if depth < max_depth:
            top_links = scored_links[:5]  # Process top 5 most relevant links
            for link in top_links:
                time.sleep(0.5)  # Rate limiting
                self.process_article(link['title'], depth + 1, max_depth)
        
        return node_entry
    
    def save_to_json(self, filename: str = 'data.json') -> None:
        """
        Save the complete knowledge graph to a JSON file.
        
        Args:
            filename: Output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_graph, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Knowledge graph saved to {filename}")
    
    def get_summary(self) -> Dict:
        """
        Get a summary of the processed knowledge graph.
        
        Returns:
            Dictionary with statistics
        """
        total_articles = len(self.knowledge_graph)
        total_links = sum(
            len(article.get('links', []))
            for article in self.knowledge_graph.values()
        )
        
        return {
            'total_articles': total_articles,
            'total_links': total_links,
            'articles': list(self.knowledge_graph.keys())
        }


def main():
    """
    Main function: Seed articles for health disparities research.
    """
    
    # Initialize fetcher
    fetcher = WikipediaFetcher()
    
    # Define seed articles for health disparities research
    seed_articles = [
        "Type 2 diabetes",
        "Health disparities",
        "African Americans",
        "Poverty and health",
        "Healthcare in the United States"
    ]
    
    print("=" * 70)
    print("OriginZero: Wikipedia Knowledge Graph Fetcher")
    print("Tracing Root Causes of Health Disparities")
    print("=" * 70)
    print()
    
    # Process each seed article
    for article_title in seed_articles:
        print(f"\n{'='*70}")
        print(f"Seed Article: {article_title}")
        print(f"{'='*70}")
        fetcher.process_article(article_title, depth=1, max_depth=2)
        time.sleep(1)  # Rate limiting between seed articles
    
    # Save results
    print(f"\n{'='*70}")
    print("Saving Knowledge Graph")
    print(f"{'='*70}")
    fetcher.save_to_json('data.json')
    
    # Print summary
    summary = fetcher.get_summary()
    print(f"\n{'='*70}")
    print("Knowledge Graph Summary")
    print(f"{'='*70}")
    print(f"Total Articles Processed: {summary['total_articles']}")
    print(f"Total Links Extracted: {summary['total_links']}")
    print(f"\nArticles in Graph:")
    for i, article in enumerate(summary['articles'], 1):
        print(f"  {i}. {article}")


if __name__ == "__main__":
    main()
