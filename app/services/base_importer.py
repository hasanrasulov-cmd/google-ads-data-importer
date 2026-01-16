"""
Base importer class for data import operations.

This is a template class that should be extended for specific data import needs.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.logger_config import get_logger

logger = get_logger(__name__)


class BaseImporter(ABC):
    """
    Base class for data importers.
    
    This template provides a standard structure for implementing data importers.
    Subclasses should implement the abstract methods to define specific import logic.
    
    Usage:
        class MyImporter(BaseImporter):
            def fetch_data(self) -> List[Dict]:
                # Fetch data from source
                pass
            
            def transform_data(self, data: List[Dict]) -> List[Dict]:
                # Transform data to target format
                pass
            
            def save_data(self, data: List[Dict]) -> bool:
                # Save data to database
                pass
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the importer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger(self.__class__.__name__)
        self.stats = {
            "fetched": 0,
            "transformed": 0,
            "saved": 0,
            "errors": 0
        }
    
    def run(self) -> Dict[str, Any]:
        """
        Main execution method that orchestrates the import process.
        
        Returns:
            Dictionary with import statistics and status
        """
        try:
            self.logger.info(f"Starting {self.__class__.__name__} import process")
            
            # Step 1: Fetch data
            self.logger.info("Fetching data from source...")
            raw_data = self.fetch_data()
            self.stats["fetched"] = len(raw_data) if raw_data else 0
            self.logger.info(f"Fetched {self.stats['fetched']} records")
            
            if not raw_data:
                self.logger.warning("No data fetched from source")
                return self._get_result()
            
            # Step 2: Transform data
            self.logger.info("Transforming data...")
            transformed_data = self.transform_data(raw_data)
            self.stats["transformed"] = len(transformed_data) if transformed_data else 0
            self.logger.info(f"Transformed {self.stats['transformed']} records")
            
            if not transformed_data:
                self.logger.warning("No data after transformation")
                return self._get_result()
            
            # Step 3: Save data
            self.logger.info("Saving data to database...")
            success = self.save_data(transformed_data)
            
            if success:
                self.stats["saved"] = len(transformed_data)
                self.logger.info(f"Successfully saved {self.stats['saved']} records")
            else:
                self.logger.error("Failed to save data")
                self.stats["errors"] += 1
            
            return self._get_result()
            
        except Exception as e:
            self.logger.error(f"Error during import process: {str(e)}", exc_info=True)
            self.stats["errors"] += 1
            return self._get_result()
    
    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from the source.
        
        This method should be implemented by subclasses to define how data
        is retrieved from the source (API, file, database, etc.).
        
        Returns:
            List of dictionaries containing raw data
        """
        pass
    
    @abstractmethod
    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform raw data into the target format.
        
        This method should be implemented by subclasses to define how data
        is transformed from source format to target format.
        
        Args:
            data: List of raw data dictionaries
            
        Returns:
            List of transformed data dictionaries
        """
        pass
    
    @abstractmethod
    def save_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Save transformed data to the target database.
        
        This method should be implemented by subclasses to define how data
        is saved to the database.
        
        Args:
            data: List of transformed data dictionaries
            
        Returns:
            True if save was successful, False otherwise
        """
        pass
    
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate data before saving.
        
        Override this method in subclasses to add custom validation logic.
        
        Args:
            data: List of data dictionaries to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        if not data:
            self.logger.warning("Data is empty")
            return False
        return True
    
    def _get_result(self) -> Dict[str, Any]:
        """
        Get result dictionary with statistics.
        
        Returns:
            Dictionary with import statistics
        """
        return {
            "status": "success" if self.stats["errors"] == 0 else "partial",
            "stats": self.stats.copy(),
            "importer": self.__class__.__name__
        }
