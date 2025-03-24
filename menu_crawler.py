#!/usr/bin/env python3

import asyncio
from typing import List, Set
from termcolor import colored
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from urllib.parse import urljoin, urlparse
import json
import os
import sys
import argparse
from datetime import datetime
import re

# Constants
BASE_URL = "https://developers.cloudflare.com/agents/"
INPUT_DIR = "input_files"  # Changed from OUTPUT_DIR
MENU_SELECTORS = [
    # Traditional documentation selectors
    "nav a",                                  # General navigation links
    "[role='navigation'] a",                  # Role-based navigation
    ".sidebar a",                             # Common sidebar class
    "[class*='nav'] a",                       # Classes containing 'nav'
    "[class*='menu'] a",                      # Classes containing 'menu'
    "aside a",                                # Side navigation
    ".toc a",                                 # Table of contents
    
    # Modern framework selectors (Mintlify, Docusaurus, etc)
    "[class*='sidebar'] [role='navigation'] [class*='group'] a",  # Navigation groups
    "[class*='sidebar'] [role='navigation'] [class*='item'] a",   # Navigation items
    "[class*='sidebar'] [role='navigation'] [class*='link'] a",   # Direct links
    "[class*='sidebar'] [role='navigation'] div[class*='text']",  # Text items
    "[class*='sidebar'] [role='navigation'] [class*='nav-item']", # Nav items
    
    # Additional common patterns
    "[class*='docs-'] a",                     # Documentation-specific links
    "[class*='navigation'] a",                # Navigation containers
    "[class*='toc'] a",                       # Table of contents variations
    ".docNavigation a",                       # Documentation navigation
    "[class*='menu-item'] a",                 # Menu items
    
    # Client-side rendered navigation
    "[class*='sidebar'] a[href]",             # Any link in sidebar
    "[class*='sidebar'] [role='link']",       # ARIA role links
    "[class*='sidebar'] [role='menuitem']",   # Menu items
    "[class*='sidebar'] [role='treeitem']",   # Tree navigation items
    "[class*='sidebar'] [onclick]",           # Elements with click handlers
    "[class*='sidebar'] [class*='link']",     # Elements with link classes
    "a[href^='/']",                           # Root-relative links
    "a[href^='./']",                          # Relative links
    "a[href^='../']"                          # Parent-relative links
]

