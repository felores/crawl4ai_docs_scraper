# Documentation Menu Crawler

A powerful Python script designed to extract all menu links from documentation websites, with special focus on handling nested menus and dynamic content. Built using the Crawl4AI library for efficient web crawling.

[![Powered by Crawl4AI](https://img.shields.io/badge/Powered%20by-Crawl4AI-blue?style=flat-square)](https://github.com/unclecode/crawl4ai)

## Features

- 🚀 Single-page crawling optimization
- 📑 Automatic nested menu expansion
- 🔄 Handles dynamic content and lazy-loaded elements
- 🎯 Configurable menu selectors
- 💾 Structured JSON output
- 🎨 Colorful terminal feedback
- 🔍 Smart URL processing
- ⚡ Asynchronous execution

## Requirements

- Python 3.7+
- Virtual Environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
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

1. Configure the target URL:
   Open `menu_crawler.py` and modify the `BASE_URL` constant to your target documentation site:
   ```python
   BASE_URL = "https://your-docs-site.com/"
   ```

2. Run the script:
   ```bash
   python menu_crawler.py
   ```

3. Results will be saved in the `scraped_docs` directory with a filename format:
   ```
   {domain}_{path}_menu_links_{timestamp}.json
   ```

## Configuration

### Menu Selectors
The script uses various CSS selectors to identify menu links. You can modify the `MENU_SELECTORS` list in the script:

```python
MENU_SELECTORS = [
    "nav a",                    # General navigation links
    "[role='navigation'] a",    # Role-based navigation
    ".sidebar a",               # Common sidebar class
    "[class*='nav'] a",        # Classes containing 'nav'
    "[class*='menu'] a",       # Classes containing 'menu'
]
```

### Browser Configuration
You can adjust browser settings by modifying the `browser_config` in the `DocsMenuCrawler` class:

```python
self.browser_config = BrowserConfig(
    headless=True,
    viewport_width=1920,
    viewport_height=1080
)
```

## Output Format

The script generates a JSON file with the following structure:

```json
{
    "start_url": "https://your-docs-site.com/",
    "total_links_found": 42,
    "menu_links": [
        "https://your-docs-site.com/page1",
        "https://your-docs-site.com/page2",
        ...
    ]
}
```

## Error Handling

The script includes comprehensive error handling with colored terminal output:
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