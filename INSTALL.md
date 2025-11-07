# Installation Guide

## Quick Install (Recommended)

### Option 1: Using pipx (macOS/Linux - RECOMMENDED)

The easiest way to install on macOS/Linux systems with externally-managed Python:

```bash
# Install pipx if you don't have it (one-time setup)
brew install pipx  # macOS
# or: python3 -m pip install --user pipx  # Linux

# Navigate to the repository
cd /path/to/crawl4ai_docs_scraper

# Install with pipx (creates isolated environment automatically)
pipx install -e .
```

**Why pipx?**
- ✅ No virtual environment activation needed
- ✅ Works from any directory immediately
- ✅ Avoids PEP 668 externally-managed-environment errors
- ✅ Automatically manages isolated environments
- ✅ Perfect for CLI tools like crawl4ai

### Option 2: Using pip in Virtual Environment

For systems that allow pip install or if you prefer traditional venv:

```bash
# Navigate to the repository
cd /path/to/crawl4ai_docs_scraper

# Install in development mode
pip install -e .
```

This installs the package while keeping it linked to your source code. Any changes you make to the code will be immediately available.

## Usage After Installation

Once installed, you can use the `crawl4ai` command from anywhere:

### Unified CLI (Recommended)

```bash
# Extract single page
crawl4ai single https://docs.example.com/page

# Extract single page to custom directory
crawl4ai single https://docs.example.com/page --output-dir ~/Desktop/docs

# Extract menu links
crawl4ai menu https://docs.example.com

# Crawl multiple URLs (individual files)
crawl4ai split urls.json --output-dir ~/Desktop/my-docs

# Crawl multiple URLs (single consolidated file)
crawl4ai multi urls.txt --output-prefix myproject

# Crawl from sitemap
crawl4ai sitemap https://example.com/sitemap.xml
```

### Individual Commands

You can also use specific crawler commands directly:

```bash
crawl4ai-single https://docs.example.com/page
crawl4ai-menu https://docs.example.com
crawl4ai-split urls.json --output-dir ~/Desktop/docs
crawl4ai-multi urls.txt --output-prefix myproject
crawl4ai-sitemap https://example.com/sitemap.xml
```

## Output Directories

### Default Behavior

- **Scraped content**: `scraped_docs/` (relative to current directory)
- **Menu outputs**: `input_files/` (relative to current directory)

### Custom Output Directories

Use `--output-dir` to save anywhere:

```bash
# Save to Desktop
crawl4ai single https://example.com --output-dir ~/Desktop/my-docs

# Save to absolute path
crawl4ai split urls.json --output-dir /tmp/scraped

# Save to current directory
crawl4ai menu https://example.com --output-dir ./extracted_menus
```

## Uninstall

```bash
pip uninstall crawl4ai-docs-scraper
```

## Alternative: Using Scripts Directly

If you don't want to install the package, you can still use the scripts directly:

```bash
# Make sure you're in the repository directory
cd /path/to/crawl4ai_docs_scraper

# Activate virtual environment
source venv/bin/activate

# Run scripts directly
python single_url_crawler.py https://docs.example.com/page
python menu_crawler.py https://docs.example.com
python split_url_crawler.py urls.json --output-dir ~/Desktop/docs
```

## For AI Agents

If you're using this with AI agents (like Claude Code), after installation, your agent can call:

```bash
crawl4ai split input_files/menu_links.json --output-dir /path/to/save
```

The agent doesn't need to be in the repository directory - it works from anywhere!

## Troubleshooting

### Command not found

If you get "command not found" after installation:

1. Make sure you installed with `pip install -e .`
2. Check that pip's bin directory is in your PATH:
   ```bash
   python -m site --user-base
   ```
3. Add it to your PATH if needed (in ~/.zshrc or ~/.bashrc):
   ```bash
   export PATH="$PATH:$(python -m site --user-base)/bin"
   ```

### Permission errors

If you get permission errors during installation, use:

```bash
pip install -e . --user
```

## Next Steps

Now you're ready to scrape documentation! Try:

```bash
# Test with a simple page
crawl4ai single https://docs.python.org/3/library/os.html --output-dir ~/Desktop/test

# Or follow a complete workflow
crawl4ai menu https://docs.example.com
crawl4ai split input_files/example_menu_links_*.json --output-dir ~/Desktop/example_docs
```