# JavaScript to expand nested menus
EXPAND_MENUS_JS = """
(async () => {
    // Wait for client-side rendering to complete
    await new Promise(r => setTimeout(r, 2000));
    
    // Function to expand all menu items
    async function expandAllMenus() {
        // Combined selectors for expandable menu items
        const expandableSelectors = [
            // Previous selectors...
            // Additional selectors for client-side rendered menus
            '[class*="sidebar"] button',
            '[class*="sidebar"] [role="button"]',
            '[class*="sidebar"] [aria-controls]',
            '[class*="sidebar"] [aria-expanded]',
            '[class*="sidebar"] [data-state]',
            '[class*="sidebar"] [class*="expand"]',
            '[class*="sidebar"] [class*="toggle"]',
            '[class*="sidebar"] [class*="collapse"]'
        ];
        
        let expanded = 0;
        let lastExpanded = -1;
        let attempts = 0;
        const maxAttempts = 10;  // Increased attempts for client-side rendering
        
        while (expanded !== lastExpanded && attempts < maxAttempts) {
            lastExpanded = expanded;
            attempts++;
            
            for (const selector of expandableSelectors) {
                const elements = document.querySelectorAll(selector);
                for (const el of elements) {
                    try {
                        // Click the element
                        el.click();
                        
                        // Try multiple expansion methods
                        el.setAttribute('aria-expanded', 'true');
                        el.setAttribute('data-state', 'open');
                        el.classList.add('expanded', 'show', 'active');
                        el.classList.remove('collapsed', 'closed');
                        
                        // Handle parent groups - multiple patterns
                        ['[class*="group"]', '[class*="parent"]', '[class*="submenu"]'].forEach(parentSelector => {
                            let parent = el.closest(parentSelector);
                            if (parent) {
                                parent.setAttribute('data-state', 'open');
                                parent.setAttribute('aria-expanded', 'true');
                                parent.classList.add('expanded', 'show', 'active');
                            }
                        });
                        
                        expanded++;
                        await new Promise(r => setTimeout(r, 200));  // Increased delay between clicks
                    } catch (e) {
                        continue;
                    }
                }
            }
            
            // Wait longer between attempts for client-side rendering
            await new Promise(r => setTimeout(r, 500));
        }
        
        // After expansion, try to convert text items to links if needed
        const textSelectors = [
            '[class*="sidebar"] [role="navigation"] [class*="text"]',
            '[class*="menu-item"]',
            '[class*="nav-item"]',
            '[class*="sidebar"] [role="menuitem"]',
            '[class*="sidebar"] [role="treeitem"]'
        ];
        
        textSelectors.forEach(selector => {
            const textItems = document.querySelectorAll(selector);
            textItems.forEach(item => {
                if (!item.querySelector('a') && item.textContent && item.textContent.trim()) {
                    const text = item.textContent.trim();
                    // Only create link if it doesn't already exist
                    if (!Array.from(item.children).some(child => child.tagName === 'A')) {
                        const link = document.createElement('a');
                        link.href = '#' + text.toLowerCase().replace(/[^a-z0-9]+/g, '-');
                        link.textContent = text;
                        item.appendChild(link);
                    }
                }
            });
        });
        
        return expanded;
    }
    
    const expandedCount = await expandAllMenus();
    // Final wait to ensure all client-side updates are complete
    await new Promise(r => setTimeout(r, 1000));
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
            viewport_height=1080,
            java_script_enabled=True  # Ensure JavaScript is enabled
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
                },
                {
                    "name": "onclick",
                    "type": "attribute",
                    "attribute": "onclick"
                },
                {
                    "name": "role",
                    "type": "attribute",
                    "attribute": "role"
                }
            ]
        }
        extraction_strategy = JsonCssExtractionStrategy(extraction_schema)
        
        # Configure crawler settings with proper wait conditions
        self.crawler_config = CrawlerRunConfig(
            extraction_strategy=extraction_strategy,
            cache_mode=CacheMode.BYPASS,  # Don't use cache for fresh results
            verbose=True,  # Enable detailed logging
            wait_for_images=True,  # Ensure lazy-loaded content is captured
            js_code=[
                # Initial wait for client-side rendering
                "await new Promise(r => setTimeout(r, 2000));",
                EXPAND_MENUS_JS
            ],  # Add JavaScript to expand nested menus
            wait_for="""js:() => {
                // Wait for sidebar and its content to be present
                const sidebar = document.querySelector('[class*="sidebar"]');
                if (!sidebar) return false;
                
                // Check if we have navigation items
                const hasNavItems = sidebar.querySelectorAll('a').length > 0;
                if (hasNavItems) return true;
                
                // If no nav items yet, check for loading indicators
                const isLoading = document.querySelector('[class*="loading"]') !== null;
                return !isLoading;  // Return true if not loading anymore
            }""",
            session_id="menu_crawler",  # Use a session to maintain state
            js_only=False  # We want full page load first
        )
        
        # Create output directory if it doesn't exist
        if not os.path.exists(INPUT_DIR):
            os.makedirs(INPUT_DIR)
            print(colored(f"Created output directory: {INPUT_DIR}", "green"))

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
                
                # Parse the base domain from start_url
                base_domain = urlparse(self.start_url).netloc
                
                # Add the base URL first (without trailing slash for consistency)
                base_url = self.start_url.rstrip('/')
                links.add(base_url)
                print(colored(f"Added base URL: {base_url}", "green"))
                
                # Extract links from the result
                if hasattr(result, 'extracted_content') and result.extracted_content:
                    try:
                        menu_links = json.loads(result.extracted_content)
                        for link in menu_links:
                            href = link.get('href', '')
                            text = link.get('text', '').strip()
                            
                            # Skip empty hrefs
                            if not href:
                                continue
                                
                            # Convert relative URLs to absolute
                            absolute_url = urljoin(self.start_url, href)
                            parsed_url = urlparse(absolute_url)
                            
                            # Accept internal links (same domain) that aren't anchors
                            if (parsed_url.netloc == base_domain and 
                                not href.startswith('#') and 
                                '#' not in absolute_url):
                                
                                # Remove any trailing slashes for consistency
                                absolute_url = absolute_url.rstrip('/')
                                
                                links.add(absolute_url)
                                print(colored(f"Found link: {text} -> {absolute_url}", "green"))
                            else:
                                print(colored(f"Skipping external or anchor link: {text} -> {href}", "yellow"))
                                
                    except json.JSONDecodeError as e:
                        print(colored(f"Error parsing extracted content: {str(e)}", "red"))
                
                print(colored(f"\nFound {len(links)} unique menu links", "green"))
                return sorted(list(links))

        except Exception as e:
            print(colored(f"Error extracting menu links: {str(e)}", "red"))
            return []

    def save_results(self, results: dict) -> str:
        """Save crawling results to a JSON file in the input_files directory."""
        try:
            # Create input_files directory if it doesn't exist
            os.makedirs(INPUT_DIR, exist_ok=True)
            
            # Generate filename using the same pattern
            filename_prefix = get_filename_prefix(self.start_url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_menu_links_{timestamp}.json"
            filepath = os.path.join(INPUT_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            
            print(colored(f"\n✓ Menu links saved to: {filepath}", "green"))
            print(colored("\nTo crawl these URLs with multi_url_crawler.py, run:", "cyan"))
            print(colored(f"python multi_url_crawler.py --urls {filename}", "yellow"))
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
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract menu links from a documentation website')
    parser.add_argument('url', type=str, help='Documentation site URL to crawl')
    parser.add_argument('--selectors', type=str, nargs='+', help='Custom menu selectors (optional)')
    args = parser.parse_args()

    try:
        # Update menu selectors if custom ones provided
        if args.selectors:
            print(colored("Using custom menu selectors:", "cyan"))
            for selector in args.selectors:
                print(colored(f"  {selector}", "yellow"))
            global MENU_SELECTORS
            MENU_SELECTORS = args.selectors

        crawler = DocsMenuCrawler(args.url)
        await crawler.crawl()
    except Exception as e:
        print(colored(f"Error in main: {str(e)}", "red"))
        sys.exit(1)

if __name__ == "__main__":
    print(colored("Starting documentation menu crawler...", "cyan"))
    asyncio.run(main()) 