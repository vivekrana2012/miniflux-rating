#!/usr/bin/env python3
"""
Backward compatibility wrapper - imports from refactored modules.
"""

# Re-export functions for backward compatibility
from gemini_client import call_gemini, create_evaluation_prompt
from blog_id import generate_blog_id
from content_fetcher import fetch_blog_content as fetch_blog
from rating_parser import parse_rating
from blog_evaluator import evaluate_blog

__all__ = [
    'call_gemini',
    'create_evaluation_prompt',
    'generate_blog_id',
    'fetch_blog',
    'parse_rating',
    'evaluate_blog'
]
