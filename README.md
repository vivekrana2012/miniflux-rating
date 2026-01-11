# Blog Evaluator with Gemini AI

A modular Python application that fetches blog posts from the web and evaluates them using the Gemini API (`gemini-2.5-flash-lite` model). Includes integration with Miniflux RSS reader for automated batch processing with quality-based filtering.

## Features

- 🤖 AI-powered blog evaluation with Gemini API
- 📊 Automatic quality categorization (high/mid/low based on ratings)
- 🔄 Exponential backoff retry logic for API 503 errors
- 💾 PostgreSQL database integration for rating persistence
- 📦 Modular architecture with focused, single-purpose modules
- 🚫 Duplicate prevention with unique blog ID generation
- ⏱️ Batch processing with configurable rate limiting
- 📁 Organized file storage in `resources/` folder
- 📝 Automatic logging with rotation (1 MB max per file)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Gemini API (required)
export GEMINI_API_KEY="your-api-key-here"

# Miniflux API (required for batch processing)
export MINIFLUX_URL="http://127.0.0.1:8081"
export MINIFLUX_API_TOKEN="your-miniflux-api-token"

# PostgreSQL Database (required for rating persistence)
export MINIFLUX_DB_NAME="miniflux"
export MINIFLUX_DB_USER="miniflux"
export MINIFLUX_DB_PASSWORD=""
export MINIFLUX_DB_HOST="localhost"
export MINIFLUX_DB_PORT="5432"
```

**Getting API Keys:**
- Gemini API: https://makersuite.google.com/app/apikey
- Miniflux API Token: Settings → API Keys → Create New Token

3. Create the database schema:
```bash
psql -d miniflux -f schema.sql
```

## Usage

### Process Miniflux Entries (Main Script)

Process unread entries from Miniflux in batches:

```bash
python miniflux.py
```

This will:
- Fetch 10 unread entries per batch (oldest first)
- Evaluate each blog post URL using Gemini API
- Save evaluations to `resources/{blog_id}.txt`
- Store ratings in PostgreSQL database
- Automatically mark low and mid quality entries as "read"
- Wait 60 seconds between batches
- Skip already evaluated blogs

**Adjust batch settings** in [miniflux.py](miniflux.py):
```python
stats = process_entries(
    miniflux_service=miniflux,
    db_service=postgres,
    batch_size=10,        # Entries per batch
    batch_delay=60,       # Seconds between batches
    max_entries=None      # Set to number or None for all
)
```

### Evaluate Individual Blog Posts

```python
from blog_evaluator import evaluate_blog

result = evaluate_blog("https://example.com/blog-post")
print(f"Blog ID: {result['blog_id']}")
print(f"Rating: {result['rating']}/10")
print(f"Saved to: {result['file_path']}")
print(f"New evaluation: {result['is_new']}")
```

### Use Individual Modules

```python
# Fetch blog content
from content_fetcher import fetch_blog_content
content = fetch_blog_content("https://example.com/blog-post")

# Call Gemini API with retry logic
from gemini_client import call_gemini
response = call_gemini("Your prompt here")

# Parse rating from evaluation text
from rating_parser import parse_rating, categorize_quality
rating = parse_rating(evaluation_text)
quality = categorize_quality(rating)  # Returns 'high', 'mid', or 'low'

# Generate unique blog ID
from blog_id import generate_blog_id
blog_id = generate_blog_id("https://example.com/blog")

# Save/load evaluations
from file_storage import save_evaluation, load_evaluation
file_path = save_evaluation(url, blog_id, content, evaluation)
existing = load_evaluation(blog_id)
```

## Output Format

Each evaluation is saved to `resources/{blog_id}.txt`:

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
[Detailed explanation covering content quality, writing style, 
depth of analysis, practical value, and overall effectiveness]
```

