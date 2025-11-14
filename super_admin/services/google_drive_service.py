# super_admin/services/google_drive_service.py
import os
import pickle
import io

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TOKEN_FILE = os.environ.get(
    "GOOGLE_TOKEN_FILE",
    os.path.join(os.getcwd(), "token.pickle")
)


class GoogleDriveService:
    def __init__(self):
        if not os.path.exists(TOKEN_FILE):
            raise RuntimeError(f"Google Drive token not found at {TOKEN_FILE}")

        with open(TOKEN_FILE, "rb") as f:
            creds: Credentials = pickle.load(f)

        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_FILE, "wb") as f:
                    pickle.dump(creds, f)
            else:
                raise RuntimeError(
                    "Saved Google OAuth token is invalid and cannot be refreshed."
                )

        self.creds = creds
        self.svc = build("drive", "v3", credentials=self.creds, cache_discovery=False)

    # ---------- helpers ----------

    @staticmethod
    def _is_audio_file(file_obj: dict) -> bool:
        """
        Decide in Python if this Drive file is an audio recording.
        Uses mimeType and file extension.
        """
        name = (file_obj.get("name") or "").lower()
        mime = (file_obj.get("mimeType") or "").lower()

        # any audio/* mimeType
        if mime.startswith("audio/"):
            return True

        # some recordings may be video/mp4
        if mime == "video/mp4":
            return True

        # fallback on file extension
        audio_exts = [
            ".m4a", ".mp3", ".wav", ".amr",
            ".3gp", ".aac", ".ogg", ".flac", ".wma",
        ]
        return any(name.endswith(ext) for ext in audio_exts)

    # ---------- core listing ----------

    def list_files_in_folder(self, folder_id, page_token=None):
        """
        List ALL non-trashed files in folder.
        Audio filtering is done in Python, not in the Drive query.
        """
        query = f"'{folder_id}' in parents and trashed = false"
        fields = (
            "nextPageToken, "
            "files(id, name, mimeType, size, createdTime, webViewLink)"
        )

        resp = self.svc.files().list(
            q=query,
            spaces="drive",
            fields=fields,
            pageToken=page_token,
            pageSize=100,
        ).execute()

        files = resp.get("files", [])
        print(f"📁 GoogleDriveService: fetched {len(files)} raw files from folder {folder_id}")
        return files, resp.get("nextPageToken")

    def iter_all_audio_files(self, folder_id):
        """
        Iterate over ONLY audio-like files in the folder.
        """
        token = None
        total_raw = 0
        total_audio = 0

        while True:
            files, token = self.list_files_in_folder(folder_id, page_token=token)
            total_raw += len(files)

            for f in files:
                if self._is_audio_file(f):
                    total_audio += 1
                    yield f

            if not token:
                break

        print(
            f"🎧 GoogleDriveService: total files in folder {folder_id}: "
            f"raw={total_raw}, audio_filtered={total_audio}"
        )

    @staticmethod
    def file_web_link(file):
        return file.get("webViewLink")

    # ---------- download ----------

    def download_file(self, file_id: str, dest_path: str) -> str:
        """
        Download a file from Google Drive to dest_path.
        dest_path should be an absolute path on the server.
        Returns dest_path on success.
        """
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        request = self.svc.files().get_media(fileId=file_id)
        fh = io.FileIO(dest_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Downloading {file_id}: {int(status.progress() * 100)}%")

        fh.close()
        return dest_path
