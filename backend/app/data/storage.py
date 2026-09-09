import os
import shutil
from abc import ABC, abstractmethod
from typing import Union, Dict, Any, Optional
from backend.app.config import settings
from backend.app.logging import app_logger

class BaseMediaStorage(ABC):
    """
    Abstract Base Class for AVATAROS Media Storage Abstraction (Milestone 10).
    Decouples generated media persistence (MP4 videos, WAV audio, image frames)
    from local filesystem assumptions to support Google Cloud Storage (GCS) on Cloud Run.
    """
    @abstractmethod
    def save_file(
        self,
        filename: str,
        source_path_or_bytes: Union[str, bytes],
        content_type: str = "video/mp4",
        trace_id: str = "system"
    ) -> str:
        """
        Saves a media asset and returns its accessible URL or path.
        """
        pass

    @abstractmethod
    def get_url(self, filename: str) -> str:
        """
        Returns web-accessible URL for the media asset.
        """
        pass

    @abstractmethod
    def get_local_path(self, filename: str) -> str:
        """
        Returns local filesystem path for inspection or FFmpeg manipulation.
        """
        pass

    @abstractmethod
    def exists(self, filename: str) -> bool:
        """
        Checks whether the media asset exists.
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Returns honest storage provider status for health and observability.
        """
        pass


class LocalMediaStorage(BaseMediaStorage):
    """
    Local filesystem media storage implementation for development, CI, and local demos.
    Validates filenames against directory traversal vulnerabilities.
    """
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or settings.VAULT_STORAGE_PATH)
        os.makedirs(self.base_dir, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        if ".." in filename or "/" in filename or "\\" in filename:
            raise ValueError(f"Invalid or unsafe media filename with path traversal: '{filename}'")
        clean_name = os.path.basename(filename).strip()
        if not clean_name or clean_name in (".", ".."):
            raise ValueError(f"Invalid or unsafe media filename: '{filename}'")
        return clean_name

    def save_file(
        self,
        filename: str,
        source_path_or_bytes: Union[str, bytes],
        content_type: str = "video/mp4",
        trace_id: str = "system"
    ) -> str:
        clean_name = self._sanitize_filename(filename)
        target_path = os.path.join(self.base_dir, clean_name)

        if isinstance(source_path_or_bytes, bytes):
            with open(target_path, "wb") as f:
                f.write(source_path_or_bytes)
        elif isinstance(source_path_or_bytes, str):
            if os.path.abspath(source_path_or_bytes) != target_path:
                shutil.copy2(source_path_or_bytes, target_path)

        app_logger.log_operation(
            trace_id=trace_id,
            operation="media_saved_local",
            status="SUCCESS",
            agent_task="media_storage",
            details={"filename": clean_name, "path": target_path, "storage": "local"}
        )
        return self.get_url(clean_name)

    def get_url(self, filename: str) -> str:
        clean_name = self._sanitize_filename(filename)
        return f"/media/{clean_name}"

    def get_local_path(self, filename: str) -> str:
        clean_name = self._sanitize_filename(filename)
        return os.path.join(self.base_dir, clean_name)

    def exists(self, filename: str) -> bool:
        try:
            clean_name = self._sanitize_filename(filename)
            return os.path.exists(os.path.join(self.base_dir, clean_name))
        except ValueError:
            return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": "local_media_storage",
            "is_real_cloud": False,
            "configured": True,
            "ready": True,
            "base_dir": self.base_dir
        }


