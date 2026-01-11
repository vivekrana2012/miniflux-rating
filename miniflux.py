#!/usr/bin/env python3
"""
Main script to process Miniflux entries and generate ratings using Gemini API.
"""

import time
from miniflux_service import MinifluxService
from postgres_service import PostgresService
from blog_evaluator import evaluate_blog
from entry_updater import update_miniflux_entries
from rating_parser import categorize_quality
from logger import logger


def process_entries(miniflux_service, db_service, batch_size=10, batch_delay=60, max_entries=None):
    """
    Process unread entries from Miniflux in batches.
    
    Args:
        miniflux_service (MinifluxService): Miniflux service instance
        db_service (PostgresService): PostgreSQL service instance
        batch_size (int): Entries per batch (default: 10)
        batch_delay (int): Delay between batches in seconds (default: 60)
        max_entries (int, optional): Maximum entries to process (None = all)
    
    Returns:
        dict: Processing statistics
    """
    stats = {
        'total': 0, 'processed': 0, 'skipped': 0, 'errors': 0, 'batches': 0,
        'high_quality': 0, 'mid_quality': 0, 'low_quality': 0
    }
    
    overall_count = 0
    offset = 0
    
    while True:
        logger.info("="*70)
        logger.info(f"Fetching batch {stats['batches'] + 1} of unread entries...")
        logger.info("="*70)
        
        entries = miniflux_service.get_entries(
            offset=offset,
            limit=batch_size,
            status="unread",
            order="published_at",
            direction="asc"
        )
        
        if not entries:
            logger.info("✓ No more unread entries")
            break
        
        stats['batches'] += 1
        stats['total'] += len(entries)
        
        # Process each entry
        for entry in entries:
            overall_count += 1
            if max_entries and overall_count > max_entries:
                return stats
            
            entry_id = entry['id']
            title = entry.get('title', 'No title')
            url = entry['url']
            existing_tags = entry.get('tags', [])
            
            logger.info(f"\n[{overall_count}] Processing entry {entry_id}")
            logger.info(f"Title: {title}")
            logger.info(f"URL: {url}")
            logger.info("-" * 70)
            
            try:
                result = evaluate_blog(url, entry_id=entry_id, db_service=db_service)
                
                if result['is_new']:
                    stats['processed'] += 1
                    logger.info("✓ New evaluation completed")
                else:
                    stats['skipped'] += 1
                    logger.info("✓ Already evaluated, skipped")
                
                rating = result.get('rating')
                if rating:
                    quality = categorize_quality(rating)
                    stats[f'{quality}_quality'] += 1
                    logger.info(f"Rating: {rating}/10 (Quality: {quality})")
                    
                    # Update this entry immediately
                    update_miniflux_entries(miniflux_service, {
                        'id': entry_id,
                        'rating': rating,
                        'existing_tags': existing_tags
                    })
                else:
                    logger.warning("⚠ Could not parse rating")
                
                logger.info(f"Blog ID: {result['blog_id']}")
                logger.info(f"File: {result['file_path']}")
                    
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"✗ Error: {e}", exc_info=True)
                continue
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Batch {stats['batches']} complete. Processed {len(entries)} entries.")
        
        # Move to next batch
        offset += batch_size
        
        if len(entries) == batch_size:
            logger.info(f"Waiting {batch_delay} seconds before next batch...")
            logger.info("="*70)
            time.sleep(batch_delay)
        else:
            logger.info("Last batch was smaller, no more entries.")
            logger.info("="*70)
            break
    
    return stats



def main():
    """Main function to process Miniflux entries."""
    logger.info("=" * 70)
    logger.info("Miniflux Entry Processor")
    logger.info("=" * 70)
    
    try:
        miniflux = MinifluxService()
        postgres = PostgresService()
        
        stats = process_entries(
            miniflux_service=miniflux,
            db_service=postgres,
            batch_size=10,
            batch_delay=60,
            max_entries=None  # Change to None to process all entries
        )
        
        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("PROCESSING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Total batches: {stats['batches']}")
        logger.info(f"Total entries: {stats['total']}")
        logger.info(f"Newly processed: {stats['processed']}")
        logger.info(f"Already evaluated: {stats['skipped']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info("\nQuality Distribution:")
        logger.info(f"  High (>8): {stats['high_quality']}")
        logger.info(f"  Mid (6-8): {stats['mid_quality']}")
        logger.info(f"  Low (<6): {stats['low_quality']}")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"\nFatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

