# Data Import Template

This project is a template for data import operations. It runs on AWS Lambda and is designed to fetch data from various sources (APIs, files, other databases) and save it to a PostgreSQL database.

## Features

- ✅ **Modular structure** - each importer is a separate class
- ✅ **Base template class** - easy to create new importers
- ✅ **Database connection pooling** - efficient database connections
- ✅ **Comprehensive logging** - all operations are logged
- ✅ **Error handling** - proper error management
- ✅ **Statistics tracking** - import statistics are automatically collected

## Quick Start

### 1. Installation

```bash
poetry install
```

### 2. Configuration

Create a `.env` file and enter your database settings:

```env
DB_HOST=your-db-host
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_PORT=5432
```

### 3. Create Your Own Importer

Create a new file in `app/services/` and extend `BaseImporter`:

```python
from app.services.base_importer import BaseImporter

class MyImporter(BaseImporter):
    def fetch_data(self):
        # Fetch data from source
        pass
    
    def transform_data(self, data):
        # Transform data
        pass
    
    def save_data(self, data):
        # Save to database
        pass
```

### 4. Update Lambda Handler

Use your importer in `app/lambda_handler.py`:

```python
from app.services.my_importer import MyImporter

def process():
    importer = MyImporter()
    return importer.run()
```

## Structure

```
app/
├── config.py                 # Configuration
├── lambda_handler.py         # Lambda entry point
├── logger_config.py          # Logging
└── services/
    ├── base_importer.py      # Base template class
    ├── database.py           # Database manager
    └── intaker_importer.py   # Example implementation
```

## Additional Information

For detailed guide, see [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md).

## Deployment

### Docker Build

```bash
docker build -t data-importer .
```

### Terraform Deploy

```bash
cd terraform/main
terraform init
terraform plan
terraform apply
```

## Testing

```bash
poetry run pytest
```

## License

MIT License
