from xml.etree import ElementTree as ET
from copy import deepcopy


class XmlOptimizer:
    """
    Optimizes Excel 2003 SpreadsheetML XML before sending it to Gemini.

    Removes:
    - Workbook metadata
    - Styles
    - Column definitions
    - Empty formatting-only cells
    - Empty rows
    - StyleID attributes

    Preserves:
    - All Data elements
    - MergeAcross / MergeDown
    - Index
    - Data Type
    - Worksheet/Table structure
    """

    SPREADSHEET_NS = "urn:schemas-microsoft-com:office:spreadsheet"

    REMOVE_TAGS = {
        "DocumentProperties",
        "OfficeDocumentSettings",
        "ExcelWorkbook",
        "Styles",
        "Names",
        "WorksheetOptions",
        "PageSetup",
        "Print",
        "Header",
        "Footer",
        "ConditionalFormatting",
    }

    def optimize(self, xml_string: str) -> str:

        try:
            root = ET.fromstring(xml_string)
        except Exception:
            return xml_string

        # -------------------------------------------------------
        # Verify SpreadsheetML
        # -------------------------------------------------------

        if not root.tag.endswith("Workbook"):
            return xml_string

        if self.SPREADSHEET_NS not in root.tag:
            return xml_string

        root = deepcopy(root)

        # -------------------------------------------------------
        # Remove workbook metadata
        # -------------------------------------------------------

        for child in list(root):

            tag = child.tag.split("}")[-1]

            if tag in self.REMOVE_TAGS:
                root.remove(child)

        # -------------------------------------------------------
        # Remove StyleID attributes
        # -------------------------------------------------------

        for element in root.iter():

            for attr in list(element.attrib.keys()):

                if attr.endswith("StyleID"):
                    del element.attrib[attr]

        # -------------------------------------------------------
        # Remove Column definitions
        # -------------------------------------------------------

        for table in root.findall(".//{*}Table"):

            for child in list(table):

                if child.tag.endswith("Column"):
                    table.remove(child)

        # -------------------------------------------------------
        # Remove formatting-only cells
        # -------------------------------------------------------

        for row in root.findall(".//{*}Row"):

            for cell in list(row.findall("{*}Cell")):

                # Preserve merged cells
                if any(
                    attr.endswith("MergeAcross") or attr.endswith("MergeDown")
                    for attr in cell.attrib
                ):
                    continue

                # Preserve cells containing data
                if cell.find("{*}Data") is not None:
                    continue

                row.remove(cell)

        # -------------------------------------------------------
        # Remove empty rows
        # -------------------------------------------------------

        for row in list(root.findall(".//{*}Row")):

            if row.findall("{*}Cell"):
                continue

            parent = self._find_parent(root, row)

            if parent is not None:
                parent.remove(row)

        # -------------------------------------------------------
        # Return optimized XML
        # -------------------------------------------------------

        return ET.tostring(
            root,
            encoding="unicode"
        )

    def _find_parent(self, root, child):

        for parent in root.iter():

            for node in parent:

                if node is child:
                    return parent

        return None