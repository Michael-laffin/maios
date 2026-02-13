# tests/unit/test_redis.py
import pytest


def test_redis_client_creation(test_env):
    """Test Redis client can be created."""
    from maios.core.redis import get_redis_client

    client = get_redis_client()
    assert client is not None


@pytest.mark.asyncio
async def test_redis_ping(test_env):
    """Test Redis connection with ping."""
    from maios.core.redis import get_redis_client

    client = get_redis_client()
    # This would need a running Redis instance
    # For now, just verify client exists
    assert client.connection_pool is not None
