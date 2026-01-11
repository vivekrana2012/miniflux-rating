#!/usr/bin/env python3
"""
Entry updater - handles Miniflux entry updates based on quality.
"""

from rating_parser import categorize_quality
from logger import logger


def prepare_entry_update(entry_data):
    """
    Prepare update data for a Miniflux entry status.
    
    Args:
        entry_data (dict): Dict with 'id', 'rating'
    
    Returns:
        dict: Update data with 'entry_id', 'should_mark_read', 'quality'
    """
    if not entry_data:
        return None
    
    entry_id = entry_data['id']
    rating = entry_data['rating']
    quality = categorize_quality(rating)
    
    # Mark low and mid quality entries as read
    should_mark_read = quality in ['low', 'mid']
    
    return {
        'entry_id': entry_id,
        'should_mark_read': should_mark_read,
        'quality': quality
    }


def batch_update_entries(miniflux_service, updates_list):
    """
    Batch update Miniflux entries status.
    
    Args:
        miniflux_service (MinifluxService): Miniflux service instance
        updates_list (list): List of update data dicts from prepare_entry_update
    
    Returns:
        dict: Stats about updates
    """
    if not updates_list:
        return {'marked_read': 0}
    
    stats = {'marked_read': 0}
    
    # Batch mark low/mid quality entries as read
    entries_to_mark_read = [u['entry_id'] for u in updates_list if u['should_mark_read']]
    
    if entries_to_mark_read:
        logger.info(f"Batch marking {len(entries_to_mark_read)} low/mid quality entries as read...")
        if miniflux_service.batch_update_entries(entries_to_mark_read, status='read'):
            stats['marked_read'] = len(entries_to_mark_read)
        else:
            logger.warning(f"⚠ Failed to batch mark entries as read")
    
    return stats
