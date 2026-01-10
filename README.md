# Blog Evaluator with Gemini AI

A Python application that fetches blog posts from the web and evaluates them using the Gemini API (`gemini-2.5-flash-lite` model). Includes integration with Miniflux RSS reader for batch processing.

## Features

- Fetch and extract blog content using trafilatura
- Evaluate blogs with AI-powered ratings and reasoning
- Unique blog ID generation to prevent duplicate evaluations
- Batch processing of Miniflux RSS feed entries
- Automatic rate limiting (10 requests per minute)
- Output saved to organized files in `resources/` folder

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Gemini API key as an environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

To get an API key, visit: https://makersuite.google.com/app/apikey

3. (Optional) For Miniflux integration, ensure PostgreSQL is running locally with the `miniflux` database.

### PostgreSQL Database Access

To access the Miniflux PostgreSQL database:

```bash
# Switch to root user
su

# Switch to postgres system user
su - postgres

# Connect to miniflux database
psql -d miniflux
```

## Usage

### Process Miniflux Entries (Batch Mode)

Process all entries from your local Miniflux database:

```bash
python process_miniflux.py
```

This will:
- Connect to PostgreSQL (database: `miniflux`)
- Fetch all entries from the `entries` table
- Evaluate each blog post URL using Gemini
- Save results to `resources/{blog_id}.txt`
- Skip already evaluated blogs automatically
- Respect rate limits (6 second delay between requests)

**Configuration:**
Edit database credentials in `process_miniflux.py` if needed:
```python
db_config = {
    'database': 'miniflux',
    'user': 'miniflux',
    'password': '',  # Add password if needed
    'host': 'localhost',
    'port': 5432
}
```

### Evaluate Individual Blog Posts

```python
from gemini_prompt import evaluate_blog

result = evaluate_blog("https://example.com/blog-post")
print(f"Blog ID: {result['blog_id']}")
print(f"Saved to: {result['file_path']}")
print(result['evaluation'])
```

### With Custom Evaluation Criteria

```python
from gemini_prompt import evaluate_blog

criteria = "Analyze this blog post for technical accuracy and readability."
result = evaluate_blog("https://example.com/blog-post", evaluation_criteria=criteria)
```

### Just Fetch Blog Content

```python
from gemini_prompt import fetch_blog

content = fetch_blog("https://example.com/blog-post")
print(content)
```

### Direct Gemini API Call

```python
from gemini_prompt import call_gemini

response = call_gemini("Your prompt here")
print(response)
```

## Output Format

Each evaluation is saved to `resources/{blog_id}.txt` with the following structure:

```
URL: https://example.com/blog-post
Blog ID: a1b2c3d4e5f6

======================================================================

BLOG CONTENT:
======================================================================
[Full blog text content]

======================================================================

EVALUATION:
======================================================================
SUMMARY:
[2-3 sentence summary]

RATING:
[1-10 numerical rating]

REASONING:
[Detailed explanation of the rating]
```

## Rate Limiting

The Gemini API allows 10 requests per minute. The batch processor automatically:
- Enforces a 6-second delay between new evaluations
- Skips already-evaluated blogs (no API call needed)
- Displays progress and statistics

## Project Structure

```
project-miniflux-rating/
├── gemini_prompt.py      # Core evaluation functions
├── process_miniflux.py   # Miniflux batch processor
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── resources/           # Evaluation output files
    └── {blog_id}.txt    # Individual blog evaluations
```
