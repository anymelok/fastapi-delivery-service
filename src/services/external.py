import logging
import redis.asyncio as redis
import httpx
from src.exceptions.exceptions import ExternalServiceException
from src.config import settings

logger = logging.getLogger(__name__)


async def get_usd_rate():
    logger.info("Started get_usd_rate task...")
    r = redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", decode_responses=True
    )
    val = await r.get("usd_rate")
    if val:
        await r.close()
        return float(val)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://www.cbr-xml-daily.ru/daily_json.js")
            data = resp.json()
            rate = data["Valute"]["USD"]["Value"]
            await r.set("usd_rate", rate, ex=3600)
            logger.info("get_usd_rate task completed successfully")
            return rate
    except (httpx.HTTPError, KeyError) as e:
        logger.error(f"External API error. get_usd_rate task failed: {e}")
        raise ExternalServiceException(
            f"During getting usd_rate exception occured: {e}"
        )

    finally:
        await r.close()
