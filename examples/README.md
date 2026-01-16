# Examples

This folder contains various data import examples.

## Available Examples

### 1. API Importer (`example_api_importer.py`)

Fetch data from API and save to database.

**Usage:**
```python
from examples.example_api_importer import APIImporter

config = {
    "api_url": "https://api.example.com/data",
    "api_key": "your-api-key",
    "table_name": "imported_data"
}

importer = APIImporter(config=config)
result = importer.run()
```

### 2. CSV Importer (`example_csv_importer.py`)

Read data from CSV file and save to database.

**Usage:**
```python
from examples.example_csv_importer import CSVImporter

config = {
    "file_path": "data.csv",
    "table_name": "imported_data",
    "delimiter": ",",
    "encoding": "utf-8"
}

importer = CSVImporter(config=config)
result = importer.run()
```

## Creating Your Own Example

1. Extend `BaseImporter`
2. Implement `fetch_data()`, `transform_data()`, and `save_data()` methods
3. Use it in `lambda_handler.py`

For detailed information, see the main [TEMPLATE_GUIDE.md](../TEMPLATE_GUIDE.md) file.
