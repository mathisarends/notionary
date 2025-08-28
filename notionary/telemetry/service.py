import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from posthog import Posthog

from notionary.telemetry.views import BaseTelemetryEvent
from notionary.util import LoggingMixin, SingletonMetaClass

load_dotenv()

POSTHOG_EVENT_SETTINGS = {
    "process_person_profile": True,
}


class ProductTelemetry(LoggingMixin, metaclass=SingletonMetaClass):
    """
    Anonymous telemetry for Notionary - enabled by default.
    Disable via: ANONYMIZED_NOTIONARY_TELEMETRY=false
    """

    USER_ID_PATH = str(Path.home() / ".cache" / "notionary" / "telemetry_user_id")
    PROJECT_API_KEY = "phc_gItKOx21Tc0l07C1taD0QPpqFnbWgWjVfRjF6z24kke"
    HOST = "https://eu.i.posthog.com"
    UNKNOWN_USER_ID = "UNKNOWN"

    _logged_init_message = False
    _curr_user_id = None

    def __init__(self):
        # Default: enabled, disable via environment variable
        telemetry_setting = os.getenv("ANONYMIZED_NOTIONARY_TELEMETRY", "true").lower()
        telemetry_disabled = telemetry_setting == "false"
        self.debug_logging = os.getenv("NOTIONARY_DEBUG", "false").lower() == "true"

        if telemetry_disabled:
            self._posthog_client = None
        else:
            if not self._logged_init_message:
                self.logger.info(
                    "Anonymous telemetry enabled to improve Notionary. "
                    "To disable: export ANONYMIZED_NOTIONARY_TELEMETRY=false"
                )
                self._logged_init_message = True

            self._posthog_client = Posthog(
                project_api_key=self.PROJECT_API_KEY,
                host=self.HOST,
                disable_geoip=True,
                enable_exception_autocapture=True,
            )

            # Silence posthog's logging unless debug mode
            if not self.debug_logging:
                import logging

                posthog_logger = logging.getLogger("posthog")
                posthog_logger.disabled = True

        if self._posthog_client is None:
            self.logger.debug("Telemetry disabled")

    def capture(self, event: BaseTelemetryEvent) -> None:
        """
        Safe event tracking that never affects library functionality

        Args:
            event: BaseTelemetryEvent instance to capture
        """
        if self._posthog_client is None:
            return

        self._direct_capture(event)

    def _direct_capture(self, event: BaseTelemetryEvent) -> None:
        """
        Direct capture method - PostHog handles threading internally
        Should not be thread blocking because posthog magically handles it
        """
        if self._posthog_client is None:
            return

        try:
            self._posthog_client.capture(
                distinct_id=self.user_id,
                event=event.name,
                properties={
                    "library": "notionary",
                    **event.properties,
                    **POSTHOG_EVENT_SETTINGS,
                },
            )

        except Exception as e:
            self.logger.error(f"Failed to send telemetry event {event.name}: {e}")

    def flush(self) -> None:
        """
        Flush pending events - simplified without threading complexity
        """
        if not self._posthog_client:
            self.logger.debug("PostHog client not available, skipping flush.")
            return

        try:
            self._posthog_client.flush()
            self.logger.debug("PostHog client telemetry queue flushed.")
        except Exception as e:
            self.logger.error(f"Failed to flush PostHog client: {e}")

    @property
    def user_id(self) -> str:
        """Anonymous, persistent user ID"""
        if self._curr_user_id:
            return self._curr_user_id

        # File access may fail due to permissions or other reasons.
        # We don't want to crash so we catch all exceptions.
        try:
            if not os.path.exists(self.USER_ID_PATH):
                os.makedirs(os.path.dirname(self.USER_ID_PATH), exist_ok=True)
                with open(self.USER_ID_PATH, "w") as f:
                    new_user_id = str(uuid.uuid4())
                    f.write(new_user_id)
                self._curr_user_id = new_user_id
            else:
                with open(self.USER_ID_PATH, "r") as f:
                    self._curr_user_id = f.read().strip()

            return self._curr_user_id
        except Exception as e:
            self.logger.debug(f"Error getting user ID: {e}")
            self._curr_user_id = self.UNKNOWN_USER_ID
            return self._curr_user_id
