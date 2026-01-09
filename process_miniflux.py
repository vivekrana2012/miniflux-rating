#!/usr/bin/env python3
"""
Script to process Miniflux entries and generate ratings using Gemini API.
Connects to local PostgreSQL database and processes feed entries.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import time
from gemini_prompt import evaluate_blog

def connect_to_db(database="miniflux", user="miniflux", password="", host="localhost", port=5432):
    """
    Connect to PostgreSQL database.
    
    Args:
        database (str): Database name
        user (str): Database user
        password (str): Database password
        host (str): Database host
        port (int): Database port
    
    Returns:
        connection: PostgreSQL connection object
    """
    try:
        conn = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port
        )
        print(f"✓ Connected to database: {database}")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

def get_entries(conn, limit=None, processed_ids=None):
    """
    Fetch entries from the database.
    
    Args:
        conn: Database connection
        limit (int, optional): Limit number of entries to fetch
        processed_ids (set, optional): Set of already processed blog IDs to skip
    
    Returns:
        list: List of entry dictionaries
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = "SELECT id, title, url FROM entries ORDER BY id"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    entries = cursor.fetchall()
    cursor.close()
    
    print(f"✓ Found {len(entries)} entries in database\n")
    return entries

def process_entries(conn, limit=None, delay=6):
    """
    Process all entries from Miniflux database.
    
    Args:
        conn: Database connection
        limit (int, optional): Limit number of entries to process
        delay (int): Delay in seconds between API calls (default: 6 to respect 10 req/min limit)
    
    Returns:
        dict: Statistics about the processing
    """
    entries = get_entries(conn, limit)
    
    stats = {
        'total': len(entries),
        'processed': 0,
        'skipped': 0,
        'errors': 0
    }
    
    for i, entry in enumerate(entries, 1):
        entry_id = entry['id']
        title = entry.get('title', 'No title')
        url = entry['url']
        
        print(f"\n[{i}/{stats['total']}] Processing entry {entry_id}")
        print(f"Title: {title}")
        print(f"URL: {url}")
        print("-" * 70)
        
        try:
            result = evaluate_blog(url)
            
            if result['is_new']:
                stats['processed'] += 1
                print(f"✓ New evaluation completed")
            else:
                stats['skipped'] += 1
                print(f"✓ Already evaluated, skipped")
            
            print(f"Blog ID: {result['blog_id']}")
            print(f"File: {result['file_path']}")
            
            # Add delay between API calls to avoid rate limiting
            if result['is_new'] and i < stats['total']:
                print(f"\nWaiting {delay}s before next API call...")
                time.sleep(delay)
                
        except Exception as e:
            stats['errors'] += 1
            print(f"✗ Error processing entry {entry_id}: {e}")
            continue
    
    return stats

def main():
    """
    Main function to process Miniflux entries.
    """
    print("=" * 70)
    print("Miniflux Entry Processor")
    print("=" * 70)
    print()
    
    # Database connection parameters
    # Modify these if your setup is different
    db_config = {
        'database': 'miniflux',
        'user': 'miniflux',
        'password': '',  # Add password if needed
        'host': 'localhost',
        'port': 5432
    }
    
    try:
        # Connect to database
        conn = connect_to_db(**db_config)
        
        # Process entries (6 second delay = 10 requests per minute max)
        # Set limit=10 to test with first 10 entries, or limit=None for all
        stats = process_entries(conn, limit=None, delay=10)
        
        # Close connection
        conn.close()
        
        # Print summary
        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Total entries: {stats['total']}")
        print(f"Newly processed: {stats['processed']}")
        print(f"Already evaluated (skipped): {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
