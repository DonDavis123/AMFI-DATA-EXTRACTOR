from copy import deepcopy
from xml.etree import ElementTree as ET
from system_logger import SystemLogger

system_logger = SystemLogger.get_logger()


class SchemeSummaryOptimizer:
    """
    Optimizes AMFI SchemeSummary XML.

    Safety Rules
    ------------
    1. XML must be valid.
    2. Root must be SchemeSummaryDocument.
    3. Exactly one SchemeSummary must exist.
    4. Every required tag must exist.
    5. If validation fails, return the original XML.
    """

    REQUIRED_TAGS = {


        "Options_Names",
        
        "Fund_Name",

        "Fund_Type",

        "Option_Names_Regular__Direct",

        "ISINs",

        "Riskometer_At_the_time_of_Launch",

        "Riskometer_as_on_Date",

        "Category_as_Per_SEBI_Categorization_Circular",

        "Description_Objective_of_the_scheme",

        "Fund_Manager_Name",
    }

    def optimize(self, xml_string: str) -> str:

        # --------------------------------------------------
        # Parse XML
        # --------------------------------------------------

        try:
            root = ET.fromstring(xml_string)

        except ET.ParseError:

            system_logger.error(
               "Invalid SchemeSummary XML."
            )

            return xml_string

        # --------------------------------------------------
        # Verify Root
        # --------------------------------------------------

        if not root.tag.endswith("SchemeSummaryDocument"):

            return xml_string

        # --------------------------------------------------
        # Verify SchemeSummary
        # --------------------------------------------------

        summaries = root.findall("SchemeSummary")

        if len(summaries) != 1:


            return xml_string

        summary = summaries[0]

        # --------------------------------------------------
        # Verify Required Tags
        # --------------------------------------------------

        existing_tags = {
            child.tag.split("}")[-1]
            for child in summary
        }

        missing = self.REQUIRED_TAGS - existing_tags

        if missing:

           

            return xml_string

        # --------------------------------------------------
        # Create Safe Copy
        # --------------------------------------------------

        optimized_root = deepcopy(root)

        optimized_summary = optimized_root.find("SchemeSummary")

        # --------------------------------------------------
        # Remove Unwanted Tags
        # --------------------------------------------------

        removed_tags = 0

        for child in list(optimized_summary):

            tag = child.tag.split("}")[-1]

            if tag not in self.REQUIRED_TAGS:

                optimized_summary.remove(child)

                removed_tags += 1

        # --------------------------------------------------
        # Normalize Whitespace
        # --------------------------------------------------

        for child in optimized_summary:

            if child.text:

                child.text = child.text.strip()

        # --------------------------------------------------
        # Generate Optimized XML
        # --------------------------------------------------

        optimized_xml = ET.tostring(
            optimized_root,
            encoding="unicode"
        )

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        original_size = len(xml_string)
        optimized_size = len(optimized_xml)

        reduction = (
            (original_size - optimized_size)
            / original_size
        ) * 100

       

        return optimized_xml