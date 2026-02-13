# tests/conftest.py
import os

import pytest


@pytest.fixture
def test_env():
    """Set up test environment variables for tests that need them."""
    # Set required environment variables for tests
    test_env_values = {
        "ZAI_API_KEY": "test-api-key",
        "DATABASE_URL": "postgresql://localhost:5432/maios_test",
        "REDIS_URL": "redis://localhost:6379/0",
    }

    original_env = {}
    for key, value in test_env_values.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    # Reset cached settings and redis pool
    import maios.core.config as config_module
    import maios.core.redis as redis_module

    config_module._settings = None
    redis_module._pool = None

    yield

    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    # Reset cached instances after test
    config_module._settings = None
    redis_module._pool = None
