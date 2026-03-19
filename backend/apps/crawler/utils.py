import os
import logging
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

def save_file_safely(model_instance, field_name, file_name, content):
    """
    Saves a file to a Django model FileField while bypassing Eventlet's 
    monkey-patched os.fdopen on Windows.
    """
    def perform_save():
        # Try to bypass eventlet's monkey-patch on Windows
        try:
            from eventlet.patcher import original
            orig_os = original('os')
            patched_fdopen = os.fdopen
            os.fdopen = orig_os.fdopen
            try:
                field = getattr(model_instance, field_name)
                field.save(file_name, ContentFile(content), save=True)
            finally:
                os.fdopen = patched_fdopen
        except (ImportError, AttributeError):
            # Fallback for Linux or when eventlet is not used
            field = getattr(model_instance, field_name)
            field.save(file_name, ContentFile(content), save=True)

    try:
        from eventlet import tpool
        tpool.execute(perform_save)
    except (ImportError, AttributeError):
        # Fallback if eventlet/tpool is not available
        perform_save()
