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
1. **Click the "Deploy to Render" button above** or go to [render.com](https://render.com)
2. **Connect your GitHub account to Render** (if you haven't already)
3. **Create a new Web Service:**
   - Connect this repository
   - **Name**: `news-mcp`
   - **Environment**: `Python 3`
   - **Plan**: `Free`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/server.py`
4. **Deploy!** (No additional environment variables needed - uses free RSS feeds)

> Note: On Render's free tier, services go idle after ~15 minutes of inactivity and may require a manual "Deploy" to wake or to pick up the latest commit. Unlike Vercel, pushes do not auto-deploy by default.

Your server will be available at `https://news-mcp.onrender.com/mcp`

## 🎯 Poke Integration

1. Go to [poke.com/settings/connections](https://poke.com/settings/connections)
2. Add the MCP URL: `https://news-mcp.onrender.com/mcp`
3. Give it a name like "News"
4. Try: "Can you use the News MCP to get headlines?"

## References

- Based on the Interaction MCP server template: [MCP Server Template](https://github.com/InteractionCo/mcp-server-template/tree/main)
- Discovered via Interaction’s HackMIT challenge: [Interaction HackMIT Challenge](https://interaction.co/HackMIT)

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
get_category_news(category="technology", limit=10)

# Read a specific RSS feed
get_rss_feed(
    feed_url="https://feeds.bbci.co.uk/news/technology/rss.xml",
    limit=5,
)
```

