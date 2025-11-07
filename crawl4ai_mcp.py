#!/usr/bin/env python3
"""
MCP Server for Crawl4AI Documentation Scraper.

This server provides tools to extract clean, AI-ready documentation from websites
using various crawling strategies. Perfect for building RAG systems and LLM training data.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pathlib import Path
import asyncio
import json
import subprocess
import sys
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP, Context

# Initialize the MCP server
mcp = FastMCP("crawl4ai_mcp")

# Constants
CHARACTER_LIMIT = 25000  # Maximum response size in characters
DEFAULT_OUTPUT_DIR = "scraped_docs"
DEFAULT_INPUT_DIR = "input_files"

# Get the directory where the MCP server is located (same as crawlers)
CRAWLER_DIR = Path(__file__).parent.resolve()

# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"

class CrawlerMode(str, Enum):
    """Available crawler modes."""
    SINGLE = "single"
    MENU = "menu"
    MULTI = "multi"
    SPLIT = "split"
    SITEMAP = "sitemap"

# Pydantic Models for Input Validation
class SinglePageInput(BaseModel):
    """Input model for single page crawling."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    url: str = Field(..., description="Target documentation URL to crawl (e.g., 'https://docs.python.org/3/library/os.html')", min_length=10, max_length=2000)
    output_dir: Optional[str] = Field(default=None, description="Directory to save output files. If not specified, saves to 'scraped_docs' in current directory")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format: 'markdown' for human-readable summary or 'json' for detailed metadata")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()

class MenuExtractInput(BaseModel):
    """Input model for menu link extraction."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    url: str = Field(..., description="Documentation site URL to extract menu from (e.g., 'https://docs.openai.com')", min_length=10, max_length=2000)
    output_dir: Optional[str] = Field(default=None, description="Directory to save menu JSON file. If not specified, saves to 'input_files' in current directory")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format for the response summary")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()

class BatchCrawlInput(BaseModel):
    """Input model for batch URL crawling (both multi and split modes)."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    urls: List[str] = Field(..., description="List of URLs to crawl (e.g., ['https://docs.example.com/page1', 'https://docs.example.com/page2'])", min_items=1, max_items=100)
    output_prefix: Optional[str] = Field(default=None, description="Custom prefix for output file/directory name (e.g., 'my-project')", max_length=100)
    output_dir: Optional[str] = Field(default=None, description="Base directory to save output files")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format for the response summary")

    @field_validator('urls')
    @classmethod
    def validate_urls(cls, v: List[str]) -> List[str]:
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL: {url}. All URLs must start with http:// or https://")
        return v

