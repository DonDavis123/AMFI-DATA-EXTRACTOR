import re
import time
from system_logger import SystemLogger

system_logger = SystemLogger.get_logger()


class GeminiErrorHandler:
    """
    Handles Gemini API errors.

    Returns
    -------
    retry         -> Retry using current API key.
    retry_forever -> Keep retrying indefinitely (503 High Demand).
    switch_key    -> Current API key quota exhausted OR invalid API key.
    failed        -> Permanent/non-retryable error.
    """

    @staticmethod
    def handle(error, attempt, retries):

        message = str(error)
        message_lower = message.lower()

        # ==================================================
        # 1. API QUOTA / RATE LIMIT (429)
        # ==================================================

        if (
            "resource_exhausted" in message_lower
            or "429" in message_lower
            or "quota" in message_lower
            or "rate limit" in message_lower
        ):

            wait = GeminiErrorHandler._get_retry_time(message)

            
            if attempt < retries - 1:

                time.sleep(wait)

                return "retry"

            system_logger.warning(
                 "Retries exhausted for current API key. Switching to next API key."
            )
            return "switch_key"

        # ==================================================
        # 2. GEMINI HIGH DEMAND (503)
        # ==================================================

        high_demand_errors = (

            "503",
            "unavailable",
            "high demand",
            "currently experiencing high demand",
            "Spikes in demand",
            "server overloaded",
            "overloaded",

        )

        if any(
            text in message_lower
            for text in high_demand_errors
        ):

            wait = GeminiErrorHandler._server_wait(attempt)

            system_logger.warning(
                 f"Gemini server busy (503). Waiting {wait} seconds before retrying."
            )
            time.sleep(wait)

            return "retry_forever"

        # ==================================================
        # 3. Temporary Errors
        # ==================================================

        temporary_errors = (

            "timeout",
            "timed out",
            "connection reset",
            "connection aborted",
            "connection refused",
            "connection error",
            "500",
            "502",
            "504",
            "internal server error",
            "gateway timeout",
            "bad gateway",

        )

        if any(
            text in message_lower
            for text in temporary_errors
        ):

            wait = GeminiErrorHandler._temporary_wait(attempt)

            system_logger.warning(
                f"Temporary Gemini error: {message}. Retrying after {wait} seconds."
            )
            time.sleep(wait)

            return "retry"

        # ==================================================
        # 4. Invalid / Deleted API Key
        # ==================================================

        invalid_key_errors = (

            "401",
            "unauthenticated",
            "authentication",
            "permission_denied",
            "api_key_invalid",
            "invalid api key",
            "api key not valid",
            "api key expired",
            "api key has expired",
            "invalid credentials",
            "credential",

        )

        if any(
            text in message_lower
            for text in invalid_key_errors
        ):

            system_logger.error(
              "Invalid, deleted, or expired Gemini API key. Switching to next API key."
            )

            return "switch_key"

        # ==================================================
        # 5. Permanent Error
        # ==================================================

        system_logger.error(
             f"Non-retryable Gemini error: {message}"
        )
        return "failed"

    # ==================================================
    # Retry time suggested by Gemini
    # ==================================================

    @staticmethod
    def _get_retry_time(message):

        match = re.search(
            r"retry in ([0-9.]+)s",
            message,
            re.IGNORECASE,
        )

        if match:

            return int(float(match.group(1))) + 2

        return 60

    # ==================================================
    # Exponential backoff for 503
    # ==================================================

    @staticmethod
    def _server_wait(attempt):

        waits = [
            15,
            30,
            60,
            120,
            300,
        ]

        if attempt < len(waits):

            return waits[attempt]

        return 300

    # ==================================================
    # Temporary Errors
    # ==================================================

    @staticmethod
    def _temporary_wait(attempt):

        waits = [
            5,
            10,
            20,
            30,
        ]

        if attempt < len(waits):

            return waits[attempt]

        return 30