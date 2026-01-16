# Data Import Template Guide

This project is a template for data import operations. Follow the steps below to customize it for importing your own data.

## Project Structure

```
app/
├── config.py                 # Configuration settings
├── lambda_handler.py         # AWS Lambda entry point
├── logger_config.py          # Logging settings
└── services/
    ├── base_importer.py      # Base class - template for all importers
    ├── database.py           # Database connection manager
    └── intaker_importer.py   # Example importer implementation
```

## How to Use

### 1. BaseImporter Class

`BaseImporter` is the base class for all data importers. It provides the following methods:

- `fetch_data()` - fetch data from source
- `transform_data()` - transform data
- `save_data()` - save data to database
- `run()` - orchestrate the entire process

### 2. Creating a New Importer

Extend `BaseImporter` to create your own importer:

```python
from app.services.base_importer import BaseImporter
from typing import List, Dict, Any

class MyCustomImporter(BaseImporter):
    def fetch_data(self) -> List[Dict[str, Any]]:
        # Write your data fetching logic here
        # Examples: from API, file, another database
        return []
    
    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Transform the data
        # Examples: rename fields, change formats
        return data
    
    def save_data(self, data: List[Dict[str, Any]]) -> bool:
        # Save data to database
        # Examples: INSERT or UPDATE queries
        return True
```

### 3. Using Database Manager

Use `db_manager` to work with the database:

```python
from app.services.database import db_manager

# Execute query
results = db_manager.execute_query("SELECT * FROM table_name WHERE id = %s", (123,))

# Update/Insert
rows_affected = db_manager.execute_update(
    "INSERT INTO table_name (name, email) VALUES (%s, %s)",
    ("John Doe", "john@example.com")
)

# Batch insert
data = [("Name1", "email1@example.com"), ("Name2", "email2@example.com")]
rows_affected = db_manager.execute_batch(
    "INSERT INTO table_name (name, email) VALUES (%s, %s)",
    data
)
```

### 4. Modifying Lambda Handler

Use your importer in the `lambda_handler.py` file:

```python
from app.services.my_custom_importer import MyCustomImporter

def process():
    config = {
        "table_name": "my_table",
        # Other settings
    }
    
    importer = MyCustomImporter(config=config)
    result = importer.run()
    return result
```

## Configuration

### Environment Variables

Configure via `.env` file or AWS Lambda environment variables:

```
DB_HOST=your-db-host
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_PORT=5432
```

### Importer Config

Each importer accepts its own specific configuration:

```python
config = {
    "table_name": "target_table",
    "api_url": "https://api.example.com/data",
    "batch_size": 100,
    # and more
}
```

## Examples

### Importing Data from API

```python
import requests
from app.services.base_importer import BaseImporter

class APIImporter(BaseImporter):
    def fetch_data(self):
        url = self.config.get("api_url")
        response = requests.get(url)
        return response.json()
    
    def transform_data(self, data):
        # Transform logic
        return data
    
    def save_data(self, data):
        # Save logic
        return True
```

### Importing from CSV File

```python
import csv
from app.services.base_importer import BaseImporter

class CSVImporter(BaseImporter):
    def fetch_data(self):
        file_path = self.config.get("file_path")
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def transform_data(self, data):
        # Transform logic
        return data
    
    def save_data(self, data):
        # Save logic
        return True
```

## Testing

To write tests:

```python
from app.services.my_importer import MyImporter

def test_importer():
    importer = MyImporter()
    result = importer.run()
    assert result["status"] == "success"
```

## Deployment

1. Build Docker image
2. Deploy via Terraform
3. Configure EventBridge schedule (optional)

## Help

If you have questions:
- `base_importer.py` - review the base class code
- `intaker_importer.py` - review the example implementation
- README.md - general information
