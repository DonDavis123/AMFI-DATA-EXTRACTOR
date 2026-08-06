import codecs
import re
from system_logger import SystemLogger

system_logger = SystemLogger.get_logger()


class XmlDecoder:
    """
    Safely decodes XML responses.

    Supported
    ---------
    • UTF-8 BOM
    • UTF-16 LE BOM
    • UTF-16 BE BOM
    • XML encoding declaration

    If no encoding can be determined,
    no special decoding is performed.
    The raw content is passed through as UTF-8 with
    replacement characters for invalid bytes so the
    remaining pipeline can continue.
    """

    @staticmethod
    def decode(content: bytes):

        # ---------------------------------------------
        # UTF-8 BOM
        # ---------------------------------------------

        if content.startswith(codecs.BOM_UTF8):

            
            return content.decode("utf-8-sig")

        # ---------------------------------------------
        # UTF-16 Little Endian
        # ---------------------------------------------

        if content.startswith(codecs.BOM_UTF16_LE):

           

            return content.decode("utf-16")

        # ---------------------------------------------
        # UTF-16 Big Endian
        # ---------------------------------------------

        if content.startswith(codecs.BOM_UTF16_BE):

            

            return content.decode("utf-16")

        # ---------------------------------------------
        # XML Encoding Declaration
        # ---------------------------------------------

        header = content[:200].decode(
            "ascii",
            errors="ignore"
        )

        match = re.search(
            r'encoding=["\']([^"\']+)["\']',
            header,
            re.IGNORECASE
        )

        if match:

            encoding = match.group(1)

           

            try:

                return content.decode(encoding)

            except Exception as e:

               system_logger.warning(
                    f"Failed to decode XML using declared encoding '{encoding}'. Falling back to UTF-8. Error: {e}"
               )

        # ---------------------------------------------
        # Unknown Encoding
        # ---------------------------------------------

       

        return content.decode(
            "utf-8",
            errors="replace"
        )