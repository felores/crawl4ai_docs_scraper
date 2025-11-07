import os
import sys
import asyncio
import re
import json
import argparse
from typing import List, Optional
from datetime import datetime
from termcolor import colored
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter
from urllib.parse import urlparse

def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from either a text file or JSON file"""
    try:
        # Create input_files directory if it doesn't exist
        input_dir = "input_files"
        os.makedirs(input_dir, exist_ok=True)

        # Check if file exists in current directory or input_files directory
        if os.path.exists(file_path):
            actual_path = file_path
        elif os.path.exists(os.path.join(input_dir, file_path)):
            actual_path = os.path.join(input_dir, file_path)
        else:
            print(colored(f"Error: File {file_path} not found", "red"))
            print(colored(f"Please place your URL files in either:", "yellow"))
            print(colored(f"1. The root directory ({os.getcwd()})", "yellow"))
            print(colored(f"2. The input_files directory ({os.path.join(os.getcwd(), input_dir)})", "yellow"))
            sys.exit(1)

        file_ext = os.path.splitext(actual_path)[1].lower()

        if file_ext == '.json':
            print(colored(f"Loading URLs from JSON file: {actual_path}", "cyan"))
            with open(actual_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    # Handle menu crawler output format
                    if isinstance(data, dict) and 'menu_links' in data:
                        urls = data['menu_links']
                    elif isinstance(data, dict) and 'urls' in data:
                        urls = data['urls']
                    elif isinstance(data, list):
                        urls = data
                    else:
                        print(colored("Error: Invalid JSON format. Expected 'menu_links' or 'urls' key, or list of URLs", "red"))
                        sys.exit(1)
                    print(colored(f"Successfully loaded {len(urls)} URLs from JSON file", "green"))
                    return urls
                except json.JSONDecodeError as e:
                    print(colored(f"Error: Invalid JSON file - {str(e)}", "red"))
                    sys.exit(1)
        else:
            print(colored(f"Loading URLs from text file: {actual_path}", "cyan"))
            with open(actual_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
                print(colored(f"Successfully loaded {len(urls)} URLs from text file", "green"))
                return urls

    except Exception as e:
        print(colored(f"Error loading URLs from file: {str(e)}", "red"))
        sys.exit(1)

class SplitUrlCrawler:
    def __init__(self, output_prefix: Optional[str] = None, base_output_dir: str = "scraped_docs", verbose: bool = True):
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=True,
            viewport_width=800,
            viewport_height=600
        )

        self.crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(
                    threshold=0.48,
                    threshold_type="fixed",
                    min_word_threshold=0
                )
            ),
        )

        self.output_prefix = output_prefix
        self.base_output_dir = base_output_dir
        self.verbose = verbose
        self.output_dir = None

    def process_markdown_content(self, content: str, url: str) -> str:
        """Process markdown content to start from first H1 and add URL as H2"""
        # Find the first H1 tag
        h1_match = re.search(r'^# .+$', content, re.MULTILINE)
        if not h1_match:
            # If no H1 found, return original content with URL as H1
            return f"# No Title Found\n\n## Source\n{url}\n\n{content}"

        # Get the content starting from the first H1
        content_from_h1 = content[h1_match.start():]

        # Remove "Was this page helpful?" section and everything after it
        helpful_patterns = [
            r'^#+\s*Was this page helpful\?.*$',  # Matches any heading level with this text
            r'^Was this page helpful\?.*$',       # Matches the text without heading
            r'^#+\s*Was this helpful\?.*$',       # Matches any heading level with shorter text
            r'^Was this helpful\?.*$'             # Matches shorter text without heading
        ]

        for pattern in helpful_patterns:
            parts = re.split(pattern, content_from_h1, flags=re.MULTILINE | re.IGNORECASE)
            if len(parts) > 1:
                content_from_h1 = parts[0].strip()
                break

        # Insert URL as H2 after the H1
        lines = content_from_h1.split('\n')
        h1_line = lines[0]
        rest_of_content = '\n'.join(lines[1:]).strip()

        return f"{h1_line}\n\n## Source\n{url}\n\n{rest_of_content}"

    def get_filename_from_url(self, url: str) -> str:
        """
        Generate a filename from a URL including path components.
        Examples:
        - https://docs.literalai.com/page -> literalai_docs_page.md
        - https://literalai.com/docs/page -> literalai_docs_page.md
        - https://api.example.com/path/to/page -> example_api_path_to_page.md
        """
        try:
            # Parse the URL
            parsed = urlparse(url)

            # Split hostname and reverse it (e.g., 'docs.example.com' -> ['com', 'example', 'docs'])
            hostname_parts = parsed.hostname.split('.')
            hostname_parts.reverse()

            # Remove common TLDs and 'www'
            hostname_parts = [p for p in hostname_parts if p not in ('com', 'org', 'net', 'www')]

            # Get path components, removing empty strings
            path_parts = [p for p in parsed.path.split('/') if p]

            # Combine hostname and path parts
            all_parts = hostname_parts + path_parts

            # Clean up parts: lowercase, remove special chars, limit length
            cleaned_parts = []
            for part in all_parts:
                # Convert to lowercase and remove special characters
                cleaned = re.sub(r'[^a-zA-Z0-9]+', '_', part.lower())
                # Remove leading/trailing underscores
                cleaned = cleaned.strip('_')
                # Only add non-empty parts
                if cleaned:
                    cleaned_parts.append(cleaned)

            # Join parts with underscores and add .md extension
            filename = '_'.join(cleaned_parts) + '.md'
            return filename

        except Exception as e:
            if self.verbose:
                print(colored(f"Error generating filename from URL: {str(e)}", "yellow"))
            # Fallback: use timestamp-based name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
            return f"page_{timestamp}.md"

    def get_project_name_from_url(self, url: str) -> str:
        """
        Extract project name from URL for directory naming.
        Examples:
        - https://docs.literalai.com -> literalai
        - https://example.com/docs -> example
        """
        try:
            parsed = urlparse(url)
            hostname_parts = parsed.hostname.split('.')

            # Find the main domain (usually second-to-last part before TLD)
            for part in reversed(hostname_parts):
                if part not in ('com', 'org', 'net', 'www', 'docs', 'api'):
                    return part.lower()

            # Fallback to first hostname part
            return hostname_parts[0].lower()
        except:
            return "project"

    def create_output_directory(self, first_url: str) -> str:
        """Create output directory based on project name and timestamp"""
        if self.output_prefix:
            project_name = self.output_prefix
        else:
            project_name = self.get_project_name_from_url(first_url)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = f"{project_name}_{timestamp}"
        output_path = os.path.join(self.base_output_dir, dir_name)

        os.makedirs(output_path, exist_ok=True)

        if self.verbose:
            print(colored(f"\nCreated output directory: {output_path}", "green"))

        return output_path

    def save_markdown_file(self, content: str, url: str, url_index: int) -> Optional[str]:
        """Save markdown content to individual file"""
        try:
            # Generate filename from URL
            filename = self.get_filename_from_url(url)
            filepath = os.path.join(self.output_dir, filename)

            # Handle duplicate filenames by appending index
            if os.path.exists(filepath):
                base_name = filename[:-3]  # Remove .md
                filepath = os.path.join(self.output_dir, f"{base_name}_{url_index}.md")

            processed_content = self.process_markdown_content(content, url)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(processed_content)

            if self.verbose:
                print(colored(f"✓ Saved: {os.path.basename(filepath)}", "green"))

            return filepath

        except Exception as e:
            print(colored(f"✗ Error saving markdown file: {str(e)}", "red"))
            return None

    async def crawl(self, urls: List[str]) -> List[dict]:
        """
        Crawl multiple URLs and save each to individual markdown files
        """
        if not urls:
            print(colored("Error: No URLs provided", "red"))
            return []

        # Create output directory using first URL
        self.output_dir = self.create_output_directory(urls[0])

        if self.verbose:
            print("\n=== Starting Split URL Crawl ===")
            total_urls = len(urls)
            print(f"Total URLs to crawl: {total_urls}")

        results = []
        successful_saves = 0

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            session_id = "split_crawl_session"  # Reuse the same session for all URLs

            for idx, url in enumerate(urls, 1):
                try:
                    if self.verbose:
                        progress = (idx / total_urls) * 100
                        print(f"\n[{idx}/{total_urls}] ({progress:.1f}%) Crawling: {url}")

                    result = await crawler.arun(
                        url=url,
                        config=self.crawler_config,
                        session_id=session_id,
                    )

                    if result.success:
                        # Save to individual file
                        filepath = self.save_markdown_file(
                            result.markdown.raw_markdown,
                            url,
                            idx
                        )

                        if filepath:
                            successful_saves += 1

                        results.append({
                            "url": url,
                            "success": True,
                            "filepath": filepath,
                            "content_length": len(result.markdown.raw_markdown),
                            "error": None
                        })

                        if self.verbose:
                            print(f"  Content length: {len(result.markdown.raw_markdown)} characters")
                    else:
                        results.append({
                            "url": url,
                            "success": False,
                            "filepath": None,
                            "content_length": 0,
                            "error": result.error_message
                        })
                        if self.verbose:
                            print(colored(f"✗ Failed to crawl: {result.error_message}", "red"))

                except Exception as e:
                    results.append({
                        "url": url,
                        "success": False,
                        "filepath": None,
                        "content_length": 0,
                        "error": str(e)
                    })
                    if self.verbose:
                        print(colored(f"✗ Error crawling URL: {str(e)}", "red"))

        if self.verbose:
            print(f"\n=== Crawl Complete ===")
            print(colored(f"Successfully saved: {successful_saves}/{total_urls} files", "green"))
            print(colored(f"Output directory: {self.output_dir}", "cyan"))

        return results

async def main():
    parser = argparse.ArgumentParser(
        description='Crawl multiple URLs and generate individual markdown files for each URL'
    )
    parser.add_argument(
        'urls_file',
        type=str,
        help='Path to file containing URLs (either .txt or .json)'
    )
    parser.add_argument(
        '--output-prefix',
        type=str,
        help='Custom prefix for output directory name (default: extracted from first URL)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='scraped_docs',
        help='Base directory to save output files (default: scraped_docs)'
    )
    args = parser.parse_args()

    try:
        # Load URLs from file
        urls = load_urls_from_file(args.urls_file)

        if not urls:
            print(colored("Error: No URLs found in the input file", "red"))
            sys.exit(1)

        print(colored(f"Found {len(urls)} URLs to crawl", "green"))

        # Initialize and run crawler
        crawler = SplitUrlCrawler(
            output_prefix=args.output_prefix,
            base_output_dir=args.output_dir,
            verbose=True
        )
        results = await crawler.crawl(urls)

        # Summary
        successful = sum(1 for r in results if r["success"])
        if successful > 0:
            print(colored(f"\n✓ Successfully created {successful} markdown files", "green"))
        else:
            print(colored("\n✗ No files were created", "red"))
            sys.exit(1)

    except Exception as e:
        print(colored(f"Error during crawling: {str(e)}", "red"))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