**Database Schema** (`ratings` table):
```sql
CREATE TABLE ratings (
    id VARCHAR(12) PRIMARY KEY,      -- Blog hash ID
    entry_id BIGINT UNIQUE NOT NULL, -- Miniflux entry ID
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Quality-Based Filtering

Entries are automatically marked as read based on their rating:

| Rating | Quality Level | Behavior |
|--------|---------------|----------|
| 8-10 | High | Kept as unread |
| 6-7 | Mid | Marked as read |
| 1-5 | Low | Marked as read |

## Error Handling

**Gemini API 503 Errors**: Automatic exponential backoff retry
- Retry 1: Wait 60 seconds
- Retry 2: Wait 120 seconds
- Retry 3: Wait 240 seconds
- Retry 4: Wait 480 seconds
- Retry 5: Wait 960 seconds

**Rate Limiting**: Default batch processing waits 60 seconds between batches of 10 entries

## Logging

All operations are automatically logged to `logs/miniflux_rating.log` with:
- **Automatic rotation**: When log file reaches 1 MB, it rotates to `miniflux_rating.log.1`
- **10 backup files**: Keeps up to 10 rotated log files
- **Console & file output**: Logs are written to both console and file
- **Timestamp & level**: Each log entry includes timestamp and severity level

**Log levels:**
- `INFO`: Normal operations (fetching, processing, saving)
- `WARNING`: Non-critical issues (could not parse rating, API retries)
- `ERROR`: Failures (connection errors, API failures, exceptions)

**Example log entries:**
```
2026-01-10 14:30:15 - miniflux_rating - INFO - Connecting to Miniflux at: http://127.0.0.1:8081
2026-01-10 14:30:16 - miniflux_rating - INFO - ✓ Connected to Miniflux API as: admin
2026-01-10 14:30:17 - miniflux_rating - INFO - [1] Processing entry 12345
2026-01-10 14:30:25 - miniflux_rating - INFO - ✓ New evaluation completed
2026-01-10 14:30:25 - miniflux_rating - INFO - Rating: 8/10 (Quality: mid)
```

## Project Structure

```
project-miniflux-rating/
├── miniflux.py              # Main orchestration script (177 lines)
├── miniflux_service.py      # Miniflux API client (165 lines)
├── logger.py                # Logging configuration with rotation (53 lines)
├── gemini_client.py         # Gemini API with retry (87 lines)
├── blog_evaluator.py        # Blog evaluation logic (72 lines)
├── entry_updater.py         # Miniflux entry updates (77 lines)
├── file_storage.py          # File save/load operations (72 lines)
├── postgres_service.py      # Database operations (73 lines)
├── rating_parser.py         # Rating extraction & categorization (45 lines)
├── content_fetcher.py       # Blog content fetching (28 lines)
├── blog_id.py               # Unique ID generation (19 lines)
├── schema.sql               # Database schema
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── logs/                    # Log files (auto-created)
│   ├── miniflux_rating.log  # Current log file
│   ├── miniflux_rating.log.1
│   └── ...                  # Up to 10 backup files
└── resources/               # Evaluation output files
    └── {blog_id}.txt        # Individual blog evaluations
```

### Module Responsibilities

**Core Modules:**
- `blog_id.py` - Generate unique SHA256-based identifiers from URLs
- `content_fetcher.py` - Extract blog content using Trafilatura
- `rating_parser.py` - Parse ratings from text and categorize quality
- `file_storage.py` - Save/load evaluation results to/from files
- `gemini_client.py` - Gemini API calls with exponential backoff
- `blog_evaluator.py` - Orchestrate fetch → evaluate → save workflow

**Service Layer:**
- `postgres_service.py` - Database CRUD operations for ratings
- `miniflux_service.py` - Miniflux REST API client
- `entry_updater.py` - Mark entries as read based on quality
- `logger.py` - Centralized logging configuration with rotation

**Main Script:**
- `miniflux.py` - Batch process unread entries with rate limiting
