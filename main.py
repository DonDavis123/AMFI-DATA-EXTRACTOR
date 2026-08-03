from fund_provider import FundProvider
from ai_services.ai_service import GeminiAI
from excel_service import ExcelService
from logger import Logger
from progress import ProgressTracker
from processors.xml_manager import XmlManager


def main():

    provider = FundProvider()
    ai = GeminiAI()
    excel = ExcelService()
    logger = Logger()
    progress = ProgressTracker()
    optimizer = XmlManager()
    
    MAX_SCHEMES = 2

    # --------------------------------------------------
    # Load Previous Progress
    # --------------------------------------------------

    saved_progress = progress.load_progress()

    last_mf_id = None
    last_index = -1

    if saved_progress:

        last_mf_id = saved_progress["mf_id"]
        last_index = saved_progress["last_index"]
        

        print("\nPrevious progress found. - main.py:35")
        print(f"Resume Fund ID : {last_mf_id} - main.py:36")
        print(f"Resume Index   : {last_index + 1} - main.py:37")

    else:

        print("\nNo previous progress found. - main.py:41")
        print("Starting from first fund. - main.py:42")

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

        print("\n - main.py:70")
        print("= - main.py:71" * 80)
        print(f"Fund House : {fund_name} - main.py:72")
        print(f"MF ID      : {mf_id} - main.py:73")
        print("= - main.py:74" * 80)

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

            print(f"Unable to fetch schemes : {e} - main.py:94")

            continue

        if not schemes:

            print("No schemes found. - main.py:100")
            continue

        print(f"Total Schemes : {len(schemes)} - main.py:103")

        # ----------------------------------------------
        # Resume Index
        # ----------------------------------------------

        if mf_id == last_mf_id:

            start_index = last_index + 1

        else:

            start_index = 0

        if start_index >= len(schemes):

            print("This fund is already completed. - main.py:119")
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
            progress.save_progress(
               mf_id=mf_id,
               last_index=index - 1,
               scheme_id=scheme_id,
               scheme_name=scheme_name,
               status="processing"
               )

            print("\n - main.py:146" + "-" * 80)
            print(f"Scheme {index + 1}/{len(schemes)} - main.py:147")
            print(f"Scheme ID   : {scheme_id} - main.py:148")
            print(f"Scheme Name : {scheme_name} - main.py:149")
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

                print("✓ XML Downloaded - main.py:167")

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
                    last_index=index-1,
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="processing"
                )

                print(f"✗ XML Error : {e} - main.py:187")

                continue
            # ------------------------------------------
            # Optimize XML
            # ------------------------------------------

            try:

                

                xml = optimizer.optimize(xml)

                

                

                
                
            except Exception as e:



                progress.save_progress(
                  mf_id=mf_id,
                  last_index=index - 1,
                  scheme_id=scheme_id,
                  scheme_name=scheme_name,
                  status="processing"
                 )

                logger.log_error(
                mf_id=mf_id,
                scheme_id=scheme_id,
                scheme_name=scheme_name,
                stage="XML Optimizer",
                error=str(e)
                )

                print(f"✗ XML Optimizer Error : {e} - main.py:226")

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

                print("✓ Gemini Success - main.py:244")

            except RuntimeError as e:

                if str(e) == "ALL API KEYS ARE EXHAUSTED":

                    print("\n - main.py:250" + "=" * 80)
                    print("Gemini quota exhausted. - main.py:251")
                    print("Saving progress and terminating program... - main.py:252")
                    print("= - main.py:253" * 80)

                    progress.save_progress(
                        mf_id=mf_id,
                        last_index=index - 1,
                        scheme_id=scheme_id,
                        scheme_name=scheme_name,
                        status="API_keys_are_exhausted"
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
                    last_index=index-1,
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="processing"
                )

                print(f"✗ Gemini Error : {e} - main.py:285")

                continue

            # ------------------------------------------
            # Excel
            # ------------------------------------------

            try:

                excel.append(result)

                print("✓ Data written to Excel. - main.py:297")

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
                    last_index=index-1,
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="processing"
                )

                print(f"✗ Excel Error : {e} - main.py:317")

                continue

            # ------------------------------------------
            # Success
            # ------------------------------------------

            progress.save_progress(
                mf_id=mf_id,
                last_index=index,
                scheme_id=scheme_id,
                scheme_name=scheme_name,
                status="completed"
            )

            logger.log_success(
                mf_id=mf_id,
                scheme_id=scheme_id,
                scheme_name=scheme_name
            )

            print("\nExtracted Data:\n - main.py:339")
            print(result.model_dump_json(indent=4))

        # ----------------------------------------------
        # Fund Summary
        # ----------------------------------------------

        if end_index >= len(schemes):

            print("\n - main.py:348" + "=" * 80)
            print(f"✓ Completed Fund House : {fund_name} - main.py:349")
            print("= - main.py:350" * 80)

            # Reset scheme index so next fund starts
            # from its first scheme.

            last_index = -1

        else:

            remaining = len(schemes) - end_index

            print("\n - main.py:361" + "=" * 80)
            print(f"Batch completed for {fund_name} - main.py:362")
            print(f"Processed upto : {end_index} - main.py:363")
            print(f"Remaining      : {remaining} - main.py:364")
            print("= - main.py:365" * 80)

            return

    # --------------------------------------------------
    # All Funds Finished
    # --------------------------------------------------

    progress.clear_progress()

    print("\n - main.py:375" + "=" * 80)
    print("ALL FUND HOUSES HAVE BEEN PROCESSED SUCCESSFULLY - main.py:376")
    print("No pending schemes remain. - main.py:377")
    print("= - main.py:378" * 80)


if __name__ == "__main__":

    try:

        main()

    # --------------------------------------------------
    # User Interrupted
    # --------------------------------------------------

    except KeyboardInterrupt:

        print("\n - main.py:393" + "=" * 80)
        print("PROGRAM INTERRUPTED BY USER - main.py:394")
        print("Progress has already been saved. - main.py:395")
        print("Restart the program to continue. - main.py:396")
        print("= - main.py:397" * 80)

    # --------------------------------------------------
    # File Permission Problems
    # --------------------------------------------------

    except PermissionError as e:

        print("\n - main.py:405" + "=" * 80)
        print("PERMISSION ERROR - main.py:406")
        print(str(e))
        print()
        print("Possible reasons: - main.py:409")
        print("Excel file is open. - main.py:410")
        print("Log file is locked. - main.py:411")
        print("No write permission. - main.py:412")
        print()
        print("Fix the issue and restart. - main.py:414")
        print("= - main.py:415" * 80)

    # --------------------------------------------------
    # Out of Memory
    # --------------------------------------------------

    except MemoryError:

        print("\n - main.py:423" + "=" * 80)
        print("OUT OF MEMORY - main.py:424")
        print()
        print("Possible reasons: - main.py:426")
        print("XML file too large. - main.py:427")
        print("Too many objects in memory. - main.py:428")
        print("System RAM exhausted. - main.py:429")
        print()
        print("Close other applications and restart. - main.py:431")
        print("= - main.py:432" * 80)

    # --------------------------------------------------
    # Any Unexpected Fatal Error
    # --------------------------------------------------

    except Exception as e:

        import traceback

        print("\n - main.py:442" + "=" * 80)
        print("UNEXPECTED FATAL ERROR - main.py:443")
        print(type(e).__name__)
        print(str(e))
        print("= - main.py:446" * 80)

        traceback.print_exc()