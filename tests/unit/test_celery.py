# tests/unit/test_celery.py
def test_celery_app_configuration():
    """Test Celery app is configured correctly."""
    from maios.workers.celery_app import app

    assert app is not None
    assert app.main == "maios"
