#!/usr/bin/env python3
"""
Crawl4AI Documentation Scraper - Main CLI
Unified command-line interface for all crawling modes
"""

import sys
import argparse
import asyncio
from termcolor import colored

# Import crawler modules
import single_url_crawler
import multi_url_crawler
import split_url_crawler
import sitemap_crawler
import menu_crawler


def print_banner():
    """Print CLI banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║         Crawl4AI Documentation Scraper CLI                ║
║         Clean, AI-ready documentation extraction          ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(colored(banner, "cyan"))


def create_parser():
    """Create the main argument parser with subcommands"""
    parser = argparse.ArgumentParser(
        description='Crawl4AI Documentation Scraper - Extract clean documentation from websites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract single page
  crawl4ai single https://docs.example.com/page

  # Extract single page to custom directory
  crawl4ai single https://docs.example.com/page --output-dir ~/Desktop/docs

  # Extract menu links
  crawl4ai menu https://docs.example.com

  # Crawl multiple URLs (individual files per page)
  crawl4ai split urls.json --output-prefix my-project --output-dir ~/Desktop/docs

  # Crawl multiple URLs (single consolidated file)
  crawl4ai multi urls.txt --output-prefix myproject --output-dir ~/Desktop/docs

  # Crawl from sitemap
  crawl4ai sitemap https://example.com/sitemap.xml --output-dir ~/Desktop/docs

All commands support --output-dir to save files anywhere on your system.

For more information, visit: https://github.com/felores/crawl4ai_docs_scraper
        """
    )

    # Create subparsers for each command
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Single URL crawler
    single_parser = subparsers.add_parser(
        'single',
        help='Extract content from a single URL',
        description='Crawl a single documentation page and save as Markdown'
    )
    single_parser.add_argument('url', type=str, help='Target documentation URL')
    single_parser.add_argument('--output-dir', type=str, default='scraped_docs',
                               help='Directory to save output (default: scraped_docs)')

    # Menu crawler
    menu_parser = subparsers.add_parser(
        'menu',
        help='Extract all menu links from documentation',
        description='Extract navigation menu structure and save as JSON'
    )
    menu_parser.add_argument('url', type=str, help='Documentation site URL')
    menu_parser.add_argument('--selectors', type=str, nargs='+',
                             help='Custom CSS selectors for menu items')
    menu_parser.add_argument('--output-dir', type=str, default='input_files',
                             help='Directory to save output (default: input_files)')

    # Multi URL crawler (consolidated)
    multi_parser = subparsers.add_parser(
        'multi',
        help='Crawl multiple URLs into single file',
        description='Process multiple URLs and combine into one Markdown file'
    )
    multi_parser.add_argument('urls_file', type=str,
                              help='File containing URLs (.txt or .json)')
    multi_parser.add_argument('--output-prefix', type=str,
                              help='Custom prefix for output filename')
    multi_parser.add_argument('--output-dir', type=str, default='scraped_docs',
                              help='Directory to save output (default: scraped_docs)')

    # Split URL crawler (individual files)
    split_parser = subparsers.add_parser(
        'split',
        help='Crawl multiple URLs into separate files',
        description='Process multiple URLs and save each as individual Markdown file'
    )
    split_parser.add_argument('urls_file', type=str,
                              help='File containing URLs (.txt or .json)')
    split_parser.add_argument('--output-prefix', type=str,
                              help='Custom prefix for output directory name')
    split_parser.add_argument('--output-dir', type=str, default='scraped_docs',
                              help='Base directory to save output (default: scraped_docs)')

    # Sitemap crawler
    sitemap_parser = subparsers.add_parser(
        'sitemap',
        help='Crawl URLs from sitemap.xml',
        description='Discover and crawl URLs from sitemap'
    )
    sitemap_parser.add_argument('sitemap_url', type=str,
                                help='URL of sitemap.xml')
    sitemap_parser.add_argument('--max-depth', type=int, default=10,
                                help='Maximum sitemap recursion depth (default: 10)')
    sitemap_parser.add_argument('--patterns', type=str, nargs='+',
                                help='URL patterns to include (e.g., "/docs/*")')
    sitemap_parser.add_argument('--output-dir', type=str, default='scraped_docs',
                                help='Directory to save output (default: scraped_docs)')

    return parser


