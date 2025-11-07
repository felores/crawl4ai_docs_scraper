# Agent's Quick Reference Guide

**Purpose**: Extract clean, AI-ready documentation from websites using crawl4ai CLI.

---

## Decision Tree: Which Command to Use?

```text
Need documentation?
│
├─ Single page only?
│  └─ Use: crawl4ai single <url>
│
├─ Don't know what pages exist?
│  └─ Use: crawl4ai menu <url>  →  Then use split or multi
│
├─ Have list of URLs?
│  ├─ Want individual files? (easier to manage, version control)
│  │  └─ Use: crawl4ai split <file>
│  └─ Want one combined file? (LLM context, offline reading)
│     └─ Use: crawl4ai multi <file>
│
└─ Site has sitemap.xml?
   └─ Use: crawl4ai sitemap <url>
```

---

## Quick Command Reference

### 1. Single Page Extraction
```bash
crawl4ai single <URL> [--output-dir DIR]
```
**Use when**: You need just one specific page
**Output**: One .md file in scraped_docs/
**Example**: `crawl4ai single https://docs.python.org/3/library/os.html`

---

### 2. Menu Discovery
```bash
crawl4ai menu <URL> [--output-dir DIR]
```
**Use when**: You need to discover all documentation pages
**Output**: JSON file in input_files/ with all menu links
**Example**: `crawl4ai menu https://docs.openai.com`
**Next step**: Feed the JSON to split or multi

---

### 3. Batch Individual Files
```bash
crawl4ai split <FILE> [--output-prefix NAME] [--output-dir DIR]
```
**Use when**: You want separate .md files for each page
**Input**: urls.txt (one per line) OR menu_links.json
**Output**: Directory with individual files: `project_timestamp/page1.md, page2.md...`
**Example**: `crawl4ai split input_files/menu_links.json --output-prefix my-docs`

**Input File Formats**:
```txt
# urls.txt
https://example.com/page1
https://example.com/page2
```
```json
// menu_links.json
{"menu_links": ["url1", "url2"]}
```

---

### 4. Batch Consolidated File
```bash
crawl4ai multi <FILE> [--output-prefix NAME] [--output-dir DIR]
```
**Use when**: You want ALL pages in one big file
**Input**: Same as split (txt or json)
**Output**: Single .md file with all pages separated by `---`
**Example**: `crawl4ai multi urls.txt --output-prefix complete-docs`

---

### 5. Sitemap Crawling
```bash
crawl4ai sitemap <SITEMAP_URL> [--max-depth N] [--patterns P1 P2...] [--output-dir DIR]
```
**Use when**: Site has sitemap.xml and you want comprehensive coverage
**Output**: Consolidated .md file
**Example**: `crawl4ai sitemap https://docs.example.com/sitemap.xml --patterns "/api/*"`

---

## Common Workflows

### Workflow 1: Complete Documentation Scrape
```bash
# Step 1: Discover all pages
crawl4ai menu https://docs.example.com

# Step 2: Review output (look in input_files/)
# You'll see: example_docs_menu_links_TIMESTAMP.json

# Step 3: Crawl all pages as individual files
crawl4ai split input_files/example_docs_menu_links_*.json --output-prefix example-docs
```

### Workflow 2: Quick API Reference
```bash
# One command to get everything
crawl4ai sitemap https://api.example.com/sitemap.xml --patterns "/api/reference/*"
```

### Workflow 3: Specific Pages Only
```bash
# Create urls.txt with your specific URLs
echo "https://docs.example.com/intro" > urls.txt
echo "https://docs.example.com/api" >> urls.txt

# Crawl them
crawl4ai split urls.txt --output-prefix custom-selection
```

---

## Output Control

### Default Locations
- `scraped_docs/` - All documentation files
- `input_files/` - Menu JSON files

### Custom Locations
```bash
# Save to Desktop
crawl4ai single <url> --output-dir ~/Desktop/docs

# Save to project folder
crawl4ai menu <url> --output-dir ./project/menus

# Absolute path
crawl4ai split urls.json --output-dir /Users/name/Documents/scraped
```

---

## Pro Tips for Agents

### 1. Always Check What Exists First
```bash
# Don't crawl blindly - discover structure first
crawl4ai menu <url>  # Get the lay of the land
```

### 2. Use Meaningful Prefixes
```bash
# Bad
crawl4ai split urls.json

# Good
crawl4ai split urls.json --output-prefix stripe-api-docs
```

