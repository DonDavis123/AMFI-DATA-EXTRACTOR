from xml.etree import ElementTree as ET

from processors.optimizer.spreadsheet_optimizer import SpreadsheetOptimizer
from processors.optimizer.scheme_summary_optimizer import SchemeSummaryOptimizer


class XmlManager:
    """
    Detects the XML format and routes it to the correct optimizer.

    Supported Formats
    -----------------
    1. Excel SpreadsheetML
    2. AMFI SchemeSummary XML

    Any unknown XML is returned unchanged.
    """

    SPREADSHEET_NS = "urn:schemas-microsoft-com:office:spreadsheet"

    def __init__(self):

        self.spreadsheet_optimizer = SpreadsheetOptimizer()
        self.scheme_optimizer = SchemeSummaryOptimizer()

    def optimize(self, xml_string: str) -> str:

        # --------------------------------------------------
        # Validate XML
        # --------------------------------------------------

        try:
            root = ET.fromstring(xml_string)

        except ET.ParseError:

            print("\nInvalid XML. - xml_manager.py:37")
            print("Skipping optimization. - xml_manager.py:38")

            return xml_string

        # --------------------------------------------------
        # Detect SpreadsheetML
        # --------------------------------------------------

        if (
            root.tag.endswith("Workbook")
            and self.SPREADSHEET_NS in root.tag
        ):

            print("\nDetected XML : SpreadsheetML - xml_manager.py:51")
            print("Using Spreadsheet Optimizer... - xml_manager.py:52")

            return self.spreadsheet_optimizer.optimize(
                xml_string
            )

        # --------------------------------------------------
        # Detect SchemeSummary XML
        # --------------------------------------------------

        if root.tag.endswith("SchemeSummaryDocument"):

            print("\nDetected XML : SchemeSummaryDocument - xml_manager.py:64")
            print("Using SchemeSummary Optimizer... - xml_manager.py:65")

            return self.scheme_optimizer.optimize(
                xml_string
            )

        # --------------------------------------------------
        # Unknown XML
        # --------------------------------------------------

        print("\nUnknown XML format. - xml_manager.py:75")
        print("Skipping optimization. - xml_manager.py:76")

        return xml_string