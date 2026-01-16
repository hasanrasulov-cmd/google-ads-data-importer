"""
Example: Import data from API.

This example demonstrates fetching data from an API and saving it to the database.
"""
import requests
from typing import List, Dict, Any
from app.services.base_importer import BaseImporter
from app.services.database import db_manager
from app.logger_config import get_logger

logger = get_logger(__name__)


class APIImporter(BaseImporter):
    """
    Example for importing data from API.
    
    This class fetches data from an API and saves it to the database.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.api_url = self.config.get("api_url", "https://api.example.com/data")
        self.api_key = self.config.get("api_key", "")
        self.table_name = self.config.get("table_name", "imported_data")
    
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from API.
        """
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.get(self.api_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # If API returns a list, return it directly
            if isinstance(data, list):
                return data
            
            # If it returns a dict with a "data" key
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            
            # Otherwise return empty list
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return []
    
    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform API data to database-compatible format.
        """
        transformed = []
        
        for record in data:
            try:
                transformed_record = {
                    "external_id": record.get("id"),
                    "name": record.get("name", "").strip(),
                    "email": record.get("email", "").lower().strip(),
                    "status": record.get("status", "active"),
                    "created_at": record.get("created_at") or record.get("date"),
                    "metadata": record  # Store original data as JSON
                }
                transformed.append(transformed_record)
            except Exception as e:
                logger.error(f"Error transforming record: {str(e)}")
                self.stats["errors"] += 1
        
        return transformed
    
    def save_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Save data to database.
        """
        if not self.validate_data(data):
            return False
        
        try:
            query = f"""
                INSERT INTO {self.table_name} 
                (external_id, name, email, status, created_at, metadata)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (external_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    status = EXCLUDED.status,
                    updated_at = NOW()
            """
            
            data_tuples = [
                (
                    record["external_id"],
                    record["name"],
                    record["email"],
                    record["status"],
                    record["created_at"],
                    str(record["metadata"])  # JSON string
                )
                for record in data
            ]
            
            rows_affected = db_manager.execute_batch(query, data_tuples)
            logger.info(f"Saved {rows_affected} records to {self.table_name}")
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}", exc_info=True)
            return False
