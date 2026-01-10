#!/usr/bin/env python3
"""
Miniflux API Service
Handles all interactions with the Miniflux RSS reader API.
"""

import requests
import os

class MinifluxService:
    """Service class for interacting with Miniflux API."""
    
    def __init__(self, base_url=None, api_token=None):
        """
        Initialize Miniflux service.
        
        Args:
            base_url (str): Base URL of Miniflux instance (default: from env or http://localhost:8080)
            api_token (str): API token for authentication (default: from MINIFLUX_API_TOKEN env var)
        """
        self.base_url = base_url or os.getenv('MINIFLUX_URL', 'http://127.0.0.1:8081')
        self.api_token = api_token or os.getenv('MINIFLUX_API_TOKEN')
        
        if not self.api_token:
            raise ValueError(
                "API token not provided. Set MINIFLUX_API_TOKEN environment variable "
                "or pass api_token parameter."
            )
        
        self.headers = {
            'X-Auth-Token': self.api_token,
            'Content-Type': 'application/json'
        }
        
        self._verify_connection()
    
    def _verify_connection(self):
        """Verify connection to Miniflux API and authenticate."""
        try:
            print(f"Connecting to Miniflux at: {self.base_url}")
            response = requests.get(
                f"{self.base_url}/v1/me", 
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            user_info = response.json()
            print(f"✓ Connected to Miniflux API as: {user_info.get('username', 'unknown')}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            print(f"Make sure Miniflux is running at {self.base_url}")
            raise
        except requests.exceptions.Timeout as e:
            print(f"Timeout error: {e}")
            print(f"The server at {self.base_url} took too long to respond")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Miniflux API: {e}")
            raise
    
    def get_entries(self, offset=0, limit=10, status="unread", order="published_at", 
                    direction="desc", **kwargs):
        """
        Fetch entries from Miniflux API with pagination support.
        
        Args:
            offset (int): Offset for pagination (default: 0)
            limit (int): Number of entries to fetch (default: 10)
            status (str): Entry status filter (unread, read, removed)
            order (str): Sort field (id, status, published_at, category_title, category_id)
            direction (str): Sort direction (asc, desc)
            **kwargs: Additional filters supported by Miniflux API:
                - before (unix timestamp)
                - after (unix timestamp)
                - published_before (unix timestamp)
                - published_after (unix timestamp)
                - changed_before (unix timestamp)
                - changed_after (unix timestamp)
                - before_entry_id (int64)
                - after_entry_id (int64)
                - starred (boolean)
                - search (str)
                - category_id (int)
        
        Returns:
            list: List of entry dictionaries
        """
        params = {
            'order': order,
            'direction': direction,
            'offset': offset,
            'limit': limit
        }
        
        if status:
            params['status'] = status
        
        # Add any additional filters passed via kwargs
        params.update(kwargs)
        
        try:
            response = requests.get(
                f"{self.base_url}/v1/entries", 
                headers=self.headers, 
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            entries = data.get('entries', [])
            print(f"✓ Fetched {len(entries)} entries (offset: {offset})")
            return entries
        except Exception as e:
            print(f"Error fetching entries: {e}")
            raise
