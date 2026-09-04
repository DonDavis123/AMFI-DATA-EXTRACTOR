import os
import json

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

        self.key_manager = ApiKeyManager()

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

Your task is to extract CURRENT REGULAR PLAN records from the XML.

The XML may use different structures for representing options and ISINs.
You MUST first identify the structure used by the XML and then apply the
appropriate mapping strategy.

Do NOT assume that all XML files use the same format.

============================================================
1. REQUIRED OUTPUT
============================================================

Extract these fields for every eligible record:

- Fund Name
- Fund Type
- Category
- Description
- Riskometer At Launch
- Riskometer As On Date
- Fund Manager Name(s)
- ISIN

Return exactly ONE output object for every distinct CURRENT REGULAR ISIN.

ISIN is the unique identity of an output record.

Never merge two different ISINs into one record.

If two records have:

- the same Fund Name
- the same option name
- the same IDCW type
- the same Fund Manager

but different ISINs,

they MUST still be returned as separate records.

============================================================
2. CURRENT REGULAR ONLY
============================================================

Extract ONLY CURRENT REGULAR PLANS.

Ignore every Direct Plan.

Any option containing "Direct" is a Direct Plan.

Examples:

Direct Growth
Direct IDCW
Direct Monthly IDCW
Direct Quarterly IDCW
Direct Weekly IDCW
Direct Plan - Growth
Direct Plan - IDCW
Direct - Super Institutional Growth

Do NOT return Direct records even if their ISINs are present.

============================================================
3. PHASED-OUT / HISTORICAL DATA
============================================================

Do NOT create current records from:

- RTA_Code_To_be_phased_out
- AMFI_Codes_To_be_phased_out

These fields contain historical/phased-out information.

Never use them to invent or infer a current ISIN.

If the option field itself contains a note saying an option is:

- discontinued
- closed
- no longer available
- no new investors can invest
- existing investors remain invested
- historical
- phased out

then treat that option as NOT CURRENT.

Do not create records for explicitly discontinued options.

Example:

Regular Bonus#
Regular Half Yearly IDCW#
Regular Monthly IDCW#

followed by:

"Bonus plan and Monthly & Half yearly Dividend payout options
are discontinued"

means those three options are historical/discontinued.

They must not produce current output records.

The "#" marker is a source marker and is not part of the option name.

============================================================
4. DETECT THE XML MAPPING FORMAT FIRST
============================================================

Before extracting ISINs, determine which of the following formats
the XML uses.

FORMAT A:
Explicit ISIN + option pairs.

FORMAT B:
<Options_Names> array where each item contains its own ISIN and
OptionsNames.

FORMAT C:
<Option_Names_Regular__Direct> contains a separate list of options
and <ISINs> contains a separate list of bare ISINs.

FORMAT D:
A mixed or unusual structure.

Use the most explicit available mapping.

Priority:

1. ISIN and option inside the SAME <Options_Names> item
2. Explicit ISIN-option pairs inside <ISINs>
3. Other explicit ISIN-option relationships
4. Separate option list + separate ISIN list using cardinality
5. If no reliable mapping is possible, DO NOT GUESS

============================================================
5. FORMAT A — EXPLICIT ISIN + OPTION PAIRS
============================================================

If <ISINs> contains entries such as:

Regular - Growth - INF090I01BB1
Regular - Daily - IDCW Reinv. - INF090I01BA3
Regular - Weekly - IDCW Payout - INF090I01BL0
Regular - Weekly - IDCW Reinv. - INF090I01BI6

then each explicit ISIN-option pair is one separate record.

Extract every eligible Regular pair.

For example:

Regular - Growth - INF090I01BB1

must produce:

ISIN = INF090I01BB1

and:

Regular - Weekly - IDCW Payout - INF090I01BL0

must produce:

ISIN = INF090I01BL0

Do NOT merge them.

============================================================
6. EXPLICIT ISIN + OPTION PAIRS WITHOUT LINE BREAKS
============================================================

The XML may contain many ISIN-option pairs in a single line.

Do NOT depend on:

- newline
- comma
- XML formatting
- spaces alone

