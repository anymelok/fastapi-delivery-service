from src.database import async_session_maker
from src.repositories.parcels import ParcelRepository
from src.services.parcels import ParcelService
import logging

logger = logging.getLogger(__name__)


async def run_delivery_calculation():
    logger.info("Starting run_delivery_calculation...")
    async with async_session_maker() as session:
        repo = ParcelRepository(session)
        service = ParcelService(repo)

        try:
            logger.info("run_delivery_calculation finished successfully")
            await service.calculate_delivery_costs()
        except Exception as e:
            logger.error(f"Erorr during run_delivery_calculation: {e}")
