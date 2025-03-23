#!/usr/bin/env python3

import asyncio
from typing import List, Set
from termcolor import colored
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from urllib.parse import urljoin, urlparse
import json
import os
from datetime import datetime
import re

# Constants
BASE_URL = "https://developers.cloudflare.com/agents/"
OUTPUT_DIR = "scraped_docs"
MENU_SELECTORS = [
    "nav a",  # General navigation links
    "[role='navigation'] a",  # Role-based navigation
    ".sidebar a",  # Common sidebar class
    "[class*='nav'] a",  # Classes containing 'nav'
    "[class*='menu'] a",  # Classes containing 'menu'
]

# JavaScript to expand nested menus
EXPAND_MENUS_JS = """
(async () => {
    // Function to expand all menu items
    async function expandAllMenus() {
        // Common selectors for expandable menu items
        const expandableSelectors = [
            'button[aria-expanded="false"]',  // ARIA standard
            '.expandable:not(.expanded)',     // Common class pattern
            '[class*="collapse"]:not(.show)', // Bootstrap-style
            '.closed',                        // Simple state class
            '[class*="menu-item-has-children"]' // WordPress-style
        ];
        
        let expanded = 0;
        let lastExpanded = -1;
        
        // Keep trying to expand until no new items are expanded
        while (expanded !== lastExpanded) {
            lastExpanded = expanded;
            
            for (const selector of expandableSelectors) {
                const elements = document.querySelectorAll(selector);
                for (const el of elements) {
                    try {
                        // Try different methods of expanding
                        el.click();
                        el.setAttribute('aria-expanded', 'true');
                        el.classList.add('expanded', 'show');
                        el.classList.remove('collapsed', 'closed');
                        expanded++;
                    } catch (e) {
                        continue;
                    }
                }
            }
            
            // Wait a bit for any animations/transitions
            await new Promise(r => setTimeout(r, 100));
        }
        
        return expanded;
    }
    
    // Execute the expansion
    const expandedCount = await expandAllMenus();
    return expandedCount;
})();
"""

def get_filename_prefix(url: str) -> str:
    """
    Generate a filename prefix from a URL including path components.
    Examples:
    - https://docs.literalai.com/page -> literalai_docs_page
    - https://literalai.com/docs/page -> literalai_docs_page
    - https://api.example.com/path/to/page -> example_api_path_to_page
    
    Args:
        url (str): The URL to process
        
    Returns:
        str: A filename-safe string derived from the URL
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

class DocsMenuCrawler:
    def __init__(self, start_url: str):
        self.start_url = start_url
        
        # Configure browser settings
        self.browser_config = BrowserConfig(
            headless=True,
            viewport_width=1920,
            viewport_height=1080
        )
        
        # Create extraction strategy for menu links
        extraction_schema = {
            "name": "MenuLinks",
            "baseSelector": ", ".join(MENU_SELECTORS),
            "fields": [
                {
                    "name": "href",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "text",
                    "type": "text"
                }
            ]
        }
        extraction_strategy = JsonCssExtractionStrategy(extraction_schema)
        
        # Configure crawler settings
        self.crawler_config = CrawlerRunConfig(
            extraction_strategy=extraction_strategy,
            cache_mode=CacheMode.BYPASS,  # Don't use cache for fresh results
            verbose=True,  # Enable detailed logging
            wait_for_images=True,  # Ensure lazy-loaded content is captured
            js_code=[EXPAND_MENUS_JS]  # Add JavaScript to expand nested menus
        )
        
        # Create output directory if it doesn't exist
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(colored(f"Created output directory: {OUTPUT_DIR}", "green"))

    async def extract_all_menu_links(self) -> List[str]:
        """Extract all menu links from the main page, including nested menus."""
        try:
            print(colored(f"Crawling main page: {self.start_url}", "cyan"))
            print(colored("Expanding all nested menus...", "yellow"))
            
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                # Get page content using crawl4ai
                result = await crawler.arun(
                    url=self.start_url,
                    config=self.crawler_config
                )

                if not result or not result.success:
                    print(colored(f"Failed to get page data", "red"))
                    if result and result.error_message:
                        print(colored(f"Error: {result.error_message}", "red"))
                    return []

                links = set()
                
                # Extract links from the result
                if hasattr(result, 'extracted_content') and result.extracted_content:
                    try:
                        menu_links = json.loads(result.extracted_content)
                        for link in menu_links:
                            href = link.get('href', '')
                            text = link.get('text', '').strip()
                            if href:
                                # Convert relative URLs to absolute
                                absolute_url = urljoin(self.start_url, href)
                                # Only include internal documentation links
                                if absolute_url.startswith(self.start_url):
                                    links.add(absolute_url)
                                    print(colored(f"Found link: {text} -> {absolute_url}", "green"))
                    except json.JSONDecodeError as e:
                        print(colored(f"Error parsing extracted content: {str(e)}", "red"))
                
                print(colored(f"\nFound {len(links)} unique menu links", "green"))
                return sorted(list(links))

        except Exception as e:
            print(colored(f"Error extracting menu links: {str(e)}", "red"))
            return []

    def save_results(self, results: dict) -> str:
        """Save crawling results to a JSON file using the same naming pattern as single_url_crawler."""
        try:
            # Generate filename using the same pattern
            filename_prefix = get_filename_prefix(self.start_url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_menu_links_{timestamp}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            
            print(colored(f"\n✓ Menu links saved to: {filepath}", "green"))
            return filepath
            
        except Exception as e:
            print(colored(f"\n✗ Error saving menu links: {str(e)}", "red"))
            return None

    async def crawl(self):
        """Main crawling method."""
        try:
            # Extract all menu links from the main page
            menu_links = await self.extract_all_menu_links()

            # Save results
            results = {
                "start_url": self.start_url,
                "total_links_found": len(menu_links),
                "menu_links": menu_links
            }

            self.save_results(results)

            print(colored(f"\nCrawling completed!", "green"))
            print(colored(f"Total unique menu links found: {len(menu_links)}", "green"))

        except Exception as e:
            print(colored(f"Error during crawling: {str(e)}", "red"))

async def main():
    try:
        crawler = DocsMenuCrawler(BASE_URL)
        await crawler.crawl()
    except Exception as e:
        print(colored(f"Error in main: {str(e)}", "red"))

if __name__ == "__main__":
    print(colored("Starting documentation menu crawler...", "cyan"))
    asyncio.run(main()) 