Use the ISIN pattern to identify each individual pair.

An ISIN is an alphanumeric identifier beginning with "INF".

When an ISIN and its option name are explicitly associated in the
same source entry, preserve that relationship.

Never assign an ISIN to another option merely because it is nearby.

============================================================
7. FORMAT B — OPTIONS_NAMES ARRAY
============================================================

If the XML contains:

<Options_Names>
    <item>
        <ISIN>...</ISIN>
        <AMFICode>...</AMFICode>
        <SchemeCode>...</SchemeCode>
        <OptionsNames>...</OptionsNames>
    </item>
</Options_Names>

process EVERY item independently.

The ISIN and OptionsNames inside the SAME item belong together.

Example:

ISIN:
INF200K01875

OptionsNames:
Regular Plan - IDCW

and:

ISIN:
INF200K01891

OptionsNames:
Regular Plan - IDCW

MUST produce TWO separate records.

Do NOT merge them because the option names are identical.

If OptionsNames contains "Direct", ignore that entire item.

Examples:

Direct Plan - IDCW
Direct Plan - Growth

must not be returned.

If OptionsNames indicates Regular, return that item.

AMFICode and SchemeCode must NEVER be used to merge records.

ISIN is the unique identity.

============================================================
8. FORMAT C — SEPARATE OPTION LIST AND ISIN LIST
============================================================

Some XML files contain:

<Option_Names_Regular__Direct>

and:

<ISINs>

where the option names and ISINs are separate lists.

In this format, do NOT assume:

one option = one ISIN.

The option determines its ISIN cardinality.

============================================================
9. IDCW CARDINALITY IN SEPARATE-LIST FORMAT
============================================================

When using the separate option-list + bare-ISIN-list format:

A Growth option normally represents:

1 ISIN

An IDCW option normally represents:

2 consecutive ISINs

Examples:

Regular Growth
→ 1 ISIN

Regular Monthly IDCW
→ 2 consecutive ISINs

Regular Quarterly IDCW
→ 2 consecutive ISINs

Regular Weekly IDCW
→ 2 consecutive ISINs

Regular Daily IDCW
→ 2 consecutive ISINs

Do NOT require the words "Payout" and "Reinvestment" to be present.

If:

Regular Monthly IDCW

corresponds to two consecutive ISINs, both ISINs are separate output
records.

Preserve the source option name.

For example:

ISIN_A → Regular Monthly IDCW
ISIN_B → Regular Monthly IDCW

Do NOT automatically rename them:

Regular Monthly IDCW Payout
Regular Monthly IDCW Reinvestment

unless the source explicitly provides those names.

============================================================
10. "REGULAR IDCW" IS ALSO AN IDCW GROUP
============================================================

If the option is:

Regular IDCW

or:

Regular Regular IDCW

and the XML uses the separate option-list + bare-ISIN-list format,
treat it as an IDCW group.

Therefore it normally consumes:

2 consecutive ISINs.

Example:

Regular Regular IDCW

with two corresponding ISINs means:

ISIN_A → Regular Regular IDCW
ISIN_B → Regular Regular IDCW

Both must be returned.

============================================================
11. REINVESTMENT & PAYOUT
============================================================

If an option contains:

Re-investment & Payout

or:

Reinvestment & Payout

do NOT automatically assume that one ISIN represents both variants.

If TWO corresponding ISINs exist, they represent TWO separate records.

Example:

Regular Weekly IDCW - Re-investment & Payout

with two corresponding ISINs:

ISIN_A
ISIN_B

must produce TWO records.

If the source explicitly distinguishes the variants, preserve the
exact source names.

If the source only says:

Regular Weekly IDCW - Re-investment & Payout

do NOT invent:

Payout
Reinvestment

as option names.

Instead preserve:

Regular Weekly IDCW - Re-investment & Payout

for both records unless the source provides more specific names.

============================================================
12. EXPLICIT PAYOUT / REINVESTMENT
============================================================

If the XML explicitly provides:

Regular Weekly IDCW Payout
Regular Weekly IDCW Reinvestment

with different ISINs,

return both as separate records.

Likewise:

Regular Monthly IDCW Payout
Regular Monthly IDCW Reinvestment

