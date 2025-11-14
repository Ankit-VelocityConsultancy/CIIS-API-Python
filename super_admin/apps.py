# super_admin/apps.py
import os
from django.apps import AppConfig


class SuperAdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "super_admin"

    def ready(self):
        import super_admin.signals  # noqa

        # Only start scheduler in the main runserver process
        if os.environ.get("RUN_MAIN") == "true":
            from super_admin.services.internal_scheduler import start_drive_sync_scheduler
            print("🚀 Starting internal Google Drive scheduler...")
            start_drive_sync_scheduler()
