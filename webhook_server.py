#!/usr/bin/env python3
"""
FastAPI webhook server for Miniflux new_entries events.
Receives webhook notifications and triggers blog evaluation.
"""

import os
import hmac
import hashlib
import threading
import time
from queue import Queue
from fastapi import FastAPI, Request, HTTPException, Header
from typing import Optional
from miniflux_service import MinifluxService
from postgres_service import PostgresService
from blog_evaluator import evaluate_blog
from entry_updater import prepare_entry_update, batch_update_entries
from rating_parser import categorize_quality
from logger import logger

app = FastAPI(title="Miniflux Rating Webhook")

# In-memory FIFO queue for webhook entries
entry_queue = Queue()

# Get webhook secret from environment
WEBHOOK_SECRET = os.getenv('MINIFLUX_WEBHOOK_SECRET')
if not WEBHOOK_SECRET:
    logger.warning("⚠ MINIFLUX_WEBHOOK_SECRET not set. Webhook signature validation will fail.")


def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verify HMAC-SHA256 signature from Miniflux webhook.
    
    Args:
        payload (bytes): Raw request body
        signature (str): HMAC signature from X-Miniflux-Signature header
    
    Returns:
        bool: True if signature is valid
    """
    if not WEBHOOK_SECRET:
        logger.error("✗ Webhook secret not configured")
        return False
    
    # Calculate expected HMAC
    expected_hmac = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_hmac, signature)


@app.post("/webhook")
async def miniflux_webhook(
    request: Request,
    x_miniflux_signature: Optional[str] = Header(None),
    x_miniflux_event_type: Optional[str] = Header(None)
):
    """
    Webhook endpoint for Miniflux events.
    
    Validates HMAC signature and processes new_entries events.
    """
    # Get raw request body for signature verification
    payload = await request.body()
    
    # Verify signature
    if not x_miniflux_signature:
        logger.error("✗ Missing X-Miniflux-Signature header")
        raise HTTPException(status_code=401, detail="Missing signature")
    
    if not verify_signature(payload, x_miniflux_signature):
        logger.error("✗ Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    logger.info("✓ Webhook signature verified")
    
    # Check event type
    if x_miniflux_event_type != "new_entries":
        logger.info(f"Ignoring event type: {x_miniflux_event_type}")
        return {"status": "ignored", "event_type": x_miniflux_event_type}
    
    # Parse JSON payload
    data = await request.json()
    entries = data.get('entries', [])
    
    logger.info(f"Received new_entries webhook with {len(entries)} entries")
    
    if not entries:
        return {"status": "success", "queued": 0}
    
    # Add entries to queue for background processing
    queued = 0
    for entry in entries:
        entry_id = entry.get('id')
        url = entry.get('url')
        title = entry.get('title', 'No title')
        
        if not url:
            logger.warning(f"⚠ Entry {entry_id} has no URL, skipping")
            continue
        
        # Add to queue
        entry_queue.put({
            'entry_id': entry_id,
            'url': url,
            'title': title
        })
        queued += 1
        logger.info(f"Queued entry {entry_id}: {title}")
    
    queue_size = entry_queue.qsize()
    logger.info(f"✓ Added {queued} entries to queue (current queue size: {queue_size})")
    
    return {
        "status": "success",
        "queued": queued,
        "queue_size": queue_size
    }


def process_queue():
    """
    Background task that polls the queue every minute and processes one entry.
    Uses gemma-3-12b-it model for webhook-based evaluations.
    """
    logger.info("Queue processor started - polling every 60 seconds")
    
    # Initialize services once
    try:
        miniflux = MinifluxService()
        postgres = PostgresService()
    except Exception as e:
        logger.error(f"✗ Failed to initialize services in queue processor: {e}")
        return
    
    while True:
        try:
            # Wait for 60 seconds before next poll
            time.sleep(60)
            
            # Check if queue has items
            if entry_queue.empty():
                continue
            
            # Get one entry from queue
            entry = entry_queue.get()
            entry_id = entry['entry_id']
            url = entry['url']
            title = entry['title']
            
            logger.info("=" * 70)
            logger.info(f"Processing queued entry {entry_id}: {title}")
            logger.info(f"Queue size: {entry_queue.qsize()}")
            logger.info("=" * 70)
            
            try:
                # Evaluate blog using webhook model
                result = evaluate_blog(
                    url, 
                    entry_id=entry_id, 
                    db_service=postgres,
                    model='gemma-3-12b-it'  # Webhook-specific model
                )
                
                if result['is_new']:
                    logger.info("✓ New evaluation completed")
                else:
                    logger.info("✓ Already evaluated, skipped")
                
                rating = result.get('rating')
                if rating:
                    quality = categorize_quality(rating)
                    logger.info(f"Rating: {rating}/10 (Quality: {quality})")
                    
                    # Prepare and execute update
                    update_data = prepare_entry_update({
                        'id': entry_id,
                        'rating': rating
                    })
                    if update_data:
                        batch_updates = [update_data]
                        update_stats = batch_update_entries(miniflux, batch_updates)
                        if update_stats['marked_read'] > 0:
                            logger.info(f"✓ Marked entry as read")
                else:
                    logger.warning("⚠ Could not parse rating")
                
            except Exception as e:
                logger.error(f"✗ Error processing queued entry {entry_id}: {e}", exc_info=True)
            finally:
                # Mark task as done
                entry_queue.task_done()
                
        except Exception as e:
            logger.error(f"✗ Error in queue processor: {e}", exc_info=True)
            time.sleep(60)  # Wait before retrying


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "queue_size": entry_queue.qsize()
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 9090
    port = int(os.getenv('WEBHOOK_PORT', '9090'))
    
    logger.info("=" * 70)
    logger.info("Miniflux Webhook Server")
    logger.info("=" * 70)
    logger.info(f"Starting server on port {port}")
    logger.info(f"Webhook endpoint: POST /webhook")
    logger.info(f"Health check: GET /health")
    logger.info(f"Model: gemma-3-12b-it (webhook queue)")
    logger.info("=" * 70)
    
    # Start queue processor in background thread
    processor_thread = threading.Thread(target=process_queue, daemon=True)
    processor_thread.start()
    logger.info("✓ Queue processor thread started")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
