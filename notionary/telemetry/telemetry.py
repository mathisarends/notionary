import os
import uuid
import atexit
import signal
import threading
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
    
    _logged_init_message = False

    def __init__(self):
        # Default: enabled, disable via ANONYMIZED_TELEMETRY=false
        telemetry_setting = os.getenv("ANONYMIZED_TELEMETRY", "true").lower()
        self.enabled = telemetry_setting != "false"

        self._user_id = None
        self._client = None
        self._shutdown_lock = threading.Lock()
        self._is_shutdown = False
        self._shutdown_registered = False

        if self.enabled:
            self._initialize_client()
            self._register_shutdown_handlers()

    def _register_shutdown_handlers(self):
        """Register shutdown handlers for clean exit"""
        with self._shutdown_lock:
            if self._shutdown_registered:
                return
            
            try:
                # Register atexit handler for normal program termination
                atexit.register(self._atexit_handler)
                
                # Register signal handlers for SIGINT (Ctrl+C) and SIGTERM
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
                
                self._shutdown_registered = True
                self.logger.debug("Telemetry shutdown handlers registered")
                
            except Exception as e:
                self.logger.debug(f"Failed to register shutdown handlers: {e}")

    def _signal_handler(self, signum, frame):
        """Handle SIGINT (Ctrl+C) and SIGTERM signals"""
        signal_name = "SIGINT" if signum == signal.SIGINT else f"SIG{signum}"
        self.logger.debug(f"Received {signal_name}, shutting down telemetry...")
        
        self.shutdown(timeout=5.0)  # Quick shutdown for signals
        
        # Let the original signal handler take over (or exit)
        if signum == signal.SIGINT:
            # Restore default handler and re-raise
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            os.kill(os.getpid(), signal.SIGINT)

    def _atexit_handler(self):
        """Handle normal program exit"""
        self.logger.debug("Normal program exit, shutting down telemetry...")
        self.shutdown(timeout=10.0)

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
        if not self.enabled or not self._client or self._is_shutdown:
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

    def flush(self, timeout: float = 5.0):
        """
        Flush events with timeout
        
        Args:
            timeout: Maximum time to wait for flush to complete
        """
        if not self.enabled or not self._client or self._is_shutdown:
            return

        try:
            # PostHog flush doesn't support timeout directly, so we do it in a thread
            flush_thread = threading.Thread(target=self._client.flush)
            flush_thread.daemon = True
            flush_thread.start()
            flush_thread.join(timeout=timeout)
            
            if flush_thread.is_alive():
                self.logger.warning(f"Telemetry flush timed out after {timeout}s")
            else:
                self.logger.debug("Telemetry events flushed successfully")
                
        except Exception as e:
            self.logger.debug(f"Error during telemetry flush: {e}")

    def shutdown(self, timeout: float = 10.0):
        """
        Clean shutdown of telemetry with timeout
        
        Args:
            timeout: Maximum time to wait for shutdown
        """
        with self._shutdown_lock:
            if self._is_shutdown:
                return
            
            self._is_shutdown = True
            
        try:
            if self._client:
                # First try to flush remaining events
                self.logger.debug("Flushing telemetry events before shutdown...")
                self.flush(timeout=timeout * 0.7)  # Use 70% of timeout for flush
                
                # Then shutdown the client
                shutdown_thread = threading.Thread(target=self._client.shutdown)
                shutdown_thread.daemon = True
                shutdown_thread.start()
                shutdown_thread.join(timeout=timeout * 0.3)  # Use 30% for shutdown
                
                if shutdown_thread.is_alive():
                    self.logger.warning(f"Telemetry client shutdown timed out after {timeout}s")
                else:
                    self.logger.debug("Telemetry client shut down successfully")
                    
        except Exception as e:
            self.logger.debug(f"Error during telemetry shutdown: {e}")
        finally:
            self._client = None

    def _initialize_client(self):
        """Initializes PostHog client and shows startup message"""
        try:
            self._client = Posthog(
                project_api_key=self.PROJECT_API_KEY,
                host=self.HOST,
                disable_geoip=True,
            )
            if not self._logged_init_message:
                self.logger.info(
                    "Anonymous telemetry enabled to improve Notionary. "
                    "To disable: export ANONYMIZED_TELEMETRY=false"
                )
                self._logged_init_message = True

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