#!/usr/bin/env python3
"""
Gemini API client - handles API calls with retry logic.
"""

import os
import time
from google import genai
from logger import logger


def call_gemini(prompt, api_key=None, max_retries=5):
    """
    Call the Gemini API with a prompt, with exponential backoff for 503 errors.
    
    Args:
        prompt (str): The prompt to send to the model
        api_key (str, optional): API key. If None, reads from GEMINI_API_KEY env var
        max_retries (int): Maximum number of retries for 503 errors (default: 5)
    
    Returns:
        str: The model's response
    """
    # Configure API key
    if api_key is None:
        api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        raise ValueError("API key not provided. Set GEMINI_API_KEY environment variable.")
    
    # Initialize the client
    client = genai.Client(api_key=api_key)
    
    retry_count = 0
    while retry_count <= max_retries:
        try:
            # Generate response
            response = client.models.generate_content(
                model='gemma-3-4b-it',
                contents=prompt
            )
            return response.text
            
        except Exception as e:
            # Check if it's a 503 error
            error_message = str(e)
            if '503' in error_message or 'Service Unavailable' in error_message:
                retry_count += 1
                if retry_count <= max_retries:
                    # Exponential backoff: 60, 120, 240, 480, 960 seconds
                    wait_time = 60 * (2 ** (retry_count - 1))
                    logger.warning(f"⚠ Gemini API returned 503 (Service Unavailable)")
                    logger.info(f"Retry {retry_count}/{max_retries} - Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"✗ Max retries ({max_retries}) reached. API still unavailable.")
                    raise
            else:
                # For other errors, raise immediately
                raise


def create_evaluation_prompt(blog_content):
    """
    Create a prompt for evaluating blog content.
    
    Args:
        blog_content (str): The blog content to evaluate
    
    Returns:
        str: The formatted prompt
    """
    return f"""Please evaluate this blog post and provide your response in the following format:

SUMMARY:
[A brief 2-3 sentence summary of the blog post]

RATING:
[A numerical rating from 1-10]

REASONING:
[Detailed explanation of why you gave this rating, covering aspects like content quality, writing style, depth of analysis, practical value, and overall effectiveness]

Blog content:
{blog_content}"""
