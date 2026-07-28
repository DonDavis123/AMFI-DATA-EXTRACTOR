import os
import json
import time

import google.generativeai as genai
from dotenv import load_dotenv

from models import FundExtraction


class GeminiAI:

    def __init__(self):

        load_dotenv()

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        self.model = genai.GenerativeModel(
            "gemini-3.5-flash-lite"
        )

    def extract(self, xml):

        if not xml or not xml.strip():
            print("Empty XML received. - ai_service.py:26")
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

        for attempt in range(retries):

            try:

                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=FundExtraction,
                        temperature=0,
                    ),
                )

                data = json.loads(response.text)

                return FundExtraction(**data)

            except Exception as e:

                error = str(e)

                # --------------------------------------------------
                # Gemini Free Tier / Quota Exhausted
                # --------------------------------------------------

                if (
                    "RESOURCE_EXHAUSTED" in error
                    or "429" in error
                    or "quota" in error.lower()
                    or "rate limit" in error.lower()
                ):

                    print("\n - ai_service.py:109" + "=" * 80)
                    print("GEMINI FREE TIER LIMIT REACHED - ai_service.py:110")
                    print("Stopping extraction. - ai_service.py:111")
                    print("Please run the program again after your quota resets. - ai_service.py:112")
                    print("= - ai_service.py:113" * 80)

                    raise RuntimeError("GEMINI_QUOTA_EXCEEDED")

                # --------------------------------------------------
                # Normal Errors
                # --------------------------------------------------

                print(
                    f"Gemini failed "
                    f"(Attempt {attempt + 1}/{retries}) : {error}"
                )

                if attempt < retries - 1:
                    time.sleep(5)

        return None