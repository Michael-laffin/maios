# tests/unit/test_config.py
import os

import pytest
from pydantic import ValidationError


def test_config_defaults():
    """Test configuration loads with defaults."""
    from maios.core.config import Settings

    settings = Settings(
        zai_api_key="test-key",
        database_url="postgresql://localhost/maios",
        redis_url="redis://localhost/6379/0",
    )

    assert settings.default_model == "glm-4-plus"
    assert settings.task_timeout_minutes == 30
    assert settings.multi_tenant_mode is False
    assert settings.log_level == "INFO"


def test_config_requires_api_key():
    """Test that API key is required."""
    from maios.core.config import Settings

    # Temporarily remove ZAI_API_KEY from environment
    original = os.environ.pop("ZAI_API_KEY", None)
    # Also reset the cached settings
    import maios.core.config as config_module

    config_module._settings = None

    try:
        with pytest.raises(ValidationError):
            Settings(
                database_url="postgresql://localhost/maios",
                redis_url="redis://localhost/6379/0",
            )
    finally:
        # Restore the environment variable
        if original is not None:
            os.environ["ZAI_API_KEY"] = original
        config_module._settings = None
