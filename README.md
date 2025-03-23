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
   - Multi-page for comprehensive library documentation
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
   - Generates individual Markdown files per page
   - Efficient batch processing
   - Shared browser session for better performance

3. **Sitemap Crawler** (`sitemap_crawler.py`)
   - Automatically discovers and crawls sitemap.xml
   - Creates Markdown files for each page
   - Supports recursive sitemap parsing
   - Handles gzipped sitemaps

4. **Menu Crawler** (`menu_crawler.py`)
   - Extracts all menu links from documentation
   - Outputs structured JSON format
   - Handles nested and dynamic menus
   - Smart menu expansion

## Requirements

- Python 3.7+
- Virtual Environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/felores/crawl4ai_docs_scraper.git
cd crawl4ai_docs_scraper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Single URL Crawler

```bash
python single_url_crawler.py --url "https://docs.example.com/page"
```

Options:
- `--url`: Target documentation URL
- `--selectors`: Custom CSS selectors (optional)
- `--output`: Custom output path (optional)

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
python multi_url_crawler.py --urls urls.txt
```

Options:
- `--urls`: Path to text file containing URLs (one per line)
- `--concurrent`: Number of concurrent crawls (default: 5)
- `--output-dir`: Custom output directory (optional)

Example urls.txt:
```text
https://docs.example.com/page1
https://docs.example.com/page2
https://docs.example.com/page3
```

### 3. Sitemap Crawler

```bash
python sitemap_crawler.py --domain "https://docs.example.com"
```

Options:
- `--domain`: Root domain to crawl
- `--max-depth`: Maximum sitemap recursion depth (optional)
- `--patterns`: URL patterns to include (optional)

### 4. Menu Crawler

```bash
python menu_crawler.py --url "https://docs.example.com"
```

Options:
- `--url`: Documentation site URL
- `--selectors`: Custom menu selectors (optional)

Output format (JSON):
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

## Output Directory Structure

```
scraped_docs/
├── single/
│   └── domain_path_timestamp.md
├── multi/
│   └── batch_timestamp/
│       ├── page1.md
│       ├── page2.md
│       └── summary.json
├── sitemap/
│   └── domain_timestamp/
│       ├── urls.json
│       └── pages/
│           ├── page1.md
│           └── page2.md
└── menu/
    └── domain_menu_links_timestamp.json
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