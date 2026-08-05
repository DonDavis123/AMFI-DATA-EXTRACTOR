import re
import time


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
            or "429" in message
            or "quota" in message_lower
            or "rate limit" in message_lower
        ):

            wait = GeminiErrorHandler._get_retry_time(message)

            print("\n - errorhandler.py:36" + "=" * 80)
            print("GEMINI API QUOTA EXHAUSTED - errorhandler.py:37")
            print(f"Attempt : {attempt + 1}/{retries} - errorhandler.py:38")
            print(f"Retry After : {wait} seconds - errorhandler.py:39")
            print("= - errorhandler.py:40" * 80)

            if attempt < retries - 1:

                time.sleep(wait)

                return "retry"

            print("\nRetries exhausted for current API Key. - errorhandler.py:48")
            print("Switching to next API Key... - errorhandler.py:49")

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

            print("\n - errorhandler.py:76" + "=" * 80)
            print("GEMINI SERVER BUSY - errorhandler.py:77")
            print("Model is experiencing high demand. - errorhandler.py:78")
            print(f"Waiting {wait} seconds before retrying... - errorhandler.py:79")
            print("Current scheme will NOT be skipped. - errorhandler.py:80")
            print("= - errorhandler.py:81" * 80)

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

            print("\n - errorhandler.py:115" + "=" * 80)
            print("TEMPORARY GEMINI ERROR - errorhandler.py:116")
            print(message)
            print(f"Retrying after {wait} seconds... - errorhandler.py:118")
            print("= - errorhandler.py:119" * 80)

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

            print("\n - errorhandler.py:150" + "=" * 80)
            print("INVALID GEMINI API KEY - errorhandler.py:151")
            print("Current API key is invalid, deleted or expired. - errorhandler.py:152")
            print("Switching to next API Key... - errorhandler.py:153")
            print("= - errorhandler.py:154" * 80)

            return "switch_key"

        # ==================================================
        # 5. Permanent Error
        # ==================================================

        print("\n - errorhandler.py:162" + "=" * 80)
        print("NONRETRYABLE GEMINI ERROR - errorhandler.py:163")
        print(message)
        print("= - errorhandler.py:165" * 80)

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