# services/sync_service.py
import os
import re

from django.conf import settings
from django.utils import timezone
from django.db import transaction
from dateutil.parser import isoparse

from ..models import CallRecording, DriveFolder, SyncLog
from .google_drive_service import GoogleDriveService


def extract_phone(name: str) -> str | None:
    """
    Try to find a 10–12 digit phone number in the filename.
    Example: 'call_9876543210_2025-11-10.m4a'
    """
    m = re.search(r"\b(\+?\d{10,12})\b", name or "")
    return m.group(1) if m else None


def parse_drive_datetime(dt_str):
    """Parse Google Drive ISO datetime into aware Django datetime."""
    try:
        dt = isoparse(dt_str)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
    except Exception:
        return timezone.now()


class DriveSyncService:
    """
    Service that syncs Google Drive audio files into the CallRecording table.
    Also downloads the audio to local disk and populates local_file_path + audio_url.
    """

    def __init__(self, drive_service: GoogleDriveService):
        self.drive = drive_service

    def _build_paths(self, folder: DriveFolder, drive_file_id: str, file_name: str):
        """
        Build relative and absolute paths for storing the audio file.
        Example relative: call_recordings/<user_id>/<drive_file_id>_<file_name>
        """
        relative_path = os.path.join(
            "call_recordings",
            str(folder.user_id),
            f"{drive_file_id}_{file_name}",
        )
        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        return relative_path, absolute_path

    def sync_single_folder(self, folder: DriveFolder):
        """Sync one Drive folder into CallRecording table."""
        print(f"➡️  Sync started for folder: {folder.name} ({folder.folder_id})")
        log = SyncLog.objects.create(folder=folder)  # status='running' by default
        found = 0
        added = 0

        try:
            for f in self.drive.iter_all_audio_files(folder.folder_id):
                found += 1

                drive_file_id = f["id"]
                name = f.get("name") or ""
                phone = extract_phone(name) or ""
                created_dt = (
                    parse_drive_datetime(f.get("createdTime"))
                    if f.get("createdTime")
                    else timezone.now()
                )
                size = int(f.get("size") or 0)
                link = self.drive.file_web_link(f)

                # Build local storage paths
                relative_path, absolute_path = self._build_paths(folder, drive_file_id, name)

                # Download file to local disk
                try:
                    self.drive.download_file(drive_file_id, absolute_path)
                except Exception as dl_err:
                    # If download fails, we still log the failure in SyncLog but skip this file
                    print(f"❌ Failed to download file {drive_file_id}: {dl_err}")
                    continue

                # Build URL for frontend (served via MEDIA_URL)
                audio_url = settings.MEDIA_URL + relative_path

                with transaction.atomic():
                    obj, created = CallRecording.objects.get_or_create(
                        google_drive_file_id=drive_file_id,
                        defaults={
                            "user_id": folder.user_id,
                            "phone_number": phone,
                            "drive_file_name": name,
                            "file_name": name,
                            "file_size": size,
                            "google_drive_link": link,
                            "status": "synced",
                            "recording_date": created_dt,
                            "last_synced_at": timezone.now(),
                            "local_file_path": relative_path,
                            "audio_url": audio_url,
                        },
                    )

                    if created:
                        added += 1
                    else:
                        # update if something has changed
                        dirty = False

                        if obj.user_id != folder.user_id:
                            obj.user_id = folder.user_id
                            dirty = True
                        if obj.drive_file_name != name:
                            obj.drive_file_name = name
                            dirty = True
                        if obj.file_name != name:
                            obj.file_name = name
                            dirty = True
                        if obj.file_size != size:
                            obj.file_size = size
                            dirty = True
                        if link and obj.google_drive_link != link:
                            obj.google_drive_link = link
                            dirty = True
                        if not obj.phone_number and phone:
                            obj.phone_number = phone
                            dirty = True
                        if not obj.local_file_path or obj.local_file_path != relative_path:
                            obj.local_file_path = relative_path
                            dirty = True
                        if not obj.audio_url or obj.audio_url != audio_url:
                            obj.audio_url = audio_url
                            dirty = True
                        if obj.status != "synced":
                            obj.status = "synced"
                            dirty = True

                        if dirty:
                            obj.last_synced_at = timezone.now()
                            obj.save(
                                update_fields=[
                                    "user_id",
                                    "drive_file_name",
                                    "file_name",
                                    "file_size",
                                    "google_drive_link",
                                    "phone_number",
                                    "local_file_path",
                                    "audio_url",
                                    "status",
                                    "last_synced_at",
                                    "updated_at",
                                ]
                            )

            log.sync_completed_at = timezone.now()
            log.total_files_found = found
            log.new_files_added = added
            log.status = "success"
            log.save()

            print(
                f"✅ Sync success for folder: {folder.name} | "
                f"found={found}, new={added}"
            )

        except Exception as e:
            log.sync_completed_at = timezone.now()
            log.total_files_found = found
            log.new_files_added = added
            log.status = "failed"
            log.error_message = str(e)
            log.save()

            print(f"❌ Sync FAILED for folder: {folder.name} | error={e}")
            raise

    def sync_all_folders(self):
        """Sync all active folders."""
        print("🔄 sync_all_folders() — fetching active DriveFolder entries...")
        folders = DriveFolder.objects.filter(is_active=True)

        if not folders.exists():
            print("⚠️  No active DriveFolder found. Nothing to sync.")
            return

        for folder in folders:
            try:
                self.sync_single_folder(folder)
            except Exception as e:
                # Continue with next folder even if one fails
                print(f"⚠️  Failed to sync folder {folder.name}: {e}")
                continue

        print("✅ sync_all_folders() finished.")
