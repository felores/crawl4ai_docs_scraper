import os
import sys
import asyncio
import re
import argparse
from datetime import datetime
from termcolor import colored
from crawl4ai import *

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
        str: Generated filename prefix
    """
    # Remove protocol and split URL parts
    clean_url = url.split('://')[1]
    url_parts = clean_url.split('/')
    
    # Get domain parts
    domain_parts = url_parts[0].split('.')
    
    # Extract main domain name (ignoring TLD)
    main_domain = domain_parts[-2]
    
    # Start building the prefix with domain
    prefix_parts = [main_domain]
    
    # Add subdomain if exists
    if len(domain_parts) > 2:
        subdomain = domain_parts[0]
        if subdomain != main_domain:
            prefix_parts.append(subdomain)
    
    # Add all path segments
    if len(url_parts) > 1:
        path_segments = [segment for segment in url_parts[1:] if segment]
        for segment in path_segments:
            # Clean up segment (remove special characters, convert to lowercase)
            clean_segment = re.sub(r'[^a-zA-Z0-9]', '', segment.lower())
            if clean_segment and clean_segment != main_domain:
                prefix_parts.append(clean_segment)
    
    # Join all parts with underscore
    return '_'.join(prefix_parts)

def process_markdown_content(content: str, url: str) -> str:
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

def save_markdown_content(content: str, url: str) -> str:
    """Save markdown content to a file"""
    try:
        # Generate filename prefix from URL
        filename_prefix = get_filename_prefix(url)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.md"
        filepath = os.path.join("scraped_docs", filename)
        
        # Create scraped_docs directory if it doesn't exist
        os.makedirs("scraped_docs", exist_ok=True)
        
        processed_content = process_markdown_content(content, url)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(processed_content)
        
        print(colored(f"\n✓ Markdown content saved to: {filepath}", "green"))
        return filepath
    except Exception as e:
        print(colored(f"\n✗ Error saving markdown content: {str(e)}", "red"))
        return None

async def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Crawl a single URL and generate markdown documentation')
    parser.add_argument('url', type=str, help='Target documentation URL to crawl')
    args = parser.parse_args()

    try:
        print(colored("\n=== Starting Single URL Crawl ===", "cyan"))
        print(colored(f"\nCrawling URL: {args.url}", "yellow"))
        
        browser_config = BrowserConfig(headless=True, verbose=True)
        async with AsyncWebCrawler(config=browser_config) as crawler:
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                markdown_generator=DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0)
                )
            )
            
            result = await crawler.arun(
                url=args.url,
                config=crawler_config
            )
            
            if result.success:
                print(colored("\n✓ Successfully crawled URL", "green"))
                print(colored(f"Content length: {len(result.markdown.raw_markdown)} characters", "cyan"))
                save_markdown_content(result.markdown.raw_markdown, args.url)
            else:
                print(colored(f"\n✗ Failed to crawl URL: {result.error_message}", "red"))
                
    except Exception as e:
        print(colored(f"\n✗ Error during crawl: {str(e)}", "red"))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())