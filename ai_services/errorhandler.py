import re
import time


class GeminiErrorHandler:
    """
    Handles Gemini API quota and retry errors.
    """

    @staticmethod
    def handle(error, attempt, retries):

        message = str(error)

        # --------------------------------------------------
        # Quota / Rate Limit
        # --------------------------------------------------

        if (
            "RESOURCE_EXHAUSTED" in message
            or "429" in message
            or "quota" in message.lower()
            or "rate limit" in message.lower()
        ):

            wait = GeminiErrorHandler._get_retry_time(message)

            print("\n - errorhandler.py:28" + "=" * 80)
            print("GEMINI RATE LIMIT REACHED - errorhandler.py:29")
            print(f"Retrying after {wait} seconds... - errorhandler.py:30")
            print("= - errorhandler.py:31" * 80)

            time.sleep(wait)

            if attempt < retries - 1:
                return "retry"

            raise RuntimeError("GEMINI_QUOTA_EXCEEDED")

        # --------------------------------------------------
        # Other Errors
        # --------------------------------------------------

        print(
            f"Gemini failed "
            f"(Attempt {attempt + 1}/{retries}) : {message}"
        )

        if attempt < retries - 1:

            time.sleep(5)

            return "retry"

        return "failed"

    @staticmethod
    def _get_retry_time(message):

        match = re.search(
            r"retry in ([0-9.]+)s",
            message,
            re.IGNORECASE
        )

        if match:

            return int(float(match.group(1))) + 2

        return 60