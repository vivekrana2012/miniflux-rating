#!/usr/bin/env python3
"""
File storage - handles saving evaluation results to files.
"""

import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "resources")


def save_evaluation(url, blog_id, content, evaluation, output_dir=None):
    """
    Save blog evaluation to a text file.
    
    Args:
        url (str): The blog URL
        blog_id (str): Unique blog identifier
        content (str): Blog content
        evaluation (str): Gemini evaluation
        output_dir (str): Directory to save files (default: script_dir/resources)
    
    Returns:
        str: Path to the saved file
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    # Create resources directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output file path
    output_file = os.path.join(output_dir, f"{blog_id}.txt")
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"URL: {url}\n")
        f.write(f"Blog ID: {blog_id}\n")
        f.write("=" * 70 + "\n")
        f.write("\nBLOG CONTENT:\n")
        f.write("=" * 70 + "\n")
        f.write(content)
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("\nEVALUATION:\n")
        f.write("=" * 70 + "\n")
        f.write(evaluation)
        f.write("\n")
    
    return output_file


def load_evaluation(blog_id, output_dir=None):
    """
    Load existing evaluation from file.
    
    Args:
        blog_id (str): Unique blog identifier
        output_dir (str): Directory containing files (default: script_dir/resources)
    
    Returns:
        dict or None: {'content': str, 'evaluation': str} or None if not found
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    output_file = os.path.join(output_dir, f"{blog_id}.txt")
    
    if not os.path.exists(output_file):
        return None
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse existing content
    parts = content.split('\n' + '='*70 + '\n')
    
    return {
        'content': parts[1] if len(parts) > 1 else '',
        'evaluation': parts[2] if len(parts) > 2 else '',
        'file_path': output_file
    }
