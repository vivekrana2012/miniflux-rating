#!/usr/bin/env python3
"""
Entry updater - handles Miniflux entry updates based on quality.
"""

from rating_parser import categorize_quality
from logger import logger


def update_miniflux_entries(miniflux_service, entry_data):
    """
    Update a Miniflux entry with quality tags and status.
    
    Args:
        miniflux_service (MinifluxService): Miniflux service instance
        entry_data (dict): Dict with 'id', 'rating', 'existing_tags'
    
    Returns:
        bool: True if successful
    """
    if not entry_data:
        return False
    
    entry_id = entry_data['id']
    rating = entry_data['rating']
    quality = categorize_quality(rating)
    
    # Prepare update data
    existing_tags = entry_data.get('existing_tags', []) or []
    new_tags = [f"LLM:rating={rating}", f"LLM:quality={quality}"]
    
    update_data = {
        'entry_id': entry_id,
        'existing_tags': existing_tags,
        'new_tags': new_tags
    }
    
    # Mark low and mid quality entries as read
    if quality in ['low', 'mid']:
        update_data['status'] = 'read'
    
    # Update this entry
    success = miniflux_service.update_entry(update_data)
    
    if success:
        logger.info(f"✓ Updated entry {entry_id} with {quality} quality tags")
    else:
        logger.warning(f"⚠ Failed to update entry {entry_id}")
    
    return success
