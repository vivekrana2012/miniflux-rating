#!/usr/bin/env python3
"""
Entry updater - handles Miniflux entry updates based on quality.
"""

from rating_parser import categorize_quality
from logger import logger


def prepare_entry_updates(entries_with_ratings):
    """
    Prepare entry updates based on quality ratings.
    
    Args:
        entries_with_ratings (list): List of dicts with 'id', 'rating', 'existing_tags'
    
    Returns:
        list: Prepared entries data for update
    """
    entries_to_update = []
    
    for entry in entries_with_ratings:
        rating = entry['rating']
        quality = categorize_quality(rating)
        
        update_data = {
            'entry_id': entry['id'],
            'existing_tags': entry.get('existing_tags', []),
            'new_tags': [f"LLM:rating={rating}", f"LLM:quality={quality}"]
        }
        
        # Mark low quality entries as read
        if quality == 'low':
            update_data['status'] = 'read'
        
        entries_to_update.append(update_data)
    
    return entries_to_update


def update_miniflux_entries(miniflux_service, entries_with_ratings):
    """
    Update Miniflux entries with quality tags and status.
    
    Args:
        miniflux_service (MinifluxService): Miniflux service instance
        entries_with_ratings (list): List of dicts with 'id', 'rating', 'existing_tags'
    
    Returns:
        dict: Statistics about updates
    """
    if not entries_with_ratings:
        return {'total': 0, 'high': 0, 'mid': 0, 'low': 0}
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Updating {len(entries_with_ratings)} Miniflux entries...")
    logger.info(f"{'='*70}")
    
    # Count by quality
    stats = {'total': 0, 'high': 0, 'mid': 0, 'low': 0}
    for entry in entries_with_ratings:
        quality = categorize_quality(entry['rating'])
        stats[quality] += 1
        stats['total'] += 1
    
    # Prepare and send updates
    entries_to_update = prepare_entry_updates(entries_with_ratings)
    miniflux_service.update_entries(entries_to_update)
    
    logger.info(f"✓ Updated {stats['total']} entries")
    logger.info(f"  High quality: {stats['high']}")
    logger.info(f"  Mid quality: {stats['mid']}")
    logger.info(f"  Low quality: {stats['low']} (marked as read)")
    
    return stats
