import asyncio
import logging
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.monitor import resource_monitor
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('monitor.log')
    ]
)

logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Starting resource monitoring service...")
        await resource_monitor.start()
    except KeyboardInterrupt:
        logger.info("Stopping resource monitoring service...")
        await resource_monitor.stop()
    except Exception as e:
        logger.error(f"Error in monitoring service: {e}")
        await resource_monitor.stop()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
