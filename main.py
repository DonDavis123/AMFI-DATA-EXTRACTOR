from fund_provider import FundProvider
from ai_service import GeminiAI
from excel_service import ExcelService
from logger import Logger
from progress import ProgressTracker


def main():

    provider = FundProvider()
    ai = GeminiAI()
    excel = ExcelService()
    logger = Logger()
    progress = ProgressTracker()

    MAX_SCHEMES = 10

    # --------------------------------------------------
    # Load Previous Progress
    # --------------------------------------------------

    saved_progress = progress.load_progress()

    last_mf_id = None
    last_index = -1

    if saved_progress:

        last_mf_id = saved_progress["mf_id"]
        last_index = saved_progress["last_index"]

        print("\nPrevious progress found. - main.py:32")
        print(f"Resume Fund ID : {last_mf_id} - main.py:33")
        print(f"Resume Index   : {last_index + 1} - main.py:34")

    else:

        print("\nNo previous progress found. - main.py:38")
        print("Starting from first fund. - main.py:39")

    # --------------------------------------------------
    # Get All Funds
    # --------------------------------------------------

    funds = provider.get_all_funds()

    resume_fund = last_mf_id is None

    # --------------------------------------------------
    # Loop Through Every Fund
    # --------------------------------------------------

    for fund in funds:

        mf_id = fund["mf_id"]
        fund_name = fund["fund_name"]

        # Skip completed funds

        if not resume_fund:

            if mf_id != last_mf_id:
                continue

            resume_fund = True

        print("\n - main.py:67")
        print("= - main.py:68" * 80)
        print(f"Fund House : {fund_name} - main.py:69")
        print(f"MF ID      : {mf_id} - main.py:70")
        print("= - main.py:71" * 80)

        # ----------------------------------------------
        # Get Schemes
        # ----------------------------------------------

        try:

            schemes = provider.get_scheme_list(mf_id)

        except Exception as e:

            logger.log_error(
                mf_id=mf_id,
                scheme_id="-",
                scheme_name="-",
                stage="Fetch Scheme List",
                error=str(e)
            )

            print(f"Unable to fetch schemes : {e} - main.py:91")

            continue

        if not schemes:

            print("No schemes found. - main.py:97")
            continue

        print(f"Total Schemes : {len(schemes)} - main.py:100")

        # ----------------------------------------------
        # Resume Index
        # ----------------------------------------------

        if mf_id == last_mf_id:

            start_index = last_index + 1

        else:

            start_index = 0

        if start_index >= len(schemes):

            print("This fund is already completed. - main.py:116")
            last_index = -1
            continue

        end_index = min(
            start_index + MAX_SCHEMES,
            len(schemes)
        )

        # ----------------------------------------------
        # Scheme Loop
        # ----------------------------------------------

        for index in range(start_index, end_index):

            scheme = schemes[index]

            scheme_id = scheme["scheme_id"]
            scheme_name = scheme["scheme_name"]

            print("\n - main.py:136" + "-" * 80)
            print(f"Scheme {index + 1}/{len(schemes)} - main.py:137")
            print(f"Scheme ID   : {scheme_id} - main.py:138")
            print(f"Scheme Name : {scheme_name} - main.py:139")
            print("" * 80)

            # ------------------------------------------
            # Download XML
            # ------------------------------------------

            try:

                xml = provider.download_xml(
                    scheme_id
                )

                if not xml.strip():
                    raise Exception(
                        "Downloaded XML is empty."
                    )

                print("✓ XML Downloaded - main.py:157")

            except Exception as e:

                logger.log_error(
                    mf_id=mf_id,
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    stage="Download XML",
                    error=str(e)
                )

                progress.save_progress(
                    mf_id=mf_id,
                    last_index=index,
                    scheme_id=scheme_id,
                    scheme_name=scheme_name
                )

                print(f"✗ XML Error : {e} - main.py:176")

                continue

            # ------------------------------------------
            # Gemini
            # ------------------------------------------

            try:

                result = ai.extract(xml)

                if result is None:

                    raise Exception(
                        "Gemini returned no data."
                    )

                print("✓ Gemini Success - main.py:194")

            except Exception as e:

                logger.log_error(
                    mf_id=mf_id,
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    stage="Gemini",
                    error=str(e)
                )

                progress.save_progress(
                    mf_id=mf_id,
                    last_index=index,
                    scheme_id=scheme_id,
                    scheme_name=scheme_name
                )

                print(f"✗ Gemini Error : {e} - main.py:213")

                continue
            # ------------------------------------------
            # Excel
            # ------------------------------------------

            try:

                excel.append(result)

                print("✓ Data written to Excel. - main.py:224")

            except Exception as e:

                logger.log_error(
                    mf_id=mf_id,
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    stage="Excel Write",
                    error=str(e)
                )

                progress.save_progress(
                    mf_id=mf_id,
                    last_index=index,
                    scheme_id=scheme_id,
                    scheme_name=scheme_name
                )

                print(f"✗ Excel Error : {e} - main.py:243")

                continue

            # ------------------------------------------
            # Success
            # ------------------------------------------

            progress.save_progress(
                mf_id=mf_id,
                last_index=index,
                scheme_id=scheme_id,
                scheme_name=scheme_name
            )

            logger.log_success(
                mf_id=mf_id,
                scheme_id=scheme_id,
                scheme_name=scheme_name
            )

            print("\nExtracted Data:\n - main.py:264")
            print(result.model_dump_json(indent=4))

        # ----------------------------------------------
        # Fund Summary
        # ----------------------------------------------

        if end_index >= len(schemes):

            print("\n - main.py:273" + "=" * 80)
            print(f"✓ Completed Fund House : {fund_name} - main.py:274")
            print("= - main.py:275" * 80)

            # Reset scheme index so next fund starts
            # from its first scheme.

            last_index = -1

        else:

            remaining = len(schemes) - end_index

            print("\n - main.py:286" + "=" * 80)
            print(f"Batch completed for {fund_name} - main.py:287")
            print(f"Processed upto : {end_index} - main.py:288")
            print(f"Remaining      : {remaining} - main.py:289")
            print("= - main.py:290" * 80)

            return

    # --------------------------------------------------
    # All Funds Finished
    # --------------------------------------------------

    progress.clear_progress()

    print("\n - main.py:300" + "=" * 80)
    print("ALL FUND HOUSES HAVE BEEN PROCESSED SUCCESSFULLY - main.py:301")
    print("No pending schemes remain. - main.py:302")
    print("= - main.py:303" * 80)


if __name__ == "__main__":
    main()            