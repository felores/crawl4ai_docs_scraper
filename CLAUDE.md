# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based documentation scraping toolkit that uses Crawl4AI to extract clean, structured content from documentation websites. The toolkit provides multiple crawling strategies optimized for different documentation formats and structures.

## Development Environment Setup

### Virtual Environment
The project uses a Python virtual environment for dependency isolation:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Core Dependencies
- `crawl4ai`: Main web crawling library with content filtering
- `aiohttp`: Async HTTP client for concurrent requests
- `termcolor`: Colored terminal output for user feedback
- `playwright`: Browser automation (installed via Crawl4AI)

## Architecture & Components

### Core Crawling Modules

1. **single_url_crawler.py**: Extracts content from individual documentation pages
   - Generates clean Markdown output
   - Smart filename generation from URLs
   - Configurable content selectors

2. **multi_url_crawler.py**: Processes multiple URLs in parallel
   - Accepts both text files (.txt) and JSON files (.json) as input
   - Generates individual Markdown files per page
   - Supports custom output prefixes via `--output-prefix`

3. **menu_crawler.py**: Extracts navigation menu structure
   - Outputs structured JSON format to `input_files/` directory
   - Comprehensive CSS selectors for modern documentation frameworks
   - Handles dynamic menus and nested navigation

4. **sitemap_crawler.py**: Discovers and crawls via sitemap.xml
   - Supports recursive sitemap parsing
   - URL pattern filtering via `--patterns`
   - Configurable crawl depth via `--max-depth`

### Directory Structure

```
crawl4ai_docs_scraper/
├── input_files/           # Input URL files and menu crawler output
├── scraped_docs/         # Generated Markdown documentation
├── *.py                  # Crawler modules
├── requirements.txt      # Python dependencies
└── venv/                # Virtual environment
```

### Data Flow

1. **Menu Discovery**: Use `menu_crawler.py` to extract all documentation links
2. **Batch Processing**: Feed menu crawler JSON output to `multi_url_crawler.py`
3. **Content Generation**: Produces clean Markdown files in `scraped_docs/`

## Common Development Tasks

### Running Crawlers

All crawlers use argparse for command-line arguments. URLs are passed as positional arguments (no flags):

```bash
# Single page crawling
python single_url_crawler.py https://docs.example.com/page

# Menu extraction (saves to input_files/)
python menu_crawler.py https://docs.example.com

# Multi-page crawling from menu output
python multi_url_crawler.py input_files/menu_links.json

# Multi-page with custom prefix
python multi_url_crawler.py input_files/urls.txt --output-prefix custom_name

# Sitemap-based crawling
python sitemap_crawler.py https://docs.example.com/sitemap.xml --max-depth 5
```

### File Formats

**Input Files**:
- Text files: One URL per line
- JSON files: `{"menu_links": ["url1", "url2", ...]}`

**Output Files**:
- Markdown files with timestamp-based naming
- JSON menu structure files

## Code Patterns

### Async Architecture
All crawlers use `asyncio` for concurrent processing with shared browser sessions for performance optimization.

### Error Handling
Comprehensive error handling with colored terminal output using `termcolor`:
- Green: Success messages
- Cyan: Processing status  
- Yellow: Warnings
- Red: Error messages

### URL Processing
Smart URL-to-filename conversion preserves domain structure and path information for organized output naming.

### Content Extraction
Uses Crawl4AI's content filtering strategies:
- `PruningContentFilter`: Removes navigation, ads, and irrelevant content
- `DefaultMarkdownGenerator`: Preserves code blocks and technical formatting

## Development Commands

### Environment Setup
```bash
# Always activate virtual environment before development
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify installation
python -c "import crawl4ai; print('Crawl4AI available')"
```

### Running Individual Crawlers
All scripts use argparse and can be executed directly:
```bash
# Check crawler help
python single_url_crawler.py --help
python menu_crawler.py --help
python multi_url_crawler.py --help
python sitemap_crawler.py --help
```

### Development Testing
No formal test suite exists. To verify functionality:
1. Test on small documentation sites first
2. Verify output quality in `scraped_docs/` and `input_files/`
3. Check terminal output for colored error/success messages

## Performance Considerations

- Crawlers share browser sessions for efficiency
- Async processing enables concurrent URL processing
- Content filtering reduces output size and improves quality
- Virtual environment isolation prevents dependency conflicts