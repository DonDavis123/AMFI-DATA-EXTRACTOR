import time
import requests


class NetworkHandler:
    """
    Handles temporary network failures.

    Features
    --------
    • Detect network errors
    • Wait until internet returns
    • Retry forever
    """

    CHECK_URL = "https://www.google.com"
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

        print("\n - network_handler.py:35" + "=" * 80)
        print("NETWORK CONNECTION LOST - network_handler.py:36")
        print("Waiting for internet... - network_handler.py:37")
        print("= - network_handler.py:38" * 80)

        while True:

            try:

                requests.get(
                    NetworkHandler.CHECK_URL,
                    timeout=5,
                )

                print("\nInternet connection restored. - network_handler.py:49")
                print("= - network_handler.py:50" * 80)

                return

            except requests.exceptions.RequestException:

                print(
                    f"No internet. Retrying in "
                    f"{NetworkHandler.RETRY_INTERVAL} seconds..."
                )

                time.sleep(
                    NetworkHandler.RETRY_INTERVAL
                )