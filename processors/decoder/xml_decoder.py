import codecs
import re


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

            print("Detected UTF8 BOM - xml_decoder.py:32")

            return content.decode("utf-8-sig")

        # ---------------------------------------------
        # UTF-16 Little Endian
        # ---------------------------------------------

        if content.startswith(codecs.BOM_UTF16_LE):

            print("Detected UTF16 LE - xml_decoder.py:42")

            return content.decode("utf-16")

        # ---------------------------------------------
        # UTF-16 Big Endian
        # ---------------------------------------------

        if content.startswith(codecs.BOM_UTF16_BE):

            print("Detected UTF16 BE - xml_decoder.py:52")

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

            print(
                f"Detected XML Encoding : {encoding}"
            )

            try:

                return content.decode(encoding)

            except Exception as e:

                print(
                    f"Declared encoding '{encoding}' failed."
                )
                print(e)

        # ---------------------------------------------
        # Unknown Encoding
        # ---------------------------------------------

        print(
            "Unknown XML encoding. Passing content without special decoding."
        )

        return content.decode(
            "utf-8",
            errors="replace"
        )