"""
Database connection and utility functions.

This module provides database connection management for the data importer.
"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from app.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
from app.logger_config import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """
    Database connection manager using connection pooling.
    
    This class manages database connections and provides utility methods
    for common database operations.
    """
    
    _connection_pool: Optional[pool.ThreadedConnectionPool] = None
    
    def __init__(self):
        """Initialize database manager."""
        self.min_conn = 1
        self.max_conn = 5
        self._create_pool()
    
    def _create_pool(self):
        """Create connection pool."""
        try:
            self._connection_pool = pool.ThreadedConnectionPool(
                minconn=self.min_conn,
                maxconn=self.max_conn,
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Error creating database connection pool: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection from the pool.
        
        Usage:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM table")
                    result = cur.fetchall()
        """
        if self._connection_pool is None:
            self._create_pool()
        
        conn = self._connection_pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            self._connection_pool.putconn(conn)
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            List of dictionaries containing query results
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.rowcount
    
    def execute_batch(self, query: str, data: List[tuple]) -> int:
        """
        Execute a batch insert/update.
        
        Args:
            query: SQL query string with placeholders
            data: List of tuples containing data for each row
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                from psycopg2.extras import execute_batch
                execute_batch(cur, query, data)
                return cur.rowcount
    
    def close_pool(self):
        """Close all connections in the pool."""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("Database connection pool closed")


# Global database manager instance
db_manager = DatabaseManager()
