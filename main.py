from fund_provider import FundProvider
from ai_service import GeminiAI
from excel_service import ExcelService
from logger import Logger
from progress import ProgressTracker
from xml_optimizer import XmlOptimizer


def main():

    provider = FundProvider()
    ai = GeminiAI()
    excel = ExcelService()
    logger = Logger()
    progress = ProgressTracker()
    optimizer=XmlOptimizer()
    
    MAX_SCHEMES = 20

    # --------------------------------------------------
    # Load Previous Progress
    # --------------------------------------------------

    saved_progress = progress.load_progress()

    last_mf_id = None
    last_index = -1

    if saved_progress:

        last_mf_id = saved_progress["mf_id"]
        last_index = saved_progress["last_index"]

        print("\nPrevious progress found. - main.py:34")
        print(f"Resume Fund ID : {last_mf_id} - main.py:35")
        print(f"Resume Index   : {last_index + 1} - main.py:36")

    else:

        print("\nNo previous progress found. - main.py:40")
        print("Starting from first fund. - main.py:41")

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

        print("\n - main.py:69")
        print("= - main.py:70" * 80)
        print(f"Fund House : {fund_name} - main.py:71")
        print(f"MF ID      : {mf_id} - main.py:72")
        print("= - main.py:73" * 80)

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

            print(f"Unable to fetch schemes : {e} - main.py:93")

            continue

        if not schemes:

            print("No schemes found. - main.py:99")
            continue

        print(f"Total Schemes : {len(schemes)} - main.py:102")

        # ----------------------------------------------
        # Resume Index
        # ----------------------------------------------

        if mf_id == last_mf_id:

            start_index = last_index + 1

        else:

            start_index = 0

        if start_index >= len(schemes):

            print("This fund is already completed. - main.py:118")
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

            print("\n - main.py:138" + "-" * 80)
            print(f"Scheme {index + 1}/{len(schemes)} - main.py:139")
            print(f"Scheme ID   : {scheme_id} - main.py:140")
            print(f"Scheme Name : {scheme_name} - main.py:141")
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

                print("✓ XML Downloaded - main.py:159")

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

                print(f"✗ XML Error : {e} - main.py:178")

                continue
            # ------------------------------------------
            # Optimize XML
            # ------------------------------------------

            try:

                original_size = len(xml)

                xml = optimizer.optimize(xml)

                optimized_size = len(xml)

                removed = original_size - optimized_size

                reduction = (removed / original_size) * 100

                print(f"✓ XML Optimized - main.py:197")
                print(f"Original Size : {original_size:,} chars - main.py:198")
                print(f"Optimized Size: {optimized_size:,} chars - main.py:199")
                print(f"Removed       : {removed:,} chars - main.py:200")
                print(f"Reduction     : {reduction:.2f}% - main.py:201")

            except Exception as e:

                logger.log_error(
                mf_id=mf_id,
                scheme_id=scheme_id,
                scheme_name=scheme_name,
                stage="XML Optimizer",
                error=str(e)
                )

                print(f"✗ XML Optimizer Error : {e} - main.py:213")

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

                print("✓ Gemini Success - main.py:231")

            except RuntimeError as e:

                if str(e) == "GEMINI_QUOTA_EXCEEDED":

                    print("\n - main.py:237" + "=" * 80)
                    print("Gemini quota exhausted. - main.py:238")
                    print("Saving progress and terminating program... - main.py:239")
                    print("= - main.py:240" * 80)

                    progress.save_progress(
                        mf_id=mf_id,
                        last_index=index - 1,
                        scheme_id=scheme_id,
                        scheme_name=scheme_name
                    )

                    return

                raise

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

                print(f"✗ Gemini Error : {e} - main.py:270")

                continue

            # ------------------------------------------
            # Excel
            # ------------------------------------------

            try:

                excel.append(result)

                print("✓ Data written to Excel. - main.py:282")

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

                print(f"✗ Excel Error : {e} - main.py:301")

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

            print("\nExtracted Data:\n - main.py:322")
            print(result.model_dump_json(indent=4))

        # ----------------------------------------------
        # Fund Summary
        # ----------------------------------------------

        if end_index >= len(schemes):

            print("\n - main.py:331" + "=" * 80)
            print(f"✓ Completed Fund House : {fund_name} - main.py:332")
            print("= - main.py:333" * 80)

            # Reset scheme index so next fund starts
            # from its first scheme.

            last_index = -1

        else:

            remaining = len(schemes) - end_index

            print("\n - main.py:344" + "=" * 80)
            print(f"Batch completed for {fund_name} - main.py:345")
            print(f"Processed upto : {end_index} - main.py:346")
            print(f"Remaining      : {remaining} - main.py:347")
            print("= - main.py:348" * 80)

            return

    # --------------------------------------------------
    # All Funds Finished
    # --------------------------------------------------

    progress.clear_progress()

    print("\n - main.py:358" + "=" * 80)
    print("ALL FUND HOUSES HAVE BEEN PROCESSED SUCCESSFULLY - main.py:359")
    print("No pending schemes remain. - main.py:360")
    print("= - main.py:361" * 80)


if __name__ == "__main__":
    main()            