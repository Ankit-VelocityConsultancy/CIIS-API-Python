# super_admin/services/internal_scheduler.py
import threading
import time

from django.utils import timezone

from super_admin.services.google_drive_service import GoogleDriveService
from super_admin.services.sync_service import DriveSyncService

RUN_EVERY_SECONDS = 100000  # 10 minutes
_scheduler_started = False  # to avoid starting multiple threads


def start_drive_sync_scheduler():
    """
    Start a background thread that calls sync_all_folders() every RUN_EVERY_SECONDS.
    This is triggered once when Django app is ready.
    """
    global _scheduler_started
    if _scheduler_started:
        # Prevent double-start (e.g. Django autoreload)
        return
    _scheduler_started = True

    def loop():
        while True:
            try:
                print("==============================================")
                print("🕒 INTERNAL CRON TRIGGERED:", timezone.now())
                print("Running Google Drive sync...")

                drive = GoogleDriveService()
                sync = DriveSyncService(drive)
                sync.sync_all_folders()

                print("✅ INTERNAL CRON DONE:", timezone.now())
                print("==============================================")
            except Exception as e:
                print("❌ INTERNAL CRON ERROR:", e)

            time.sleep(RUN_EVERY_SECONDS)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