must remain separate when their ISINs differ.

Never merge them.

============================================================
13. PLAIN "IDCW" RULE
============================================================

If an option says only:

IDCW

do NOT automatically rename it to:

IDCW Payout

or:

IDCW Reinvestment.

Preserve the exact source wording.

However, in the separate option-list + bare-ISIN-list format,
plain IDCW is treated as an IDCW group and normally consumes two
consecutive ISINs.

============================================================
14. SEQUENTIAL MAPPING
============================================================

For the separate option-list + bare-ISIN-list format:

1. Read the COMPLETE option list.
2. Identify actual option entries.
3. Remove explanatory notes.
4. Remove explicitly discontinued options.
5. Identify Direct options.
6. Identify current Regular options.
7. Determine the cardinality of every option.
8. Verify the expected ISIN count against the supplied ISIN count.
9. Only then map ISINs sequentially in XML order.

Cardinality:

Growth = 1 ISIN

IDCW = 2 ISINs

Explicit Payout/Reinvestment pair = 1 ISIN each

Combined Re-investment & Payout option with two corresponding ISINs
= 2 ISINs

============================================================
15. COUNT VALIDATION
============================================================

Before mapping a separate option list to a bare ISIN list, calculate:

EXPECTED ISIN COUNT =
sum of the cardinality of every option represented in the XML.

Compare this against the number of ISINs supplied.

If the counts match:

perform sequential mapping in XML order.

If the counts do not match:

DO NOT guess.

Do not shift ISINs arbitrarily.

Do not invent missing ISINs.

Do not silently discard extra ISINs.

Look for:

- discontinued options
- Direct options
- notes
- explicit payout/reinvestment variants
- IDCW groups
- historical options
- unusual option structures

Only create records when the mapping is reliably supported.

============================================================
16. IMPORTANT EXAMPLE
============================================================

Suppose:

<Option_Names_Regular__Direct>

contains:

Direct Growth
Direct Monthly IDCW
Regular Bonus#
Regular Growth Option
Regular Half Yearly IDCW#
Regular Monthly IDCW#
Regular Quarterly IDCW

and the XML note says:

"Bonus plan and Monthly & Half yearly Dividend payout options
are discontinued"

Then:

Regular Bonus
= discontinued

Regular Half Yearly IDCW
= discontinued

Regular Monthly IDCW
= discontinued

The remaining options are:

Direct Growth
Direct Monthly IDCW
Regular Growth Option
Regular Quarterly IDCW

Cardinality:

Direct Growth
= 1

Direct Monthly IDCW
= 2

Regular Growth Option
= 1

Regular Quarterly IDCW
= 2

Total = 6 ISINs.

If the six ISINs are:

INF579M01290
INF579M01324
INF579M01266
INF579M01217
INF579M01241
INF579M01183

map them:

Direct Growth
→ INF579M01290

Direct Monthly IDCW
→ INF579M01324
→ INF579M01266

Regular Growth Option
→ INF579M01217

Regular Quarterly IDCW
→ INF579M01241
→ INF579M01183

Return ONLY:

INF579M01217
INF579M01241
INF579M01183

============================================================
17. IMPORTANT EXAMPLE — EXPLICIT PAIRS
============================================================

If the XML contains:

Regular - Growth - INF090I01BB1
Regular - Daily - IDCW Reinv. - INF090I01BA3
Regular - Weekly - IDCW Payout - INF090I01BL0
Regular - Weekly - IDCW Reinv. - INF090I01BI6
Direct - Super Institutional Growth - INF090I01JV2

then:

INF090I01BB1
INF090I01BA3
INF090I01BL0
INF090I01BI6

are eligible Regular records.

INF090I01JV2 must be ignored.

Do not use the separate option-list cardinality rules because the
ISIN-option relationship is already explicitly provided.

============================================================
18. IMPORTANT EXAMPLE — OPTIONS_NAMES ARRAY
============================================================

If the XML contains:

<item>
<ISIN>INF200K01875</ISIN>
<OptionsNames>Regular Plan - IDCW</OptionsNames>
</item>