class SitemapCrawlInput(BaseModel):
    """Input model for sitemap-based crawling."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    sitemap_url: str = Field(..., description="URL of sitemap.xml file (e.g., 'https://docs.example.com/sitemap.xml')", min_length=10, max_length=2000)
    max_depth: Optional[int] = Field(default=10, description="Maximum sitemap recursion depth", ge=1, le=50)
    patterns: Optional[List[str]] = Field(default=None, description="URL patterns to include (e.g., ['/docs/*', '/guide/*'])", max_items=20)
    output_dir: Optional[str] = Field(default=None, description="Directory to save output files")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format for the response summary")

    @field_validator('sitemap_url')
    @classmethod
    def validate_sitemap_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Sitemap URL must start with http:// or https://")
        if not any(x in v.lower() for x in ['sitemap', '.xml']):
            raise ValueError("URL should point to a sitemap XML file")
        return v.strip()

# Shared utility functions
async def _run_crawler_command(cmd: List[str], ctx: Context) -> Dict[str, Any]:
    """Execute a crawler command and capture output."""
    try:
        await ctx.report_progress(0.1, f"Starting crawler: {cmd[0]}")

        # Run the command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(CRAWLER_DIR)
        )

        await ctx.report_progress(0.5, "Crawling in progress...")

        stdout, stderr = await process.communicate()

        await ctx.report_progress(0.9, "Processing results...")

        return {
            "success": process.returncode == 0,
            "stdout": stdout.decode('utf-8'),
            "stderr": stderr.decode('utf-8'),
            "return_code": process.returncode
        }

    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "return_code": -1
        }

def _handle_crawler_error(result: Dict[str, Any], mode: str) -> str:
    """Format error messages from crawler execution."""
    if result["return_code"] == -1:
        return f"Error: Failed to execute {mode} crawler. {result['stderr']}"

    error_msg = result['stderr']

    if "No URLs found" in error_msg:
        return "Error: No URLs found in the input. Please check your URL list or menu extraction results."
    elif "Permission denied" in error_msg:
        return "Error: Permission denied writing to output directory. Try specifying a different --output_dir with write permissions."
    elif "Connection" in error_msg or "timeout" in error_msg.lower():
        return "Error: Network connection issue. Please check your internet connection and try again."
    elif "Invalid URL" in error_msg:
        return "Error: Invalid URL format detected. Ensure all URLs start with http:// or https://"

    return f"Error during {mode} crawling: {error_msg[:500]}"

def _format_markdown_summary(mode: str, result: Dict[str, Any], output_files: List[str]) -> str:
    """Format a markdown summary of crawling results."""
    lines = [f"# Crawl4AI {mode.title()} Crawler Results", ""]

    if result["success"]:
        lines.append("✅ **Status**: Success")
        lines.append("")
        lines.append("## Output Files")
        for file in output_files:
            lines.append(f"- `{file}`")
        lines.append("")

        # Extract stats from stdout if available
        stdout = result["stdout"]
        if "Successfully" in stdout:
            lines.append("## Summary")
            # Extract key information from stdout
            for line in stdout.split('\n'):
                if any(keyword in line for keyword in ['Successfully', 'Total', 'Found', 'Created']):
                    lines.append(f"- {line.strip()}")
    else:
        lines.append("❌ **Status**: Failed")
        lines.append("")
        lines.append("## Error Details")
        lines.append(f"```\n{result['stderr'][:1000]}\n```")

    return "\n".join(lines)

# Tool definitions
@mcp.tool(
    name="crawl4ai_single_page",
    annotations={
        "title": "Crawl Single Documentation Page",
        "readOnlyHint": False,  # Writes files
        "destructiveHint": False,
        "idempotentHint": True,  # Same URL produces same output
        "openWorldHint": True  # Accesses external URLs
    }
)
async def crawl4ai_single_page(params: SinglePageInput, ctx: Context) -> str:
    """Extract clean documentation content from a single web page.

    This tool crawls a single documentation page and extracts clean, formatted Markdown
    content suitable for LLM training or RAG systems. It automatically removes navigation,
    ads, and other noise, preserving only the core documentation content.

    Args:
        params (SinglePageInput): Validated input parameters containing:
            - url (str): Target documentation URL (e.g., "https://docs.python.org/3/library/os.html")
            - output_dir (Optional[str]): Directory to save output (default: "scraped_docs" in current directory)
            - response_format (ResponseFormat): Output format for response summary

    Returns:
        str: Markdown or JSON summary of the crawling operation including:
            - Operation status (success/failure)
            - Output file path
            - Content statistics
            - Any errors encountered

    Examples:
        - Use when: "Extract the Python os module documentation"
        - Use when: "Get clean Markdown from https://docs.example.com/api"
        - Don't use when: You need to crawl multiple pages (use crawl4ai_batch_urls_split instead)
        - Don't use when: You need to extract menu links first (use crawl4ai_extract_menu instead)

    Error Handling:
        - Returns actionable error if URL is invalid or inaccessible
        - Returns permission error if output directory is not writable
        - Returns network error if connection fails
        - Suggests using menu extraction if page is a navigation page
    """
    try:
        # Build command
        cmd = [
            sys.executable,
            str(CRAWLER_DIR / "single_url_crawler.py"),
            params.url
        ]

        if params.output_dir:
            cmd.extend(["--output-dir", params.output_dir])

        # Execute crawler
        result = await _run_crawler_command(cmd, ctx)

        if not result["success"]:
            return _handle_crawler_error(result, "single page")

        # Find output file from stdout
        output_files = []
        for line in result["stdout"].split('\n'):
            if "saved to:" in line.lower():
                # Extract file path
                file_path = line.split("saved to:")[-1].strip()
                output_files.append(file_path)

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            return _format_markdown_summary("single page", result, output_files)
        else:
            return json.dumps({
                "success": True,
                "mode": "single_page",
                "url": params.url,
                "output_files": output_files,
                "output_dir": params.output_dir or DEFAULT_OUTPUT_DIR
            }, indent=2)

    except Exception as e:
        await ctx.log_error("Single page crawl failed", {"error": str(e), "url": params.url})
        return f"Error: Unexpected error during crawling: {type(e).__name__}: {str(e)}"

@mcp.tool(
    name="crawl4ai_extract_menu",
    annotations={
        "title": "Extract Documentation Menu Links",
        "readOnlyHint": False,  # Writes JSON file
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def crawl4ai_extract_menu(params: MenuExtractInput, ctx: Context) -> str:
    """Extract all navigation menu links from a documentation website.

    This tool analyzes a documentation site's navigation structure and extracts all
    menu links into a structured JSON file. It handles nested menus, dynamic content,
    and lazy-loaded navigation elements. The output can be fed directly to batch
    crawling tools for comprehensive documentation extraction.

    Args:
        params (MenuExtractInput): Validated input parameters containing:
            - url (str): Documentation site URL (e.g., "https://docs.openai.com")
            - output_dir (Optional[str]): Directory to save menu JSON (default: "input_files")
            - response_format (ResponseFormat): Output format for response summary

    Returns:
        str: Markdown or JSON summary including:
            - Number of menu links found
            - Output JSON file path
            - Suggested next steps (batch crawling commands)
            - Any errors encountered

    Examples:
        - Use when: "Find all documentation pages on docs.example.com"
        - Use when: "Extract the complete navigation structure"
        - Use when: Setting up a comprehensive crawl of documentation
        - Don't use when: You already have a list of URLs to crawl
        - Don't use when: The site doesn't have a navigation menu (use sitemap instead)

    Error Handling:
        - Returns error if URL is not accessible
        - Returns warning if no menu links found (suggests checking selectors)
        - Returns permission error if output directory is not writable
        - Suggests using sitemap crawler if menu extraction fails
    """
    try:
        # Build command
        cmd = [
            sys.executable,
            str(CRAWLER_DIR / "menu_crawler.py"),
            params.url
        ]

        if params.output_dir:
            cmd.extend(["--output-dir", params.output_dir])

        # Execute crawler
        result = await _run_crawler_command(cmd, ctx)

        if not result["success"]:
            error_msg = _handle_crawler_error(result, "menu extraction")
            error_msg += "\n\nTip: If menu extraction fails, try using crawl4ai_from_sitemap if the site has a sitemap.xml"
            return error_msg

        # Extract output file and stats from stdout
        output_files = []
        total_links = 0

        for line in result["stdout"].split('\n'):
            if "saved to:" in line.lower():
                file_path = line.split("saved to:")[-1].strip()
                output_files.append(file_path)
            elif "unique menu links" in line.lower():
                try:
                    total_links = int(''.join(filter(str.isdigit, line.split("unique")[0])))
                except:
                    pass

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            summary = _format_markdown_summary("menu extraction", result, output_files)

            # Add next steps
            if output_files and total_links > 0:
                summary += "\n\n## Next Steps\n\n"
                summary += "You can now crawl all these URLs using:\n\n"
                summary += f"**Individual files per page:**\n"
                summary += f"```python\ncrawl4ai_batch_urls_split(urls=[...], output_prefix='project-name')\n```\n\n"
                summary += f"**Single consolidated file:**\n"
                summary += f"```python\ncrawl4ai_batch_urls_consolidated(urls=[...], output_prefix='project-name')\n```"

            return summary
        else:
            return json.dumps({
                "success": True,
                "mode": "menu_extraction",
                "url": params.url,
                "total_links_found": total_links,
                "output_files": output_files,
                "output_dir": params.output_dir or DEFAULT_INPUT_DIR
            }, indent=2)

    except Exception as e:
        await ctx.log_error("Menu extraction failed", {"error": str(e), "url": params.url})
        return f"Error: Unexpected error during menu extraction: {type(e).__name__}: {str(e)}"

@mcp.tool(
    name="crawl4ai_batch_urls_split",
    annotations={
        "title": "Crawl Multiple URLs into Individual Files",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def crawl4ai_batch_urls_split(params: BatchCrawlInput, ctx: Context) -> str:
    """Crawl multiple URLs and save each as an individual Markdown file.

    This tool processes multiple documentation URLs and generates a separate Markdown
    file for each page, organized in a timestamped subdirectory. This is ideal for
    version control, granular updates, and when you need to work with documentation
    pages individually.

    Args:
        params (BatchCrawlInput): Validated input parameters containing:
            - urls (List[str]): List of URLs to crawl (1-100 URLs)
            - output_prefix (Optional[str]): Custom prefix for output directory name
            - output_dir (Optional[str]): Base directory for output (default: "scraped_docs")
            - response_format (ResponseFormat): Output format for response summary

    Returns:
        str: Markdown or JSON summary including:
            - Number of files successfully created
            - Output directory path
            - Individual file names
            - Success/failure statistics

    Examples:
        - Use when: "Crawl these 50 documentation pages and keep them as separate files"
        - Use when: You want version control friendly output
        - Use when: You need to update individual pages later
        - Don't use when: You want a single consolidated file (use crawl4ai_batch_urls_consolidated)
        - Don't use when: You're only crawling 1-2 pages (use crawl4ai_single_page)

    Error Handling:
        - Returns partial success if some URLs fail
        - Returns actionable errors for each failed URL
        - Suggests filtering or reducing URL count if rate limited
        - Recommends checking URLs if many fail
    """
    try:
        # Create temporary JSON file with URLs
        temp_file = CRAWLER_DIR / f"temp_urls_{id(params)}.json"
        with open(temp_file, 'w') as f:
            json.dump({"urls": params.urls}, f)

        try:
            # Build command
            cmd = [
                sys.executable,
                str(CRAWLER_DIR / "split_url_crawler.py"),
                str(temp_file)
            ]

            if params.output_prefix:
                cmd.extend(["--output-prefix", params.output_prefix])
            if params.output_dir:
                cmd.extend(["--output-dir", params.output_dir])

            # Execute crawler
            result = await _run_crawler_command(cmd, ctx)

            if not result["success"]:
                return _handle_crawler_error(result, "batch split")

            # Extract output directory from stdout
            output_files = []
            output_directory = None
            successful_count = 0

            for line in result["stdout"].split('\n'):
                if "Output directory:" in line:
                    output_directory = line.split("Output directory:")[-1].strip()
                elif "Successfully saved:" in line or "Successfully created" in line:
                    try:
                        successful_count = int(''.join(filter(str.isdigit, line)))
                    except:
                        pass

            # Format response
            if params.response_format == ResponseFormat.MARKDOWN:
                return _format_markdown_summary("batch split", result, [output_directory] if output_directory else [])
            else:
                return json.dumps({
                    "success": True,
                    "mode": "batch_split",
                    "total_urls": len(params.urls),
                    "successful_files": successful_count,
                    "output_directory": output_directory,
                    "output_base_dir": params.output_dir or DEFAULT_OUTPUT_DIR
                }, indent=2)

        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

    except Exception as e:
        await ctx.log_error("Batch split crawl failed", {"error": str(e), "url_count": len(params.urls)})
        return f"Error: Unexpected error during batch crawling: {type(e).__name__}: {str(e)}"

@mcp.tool(
    name="crawl4ai_batch_urls_consolidated",
    annotations={
        "title": "Crawl Multiple URLs into Single File",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def crawl4ai_batch_urls_consolidated(params: BatchCrawlInput, ctx: Context) -> str:
    """Crawl multiple URLs and combine into a single consolidated Markdown file.

    This tool processes multiple documentation URLs and combines all content into one
    large Markdown file with page separators. This is ideal for LLM context windows,
    offline reading, or when you want complete documentation in a single file.

    Args:
        params (BatchCrawlInput): Validated input parameters containing:
            - urls (List[str]): List of URLs to crawl (1-100 URLs)
            - output_prefix (Optional[str]): Custom prefix for output file name
            - output_dir (Optional[str]): Directory for output (default: "scraped_docs")
            - response_format (ResponseFormat): Output format for response summary

    Returns:
        str: Markdown or JSON summary including:
            - Output file path
            - Total pages combined
            - File size information
            - Success/failure statistics

    Examples:
        - Use when: "Combine all API documentation into one file for my LLM"
        - Use when: You want documentation for offline reading
        - Use when: Building context for RAG system
        - Don't use when: You need individual files (use crawl4ai_batch_urls_split)
        - Don't use when: You're crawling >50 pages (output may be too large)

    Error Handling:
        - Returns partial success if some URLs fail
        - Warns if output file is very large (>10MB)
        - Suggests splitting if file size exceeds reasonable limits
        - Returns actionable errors for each failed URL
    """
    try:
        # Create temporary JSON file with URLs
        temp_file = CRAWLER_DIR / f"temp_urls_{id(params)}.json"
        with open(temp_file, 'w') as f:
            json.dump({"urls": params.urls}, f)

        try:
            # Build command
            cmd = [
                sys.executable,
                str(CRAWLER_DIR / "multi_url_crawler.py"),
                str(temp_file)
            ]

            if params.output_prefix:
                cmd.extend(["--output-prefix", params.output_prefix])
            if params.output_dir:
                cmd.extend(["--output-dir", params.output_dir])

            # Execute crawler
            result = await _run_crawler_command(cmd, ctx)

            if not result["success"]:
                return _handle_crawler_error(result, "batch consolidated")

            # Extract output file from stdout
            output_files = []
            successful_count = 0

            for line in result["stdout"].split('\n'):
                if "saved to:" in line.lower():
                    file_path = line.split("saved to:")[-1].strip()
                    output_files.append(file_path)
                elif "Successfully crawled:" in line:
                    try:
                        parts = line.split(":")[-1].strip().split("/")
                        successful_count = int(parts[0])
                    except:
                        pass

            # Format response
            if params.response_format == ResponseFormat.MARKDOWN:
                summary = _format_markdown_summary("batch consolidated", result, output_files)

                # Add file size warning if needed
                if output_files:
                    try:
                        file_size = Path(output_files[0]).stat().st_size
                        if file_size > 10_000_000:  # 10MB
                            summary += f"\n\n⚠️ **Warning**: Output file is {file_size / 1_000_000:.1f}MB. Consider using split mode for easier handling."
                    except:
                        pass

                return summary
            else:
                return json.dumps({
                    "success": True,
                    "mode": "batch_consolidated",
                    "total_urls": len(params.urls),
                    "successful_pages": successful_count,
                    "output_files": output_files,
                    "output_dir": params.output_dir or DEFAULT_OUTPUT_DIR
                }, indent=2)

        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

    except Exception as e:
        await ctx.log_error("Batch consolidated crawl failed", {"error": str(e), "url_count": len(params.urls)})
        return f"Error: Unexpected error during batch crawling: {type(e).__name__}: {str(e)}"

@mcp.tool(
    name="crawl4ai_from_sitemap",
    annotations={
        "title": "Crawl Documentation from Sitemap",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def crawl4ai_from_sitemap(params: SitemapCrawlInput, ctx: Context) -> str:
    """Discover and crawl all documentation pages from a sitemap.xml file.

    This tool automatically discovers URLs from a sitemap.xml file and crawls them
    all into a single consolidated Markdown file. It supports recursive sitemap
    parsing and URL pattern filtering for targeted documentation extraction.

    Args:
        params (SitemapCrawlInput): Validated input parameters containing:
            - sitemap_url (str): URL of sitemap.xml (e.g., "https://docs.example.com/sitemap.xml")
            - max_depth (Optional[int]): Maximum recursion depth for nested sitemaps (default: 10)
            - patterns (Optional[List[str]]): URL patterns to include (e.g., ["/docs/*", "/api/*"])
            - output_dir (Optional[str]): Directory for output (default: "scraped_docs")
            - response_format (ResponseFormat): Output format for response summary

    Returns:
        str: Markdown or JSON summary including:
            - Number of URLs discovered
            - Number of pages successfully crawled
            - Output file path
            - Pattern filtering results (if used)

    Examples:
        - Use when: "Crawl all pages from the sitemap at docs.example.com/sitemap.xml"
        - Use when: You want comprehensive documentation coverage
        - Use when: The site has a well-maintained sitemap
        - Use when: "Only crawl the /api/* pages from the sitemap"
        - Don't use when: The site doesn't have a sitemap (use menu extraction)
        - Don't use when: You only need specific pages (use direct URL crawling)

    Error Handling:
        - Returns error if sitemap URL is invalid or not accessible
        - Returns warning if no URLs match the patterns
        - Suggests checking patterns if filtering results in zero URLs
        - Suggests using menu extraction if sitemap is missing or empty
    """
    try:
        # Build command
        cmd = [
            sys.executable,
            str(CRAWLER_DIR / "sitemap_crawler.py"),
            params.sitemap_url,
            "--max-depth", str(params.max_depth)
        ]

        if params.patterns:
            cmd.extend(["--patterns"] + params.patterns)
        if params.output_dir:
            cmd.extend(["--output-dir", params.output_dir])

        # Execute crawler
        result = await _run_crawler_command(cmd, ctx)

        if not result["success"]:
            error_msg = _handle_crawler_error(result, "sitemap")
            error_msg += "\n\nTip: If sitemap crawling fails, try using crawl4ai_extract_menu to extract URLs from the navigation menu."
            return error_msg

        # Extract stats from stdout
        output_files = []
        urls_found = 0
        urls_crawled = 0

        for line in result["stdout"].split('\n'):
            if "saved to:" in line.lower():
                file_path = line.split("saved to:")[-1].strip()
                output_files.append(file_path)
            elif "Found" in line and "URLs" in line:
                try:
                    urls_found = int(''.join(filter(str.isdigit, line.split("Found")[1].split("URLs")[0])))
                except:
                    pass
            elif "Successfully crawled:" in line:
                try:
                    parts = line.split(":")[-1].strip().split("/")
                    urls_crawled = int(parts[0])
                except:
                    pass

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            summary = _format_markdown_summary("sitemap", result, output_files)

            if params.patterns and urls_found < 5:
                summary += f"\n\n⚠️ **Note**: Pattern filtering resulted in only {urls_found} URLs. You may want to check your patterns."

            return summary
        else:
            return json.dumps({
                "success": True,
                "mode": "sitemap",
                "sitemap_url": params.sitemap_url,
                "urls_discovered": urls_found,
                "urls_crawled": urls_crawled,
                "patterns_used": params.patterns,
                "output_files": output_files,
                "output_dir": params.output_dir or DEFAULT_OUTPUT_DIR
            }, indent=2)

    except Exception as e:
        await ctx.log_error("Sitemap crawl failed", {"error": str(e), "sitemap_url": params.sitemap_url})
        return f"Error: Unexpected error during sitemap crawling: {type(e).__name__}: {str(e)}"

if __name__ == "__main__":
    mcp.run()
