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

class MultiUrlCrawler:
    def __init__(self, verbose: bool = True):
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
        
        self.verbose = verbose
        
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
        rest_of_content = '\n'.join(lines[1:])
        
        return f"{h1_line}\n\n## Source\n{url}\n\n{rest_of_content}"
        
    def get_filename_prefix(self, url: str) -> str:
        """
        Generate a filename prefix from a URL including path components.
        Examples:
        - https://docs.literalai.com/page -> literalai_docs_page
        - https://literalai.com/docs/page -> literalai_docs_page
        - https://api.example.com/path/to/page -> example_api_path_to_page
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
            
            # Join parts with underscores
            return '_'.join(cleaned_parts)
        
        except Exception as e:
            print(colored(f"Error generating filename prefix: {str(e)}", "red"))
            return "default"

    def save_markdown_content(self, results: List[dict], filename_prefix: str = None):
        """Save all markdown content to a single file"""
        try:
            # Use the first successful URL to generate the filename prefix if none provided
            if not filename_prefix and results:
                # Find first successful result
                first_url = next((result["url"] for result in results if result["success"]), None)
                if first_url:
                    filename_prefix = self.get_filename_prefix(first_url)
                else:
                    filename_prefix = "docs"  # Fallback if no successful results
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.md"
            filepath = os.path.join("scraped_docs", filename)
            
            # Create scraped_docs directory if it doesn't exist
            os.makedirs("scraped_docs", exist_ok=True)
            
            with open(filepath, "w", encoding="utf-8") as f:
                for result in results:
                    if result["success"]:
                        processed_content = self.process_markdown_content(
                            result["markdown_content"],
                            result["url"]
                        )
                        f.write(processed_content)
                        f.write("\n\n---\n\n")
            
            if self.verbose:
                print(colored(f"\nMarkdown content saved to: {filepath}", "green"))
            return filepath
            
        except Exception as e:
            print(colored(f"\nError saving markdown content: {str(e)}", "red"))
            return None

    async def crawl(self, urls: List[str]) -> List[dict]:
        """
        Crawl multiple URLs sequentially using session reuse for optimal performance
        """
        if self.verbose:
            print("\n=== Starting Crawl ===")
            total_urls = len(urls)
            print(f"Total URLs to crawl: {total_urls}")

        results = []
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            session_id = "crawl_session"  # Reuse the same session for all URLs
            for idx, url in enumerate(urls, 1):
                try:
                    if self.verbose:
                        progress = (idx / total_urls) * 100
                        print(f"\nProgress: {idx}/{total_urls} ({progress:.1f}%)")
                        print(f"Crawling: {url}")
                    
                    result = await crawler.arun(
                        url=url,
                        config=self.crawler_config,
                        session_id=session_id,
                    )
                    
                    results.append({
                        "url": url,
                        "success": result.success,
                        "content_length": len(result.markdown.raw_markdown) if result.success else 0,
                        "markdown_content": result.markdown.raw_markdown if result.success else "",
                        "error": result.error_message if not result.success else None
                    })
                    
                    if self.verbose and result.success:
                        print(f"✓ Successfully crawled URL {idx}/{total_urls}")
                        print(f"Content length: {len(result.markdown.raw_markdown)} characters")
                except Exception as e:
                    results.append({
                        "url": url,
                        "success": False,
                        "content_length": 0,
                        "markdown_content": "",
                        "error": str(e)
                    })
                    if self.verbose:
                        print(f"✗ Error crawling URL {idx}/{total_urls}: {str(e)}")

        if self.verbose:
            successful = sum(1 for r in results if r["success"])
            print(f"\n=== Crawl Complete ===")
            print(f"Successfully crawled: {successful}/{total_urls} URLs")

        return results

async def main():
    parser = argparse.ArgumentParser(description='Crawl multiple URLs and generate markdown documentation')
    parser.add_argument('--urls', type=str, help='Path to file containing URLs (either .txt or .json)')
    parser.add_argument('--output-prefix', type=str, help='Prefix for output markdown file (optional)')
    args = parser.parse_args()

    if not args.urls:
        print(colored("Error: Please provide a file containing URLs using --urls", "red"))
        parser.print_help()
        sys.exit(1)

    try:
        # Load URLs from file
        urls = load_urls_from_file(args.urls)
        
        if not urls:
            print(colored("Error: No URLs found in the input file", "red"))
            sys.exit(1)
            
        print(colored(f"Found {len(urls)} URLs to crawl", "green"))
        
        # Initialize and run crawler
        crawler = MultiUrlCrawler(verbose=True)
        results = await crawler.crawl(urls)
        
        # Save results to markdown file - only pass output_prefix if explicitly set
        crawler.save_markdown_content(results, args.output_prefix if args.output_prefix else None)
        
    except Exception as e:
        print(colored(f"Error during crawling: {str(e)}", "red"))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 