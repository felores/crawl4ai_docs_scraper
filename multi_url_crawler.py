import os
import sys
import asyncio
import re
from typing import List, Optional
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

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

async def main():
    # Example usage
    urls = [
        "https://developers.cloudflare.com/agents/model-context-protocol/authorization/",
        "https://developers.cloudflare.com/agents/model-context-protocol/tools/",
        "https://developers.cloudflare.com/agents/model-context-protocol/transport/"
    ]
    
    crawler = MultiUrlCrawler(verbose=True)
    results = await crawler.crawl(urls)
    
    # Save results to markdown file
    crawler.save_markdown_content(results, "docs")

if __name__ == "__main__":
    asyncio.run(main()) 