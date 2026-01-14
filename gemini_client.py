#!/usr/bin/env python3
"""
Gemini API client - handles API calls with retry logic.
"""

import os
import time
from google import genai
from logger import logger


def call_gemini(prompt, api_key=None, max_retries=5, model='gemma-3-4b-it'):
    """
    Call the Gemini API with a prompt, with exponential backoff for 503 errors.
    
    Args:
        prompt (str): The prompt to send to the model
        api_key (str, optional): API key. If None, reads from GEMINI_API_KEY env var
        max_retries (int): Maximum number of retries for 503 errors (default: 5)
        model (str): The model to use (default: 'gemma-3-4b-it')
    
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
                model=model,
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
    return f"""Please evaluate this blog post using a STRICT rating scale. Be critical and discerning.

RATING GUIDELINES:
8-10: EXCEPTIONAL - Reserved ONLY for truly profound content:
  - Deep life lessons with transformative insights
  - Rigorous technical analysis with novel research or findings
  - Original thought that challenges conventional wisdom
  - Simply being well-written or based on something is NOT enough
  
6-7: STRONG - High quality but not groundbreaking:
  - Well-researched technical content with good depth
  - Practical insights with clear value
  - Good analysis but not revolutionary
  
4-5: AVERAGE - Competent but unremarkable:
  - Standard technical tutorials or explanations
  - Surface-level analysis
  - Derivative content without unique perspective
  
1-3: WEAK - Poor quality or minimal value:
  - Superficial content
  - Poorly written or organized
  - Little practical or intellectual value

Provide your response in the following format:

SUMMARY:
[A brief 2-3 sentence summary of the blog post]

RATING:
[A numerical rating from 1-10]

REASONING:
[Detailed explanation of why you gave this rating. Be specific about what makes it profound (or not), the depth of analysis, originality of thought, and practical value. For ratings above 8, clearly explain what makes this content exceptional and transformative.]

Blog content:
{blog_content}"""
