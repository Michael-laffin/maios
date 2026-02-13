# maios/core/redis.py
from redis.asyncio import ConnectionPool, Redis

from maios.core.config import settings


# Create connection pool
_pool: ConnectionPool | None = None


def get_redis_client() -> Redis:
    """Get Redis client instance."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return Redis(connection_pool=_pool)


async def close_redis():
    """Close Redis connection pool."""
    global _pool
    if _pool:
        await _pool.aclose()
        _pool = None
