#!/usr/bin/env python3
"""
Blog ID generator - creates unique identifiers from URLs.
"""

import hashlib


def generate_blog_id(url):
    """
    Generate a unique identifier for a blog URL using hash.
    
    Args:
        url (str): The URL of the blog post
    
    Returns:
        str: A unique identifier (first 12 characters of SHA256 hash)
    """
    return hashlib.sha256(url.encode()).hexdigest()[:12]
