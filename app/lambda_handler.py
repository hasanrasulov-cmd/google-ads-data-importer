"""
AWS Lambda handler for data import.

This is the entry point for the Lambda function. It orchestrates the data import process.
"""
from app.logger_config import get_logger
from app.services.intaker_importer import IntakerImporter

logger = get_logger(__name__)


def process():
    """
    Main processing function that runs the data import.
    
    This function:
    1. Initializes the importer
    2. Runs the import process
    3. Returns the result
    
    Customize this function to use different importers or add additional logic.
    """
    try:
        # Initialize the importer with optional configuration
        config = {
            # Add your configuration here
            # "table_name": "your_table",
            # "api_url": "https://api.example.com",
            # etc.
        }

        importer = IntakerImporter(config=config)
        print(importer)
        # Run the import process
        result = importer.run()

        logger.info(f"Import process completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in process function: {str(e)}", exc_info=True)
        raise


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    This function is called by AWS Lambda when the function is invoked.
    It can be triggered by:
    - EventBridge schedules
    - API Gateway
    - S3 events
    - etc.
    
    Args:
        event: Lambda event object (dict)
        context: Lambda context object
        
    Returns:
        Response dictionary with status code and body
    """
    logger.info("Lambda function invoked")
    logger.info(f"Event: {event}")

    try:
        # Run the import process
        result = process()

        return {
            "statusCode": 200,
            "body": {
                "message": "Data import completed successfully",
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {
                "message": "Data import failed",
                "error": str(e)
            }
        }
