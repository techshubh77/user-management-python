import json
import redis.asyncio as aioredis
from app.config.settings import settings
from app.utils.logger import logger
from app.exceptions.custom_exceptions import AppException


class Redis:
    _redis = aioredis.from_url(settings.celery_broker_url, decode_responses=True)

    @classmethod
    async def set(cls, key: str, value: any, ttl: int = 3600):
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)


            await cls._redis.set(name=key, value=value, ex=ttl)
            logger.info(f"Key '{key}' set successfully in Redis")
            return True
        except Exception as e:
            logger.error(f"Error setting key '{key}' in Redis: {e}")
            raise AppException("Failed to set key in Redis", 500)

    @classmethod
    async def get(cls, key: str):
        try:
            value = await cls._redis.get(name=key)

            if not value:
                return None

            try:
                logger.info(f"Key '{key}' retrieved successfully from Redis")
                return json.loads(value)
            except json.JSONDecodeError:
                logger.info(f"Key '{key}' retrieved successfully from Redis")
                return value
        except Exception as e:
            logger.error(f"Error getting key '{key}' from Redis: {e}")
            raise AppException("Failed to get key from Redis", 500)

    @classmethod
    async def delete(cls, key: str):
        try:
            await cls._redis.delete(key)
            logger.info(f"Key '{key}' deleted successfully from Redis")
            return True
        except Exception as e:
            logger.error(f"Error deleting key '{key}' from Redis: {e}")
            raise AppException("Failed to delete key from Redis", 500)



