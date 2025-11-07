# Crawl4AI Documentation Scraper

Keep your dependency documentation lean, current, and AI-ready. This toolkit helps you extract clean, focused documentation from any framework or library website, perfect for both human readers and LLM consumption.

## Why This Tool?

In today's fast-paced development environment, you need:
- 📚 Quick access to dependency documentation without the bloat
- 🤖 Documentation in a format that's ready for RAG systems and LLMs
- 🎯 Focused content without navigation elements, ads, or irrelevant sections
- ⚡ Fast, efficient way to keep documentation up-to-date
- 🧹 Clean Markdown output for easy integration with documentation tools

Traditional web scraping often gives you everything - including navigation menus, footers, ads, and other noise. This toolkit is specifically designed to extract only what matters: the actual documentation content.

### Key Benefits

1. **Clean Documentation Output**
   - Markdown format for content-focused documentation
   - JSON format for structured menu data
   - Perfect for documentation sites, wikis, and knowledge bases
   - Ideal format for LLM training and RAG systems

2. **Smart Content Extraction**
   - Automatically identifies main content areas
   - Strips away navigation, ads, and irrelevant sections
   - Preserves code blocks and technical formatting
   - Maintains proper Markdown structure

3. **Flexible Crawling Strategies**
   - Single page for quick reference docs
   - Multi-page consolidated for comprehensive library documentation
   - Split files for individual page management
   - Sitemap-based for complete framework coverage
   - Menu-based for structured documentation hierarchies

4. **LLM and RAG Ready**
   - Clean Markdown text suitable for embeddings
   - Preserved code blocks for technical accuracy
   - Structured menu data in JSON format
   - Consistent formatting for reliable processing

A comprehensive Python toolkit for scraping documentation websites using different crawling strategies. Built using the Crawl4AI library for efficient web crawling.

