#!/usr/bin/env python3
"""
News MCP Server
A FastMCP server that provides access to news headlines and articles from RSS feeds.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
import httpx
from fastmcp import FastMCP
import feedparser
from datetime import datetime

# Create the FastMCP server
mcp = FastMCP("News MCP Server")

# News sources configuration
NEWS_SOURCES = {
    "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
    "reuters": "https://feeds.reuters.com/reuters/topNews",
    "ap": "https://feeds.apnews.com/rss/apf-topnews",
    "techcrunch": "https://techcrunch.com/feed/",
    "cnn": "http://rss.cnn.com/rss/edition.rss",
    "npr": "https://feeds.npr.org/1001/rss.xml",
    "guardian": "https://www.theguardian.com/world/rss",
    "nytimes": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
}

# Category mappings for filtering with expanded keywords
CATEGORY_KEYWORDS = {
    "politics": [
        "politics", "political", "government", "election", "president", "congress", "senate", 
        "democracy", "policy", "voting", "campaign", "candidate", "parliament", "minister",
        "trump", "biden", "republican", "democrat", "liberal", "conservative", "federal",
        "state", "local", "mayor", "governor", "senator", "representative", "cabinet"
    ],
    "technology": [
        "technology", "tech", "ai", "artificial intelligence", "software", "startup", 
        "innovation", "digital", "computer", "internet", "app", "mobile", "smartphone",
        "machine learning", "ml", "neural network", "deep learning", "chatgpt", "openai",
        "gpt", "llm", "blockchain", "crypto", "cryptocurrency", "bitcoin", "ethereum",
        "apple", "google", "microsoft", "amazon", "meta", "facebook", "twitter", "x",
        "tesla", "spacex", "nvidia", "intel", "amd", "qualcomm", "samsung", "huawei"
    ],
    "business": [
        "business", "economy", "market", "finance", "stock", "trading", "investment",
        "corporate", "company", "earnings", "revenue", "profit", "loss", "merger",
        "acquisition", "ipo", "venture capital", "funding", "startup", "unicorn",
        "wall street", "nasdaq", "dow jones", "s&p", "ftse", "nikkei", "dax",
        "ceo", "cfo", "cto", "board", "shareholder", "dividend", "bankruptcy"
    ],
    "sports": [
        "sports", "sport", "football", "basketball", "baseball", "soccer", "olympics",
        "athletics", "tennis", "golf", "hockey", "cricket", "rugby", "boxing", "mma",
        "nfl", "nba", "mlb", "nhl", "mls", "premier league", "champions league",
        "world cup", "super bowl", "stanley cup", "nba finals", "world series",
        "athlete", "player", "team", "coach", "championship", "tournament", "match"
    ],
    "health": [
        "health", "healthcare", "medical", "medicine", "covid", "pandemic", "disease",
        "virus", "bacteria", "infection", "vaccine", "vaccination", "treatment",
        "therapy", "surgery", "hospital", "doctor", "nurse", "patient", "diagnosis",
        "symptoms", "cure", "prevention", "mental health", "depression", "anxiety",
        "cancer", "diabetes", "heart", "stroke", "alzheimer", "dementia", "autism"
    ],
    "science": [
        "science", "scientific", "research", "study", "discovery", "space", "climate",
        "physics", "chemistry", "biology", "mathematics", "engineering", "medicine",
        "nasa", "spacex", "astronomy", "mars", "moon", "satellite", "rocket", "mission",
        "climate change", "global warming", "environment", "carbon", "emissions",
        "renewable", "solar", "wind", "nuclear", "fossil fuel", "green energy",
        "evolution", "genetics", "dna", "genome", "quantum", "particle", "atom"
    ],
    "world": [
        "world", "international", "global", "foreign", "diplomacy", "diplomatic",
        "united nations", "un", "nato", "eu", "european union", "brexit", "trade",
        "war", "conflict", "peace", "treaty", "agreement", "summit", "conference",
        "embassy", "ambassador", "minister", "secretary", "president", "prime minister",
        "china", "russia", "india", "japan", "germany", "france", "uk", "canada",
        "australia", "brazil", "mexico", "africa", "asia", "europe", "americas"
    ]
}

def parse_rss_feed(feed_url: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Parse RSS feed and return formatted articles."""
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries[:limit]:
            # Extract publication date
            pub_date = ""
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime(*entry.updated_parsed[:6]).isoformat()
            
            article = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": pub_date,
                "source": feed.feed.get("title", "Unknown"),
                "author": entry.get("author", ""),
                "tags": [tag.term for tag in entry.get("tags", [])]
            }
            articles.append(article)
        
        return articles
        
    except Exception as e:
        print(f"Error parsing RSS feed {feed_url}: {e}")
        return []

