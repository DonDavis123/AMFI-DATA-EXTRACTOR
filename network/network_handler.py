import time
import requests
from system_logger import SystemLogger

system_logger = SystemLogger.get_logger()


class NetworkHandler:
    """
    Handles temporary network failures.

    Features
    --------
    • Detect network errors
    • Wait until internet returns
    • Retry forever
    """

    CHECK_URL = "https://www.amfiindia.com"
    RETRY_INTERVAL = 30  # seconds

    @staticmethod
    def is_network_error(error):

        return isinstance(
            error,
            (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
            ),
        )

    @staticmethod
    def wait_until_online():
        system_logger.warning(
          "Network connection lost. Waiting for internet..."
        )
       
        while True:

            try:

                requests.get(
                    NetworkHandler.CHECK_URL,
                    timeout=5,
                )

                system_logger.info(
                    "Internet connection restored."
                )
                return

            except requests.exceptions.RequestException:

                

                time.sleep(
                    NetworkHandler.RETRY_INTERVAL
                )