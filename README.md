# News MCP Server

A FastMCP server that provides access to news headlines and articles from RSS feeds for Poke integration.

## 🚀 Features

- **get_headlines**: Get headlines from major news sources
- **search_news**: Search for news articles by keyword
- **get_category_news**: Get news by category (politics, tech, sports, etc.)
- **get_rss_feed**: Get articles from any RSS feed URL

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python src/server.py
```

## 🚢 Deployment

### Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Steps:**
1. **Fork this repository** (if you haven't already)
2. **Connect your GitHub account to Render** (if you haven't already)
3. **Click the "Deploy to Render" button above** or go to [render.com](https://render.com)
4. **Create a new Web Service:**
   - Connect your forked repository
   - **Name**: `news-mcp`
   - **Environment**: `Python 3`
   - **Plan**: `Free`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/server.py`
5. **Deploy!** (No additional environment variables needed - uses free RSS feeds)

Your server will be available at `https://news-mcp.onrender.com/mcp`

## 🎯 Poke Integration

1. Go to [poke.com/settings/connections](https://poke.com/settings/connections)
2. Add the MCP URL: `https://news-mcp.onrender.com/mcp`
3. Give it a name like "News"
4. Test with: "Tell the subagent to use the News integration's get_headlines tool"

## 🔧 Available Tools

- `get_headlines(source="all", limit=10)`: Get headlines from news sources
- `search_news(query, limit=10)`: Search for news articles by keyword
- `get_category_news(category, limit=10)`: Get news by category
- `get_rss_feed(feed_url, limit=10)`: Get articles from any RSS feed

## 📝 Example Usage

```python
# Get headlines from all sources
get_headlines(source="all", limit=10)

# Get headlines from BBC
get_headlines(source="bbc", limit=5)

# Search for AI news
search_news(query="artificial intelligence", limit=10)

# Get technology news
get_category_news(category="technology", limit=8)

# Get articles from custom RSS feed
get_rss_feed(feed_url="https://example.com/feed.xml", limit=5)
```

## 📰 News Sources

The server includes these major news sources:

- **BBC News**: `bbc`
- **Reuters**: `reuters`
- **Associated Press**: `ap`
- **TechCrunch**: `techcrunch`
- **CNN**: `cnn`
- **NPR**: `npr`
- **The Guardian**: `guardian`
- **New York Times**: `nytimes`

## 🏷️ Categories

Available news categories for filtering:

- `politics`: Government, elections, political news
- `technology`: Tech news, AI, software, startups
- `business`: Economy, markets, finance
- `sports`: Sports news and updates
- `health`: Medical news, health updates
- `science`: Scientific discoveries, research
- `world`: International news, global events

## 📊 Article Data Structure

Each article returned includes:

- `title`: Article headline
- `link`: Direct link to the article
- `summary`: Article summary/description
- `published`: Publication date (ISO format)
- `source`: News source name
- `source_name`: Source identifier
- `author`: Article author (if available)
- `tags`: Article tags/categories

## 🔍 Search Features

- **Keyword Search**: Search across titles, summaries, and tags
- **Category Filtering**: Filter by predefined categories
- **Source Selection**: Get news from specific sources or all sources
- **Custom RSS**: Support for any RSS feed URL
- **Date Sorting**: Articles sorted by publication date (newest first)

## ⚠️ Rate Limits

RSS feeds are generally free and don't have strict rate limits, but:
- The server includes reasonable delays between requests
- Large requests are automatically limited to prevent overload
- Some RSS feeds may have their own rate limiting

## 🧪 Testing

Test the server locally:

```bash
# Test health endpoint
curl http://localhost:8000/

# Test MCP endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

## 📝 Notes

- **No API Keys Required**: Uses free RSS feeds from major news sources
- **Real-time Data**: Gets the latest articles from RSS feeds
- **Multiple Sources**: Aggregates news from 8 major sources
- **Flexible Filtering**: Search by keyword, category, or source
- **RSS Support**: Works with any RSS feed URL
- **Error Handling**: Comprehensive error handling with descriptive messages

