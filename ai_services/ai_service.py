import os
import json
import time


from google import genai
from google.genai import types
from dotenv import load_dotenv


from ai_services.errorhandler import GeminiErrorHandler
from models import FundExtraction
from ai_services.api_keymanager import ApiKeyManager
from system_logger import SystemLogger

system_logger = SystemLogger.get_logger()


class GeminiAI:

    def __init__(self):

        load_dotenv()
        

        self.key_manager=ApiKeyManager()

        self.client = genai.Client(
            api_key=self.key_manager.get_key()
        )

    def extract(self, xml):

        if not xml or not xml.strip():
            system_logger.warning(
              "Empty XML received. Skipping Gemini extraction."
)
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

   Return a clean, readable description.

   Remove:
   - Unnecessary line breaks
   - \n characters
   - \r characters
   - \t characters
   - Repeated spaces
   - Unnecessary whitespace at the beginning or end
   - Formatting artifacts caused by XML

   Convert text that is split across multiple lines into normal
   sentences with appropriate spaces.

   Example:

   Source:
   "The scheme seeks to generate
   regular income through
   investments in debt instruments."

   Output:
   "The scheme seeks to generate regular income through investments in debt instruments."

   Do NOT change the meaning of the description.
   Do NOT summarize it.
   Do NOT rewrite it.
   Do NOT invent missing text.

5. Extract ALL Fund Manager Names.

   A scheme may have one or multiple fund managers.

   Extract EVERY actual fund manager name present in the XML.

   If the XML contains:
   - FM1
   - FM2
   - FM3
   - Fund Manager 1
   - Fund Manager 2
   - Fund Manager 3

   extract the name associated with EACH manager.

   Do NOT return only the first manager.

   Remove structural labels such as:
   - FM1
   - FM2
   - FM3
   - Fund Manager 1
   - Fund Manager 2
   - Fund Manager 3

   Remove numbering.

   Remove portfolio-role annotations only when they are clearly
   annotations, such as:
   - (FI Portion)
   - (Equity Portion)
   - (Debt Portion)
   - (Overseas Portion)

   Do NOT remove legitimate parts of a person's name.

   Return every manager as a separate item in fund_manager_name.

   Example:

   Source:
   FM1: John Smith
   FM2: Jane Doe
   FM3: Robert Brown

   Output:
   [
       "John Smith",
       "Jane Doe",
       "Robert Brown"
   ]

   If only one manager exists, return one item.

   If no manager is present, return an empty array.

   Never invent a manager name.
   Never omit a manager that is present in the XML.

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

16. Preserve the original meaning of all extracted text.

17. Do not include XML tags, XML formatting artifacts, escape
    characters, or unnecessary whitespace in the output.

18. For descriptions, normalize whitespace but do not summarize,
    shorten, or paraphrase the source text.

19. For fund manager names, return ALL managers found in the XML.
    Never reduce multiple managers to a single name.

XML



{xml}
"""

        retries = 3

        while True:

            for attempt in range(retries):

                try:

                   

                    

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