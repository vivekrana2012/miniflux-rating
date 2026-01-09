#!/usr/bin/env python3
"""
Script to call the Gemini API using the gemini-2.5-flash-lite model.
Fetches blog posts from the web using trafilatura and evaluates them.
"""

import os
import hashlib
import trafilatura
from google import genai

def call_gemini(prompt, api_key=None):
    """
    Call the Gemini API with a prompt.
    
    Args:
        prompt (str): The prompt to send to the model
        api_key (str, optional): API key. If None, reads from GEMINI_API_KEY env var
    
    Returns:
        str: The model's response
    """
    # Configure API key
    if api_key is None:
        api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        raise ValueError("API key not provided. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
    
    # Initialize the client
    client = genai.Client(api_key=api_key)
    
    # Generate response
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    
    return response.text

def generate_blog_id(url):
    """
    Generate a unique identifier for a blog URL using hash.
    
    Args:
        url (str): The URL of the blog post
    
    Returns:
        str: A unique identifier (first 12 characters of SHA256 hash)
    """
    return hashlib.sha256(url.encode()).hexdigest()[:12]

def fetch_blog(url):
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

def evaluate_blog(url, evaluation_criteria=None, api_key=None, output_dir="resources"):
    """
    Fetch a blog post and evaluate it using Gemini.
    Saves output to a file in the resources folder.
    
    Args:
        url (str): The URL of the blog post to evaluate
        evaluation_criteria (str, optional): Specific criteria for evaluation
        api_key (str, optional): API key for Gemini
        output_dir (str): Directory to save output files (default: "resources")
    
    Returns:
        dict: Contains 'blog_id', 'file_path', 'content', 'evaluation', and 'is_new'
    """
    # Generate unique blog ID
    blog_id = generate_blog_id(url)
    
    # Create resources directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output file path
    output_file = os.path.join(output_dir, f"{blog_id}.txt")
    
    # Check if blog has already been evaluated
    if os.path.exists(output_file):
        print(f"Blog already evaluated (ID: {blog_id})")
        print(f"Reading existing evaluation from: {output_file}\n")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse existing content
        parts = content.split('\n' + '='*70 + '\n')
        return {
            'blog_id': blog_id,
            'file_path': output_file,
            'content': parts[1] if len(parts) > 1 else '',
            'evaluation': parts[2] if len(parts) > 2 else '',
            'is_new': False
        }
    
    print(f"Blog ID: {blog_id}")
    print(f"Fetching blog from: {url}")
    blog_content = fetch_blog(url)
    print(f"Fetched {len(blog_content)} characters\n")
    
    # Create evaluation prompt
    if evaluation_criteria:
        prompt = f"{evaluation_criteria}\n\nBlog content:\n{blog_content}"
    else:
        prompt = f"""Please evaluate this blog post and provide your response in the following format:

SUMMARY:
[A brief 2-3 sentence summary of the blog post]

RATING:
[A numerical rating from 1-10]

REASONING:
[Detailed explanation of why you gave this rating, covering aspects like content quality, writing style, depth of analysis, practical value, and overall effectiveness]

Blog content:
{blog_content}"""
    
    print("Sending to Gemini for evaluation...\n")
    evaluation = call_gemini(prompt, api_key)
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"URL: {url}\n")
        f.write(f"Blog ID: {blog_id}\n")
        f.write("=" * 70 + "\n")
        f.write("\nBLOG CONTENT:\n")
        f.write("=" * 70 + "\n")
        f.write(blog_content)
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("\nEVALUATION:\n")
        f.write("=" * 70 + "\n")
        f.write(evaluation)
        f.write("\n")
    
    print(f"Evaluation saved to: {output_file}\n")
    
    return {
        'blog_id': blog_id,
        'file_path': output_file,
        'content': blog_content,
        'evaluation': evaluation,
        'is_new': True
    }

def main():
    """
    Example usage: Fetch and evaluate a blog post.
    """
    # Example URL - replace with your blog URL
    url = "https://cedardb.com/blog/german_strings/"  # Replace with actual blog URL
    
    try:
        result = evaluate_blog(url)
        
        if result['is_new']:
            print(f"✓ New blog evaluation completed")
        else:
            print(f"✓ Retrieved existing evaluation")
        
        print(f"Blog ID: {result['blog_id']}")
        print(f"Saved to: {result['file_path']}")
        print("\nEvaluation preview:")
        print("=" * 70)
        print(result['evaluation'][:300] + "..." if len(result['evaluation']) > 300 else result['evaluation'])
        print("=" * 70)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTo use this script, provide a valid blog URL.")
        print("Example:")
        print('  python gemini_prompt.py')
        print('\nOr import and use directly:')
        print('  from gemini_prompt import evaluate_blog')
        print('  result = evaluate_blog("https://your-blog-url.com")')

if __name__ == "__main__":
    main()