[![Powered by Crawl4AI](https://img.shields.io/badge/Powered%20by-Crawl4AI-blue?style=flat-square)](https://github.com/unclecode/crawl4ai)

## Features

### Core Features
- 🚀 Multiple crawling strategies
- 📦 **Install globally** - use from any directory
- 🎯 **Custom output directories** - save anywhere with `--output-dir`
- 🔧 **Unified CLI** - single `crawl4ai` command for all modes
- 🤖 **MCP Server** - AI agents can use tools directly via Model Context Protocol
- 📑 Automatic nested menu expansion
- 🔄 Handles dynamic content and lazy-loaded elements
- 🎯 Configurable selectors
- 📝 Clean Markdown output for documentation
- 📊 JSON output for menu structure
- 🎨 Colorful terminal feedback
- 🔍 Smart URL processing
- ⚡ Asynchronous execution

### Available Crawlers
1. **Single URL Crawler** (`single_url_crawler.py`)
   - Extracts content from a single documentation page
   - Outputs clean Markdown format
   - Perfect for targeted content extraction
   - Configurable content selectors

2. **Multi URL Crawler** (`multi_url_crawler.py`)
   - Processes multiple URLs in parallel
   - Generates a single consolidated Markdown file
   - All pages combined with separators
   - Shared browser session for better performance

3. **Split URL Crawler** (`split_url_crawler.py`) ⭐ NEW
   - Processes multiple URLs from a file
   - Generates individual Markdown files per URL
   - Organized in subdirectories by project
   - Perfect for maintaining separate documentation files
   - Supports custom output prefixes

4. **Sitemap Crawler** (`sitemap_crawler.py`)
   - Automatically discovers and crawls sitemap.xml
   - Creates Markdown files for each page
   - Supports recursive sitemap parsing
   - Handles gzipped sitemaps

5. **Menu Crawler** (`menu_crawler.py`)
   - Extracts all menu links from documentation
   - Outputs structured JSON format
   - Handles nested and dynamic menus
   - Smart menu expansion

## Requirements

- Python 3.7+
- Virtual Environment (recommended)

## Installation

### Option 1: Install as Package (Recommended)

Install globally to use the unified CLI from anywhere:

```bash
# Clone and install
git clone https://github.com/felores/crawl4ai_docs_scraper.git
cd crawl4ai_docs_scraper
pip install -e .
```

**After installation, you get:**
- ✅ `crawl4ai` - Unified command for all crawling modes
- ✅ Individual commands: `crawl4ai-single`, `crawl4ai-menu`, `crawl4ai-split`, etc.
- ✅ Works from any directory on your system

**Documentation:**
- 📖 [INSTALL.md](INSTALL.md) - Complete installation guide
- 🤖 [AGENT_GUIDE.md](AGENT_GUIDE.md) - Quick reference for AI agents
- 🔌 [MCP_SERVER.md](MCP_SERVER.md) - MCP server setup and usage

### Option 2: Local Development

Use scripts directly without installation:

```bash
# Clone the repository
git clone https://github.com/felores/crawl4ai_docs_scraper.git
cd crawl4ai_docs_scraper

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Unified CLI (After Installation)

If you installed as a package, use the unified `crawl4ai` command:

```bash
# Extract single page
crawl4ai single https://docs.example.com/page

# Save to custom directory
crawl4ai single https://docs.example.com/page --output-dir ~/Desktop/docs

# Extract menu links
crawl4ai menu https://docs.example.com

# Crawl multiple URLs (individual files)
crawl4ai split urls.json --output-dir ~/Desktop/my-docs

# Crawl multiple URLs (consolidated file)
crawl4ai multi urls.txt --output-prefix myproject

# Crawl from sitemap
crawl4ai sitemap https://example.com/sitemap.xml
```

### Direct Script Usage

If using scripts directly (without installation):

### 1. Single URL Crawler

```bash
python single_url_crawler.py https://docs.example.com/page

# Save to custom directory
python single_url_crawler.py https://docs.example.com/page --output-dir ~/Desktop/docs
```

Arguments:
- `url`: Target documentation URL (required)
- `--output-dir`: Directory to save output files (default: `scraped_docs`)

Output format (Markdown):
```markdown
# Page Title

## Section 1
Content with preserved formatting, including:
- Lists
- Links
- Tables

### Code Examples
```python
def example():
    return "Code blocks are preserved"
```

### 2. Multi URL Crawler

```bash
# Using a text file with URLs
python multi_url_crawler.py urls.txt

# Using JSON output from menu crawler
python multi_url_crawler.py menu_links.json

# Using custom output prefix and directory
python multi_url_crawler.py menu_links.json --output-prefix custom_name --output-dir ~/Desktop/docs
```

Arguments:
- `urls_file`: Path to file containing URLs (required)
  - Can be .txt with one URL per line
  - Or .json from menu crawler output
- `--output-prefix`: Custom prefix for output markdown file (optional)
- `--output-dir`: Directory to save output files (default: `scraped_docs`)

Note: Use quotes only if your file path contains spaces.

Output filename format:
- Without `--output-prefix`: `domain_path_docs_content_timestamp.md` (e.g., `cloudflare_agents_docs_content_20240323_223656.md`)
- With `--output-prefix`: `custom_prefix_docs_content_timestamp.md` (e.g., `custom_name_docs_content_20240323_223656.md`)

The crawler accepts two types of input files:
1. Text file with one URL per line:
```text
https://docs.example.com/page1
https://docs.example.com/page2
https://docs.example.com/page3
```

2. JSON file (compatible with menu crawler output):
```json
{
    "menu_links": [
        "https://docs.example.com/page1",
        "https://docs.example.com/page2"
    ]
}
```

### 3. Split URL Crawler

```bash
# Using a text file with URLs
python split_url_crawler.py urls.txt

# Using JSON output from menu crawler
python split_url_crawler.py menu_links.json

# Using custom output prefix and base directory
python split_url_crawler.py menu_links.json --output-prefix my-project --output-dir ~/Desktop/docs
```

Arguments:
- `urls_file`: Path to file containing URLs (required)
  - Can be .txt with one URL per line
  - Or .json from menu crawler output
- `--output-prefix`: Custom prefix for output directory name (optional)
- `--output-dir`: Base directory to save output files (default: `scraped_docs`)

**Key Differences from Multi URL Crawler:**
- Creates **individual .md files** for each URL (not a single consolidated file)
- Files organized in **project subdirectories**: `scraped_docs/{project}_{timestamp}/`
- Filenames based on URL structure (e.g., `literalai_docs_authentication.md`)
- Perfect for maintaining separate documentation files

**Output Structure:**
```text
scraped_docs/
  └── literalai_20250106_120000/
      ├── literalai_docs_getting_started.md
      ├── literalai_docs_api_authentication.md
      └── literalai_docs_advanced_features.md
```

**When to Use:**
- Use **split_url_crawler.py** when you want individual files for each page (easier to navigate, version control friendly)
- Use **multi_url_crawler.py** when you want a single consolidated document (better for LLM context or offline reading)

### 4. Sitemap Crawler

```bash
python sitemap_crawler.py https://docs.example.com/sitemap.xml

# With custom directory and filters
python sitemap_crawler.py https://docs.example.com/sitemap.xml --max-depth 5 --patterns "/docs/*" --output-dir ~/Desktop/docs
```

Arguments:
- `sitemap_url`: URL of sitemap.xml (required)
- `--max-depth`: Maximum sitemap recursion depth (default: 10)
- `--patterns`: URL patterns to include (e.g., "/docs/*" "/guide/*")
- `--output-dir`: Directory to save output files (default: `scraped_docs`)

### 5. Menu Crawler

```bash
python menu_crawler.py https://docs.example.com

# Save to custom directory
python menu_crawler.py https://docs.example.com --output-dir ~/Desktop/menu_data
```

Arguments:
- `url`: Documentation site URL (required)
- `--selectors`: Custom CSS selectors for menu items (optional)
- `--output-dir`: Directory to save output files (default: `input_files`)

The menu crawler now saves its output to the `input_files` directory, making it ready for immediate use with the multi-url crawler. The output JSON has this format:
```json
{
    "start_url": "https://docs.example.com/",
    "total_links_found": 42,
    "menu_links": [
        "https://docs.example.com/page1",
        "https://docs.example.com/page2"
    ]
}
```

After running the menu crawler, you'll get a command to run the multi-url crawler with the generated file.

## MCP Server for AI Agents

The toolkit includes a **Model Context Protocol (MCP) server** that allows AI agents like Claude to use the crawling tools directly.

### Quick Setup

1. Install MCP dependencies:
```bash
pip install mcp
```

2. Configure in Claude Desktop (see [MCP_SERVER.md](MCP_SERVER.md) for details):
```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "python",
      "args": ["/absolute/path/to/crawl4ai_docs_scraper/crawl4ai_mcp.py"]
    }
  }
}
```

### Available MCP Tools

Once configured, AI agents can use these tools:

- `crawl4ai_single_page` - Extract content from a single URL
- `crawl4ai_extract_menu` - Extract all menu links from a site
- `crawl4ai_batch_urls_split` - Crawl multiple URLs into individual files
- `crawl4ai_batch_urls_consolidated` - Crawl multiple URLs into one file
- `crawl4ai_from_sitemap` - Crawl from sitemap.xml

See [MCP_SERVER.md](MCP_SERVER.md) for complete documentation and examples.

## Directory Structure

```bash
crawl4ai_docs_scraper/
├── input_files/              # Input files for URL processing
│   ├── urls.txt             # Text file with URLs
│   └── menu_links.json      # JSON output from menu crawler
├── scraped_docs/            # Output directory for markdown files
│   ├── docs_timestamp.md    # Single consolidated file (multi_url_crawler)
│   └── project_timestamp/   # Subdirectory with individual files (split_url_crawler)
│       ├── page1.md
│       ├── page2.md
│       └── page3.md
├── single_url_crawler.py
├── multi_url_crawler.py
├── split_url_crawler.py
├── sitemap_crawler.py
├── menu_crawler.py
└── requirements.txt
```

## Error Handling

All crawlers include comprehensive error handling with colored terminal output:
- 🟢 Green: Success messages
- 🔵 Cyan: Processing status
- 🟡 Yellow: Warnings
- 🔴 Red: Error messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Attribution

This project uses [Crawl4AI](https://github.com/unclecode/crawl4ai) for web data extraction.

## Acknowledgments

- Built with [Crawl4AI](https://github.com/unclecode/crawl4ai)
- Uses [termcolor](https://pypi.org/project/termcolor/) for colorful terminal output
