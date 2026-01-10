#!/usr/bin/env python3
"""
Content fetcher - downloads and extracts blog content.
"""

import trafilatura


def fetch_blog_content(url):
    """
    Fetch and extract blog content from a URL using trafilatura.
    
    Args:
        url (str): The URL of the blog post to fetch
    
    Returns:
        str: The extracted text content from the blog post
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        raise ValueError(f"Could not fetch content from URL: {url}")
    
    # Extract main content
    text = trafilatura.extract(downloaded)
    if text is None:
        raise ValueError(f"Could not extract text content from URL: {url}")
    
    return text