### 3. Batch Size Recommendations
- **1-20 URLs**: Fast, no issues
- **20-50 URLs**: Good performance, split mode recommended
- **50+ URLs**: Use split mode, consider batching into multiple runs

### 4. Error Recovery Pattern
```bash
# If crawl fails mid-way:
# 1. Check which files were created
ls scraped_docs/project_*/

# 2. Remove completed URLs from input file
# 3. Re-run with remaining URLs
```

---

## Troubleshooting Guide

### "No URLs found"
**Cause**: Empty or invalid input file
**Fix**: Check file format (see Input File Formats above)

### "Permission denied"
**Cause**: Can't write to output directory
**Fix**: Use `--output-dir` to specify writable location

### Network timeouts
**Cause**: Site is slow or blocking requests
**Fix**: Reduce batch size, try again later

### Menu extraction returns 0 links
**Cause**: Site uses different navigation structure
**Fix**: Try sitemap instead: `crawl4ai sitemap <sitemap_url>`

---

## Quick Checks

### Verify Installation
```bash
crawl4ai --help          # Should show all commands
crawl4ai single --help   # Should show single command options
```

### Test Run
```bash
# Simple test that should always work
crawl4ai single https://docs.python.org/3/library/os.html --output-dir /tmp/test
```

---

## Output File Patterns

### Single Page
```text
scraped_docs/
  └── python_docs_library_os_20250106_123000.md
```

### Split Mode
```text
scraped_docs/
  └── my-project_20250106_123000/
      ├── example_docs_intro.md
      ├── example_docs_api.md
      └── example_docs_guide.md
```

### Multi/Sitemap Mode
```text
scraped_docs/
  └── my-project_20250106_123000.md    # One big file
```

### Menu Output
```text
input_files/
  └── example_docs_menu_links_20250106_123000.json
```

---

## When to Use What: Quick Summary

| Scenario | Command | Output |
|----------|---------|--------|
| One specific page | `crawl4ai single` | 1 .md file |
| Discover all pages | `crawl4ai menu` | 1 .json file |
| Multiple pages, separate files | `crawl4ai split` | Directory of .md files |
| Multiple pages, one file | `crawl4ai multi` | 1 big .md file |
| Full site coverage | `crawl4ai sitemap` | 1 big .md file |

---

## Advanced Patterns

### Filtered Sitemap Crawl
```bash
# Only crawl docs and API sections
crawl4ai sitemap https://example.com/sitemap.xml \
  --patterns "/docs/*" "/api/*" \
  --max-depth 5
```

### Custom Organization
```bash
# Organize by project
mkdir -p ~/Documentation/Projects/stripe
crawl4ai split stripe_urls.json \
  --output-prefix stripe-api \
  --output-dir ~/Documentation/Projects/stripe
```

### Incremental Updates
```bash
# Day 1: Get initial docs
crawl4ai menu https://docs.example.com
crawl4ai split input_files/menu_*.json --output-prefix docs-v1

# Day 30: Get updates
crawl4ai menu https://docs.example.com
crawl4ai split input_files/menu_*.json --output-prefix docs-v2

# Compare: diff docs-v1/ docs-v2/
```

---

## Performance Tips

1. **Use menu extraction first** - Prevents crawling unnecessary pages
2. **Split mode for large batches** - Easier to manage than one huge file
3. **Meaningful prefixes** - Makes finding output easier
4. **Custom output dirs** - Keep organized, avoid cluttering scraped_docs/
5. **Sitemap patterns** - Filter before crawling to save time

---

## Error Messages Decoded

| Message | Meaning | Solution |
|---------|---------|----------|
| "No URLs found in input file" | Empty/invalid input | Check file format |
| "Permission denied writing" | No write access | Use different --output-dir |
| "Connection timeout" | Network issue | Check connection, try again |
| "Invalid URL format" | URL missing http:// | Add http:// or https:// |
| "No menu links found" | Menu extraction failed | Try sitemap instead |

---

## Remember

- ✅ **DO**: Extract menu first for comprehensive crawls
- ✅ **DO**: Use split mode for 10+ pages
- ✅ **DO**: Specify output-dir for better organization
- ✅ **DO**: Use meaningful prefixes

- ❌ **DON'T**: Blindly crawl hundreds of URLs without checking
- ❌ **DON'T**: Use multi mode for 50+ pages (file too large)
- ❌ **DON'T**: Forget to check input_files/ for menu JSON
- ❌ **DON'T**: Run same crawl multiple times (check existing output)

---

**Quick Help**: `crawl4ai <command> --help` for any command
