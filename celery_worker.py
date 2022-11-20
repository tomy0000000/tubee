from app import app

from tubee import celery  # noqa: F401

# Push flask context for celery
app.app_context().push()
