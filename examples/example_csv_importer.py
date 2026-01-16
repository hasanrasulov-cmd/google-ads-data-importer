"""
Example: Import data from CSV file.

This example demonstrates reading data from a CSV file and saving it to the database.
"""
import csv
from typing import List, Dict, Any
from app.services.base_importer import BaseImporter
from app.services.database import db_manager
from app.logger_config import get_logger

logger = get_logger(__name__)


class CSVImporter(BaseImporter):
    """
    Example for importing data from CSV file.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.file_path = self.config.get("file_path", "data.csv")
        self.table_name = self.config.get("table_name", "imported_data")
        self.delimiter = self.config.get("delimiter", ",")
        self.encoding = self.config.get("encoding", "utf-8")
    
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Read data from CSV file.
        """
        try:
            data = []
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                for row in reader:
                    data.append(row)
            
            logger.info(f"Read {len(data)} records from {self.file_path}")
            return data
            
        except FileNotFoundError:
            logger.error(f"File not found: {self.file_path}")
            return []
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            return []
    
    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform CSV data to database-compatible format.
        """
        transformed = []
        
        for record in data:
            try:
                # Map CSV column names to database column names
                transformed_record = {
                    "external_id": record.get("ID") or record.get("id"),
                    "name": record.get("Name") or record.get("name", "").strip(),
                    "email": record.get("Email") or record.get("email", "").lower().strip(),
                    "phone": record.get("Phone") or record.get("phone", "").strip(),
                    "status": record.get("Status") or record.get("status", "active"),
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
                (external_id, name, email, phone, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (external_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    status = EXCLUDED.status,
                    updated_at = NOW()
            """
            
            data_tuples = [
                (
                    record["external_id"],
                    record["name"],
                    record["email"],
                    record.get("phone"),
                    record["status"]
                )
                for record in data
            ]
            
            rows_affected = db_manager.execute_batch(query, data_tuples)
            logger.info(f"Saved {rows_affected} records to {self.table_name}")
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}", exc_info=True)
            return False
