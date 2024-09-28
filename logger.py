import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Log to file
        logging.StreamHandler()          # Also log to console
    ]
)

# Create a logger object that can be imported in other files
log = logging.getLogger(__name__)
