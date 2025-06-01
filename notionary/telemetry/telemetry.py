import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from posthog import Posthog
from dotenv import load_dotenv

from notionary.util import LoggingMixin
from notionary.util import singleton

load_dotenv()

@singleton
class NotionaryTelemetry(LoggingMixin):
    """
    Anonymous telemetry for Notionary - enabled by default.
    Disable via: ANONYMIZED_TELEMETRY=false
    """

    USER_ID_PATH = str(Path.home() / ".cache" / "notionary" / "telemetry_user_id")
    PROJECT_API_KEY = (
        "phc_gItKOx21Tc0l07C1taD0QPpqFnbWgWjVfRjF6z24kke"  # write-only so no worries
    )
    HOST = "https://eu.i.posthog.com"

    def __init__(self):
        # Default: enabled, disable via ANONYMIZED_TELEMETRY=false
        telemetry_setting = os.getenv("ANONYMIZED_TELEMETRY", "true").lower()
        self.enabled = telemetry_setting != "false"

        self._user_id = None
        self._client = None

        if self.enabled:
            self._initialize_client()

    @property
    def user_id(self) -> str:
        """Anonymous, persistent user ID"""
        if self._user_id:
            return self._user_id

        try:
            if not os.path.exists(self.USER_ID_PATH):
                os.makedirs(os.path.dirname(self.USER_ID_PATH), exist_ok=True)
                with open(self.USER_ID_PATH, "w") as f:
                    new_user_id = str(uuid.uuid4())
                    f.write(new_user_id)
                self._user_id = new_user_id
            else:
                with open(self.USER_ID_PATH, "r") as f:
                    self._user_id = f.read().strip()

            return self._user_id
        except Exception as e:
            self.logger.debug(f"Error getting user ID: {e}")
            return "anonymous_user"

    def capture(self, event_name: str, properties: Optional[Dict[str, Any]] = None):
        """
        Safe event tracking that never affects library functionality

        Args:
            event_name: Event name (e.g. 'page_factory_used')
            properties: Event properties as dictionary
        """
        if not self.enabled or not self._client:
            return

        try:
            # Add base properties
            event_properties = {
                "library": "notionary",
                "library_version": self._get_notionary_version(),
                **(properties or {}),
            }

            self._client.capture(
                distinct_id=self.user_id, event=event_name, properties=event_properties
            )

        except Exception:
            pass

    def flush(self):
        """Flush events on app exit"""
        if self.enabled and self._client:
            try:
                self._client.flush()
            except Exception:
                pass

    def shutdown(self):
        """Clean shutdown of telemetry"""
        self.flush()
        if self._client:
            try:
                self._client.shutdown()
            except Exception:
                pass

    def _initialize_client(self):
        """Initializes PostHog client and shows startup message"""
        try:
            self._client = Posthog(
                project_api_key=self.PROJECT_API_KEY,
                host=self.HOST,
                disable_geoip=True,
            )
            self.logger.info(
                "Anonymous telemetry enabled to improve Notionary. "
                "To disable: export ANONYMIZED_TELEMETRY=false"
            )

            # Initial event
            self._track_initialization()

        except Exception as e:
            self.logger.debug(f"Telemetry initialization failed: {e}")
            self.enabled = False
            self._client = None

    def _track_initialization(self):
        """Tracks library initialization"""
        self.capture(
            "notionary_initialized",
            {
                "version": self._get_notionary_version(),
            },
        )

    def _get_notionary_version(self) -> str:
        """Determines the Notionary version"""
        import notionary

        return getattr(notionary, "__version__", "0.2.10")