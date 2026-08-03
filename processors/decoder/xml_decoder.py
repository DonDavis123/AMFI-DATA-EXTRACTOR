import codecs
import re


class XmlDecoder:
    """
    Safely decodes XML responses.

    Supported:
    - UTF-8 BOM
    - UTF-16 LE BOM
    - UTF-16 BE BOM
    - XML encoding declaration

    If no known encoding is detected,
    returns None so the caller can use the
    original response.text.
    """

    @staticmethod
    def decode(content: bytes):

        # ---------------------------------------------
        # UTF-8 BOM
        # ---------------------------------------------

        if content.startswith(codecs.BOM_UTF8):

            print("Detected UTF8 BOM - xml_decoder.py:29")

            return content.decode("utf-8-sig")

        # ---------------------------------------------
        # UTF-16 Little Endian
        # ---------------------------------------------

        if content.startswith(codecs.BOM_UTF16_LE):

            print("Detected UTF16 LE - xml_decoder.py:39")

            return content.decode("utf-16")

        # ---------------------------------------------
        # UTF-16 Big Endian
        # ---------------------------------------------

        if content.startswith(codecs.BOM_UTF16_BE):

            print("Detected UTF16 BE - xml_decoder.py:49")

            return content.decode("utf-16")

        # ---------------------------------------------
        # XML Declaration
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

            print(
                f"Detected XML Encoding : {encoding}"
            )

            try:

                return content.decode(encoding)

            except Exception:

                print(
                    "Declared encoding failed."
                )

                return None

        # ---------------------------------------------
        # Unknown
        # ---------------------------------------------

        print(
            "Unknown XML encoding."
        )

        return None