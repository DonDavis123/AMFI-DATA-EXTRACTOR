import os
from dotenv import load_dotenv


class ApiKeyManager:
    """
    Manages multiple Gemini API keys.

    Responsibilities
    ----------------
    • Load API keys from environment
    • Return current API key
    • Switch to next API key
    • Detect when all keys are exhausted
    """

    def __init__(self):

        load_dotenv()

        self.api_keys = []

        index = 1

        while True:

            key = os.getenv(f"GEMINI_API_KEY_{index}")

            if not key:
                break

            self.api_keys.append(key)

            index += 1

        if not self.api_keys:

            raise RuntimeError(
                "No Gemini API keys found in .env"
            )

        self.current_index = 0

    # --------------------------------------------------
    # Current Key
    # --------------------------------------------------

    def get_key(self):

        return self.api_keys[self.current_index]

    # --------------------------------------------------
    # Switch Key
    # --------------------------------------------------

    def switch_key(self):

        if self.current_index >= len(self.api_keys) - 1:

            raise RuntimeError(
                "ALL_API_KEYS_EXHAUSTED"
            )

        self.current_index += 1

        print("\n - api_keymanager.py:66" + "=" * 80)
        print("Switching Gemini API Key - api_keymanager.py:67")
        print(
            f"Using API Key "
            f"{self.current_index + 1}/{len(self.api_keys)}"
        )
        print("= - api_keymanager.py:72" * 80)

        return self.get_key()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def current_key_number(self):

        return self.current_index + 1

    def total_keys(self):

        return len(self.api_keys)