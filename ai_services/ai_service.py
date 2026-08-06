import os
import json
import time

from google import genai
from google.genai import types
from dotenv import load_dotenv


from ai_services.errorhandler import GeminiErrorHandler
from models import FundExtraction
from ai_services.api_keymanager import ApiKeyManager


class GeminiAI:

    def __init__(self):

        load_dotenv()
        

        self.key_manager=ApiKeyManager()

        self.client = genai.Client(
            api_key=self.key_manager.get_key()
        )

    def extract(self, xml):

        if not xml or not xml.strip():
            print("Empty XML received. - ai_service.py:31")
            return None

        prompt = f"""
You are an expert Mutual Fund XML extraction engine.

Read the XML carefully.

Extract ONLY REGULAR PLANS.

Ignore every Direct Plan.

Rules:

1. Extract Fund Name.
2. Extract Fund Type.
3. Extract Category.
4. Extract Description.
5. Extract Fund Manager Name.
Extract ONLY the actual fund manager names.

 Remove labels such as FM1, FM2, FM3, Fund Manager 1, etc.

 Remove numbering.

 Remove brackets and explanatory text such as:
   - (FI Portion)
   - (Equity Portion)
   - (Debt Portion)
   - (Overseas Portion)

 Return only clean human names.

6. Extract Riskometer At Launch.
7. Extract Riskometer As On Date.
8. Read Option_Names_Regular__Direct.
9. Read ISINs.
10. Match every option with the ISIN on the SAME LINE.
11. Ignore every option containing the word "Direct".
12. Return one object for every Regular Plan.
13. Never invent values.
14. Never return Direct Plans.
15. Return valid JSON only.

XML

{xml}
"""

        retries = 3

        while True:

            for attempt in range(retries):

                try:

                    print(
                        f"Using API Key : "
                        f"{self.key_manager.current_key_number()}/"
                        f"{self.key_manager.total_keys()}"
                    )

                    

                    response = self.client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=FundExtraction,
                            temperature=0,
                        ),
                    )

                    data = json.loads(response.text)

                    return FundExtraction(**data)

                except Exception as e:

                    import traceback

                    
                    print(type(e))
                    print(repr(e))
                    traceback.print_exc()
                    

                    action = GeminiErrorHandler.handle(
                        e,
                        attempt,
                        retries
                    )

                    # ------------------------------------------
                    # Retry using the same API key
                    # ------------------------------------------

                    if action == "retry":
                        continue
                    if action == "retry_forever":

                        print("\nWaiting for Gemini service to recover... - ai_service.py:134")

                        break

                    # ------------------------------------------
                    # Switch to next API key
                    # ------------------------------------------

                    if action == "switch_key":

                        try:

                            new_key = self.key_manager.switch_key()

                            self.client = genai.Client(
                                api_key=new_key
                            )

                            print("\n - ai_service.py:152" + "=" * 80)
                            print(
                                f"Switched to API Key "
                                f"{self.key_manager.current_key_number()}/"
                                f"{self.key_manager.total_keys()}"
                            )
                            print("= - ai_service.py:158" * 80)

                            # Exit retry loop and restart with new key
                            break

                        except RuntimeError:

                            raise RuntimeError(
                                "ALL_API_KEYS_EXHAUSTED"
                            )

                    # ------------------------------------------
                    # Non-retryable error
                    # ------------------------------------------

                    if action == "failed":
                        return None

            else:
                # Success never happened and no key switch occurred.
                return None

            # We switched to a new API key.
            # Restart retry loop using the new key.
            continue