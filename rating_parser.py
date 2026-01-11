#!/usr/bin/env python3
"""
Rating parser - extracts numerical ratings from evaluation text.
"""

import re


def parse_rating(evaluation_text):
    """
    Extract numerical rating from evaluation text.
    
    Supports various markdown and formatting styles:
    - Plain: RATING: 8
    - Bold: **RATING:** 8/10
    - Headers: ## RATING: 7
    - Mixed: ## **RATING:** 8 / 10
    - Flexible spacing and newlines
    
    Args:
        evaluation_text (str): The evaluation text from Gemini
    
    Returns:
        int or None: The rating as an integer (1-10), or None if not found
    """
    # Flexible pattern that handles:
    # - 0-3 # (markdown headers: #, ##, ###)
    # - 0-3 * (markdown bold: *, **, ***)
    # - Multiple spaces, newlines (\n, \r\n)
    # - Optional /10 suffix with flexible spacing
    match = re.search(r'#{0,3}\s*\*{0,3}\s*RATING\s*:\s*\*{0,3}\s*[\n\r]*\s*(\d+)(?:\s*/\s*10)?', evaluation_text, re.IGNORECASE)
    if match:
        rating = int(match.group(1))
        # Ensure rating is in valid range
        if 1 <= rating <= 10:
            return rating
    
    return None


def categorize_quality(rating):
    """
    Categorize a rating into quality levels.
    
    Args:
        rating (int): Numeric rating from 1-10
    
    Returns:
        str: 'high' (8-10), 'mid' (6-7), or 'low' (1-5)
    """
    if rating >= 8:
        return 'high'
    elif rating >= 6:
        return 'mid'
    else:
        return 'low'