class GCSMediaStorage(BaseMediaStorage):
    """
    Google Cloud Storage (GCS) adapter for production deployment on Cloud Run.
    Persists master renders and frame assets to a cloud bucket, with local caching for low-latency inspection.
    Falls back gracefully to LocalMediaStorage when GCS credentials or bucket are unconfigured.
    """
    def __init__(self, bucket_name: Optional[str] = None, fallback: Optional[BaseMediaStorage] = None):
        self.bucket_name = bucket_name or settings.GOOGLE_CLOUD_STORAGE_BUCKET
        self.fallback = fallback or LocalMediaStorage()
        self._gcs_client = None
        self._bucket = None
        self._is_configured = False

        self._init_error: Optional[str] = None

        if settings.MEDIA_STORAGE_PROVIDER != "gcs":
            # Not selected. Local storage is the intended behaviour, not a failure.
            return

        if not self.bucket_name:
            self._init_error = "MEDIA_STORAGE_PROVIDER=gcs but GOOGLE_CLOUD_STORAGE_BUCKET is unset"
            app_logger.log_operation(
                trace_id="system",
                operation="gcs_storage_init",
                status="ERROR",
                agent_task="media_storage",
                details={"error": self._init_error, "consequence": "using local media storage"},
            )
            return

        try:
            from google.cloud import storage

            self._gcs_client = storage.Client()
            self._bucket = self._gcs_client.bucket(self.bucket_name)
            # Confirm the bucket is actually reachable. Constructing a handle does
            # no I/O, so without this the first failure would surface mid-render.
            self._bucket.reload()
            self._is_configured = True
            app_logger.log_operation(
                trace_id="system",
                operation="gcs_storage_init",
                status="CONNECTED",
                agent_task="media_storage",
                details={"bucket": self.bucket_name},
            )
        except ImportError as e:
            self._init_error = (
                f"google-cloud-storage is not installed ({e}). "
                "Add it to backend/requirements.txt to enable the GCS media vault."
            )
            app_logger.log_operation(
                trace_id="system", operation="gcs_storage_init", status="ERROR",
                agent_task="media_storage",
                details={"error": self._init_error, "consequence": "using local media storage"},
            )
            self._is_configured = False
        except Exception as e:
            # Configured but unreachable - wrong bucket, missing IAM, no ADC.
            # Recorded as an error so the provider matrix can report it honestly
            # instead of showing a green "gcs" that is really writing to /app.
            self._init_error = f"{type(e).__name__}: {e}"
            app_logger.log_operation(
                trace_id="system", operation="gcs_storage_init", status="ERROR",
                agent_task="media_storage",
                details={
                    "bucket": self.bucket_name,
                    "error": self._init_error[:300],
                    "consequence": "using local media storage",
                },
            )
            self._is_configured = False

    def save_file(
        self,
        filename: str,
        source_path_or_bytes: Union[str, bytes],
        content_type: str = "video/mp4",
        trace_id: str = "system"
    ) -> str:
        # First ensure local file is written for synchronous pipeline steps (e.g. ffprobe/guardian)
        local_url = self.fallback.save_file(filename, source_path_or_bytes, content_type, trace_id)
        if not self._is_configured or not self._bucket:
            return local_url

        try:
            clean_name = os.path.basename(filename)
            blob = self._bucket.blob(f"media/{clean_name}")
            local_path = self.fallback.get_local_path(filename)
            blob.upload_from_filename(local_path, content_type=content_type)
            gcs_url = f"https://storage.googleapis.com/{self.bucket_name}/media/{clean_name}"
            
            app_logger.log_operation(
                trace_id=trace_id,
                operation="media_saved_gcs",
                status="SUCCESS",
                agent_task="media_storage",
                details={"filename": clean_name, "gcs_url": gcs_url, "bucket": self.bucket_name}
            )
            return gcs_url
        except Exception as e:
            app_logger.log_operation(
                trace_id=trace_id,
                operation="gcs_upload_fallback",
                status="NOTICE",
                agent_task="media_storage",
                details={"message": "GCS upload failed, using local URL", "error": str(e)}
            )
            return local_url

    def get_url(self, filename: str) -> str:
        if self._is_configured and self.bucket_name:
            clean_name = os.path.basename(filename)
            return f"https://storage.googleapis.com/{self.bucket_name}/media/{clean_name}"
        return self.fallback.get_url(filename)

    def get_local_path(self, filename: str) -> str:
        return self.fallback.get_local_path(filename)

    def exists(self, filename: str) -> bool:
        if self._is_configured and self._bucket:
            try:
                clean_name = os.path.basename(filename)
                blob = self._bucket.blob(f"media/{clean_name}")
                return blob.exists()
            except Exception:
                pass
        return self.fallback.exists(filename)

    def get_status(self) -> Dict[str, Any]:
        status = {
            "provider": "google_cloud_storage" if self._is_configured else "local_media_storage",
            "is_real_cloud": self._is_configured,
            "configured": self._is_configured,
            "ready": True,
            "bucket": self.bucket_name if self._is_configured else "local_filesystem",
        }
        if self._init_error:
            # GCS was requested and did not come up. Surfacing the reason is the
            # difference between "storage is local by design" and "storage is
            # local because something is broken and nobody noticed".
            status["degraded"] = True
            status["error"] = self._init_error[:300]
        return status


def get_media_storage() -> BaseMediaStorage:
    """
    Factory resolving active media storage provider based on configuration.
    """
    if settings.MEDIA_STORAGE_PROVIDER == "gcs" and settings.GOOGLE_CLOUD_STORAGE_BUCKET:
        return GCSMediaStorage()
    return LocalMediaStorage()

# Global default media storage singleton
media_storage = get_media_storage()
