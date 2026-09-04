import os

from dotenv import load_dotenv
from system_logger import SystemLogger


system_logger = SystemLogger.get_logger()


class ApiKeyManager:
    """
    Manages multiple Gemini API keys.

    Responsibilities
    ----------------
    • Load API keys from environment
    • Return current API key
    • Switch to next API key
    • Detect when all keys are exhausted
    • Reset key rotation after quota reset
    """

    def __init__(self):

        load_dotenv()

        self.api_keys = []

        index = 1

        # --------------------------------------------------
        # Load Gemini API Keys
        # --------------------------------------------------

        while True:

            key = os.getenv(
                f"GEMINI_API_KEY_{index}"
            )

            if not key:
                break

            self.api_keys.append(key)

            index += 1

        # --------------------------------------------------
        # Validate Keys
        # --------------------------------------------------

        if not self.api_keys:

            raise RuntimeError(
                "No Gemini API keys found in .env"
            )

        # --------------------------------------------------
        # Start With First Key
        # --------------------------------------------------

        self.current_index = 0

    # ==================================================
    # Current Key
    # ==================================================

    def get_key(self):

        return self.api_keys[
            self.current_index
        ]

    # ==================================================
    # Switch To Next Key
    # ==================================================

    def switch_key(self):

        # --------------------------------------------------
        # Already On Last Key
        # --------------------------------------------------

        if (
            self.current_index
            >= len(self.api_keys) - 1
        ):

            system_logger.error(
                "All Gemini API keys exhausted."
            )

            raise RuntimeError(
                "ALL_API_KEYS_EXHAUSTED"
            )

        # --------------------------------------------------
        # Move To Next Key
        # --------------------------------------------------

        self.current_index += 1

        system_logger.warning(
            f"Switching to Gemini API key "
            f"{self.current_key_number()} "
            f"of {self.total_keys()}."
        )

        return self.get_key()

    # ==================================================
    # Reset Key Rotation
    # ==================================================

    def reset(self):

        self.current_index = 0

        system_logger.info(
            "Gemini API key rotation reset. "
            "Starting from API key 1."
        )

        return self.get_key()

    # ==================================================
    # Current Key Number
    # ==================================================

    def current_key_number(self):

        return self.current_index + 1

    # ==================================================
    # Total Keys
    # ==================================================

    def total_keys(self):

        return len(self.api_keys)