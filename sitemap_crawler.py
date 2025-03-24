import os
import sys
import asyncio
import re
import xml.etree.ElementTree as ET
import aiohttp
import argparse
from typing import List, Optional, Dict
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter
from termcolor import colored

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

    async def fetch_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Fetch and parse an XML sitemap to extract URLs.
        
        Args:
            sitemap_url (str): The URL of the XML sitemap
            
        Returns:
            List[str]: List of URLs found in the sitemap
        """
        if self.verbose:
            print(f"\nFetching sitemap from: {sitemap_url}")
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(sitemap_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch sitemap: HTTP {response.status}")
                    
                    content = await response.text()
                    
                # Parse XML content
                root = ET.fromstring(content)
                
                # Handle both standard sitemaps and sitemap indexes
                urls = []
                
                # Remove XML namespace for easier parsing
                namespace = root.tag.split('}')[0] + '}' if '}' in root.tag else ''
                
                if root.tag == f"{namespace}sitemapindex":
                    # This is a sitemap index file
                    if self.verbose:
                        print("Found sitemap index, processing nested sitemaps...")
                    
                    for sitemap in root.findall(f".//{namespace}sitemap"):
                        loc = sitemap.find(f"{namespace}loc")
                        if loc is not None and loc.text:
                            nested_urls = await self.fetch_sitemap(loc.text)
                            urls.extend(nested_urls)
                else:
                    # This is a standard sitemap
                    for url in root.findall(f".//{namespace}url"):
                        loc = url.find(f"{namespace}loc")
                        if loc is not None and loc.text:
                            urls.append(loc.text)
                
                if self.verbose:
                    print(f"Found {len(urls)} URLs in sitemap")
                return urls
                
            except Exception as e:
                print(f"Error fetching sitemap: {str(e)}")
                return []
        
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
        
    def save_markdown_content(self, results: List[dict], filename_prefix: str = "vercel_ai_docs"):
        """Save all markdown content to a single file"""
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
            print(f"\nMarkdown content saved to: {filepath}")
        return filepath

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

    def get_filename_prefix(self, url: str) -> str:
        """
        Generate a filename prefix from a sitemap URL.
        Examples:
        - https://docs.literalai.com/sitemap.xml -> literalai_documentation
        - https://literalai.com/docs/sitemap.xml -> literalai_docs
        - https://api.example.com/sitemap.xml -> example_api
        
        Args:
            url (str): The sitemap URL
            
        Returns:
            str: Generated filename prefix
        """
        # Remove protocol and split URL parts
        clean_url = url.split('://')[1]
        url_parts = clean_url.split('/')
        
        # Get domain parts
        domain_parts = url_parts[0].split('.')
        
        # Extract main domain name (ignoring TLD)
        main_domain = domain_parts[-2]
        
        # Determine the qualifier (subdomain or path segment)
        qualifier = None
        
        # First check subdomain
        if len(domain_parts) > 2:
            qualifier = domain_parts[0]
        # Then check path
        elif len(url_parts) > 2:
            # Get the first meaningful path segment
            for segment in url_parts[1:]:
                if segment and segment != 'sitemap.xml':
                    qualifier = segment
                    break
        
        # Build the prefix
        if qualifier:
            # Clean up qualifier (remove special characters, convert to lowercase)
            qualifier = re.sub(r'[^a-zA-Z0-9]', '', qualifier.lower())
            # Don't duplicate parts if they're the same
            if qualifier != main_domain:
                return f"{main_domain}_{qualifier}"
        
        return main_domain

async def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Crawl a sitemap and generate markdown documentation')
    parser.add_argument('sitemap_url', type=str, help='URL of the sitemap (e.g., https://docs.example.com/sitemap.xml)')
    parser.add_argument('--max-depth', type=int, default=10, help='Maximum sitemap recursion depth')
    parser.add_argument('--patterns', type=str, nargs='+', help='URL patterns to include (e.g., "/docs/*" "/guide/*")')
    args = parser.parse_args()

    try:
        print(colored(f"\nFetching sitemap: {args.sitemap_url}", "cyan"))
        
        # Initialize crawler
        crawler = MultiUrlCrawler(verbose=True)
        
        # Fetch URLs from sitemap
        urls = await crawler.fetch_sitemap(args.sitemap_url)
        
        if not urls:
            print(colored("No URLs found in sitemap", "red"))
            sys.exit(1)
            
        # Filter URLs by pattern if specified
        if args.patterns:
            print(colored("\nFiltering URLs by patterns:", "cyan"))
            for pattern in args.patterns:
                print(colored(f"  {pattern}", "yellow"))
            
            filtered_urls = []
            for url in urls:
                if any(pattern.replace('*', '') in url for pattern in args.patterns):
                    filtered_urls.append(url)
            
            print(colored(f"\nFound {len(filtered_urls)} URLs matching patterns", "green"))
            urls = filtered_urls
        
        # Crawl the URLs
        results = await crawler.crawl(urls)
        
        # Save results to markdown file with dynamic name
        filename_prefix = crawler.get_filename_prefix(args.sitemap_url)
        crawler.save_markdown_content(results, filename_prefix)
        
    except Exception as e:
        print(colored(f"Error during crawling: {str(e)}", "red"))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 