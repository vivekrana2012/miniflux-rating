#!/usr/bin/env python3
"""
Rating parser - extracts numerical ratings from evaluation text.
"""

import re


def parse_rating(evaluation_text):
    """
    Extract numerical rating from evaluation text.
    
    Args:
        evaluation_text (str): The evaluation text from Gemini
    
    Returns:
        int or None: The rating as an integer (1-10), or None if not found
    """
    # Look for various rating formats: "RATING:", "**RATING:**", "## RATING:", etc.
    # More flexible pattern to handle spaces and markdown formatting
    match = re.search(r'#{0,3}\s*\*{0,2}\s*RATING\s*:\s*\*{0,2}\s*[\n\r]*\s*(\d+)(?:\s*/\s*10)?', evaluation_text, re.IGNORECASE)
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
        str: 'high' (>8), 'mid' (6-8), or 'low' (<6)
    """
    if rating >= 8:
        return 'high'
    elif rating >= 6:
        return 'mid'
    else:
        return 'low'
