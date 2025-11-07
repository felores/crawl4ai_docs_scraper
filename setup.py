#!/usr/bin/env python3
"""
Crawl4AI Documentation Scraper
Setup script for package installation
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    filepath = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='crawl4ai-docs-scraper',
    version='1.0.0',
    description='A comprehensive Python toolkit for scraping documentation websites using Crawl4AI',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='Felo Restrepo',
    author_email='your-email@example.com',
    url='https://github.com/felores/crawl4ai_docs_scraper',
    license='MIT',

    # Package discovery
    py_modules=[
        'crawl4ai_cli',
        'crawl4ai_mcp',
        'single_url_crawler',
        'multi_url_crawler',
        'split_url_crawler',
        'sitemap_crawler',
        'menu_crawler'
    ],

    # Dependencies
    install_requires=read_requirements(),

    # Python version requirement
    python_requires='>=3.7',

    # Entry points for CLI commands
    entry_points={
        'console_scripts': [
            'crawl4ai=crawl4ai_cli:main',
            'crawl4ai-single=single_url_crawler:main',
            'crawl4ai-multi=multi_url_crawler:main',
            'crawl4ai-split=split_url_crawler:main',
            'crawl4ai-sitemap=sitemap_crawler:main',
            'crawl4ai-menu=menu_crawler:main',
        ],
    },

    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
    ],

    # Keywords
    keywords='web-scraping documentation crawl4ai markdown scraper docs',

    # Include package data
    include_package_data=True,

    # Project URLs
    project_urls={
        'Bug Reports': 'https://github.com/felores/crawl4ai_docs_scraper/issues',
        'Source': 'https://github.com/felores/crawl4ai_docs_scraper',
    },
)
