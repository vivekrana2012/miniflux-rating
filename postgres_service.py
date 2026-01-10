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
            user (str): Database user (default: from env or 'postgres')
            password (str): Database password (default: from env or None for peer auth)
            host (str): Database host (default: from env or None for Unix socket)
            port (str): Database port (default: from env or '5432')
        """
        self.dbname = dbname or os.getenv('MINIFLUX_DB_NAME', 'miniflux')
        self.user = user or os.getenv('MINIFLUX_DB_USER', 'postgres')
        self.password = password or os.getenv('MINIFLUX_DB_PASSWORD')
        self.host = host or os.getenv('MINIFLUX_DB_HOST')
        self.port = port or os.getenv('MINIFLUX_DB_PORT', '5432')
    
    def _get_connection(self):
        """Create and return a database connection."""
        # Build connection params, omitting None values for Unix socket auth
        conn_params = {'dbname': self.dbname, 'user': self.user}
        
        if self.password:
            conn_params['password'] = self.password
        if self.host:
            conn_params['host'] = self.host
        if self.port:
            conn_params['port'] = self.port
        
        return psycopg2.connect(**conn_params)
    
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

