# Crawl4AI MCP Server

## Overview

The Crawl4AI MCP (Model Context Protocol) server enables AI agents like Claude to directly use the documentation scraping tools through a standardized interface. This provides a seamless way for AI assistants to extract clean, structured documentation from any website.

## Installation

### Prerequisites

1. Install the crawl4ai package:
```bash
cd /path/to/crawl4ai_docs_scraper
pip install -e .
```

2. Install MCP Python SDK:
```bash
pip install mcp
```

### Configure in Claude Desktop

Add this to your Claude Desktop MCP settings file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "python",
      "args": [
        "/absolute/path/to/crawl4ai_docs_scraper/crawl4ai_mcp.py"
      ]
    }
  }
}
```

**Important**: Replace `/absolute/path/to/` with the actual absolute path to your repository.

### Verify Installation

After adding the configuration:

1. Restart Claude Desktop
2. Look for the 🔌 icon in the bottom right
3. Click it to see available MCP servers
4. You should see "crawl4ai_mcp" listed with 5 tools

## Available Tools

### 1. crawl4ai_single_page

Extract clean documentation from a single web page.

**Parameters:**
- `url` (required): Target documentation URL
- `output_dir` (optional): Where to save output files
- `response_format` (optional): "markdown" or "json"

**Example:**
```python
crawl4ai_single_page(
    url="https://docs.python.org/3/library/os.html",
    output_dir="~/Desktop/docs"
)
```

**Use when:**
- You need content from a specific documentation page
- Quick extraction of a single article or guide
- Testing before bulk scraping

---

### 2. crawl4ai_extract_menu

Extract all navigation menu links from a documentation site.

**Parameters:**
- `url` (required): Documentation site homepage URL
- `output_dir` (optional): Where to save menu JSON file
- `response_format` (optional): "markdown" or "json"

**Example:**
```python
crawl4ai_extract_menu(
    url="https://docs.openai.com",
    output_dir="~/Desktop/menus"
)
```

**Use when:**
- Starting a comprehensive documentation scrape
- You want to discover all available documentation pages
- Building a complete site map

**Output:** JSON file with all discovered menu links, ready for batch crawling

---

### 3. crawl4ai_batch_urls_split

Crawl multiple URLs and save each as an individual Markdown file.

**Parameters:**
- `urls` (required): List of URLs to crawl (1-100)
- `output_prefix` (optional): Custom prefix for output directory
- `output_dir` (optional): Base directory for output
- `response_format` (optional): "markdown" or "json"

**Example:**
```python
crawl4ai_batch_urls_split(
    urls=[
        "https://docs.example.com/intro",
        "https://docs.example.com/api",
        "https://docs.example.com/guide"
    ],
    output_prefix="example-docs",
    output_dir="~/Desktop/scraped"
)
```

**Use when:**
- You want individual files for each documentation page
- Version control friendly output needed
- Easier to update individual pages later

**Output:** Directory with individual .md files per URL

---

### 4. crawl4ai_batch_urls_consolidated

Crawl multiple URLs and combine into a single Markdown file.

**Parameters:**
- `urls` (required): List of URLs to crawl (1-100)
- `output_prefix` (optional): Custom prefix for output filename
- `output_dir` (optional): Directory for output
- `response_format` (optional): "markdown" or "json"

**Example:**
```python
crawl4ai_batch_urls_consolidated(
    urls=[
        "https://docs.example.com/intro",
        "https://docs.example.com/api"
    ],
    output_prefix="complete-docs"
)
```

**Use when:**
- You want all documentation in one file
- Building LLM context or RAG system
- Offline documentation reading

**Output:** Single large Markdown file with all pages

---

### 5. crawl4ai_from_sitemap

Discover and crawl all documentation pages from sitemap.xml.

**Parameters:**
- `sitemap_url` (required): URL to sitemap.xml file
- `max_depth` (optional): Maximum recursion depth (default: 10)
- `patterns` (optional): URL patterns to include (e.g., ["/docs/*"])
- `output_dir` (optional): Directory for output
- `response_format` (optional): "markdown" or "json"

**Example:**
```python
crawl4ai_from_sitemap(
    sitemap_url="https://docs.example.com/sitemap.xml",
    patterns=["/docs/*", "/api/*"],
    max_depth=5
)
```

**Use when:**
- Site has a well-maintained sitemap
- You want comprehensive coverage
- Need to filter by URL patterns

**Output:** Single consolidated Markdown file with all discovered pages

---

## Common Workflows

### Workflow 1: Complete Documentation Extraction

```text
1. Extract menu links
   crawl4ai_extract_menu(url="https://docs.example.com")

2. Review the extracted URLs
   (Check the output JSON file)

3. Crawl all pages as individual files
   crawl4ai_batch_urls_split(
       urls=[list of URLs from step 1],
       output_prefix="example-docs"
   )
```

### Workflow 2: Quick API Documentation

```text
1. Crawl from sitemap with filtering
   crawl4ai_from_sitemap(
       sitemap_url="https://api.example.com/sitemap.xml",
       patterns=["/api/reference/*"]
   )
```

### Workflow 3: Single Page Quick Extract

```text
1. Get specific page
   crawl4ai_single_page(
       url="https://docs.example.com/specific-guide"
   )
```

## Output Locations

By default, outputs are saved relative to your **current working directory** when Claude runs the tool:

- **Documentation files**: `./scraped_docs/`
- **Menu JSON files**: `./input_files/`

You can override these with the `output_dir` parameter to save anywhere on your system.

## Troubleshooting

### MCP Server Not Showing Up

1. Check the config file path is correct
2. Ensure the absolute path to `crawl4ai_mcp.py` is correct
3. Restart Claude Desktop completely
4. Check for errors in Claude's logs

### Tool Execution Errors

Common issues and solutions:

**"Permission denied"**
- Specify a different `output_dir` with write permissions
- Ensure the directory exists or can be created

**"No URLs found"**
- Verify the URL is accessible
- Check your internet connection
- Try menu extraction if sitemap is empty

**"Invalid URL"**
- Ensure URL starts with `http://` or `https://`
- Check for typos in the URL

### Network Issues

If you encounter connection timeouts:
- Check your internet connection
- Try again later (site might be down)
- Reduce the number of URLs in batch operations

## Performance Tips

1. **Batch Size**: Keep batch operations under 50 URLs for best performance
2. **Menu First**: Always extract menu links before batch crawling
3. **Patterns**: Use sitemap patterns to reduce unnecessary crawling
4. **Split vs Consolidated**: Use split mode for large batches (easier to handle)

## Advanced Usage

### Custom Output Locations

Save to any directory on your system:

```python
crawl4ai_single_page(
    url="https://docs.example.com",
    output_dir="/Users/yourname/Documents/my-docs"
)
```

### Filtering Sitemap Results

Only crawl specific sections:

```python
crawl4ai_from_sitemap(
    sitemap_url="https://docs.example.com/sitemap.xml",
    patterns=["/api/v2/*", "/guides/*"],
    max_depth=3
)
```

## Security Notes

- The MCP server only performs read operations (web crawling)
- It writes files to locations you specify
- No sensitive data is transmitted or stored
- All network requests go directly to target URLs (no proxy)

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [INSTALL.md](INSTALL.md) for installation help
- Report bugs at https://github.com/felores/crawl4ai_docs_scraper/issues