async def run_single(args):
    """Run single URL crawler"""
    print(colored("\n=== Single URL Crawler ===", "cyan"))
    print(colored(f"URL: {args.url}", "yellow"))
    print(colored(f"Output: {args.output_dir}", "yellow"))

    # Create a mock args object for the crawler
    class CrawlerArgs:
        def __init__(self, url, output_dir):
            self.url = url
            self.output_dir = output_dir

    crawler_args = CrawlerArgs(args.url, args.output_dir)

    # Replace sys.argv temporarily to pass args
    original_argv = sys.argv
    sys.argv = ['single_url_crawler', args.url, '--output-dir', args.output_dir]

    try:
        await single_url_crawler.main()
    finally:
        sys.argv = original_argv


async def run_menu(args):
    """Run menu crawler"""
    print(colored("\n=== Menu Crawler ===", "cyan"))
    print(colored(f"URL: {args.url}", "yellow"))
    print(colored(f"Output: {args.output_dir}", "yellow"))

    # Build sys.argv for menu crawler
    original_argv = sys.argv
    sys.argv = ['menu_crawler', args.url, '--output-dir', args.output_dir]

    if args.selectors:
        sys.argv.extend(['--selectors'] + args.selectors)

    try:
        await menu_crawler.main()
    finally:
        sys.argv = original_argv


async def run_multi(args):
    """Run multi URL crawler"""
    print(colored("\n=== Multi URL Crawler ===", "cyan"))
    print(colored(f"Input: {args.urls_file}", "yellow"))
    print(colored(f"Output: {args.output_dir}", "yellow"))

    original_argv = sys.argv
    sys.argv = ['multi_url_crawler', args.urls_file, '--output-dir', args.output_dir]

    if args.output_prefix:
        sys.argv.extend(['--output-prefix', args.output_prefix])

    try:
        await multi_url_crawler.main()
    finally:
        sys.argv = original_argv


async def run_split(args):
    """Run split URL crawler"""
    print(colored("\n=== Split URL Crawler ===", "cyan"))
    print(colored(f"Input: {args.urls_file}", "yellow"))
    print(colored(f"Output: {args.output_dir}", "yellow"))

    original_argv = sys.argv
    sys.argv = ['split_url_crawler', args.urls_file, '--output-dir', args.output_dir]

    if args.output_prefix:
        sys.argv.extend(['--output-prefix', args.output_prefix])

    try:
        await split_url_crawler.main()
    finally:
        sys.argv = original_argv


async def run_sitemap(args):
    """Run sitemap crawler"""
    print(colored("\n=== Sitemap Crawler ===", "cyan"))
    print(colored(f"Sitemap: {args.sitemap_url}", "yellow"))
    print(colored(f"Output: {args.output_dir}", "yellow"))

    original_argv = sys.argv
    sys.argv = ['sitemap_crawler', args.sitemap_url,
                '--max-depth', str(args.max_depth),
                '--output-dir', args.output_dir]

    if args.patterns:
        sys.argv.extend(['--patterns'] + args.patterns)

    try:
        await sitemap_crawler.main()
    finally:
        sys.argv = original_argv


def main():
    """Main entry point for CLI"""
    parser = create_parser()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Show help if no command specified
    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)

    print_banner()

    # Route to appropriate crawler
    try:
        if args.command == 'single':
            asyncio.run(run_single(args))
        elif args.command == 'menu':
            asyncio.run(run_menu(args))
        elif args.command == 'multi':
            asyncio.run(run_multi(args))
        elif args.command == 'split':
            asyncio.run(run_split(args))
        elif args.command == 'sitemap':
            asyncio.run(run_sitemap(args))
        else:
            print(colored(f"Unknown command: {args.command}", "red"))
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print(colored("\n\nCrawling interrupted by user", "yellow"))
        sys.exit(130)
    except Exception as e:
        print(colored(f"\nError: {str(e)}", "red"))
        sys.exit(1)


if __name__ == '__main__':
    main()
