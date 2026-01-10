#!/usr/bin/env python3
"""
PostgreSQL Service - handles database interactions for ratings storage.
"""

import os
import psycopg2
from logger import logger


class PostgresService:
    """Service class for interacting with PostgreSQL database."""
    
    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        """
        Initialize PostgreSQL service.
        
        Args:
            dbname (str): Database name (default: from env or 'miniflux')
            user (str): Database user (default: from env or 'miniflux')
            password (str): Database password (default: from env or '')
            host (str): Database host (default: from env or 'localhost')
            port (str): Database port (default: from env or '5432')
        """
        self.dbname = dbname or os.getenv('MINIFLUX_DB_NAME', 'miniflux')
        self.user = user or os.getenv('MINIFLUX_DB_USER', 'miniflux')
        self.password = password or os.getenv('MINIFLUX_DB_PASSWORD', '')
        self.host = host or os.getenv('MINIFLUX_DB_HOST', 'localhost')
        self.port = port or os.getenv('MINIFLUX_DB_PORT', '5432')
    
    def _get_connection(self):
        """Create and return a database connection."""
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
    
    def save_rating(self, blog_id, entry_id):
        """
        Save blog evaluation record to the ratings table.
        
        Args:
            blog_id (str): The hash ID of the blog
            entry_id (int): The Miniflux entry ID
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO ratings (id, entry_id) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
                (blog_id, entry_id)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✓ Saved to database: blog_id={blog_id}, entry_id={entry_id}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠ Warning: Could not save to database: {e}")
            return False

