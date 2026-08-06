from xml.etree import ElementTree as ET

from processors.optimizer.spreadsheet_optimizer import SpreadsheetOptimizer
from processors.optimizer.scheme_summary_optimizer import SchemeSummaryOptimizer
from system_logger import SystemLogger

system_logger = SystemLogger.get_logger()


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

        except ET.ParseError as e:

         system_logger.error(
            f"XML parse error: {e}"
        )

         return xml_string

        # --------------------------------------------------
        # Detect SpreadsheetML
        # --------------------------------------------------

        if (
            root.tag.endswith("Workbook")
            and self.SPREADSHEET_NS in root.tag
        ):

            

            return self.spreadsheet_optimizer.optimize(
                xml_string
            )

        # --------------------------------------------------
        # Detect SchemeSummary XML
        # --------------------------------------------------

        if root.tag.endswith("SchemeSummaryDocument"):

           

            return self.scheme_optimizer.optimize(
                xml_string
            )

        # --------------------------------------------------
        # Unknown XML
        # --------------------------------------------------

        system_logger.warning(
           f"Unknown XML format encountered: {root.tag}"
        )
        return xml_string