<item>
<ISIN>INF200K01891</ISIN>
<OptionsNames>Regular Plan - IDCW</OptionsNames>
</item>

both must be returned.

The result is TWO records.

Do not merge them.

============================================================
19. OPTION NAME PRESERVATION
============================================================

Preserve source option wording.

Do NOT:

- rename IDCW to Payout
- rename IDCW to Reinvestment
- rename Reinv. to Reinvestment
- invent Payout
- invent Reinvestment
- remove legitimate plan identifiers
- merge different options

Clean only obvious XML formatting artifacts.

============================================================
20. FUND MANAGERS
============================================================

Extract ALL actual Fund Manager names.

If the XML contains:

Mr. A, Mr. B, Mr. C

return:

[
    "Mr. A",
    "Mr. B",
    "Mr. C"
]

If manager information appears as FM1, FM2, FM3 or similar labels,
extract the actual names.

Remove structural labels and numbering.

Do not remove legitimate parts of a person's name.

If no actual manager exists, return an empty array.

Never invent a manager.

============================================================
21. DESCRIPTION
============================================================

Clean the description by removing:

- unnecessary line breaks
- \n
- \r
- \t
- repeated spaces
- XML formatting artifacts
- leading/trailing whitespace

Convert broken lines into normal sentences.

Do NOT:

- summarize
- shorten
- paraphrase
- rewrite
- change meaning

============================================================
22. ABSOLUTE SAFETY RULES
============================================================

NEVER:

- invent an ISIN
- invent an option
- invent a Payout/Reinvestment relationship
- merge different ISINs
- omit an explicitly eligible Regular ISIN
- return Direct plans
- return explicitly discontinued options
- use phased-out RTA codes
- use phased-out AMFI codes to create current records
- reorder explicitly paired ISINs
- guess when the mapping is ambiguous

ALWAYS:

- identify the XML structure first
- prefer explicit ISIN-option relationships
- process every Options_Names item
- treat every distinct ISIN as a separate identity
- use IDCW cardinality only when the XML uses the separate option-list
  + bare-ISIN-list format
- validate ISIN counts before sequential mapping
- preserve source option wording
- return ALL eligible Regular records

============================================================
23. FINAL VALIDATION BEFORE OUTPUT
============================================================

Before returning JSON, verify:

1. Every returned ISIN exists in the XML.
2. Every returned ISIN belongs to a CURRENT Regular option.
3. No returned ISIN belongs to Direct.
4. No returned ISIN belongs only to phased-out data.
5. No two output objects have been merged.
6. No eligible Regular ISIN has been omitted.
7. No ISIN has been invented.
8. The number of records equals the number of eligible Regular ISINs.
9. Explicit mappings were preferred over inferred mappings.
10. IDCW cardinality was used only when appropriate.
11. Discontinued-option notes were respected.
12. The output is valid JSON matching the provided response schema.

Return JSON only.

XML:

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

                    # Optional debugging: print exactly what Gemini extracted
                    system_logger.info(
                        "Gemini extraction successful. "
                        f"Extracted {len(data.get('funds', []))} fund records."
                    )

                    for fund in data.get("funds", []):
                        system_logger.info(
                            f"Extracted ISIN: {fund.get('isin')} | "
                            f"Fund: {fund.get('fund_name')} | "
                            f"Managers: {fund.get('fund_manager_name')}"
                        )

                    return FundExtraction(**data)

                except Exception as e:

                    action = GeminiErrorHandler.handle(
                        e,
                        attempt,
                        retries
                    )

                    # Retry using the same API key
                    if action == "retry":
                        continue

                    if action == "retry_forever":
                        break

                    # Switch to next API key
                    if action == "switch_key":

                        try:

                            new_key = self.key_manager.switch_key()

                            self.client = genai.Client(
                                api_key=new_key
                            )

                            # Restart extraction using new key
                            break

                        except RuntimeError:

                            raise RuntimeError(
                                "ALL_API_KEYS_EXHAUSTED"
                            )

                    # Non-retryable error
                    if action == "failed":
                        return None

            else:
                return None

            # A new API key was selected.
            # Restart extraction for the SAME XML.
            continue