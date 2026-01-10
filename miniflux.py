#!/usr/bin/env python3
"""
Script to process Miniflux entries and generate ratings using Gemini API.
Connects to Miniflux API and processes feed entries.
"""

import time
from miniflux_service import MinifluxService
from gemini import evaluate_blog


def process_entries(miniflux_service, batch_size=10, batch_delay=60, max_entries=None):
    """
    Process unread entries from Miniflux API in batches.
    Fetches entries oldest first, processes them, waits, then fetches the next batch.
    
    Args:
        miniflux_service (MinifluxService): Miniflux service instance
        batch_size (int): Number of entries to fetch per batch (default: 10)
        batch_delay (int): Delay in seconds between batches (default: 60)
        max_entries (int, optional): Maximum number of entries to process (None = all)
    
    Returns:
        dict: Statistics about the processing
    """
    stats = {
        'total': 0,
        'processed': 0,
        'skipped': 0,
        'errors': 0,
        'batches': 0
    }
    
    overall_count = 0
    offset = 0
    
    while True:
        # Fetch unread entries ordered by published_at ascending (oldest first)
        print(f"\n{'='*70}")
        print(f"Fetching batch {stats['batches'] + 1} of unread entries...")
        print(f"{'='*70}")
        
        entries = miniflux_service.get_entries(
            offset=offset,
            limit=batch_size,
            status="unread",
            order="published_at",
            direction="asc"
        )
        
        # Stop if no more entries
        if not entries:
            print("✓ No more unread entries to process")
            break
        
        stats['batches'] += 1
        stats['total'] += len(entries)
        
        # Process each entry in the batch
        for entry in entries:
            overall_count += 1
            entry_id = entry['id']
            title = entry.get('title', 'No title')
            url = entry['url']
            
            print(f"\n[{overall_count}] Processing entry {entry_id}")
            print(f"Title: {title}")
            print(f"URL: {url}")
            print("-" * 70)
            
            try:
                # Call Gemini API and write response to file
                result = evaluate_blog(url)
                
                if result['is_new']:
                    stats['processed'] += 1
                    print(f"✓ New evaluation completed")
                else:
                    stats['skipped'] += 1
                    print(f"✓ Already evaluated, skipped")
                
                print(f"Blog ID: {result['blog_id']}")
                print(f"File: {result['file_path']}")
                    
            except Exception as e:
                stats['errors'] += 1
                print(f"✗ Error processing entry {entry_id}: {e}")
                continue
            
            # Check if we've reached max_entries limit
            if max_entries and overall_count >= max_entries:
                print(f"\n✓ Reached maximum entry limit ({max_entries})")
                return stats
        
        # Wait before fetching next batch (unless we've processed all entries or hit limit)
        print(f"\n{'='*70}")
        print(f"Batch {stats['batches']} complete. Processed {len(entries)} entries.")
        
        # Increment offset for next batch
        offset += batch_size
        
        # Check if there might be more entries
        if len(entries) == batch_size:
            print(f"Waiting {batch_delay} seconds before fetching next batch...")
            print(f"{'='*70}")
            time.sleep(batch_delay)
        else:
            print("Last batch was smaller than batch size, likely no more entries.")
            print(f"{'='*70}")
            break
    
    return stats

def main():
    """
    Main function to process Miniflux entries.
    """
    print("=" * 70)
    print("Miniflux Entry Processor")
    print("=" * 70)
    print()
    
    try:
        # Initialize Miniflux service (reads from env vars)
        miniflux = MinifluxService()
        
        # Process entries
        # Fetches 10 unread entries (oldest first), processes them, waits 60 seconds, repeats
        # max_entries=None processes all entries, or set a number to limit
        stats = process_entries(
            miniflux_service=miniflux,
            batch_size=10,
            batch_delay=60,
            max_entries=2
        )
        
        # Print summary
        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Total batches: {stats['batches']}")
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