def filter_articles_by_category(articles: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    """Filter articles by category keywords."""
    if category not in CATEGORY_KEYWORDS:
        return articles
    
    keywords = CATEGORY_KEYWORDS[category]
    filtered = []
    
    for article in articles:
        title_lower = article.get("title", "").lower()
        summary_lower = article.get("summary", "").lower()
        tags_lower = " ".join(article.get("tags", [])).lower()
        
        # Check if any keyword matches
        text_to_search = f"{title_lower} {summary_lower} {tags_lower}"
        if any(keyword in text_to_search for keyword in keywords):
            filtered.append(article)
    
    return filtered

def expand_query_synonyms(query: str) -> List[str]:
    """Expand query with synonyms and related terms.
    
    Uses curated synonym mappings for common news topics to improve
    search relevance. In production, this could be enhanced with:
    - NLP-based synonym detection
    - User feedback learning
    - Domain-specific ontologies
    """
    query_lower = query.lower().strip()
    
    # Define synonym mappings
    synonym_groups = {
        "ai": ["artificial intelligence", "machine learning", "ml", "neural network", "deep learning", "chatgpt", "openai", "gpt", "llm", "large language model"],
        "artificial intelligence": ["ai", "machine learning", "ml", "neural network", "deep learning", "chatgpt", "openai", "gpt", "llm", "large language model"],
        "machine learning": ["ai", "artificial intelligence", "ml", "neural network", "deep learning", "data science"],
        "crypto": ["cryptocurrency", "bitcoin", "ethereum", "blockchain", "crypto", "digital currency"],
        "cryptocurrency": ["crypto", "bitcoin", "ethereum", "blockchain", "digital currency"],
        "bitcoin": ["crypto", "cryptocurrency", "btc", "digital currency"],
        "climate": ["climate change", "global warming", "environment", "carbon", "emissions", "sustainability"],
        "climate change": ["climate", "global warming", "environment", "carbon", "emissions", "sustainability"],
        "tech": ["technology", "tech", "software", "startup", "innovation", "digital"],
        "technology": ["tech", "software", "startup", "innovation", "digital", "tech"],
        "politics": ["political", "government", "election", "democracy", "policy", "congress", "senate"],
        "business": ["economy", "market", "finance", "trading", "investment", "corporate", "company"],
        "health": ["medical", "healthcare", "medicine", "covid", "pandemic", "disease", "health"],
        "sports": ["football", "basketball", "baseball", "soccer", "olympics", "athletics", "sport"],
        "science": ["research", "study", "discovery", "space", "physics", "chemistry", "biology"],
        "space": ["nasa", "spacex", "astronomy", "mars", "moon", "satellite", "rocket"],
        "tesla": ["elon musk", "electric vehicle", "ev", "tesla", "model s", "model 3", "model x", "model y"],
        "apple": ["iphone", "ipad", "mac", "ios", "macos", "tim cook", "apple"],
        "google": ["alphabet", "android", "chrome", "youtube", "search", "google"],
        "microsoft": ["windows", "office", "azure", "xbox", "microsoft", "satya nadella"],
        "amazon": ["aws", "prime", "bezos", "amazon", "alexa", "echo"],
        "meta": ["facebook", "instagram", "whatsapp", "zuckerberg", "meta", "vr", "virtual reality"],
        "facebook": ["meta", "instagram", "whatsapp", "zuckerberg", "facebook", "social media"],
        "twitter": ["x", "elon musk", "tweet", "twitter", "social media"],
        "x": ["twitter", "elon musk", "tweet", "x", "social media"]
    }
    
    # Start with the original query
    expanded_terms = [query_lower]
    
    # Add synonyms for exact matches
    if query_lower in synonym_groups:
        expanded_terms.extend(synonym_groups[query_lower])
    
    # Add synonyms for partial matches
    for key, synonyms in synonym_groups.items():
        if key in query_lower or any(syn in query_lower for syn in synonyms):
            expanded_terms.extend(synonyms)
    
    # Remove duplicates and empty strings
    expanded_terms = list(set([term.strip() for term in expanded_terms if term.strip()]))
    
    return expanded_terms

def search_articles(articles: List[Dict[str, Any]], query: str) -> tuple:
    """Search articles by query string with robust keyword expansion.
    
    Returns:
        tuple: (filtered_articles, search_terms_used)
    """
    if not query.strip():
        return [], []
    
    # Expand query with synonyms
    search_terms = expand_query_synonyms(query)
    
    filtered = []
    
    for article in articles:
        title_lower = article.get("title", "").lower()
        summary_lower = article.get("summary", "").lower()
        tags_lower = " ".join(article.get("tags", [])).lower()
        author_lower = article.get("author", "").lower()
        
        # Combine all searchable text
        text_to_search = f"{title_lower} {summary_lower} {tags_lower} {author_lower}"
        
        # Check if any search term matches
        match_found = False
        for term in search_terms:
            if term in text_to_search:
                match_found = True
                break
        
        if match_found:
            # Add relevance score based on where the match was found
            relevance_score = 0
            for term in search_terms:
                if term in title_lower:
                    relevance_score += 3  # Title matches are most important
                if term in summary_lower:
                    relevance_score += 2  # Summary matches are important
                if term in tags_lower:
                    relevance_score += 1  # Tag matches are less important
                if term in author_lower:
                    relevance_score += 1  # Author matches are less important
            
            article["relevance_score"] = relevance_score
            filtered.append(article)
    
    # Sort by relevance score (highest first), then by publication date
    filtered.sort(key=lambda x: (x.get("relevance_score", 0), x.get("published", "")), reverse=True)
    
    return filtered, search_terms


@mcp.tool()
def get_headlines(source: str = "all", limit: int = 10) -> str:
    """Get headlines from major news sources.
    
    Args:
        source: News source (all, bbc, reuters, ap, techcrunch, cnn, npr, guardian, nytimes)
        limit: Number of headlines to return (default: 10, max: 50)
    
    Returns:
        JSON string with headlines data
    """
    try:
        limit = min(max(limit, 1), 50)  # Clamp between 1 and 50
        
        if source == "all":
            # Get headlines from all sources
            all_articles = []
            for source_name, feed_url in NEWS_SOURCES.items():
                articles = parse_rss_feed(feed_url, limit=5)  # Get 5 from each source
                for article in articles:
                    article["source_name"] = source_name
                all_articles.extend(articles)
            
            # Sort by publication date (newest first)
            all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
            all_articles = all_articles[:limit]
            
            return json.dumps({
                "articles": all_articles,
                "total": len(all_articles),
                "sources": list(NEWS_SOURCES.keys())
            }, indent=2)
        
        elif source in NEWS_SOURCES:
            # Get headlines from specific source
            articles = parse_rss_feed(NEWS_SOURCES[source], limit)
            for article in articles:
                article["source_name"] = source
            
            return json.dumps({
                "articles": articles,
                "total": len(articles),
                "source": source
            }, indent=2)
        
        else:
            return json.dumps({
                "error": f"Unknown source '{source}'. Available sources: {', '.join(['all'] + list(NEWS_SOURCES.keys()))}"
            }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error fetching headlines: {str(e)}"}, indent=2)

@mcp.tool()
def search_news(query: str, limit: int = 10) -> str:
    """Search for news articles by keyword.
    
    Args:
        query: Search query string
        limit: Number of results to return (default: 10, max: 50)
    
    Returns:
        JSON string with search results
    """
    try:
        if not query.strip():
            return json.dumps({"error": "Query cannot be empty"}, indent=2)
        
        limit = min(max(limit, 1), 50)  # Clamp between 1 and 50
        
        # Search across all sources
        all_articles = []
        for source_name, feed_url in NEWS_SOURCES.items():
            articles = parse_rss_feed(feed_url, limit=10)  # Get more to search through
            for article in articles:
                article["source_name"] = source_name
            all_articles.extend(articles)
        
        # Filter by search query
        filtered_articles, search_terms = search_articles(all_articles, query)
        
        # Limit results
        filtered_articles = filtered_articles[:limit]
        
        return json.dumps({
            "articles": filtered_articles,
            "total": len(filtered_articles),
            "query": query,
            "search_terms_used": search_terms[:10]  # Show first 10 search terms for debugging
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error searching news: {str(e)}"}, indent=2)

@mcp.tool()
def get_category_news(category: str, limit: int = 10) -> str:
    """Get news by category.
    
    Args:
        category: News category (politics, technology, business, sports, health, science, world)
        limit: Number of articles to return (default: 10, max: 50)
    
    Returns:
        JSON string with category news data
    """
    try:
        if category not in CATEGORY_KEYWORDS:
            return json.dumps({
                "error": f"Unknown category '{category}'. Available categories: {', '.join(CATEGORY_KEYWORDS.keys())}"
            }, indent=2)
        
        limit = min(max(limit, 1), 50)  # Clamp between 1 and 50
        
        # Get articles from all sources
        all_articles = []
        for source_name, feed_url in NEWS_SOURCES.items():
            articles = parse_rss_feed(feed_url, limit=10)  # Get more to filter through
            for article in articles:
                article["source_name"] = source_name
            all_articles.extend(articles)
        
        # Filter by category
        filtered_articles = filter_articles_by_category(all_articles, category)
        
        # Sort by publication date (newest first)
        filtered_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
        filtered_articles = filtered_articles[:limit]
        
        return json.dumps({
            "articles": filtered_articles,
            "total": len(filtered_articles),
            "category": category
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error fetching category news: {str(e)}"}, indent=2)

@mcp.tool()
def get_rss_feed(feed_url: str, limit: int = 10) -> str:
    """Get articles from any RSS feed URL.
    
    Args:
        feed_url: RSS feed URL
        limit: Number of articles to return (default: 10, max: 50)
    
    Returns:
        JSON string with RSS feed data
    """
    try:
        if not feed_url.strip():
            return json.dumps({"error": "Feed URL cannot be empty"}, indent=2)
        
        limit = min(max(limit, 1), 50)  # Clamp between 1 and 50
        
        articles = parse_rss_feed(feed_url, limit)
        
        return json.dumps({
            "articles": articles,
            "total": len(articles),
            "feed_url": feed_url
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error fetching RSS feed: {str(e)}"}, indent=2)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        stateless_http=True
    )
