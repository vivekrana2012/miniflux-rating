#!/usr/bin/env python3
"""
Blog evaluator - main logic for evaluating blog posts.
"""

from blog_id import generate_blog_id
from content_fetcher import fetch_blog_content
from gemini_client import call_gemini, create_evaluation_prompt
from rating_parser import parse_rating
from file_storage import save_evaluation, load_evaluation
from logger import logger


def evaluate_blog(url, entry_id=None, db_service=None, output_dir=None):
    """
    Fetch a blog post and evaluate it using Gemini.
    
    Args:
        url (str): The URL of the blog post to evaluate
        entry_id (int, optional): Miniflux entry ID to save in database
        db_service (PostgresService, optional): Database service instance
        output_dir (str, optional): Directory to save output files (default: script_dir/resources)
    
    Returns:
        dict: Contains 'blog_id', 'file_path', 'rating', and 'is_new'
    """
    # Generate unique blog ID
    blog_id = generate_blog_id(url)
    
    # Check if blog has already been evaluated
    existing = load_evaluation(blog_id, output_dir)
    if existing:
        logger.info(f"Blog already evaluated (ID: {blog_id})")
        logger.info(f"Reading existing evaluation from: {existing['file_path']}")
        
        rating = parse_rating(existing['evaluation'])
        return {
            'blog_id': blog_id,
            'file_path': existing['file_path'],
            'rating': rating,
            'is_new': False
        }
    
    # Fetch and evaluate new blog
    logger.info(f"Blog ID: {blog_id}")
    logger.info(f"Fetching blog from: {url}")
    content = fetch_blog_content(url)
    logger.info(f"Fetched {len(content)} characters")
    
    logger.info("Sending to Gemini for evaluation...")
    prompt = create_evaluation_prompt(content)
    evaluation = call_gemini(prompt)
    
    # Parse rating
    rating = parse_rating(evaluation)
    
    # Save to file
    file_path = save_evaluation(url, blog_id, content, evaluation, output_dir)
    logger.info(f"Evaluation saved to: {file_path}")
    
    # Save to database if provided
    if entry_id is not None and db_service is not None:
        db_service.save_rating(blog_id, entry_id)
    
    return {
        'blog_id': blog_id,
        'file_path': file_path,
        'rating': rating,
        'is_new': True
    }
