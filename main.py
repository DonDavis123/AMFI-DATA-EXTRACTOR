from fund_provider import FundProvider
from ai_services.ai_service import GeminiAI
from csv_service import CsvService
from logger import Logger
from progress import ProgressTracker
from processors.xml_manager import XmlManager
from scheduler.daily_reset_scheduler import DailyResetScheduler
from scheduler.monthly_scheduler import MonthlyScheduler
from scheme_details_service import SchemeDetailsRepository
scheme_repository = SchemeDetailsRepository()


def main():

    provider = FundProvider()
    ai = GeminiAI()
    csv_service = CsvService()
    logger = Logger()
    progress = ProgressTracker()
    optimizer = XmlManager()
    
    

    # --------------------------------------------------
    # Load Previous Progress
    # --------------------------------------------------

    saved_progress = progress.load_progress()

    last_mf_id = None
    last_index = -1

    if saved_progress:

        last_mf_id = saved_progress["mf_id"]
        last_index = saved_progress["last_index"]
        

        print("\nPrevious progress found. - main.py:39")
        print(f"Resume Fund ID : {last_mf_id} - main.py:40")
        print(f"Resume Index   : {last_index + 1} - main.py:41")

    else:

        print("\nNo previous progress found. - main.py:45")
        print("Starting from first fund. - main.py:46")

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

        print("\n - main.py:74")
        print("= - main.py:75" * 80)
        print(f"Fund House : {fund_name} - main.py:76")
        print(f"MF ID      : {mf_id} - main.py:77")
        print("= - main.py:78" * 80)

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

            print(f"Unable to fetch schemes : {e} - main.py:98")

            continue

        if not schemes:

            print("No schemes found. - main.py:104")
            continue

        print(f"Total Schemes : {len(schemes)} - main.py:107")

        # ----------------------------------------------
        # Resume Index
        # ----------------------------------------------

        if mf_id == last_mf_id:

            start_index = last_index + 1

        else:

            start_index = 0

        if start_index >= len(schemes):

            print("This fund is already completed. - main.py:123")
            last_index = -1
            continue


        # ----------------------------------------------
        # Scheme Loop
        # ----------------------------------------------

        for index in range(start_index, len(schemes)):

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
                    

                    return "API_KEYS_EXHAUSTED"

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

                print(f"✗ Gemini Error : {e} - main.py:286")

                continue

            # ------------------------------------------
            # CSV
            # ------------------------------------------
            try:

               csv_service.append(result)
               scheme_repository.upsert(result)    

               print("✓ Data written to CSV. - main.py:298")
               print("✓ Scheme details updated. - main.py:299")

            except Exception as e:

               logger.log_error(
                 mf_id=mf_id,
                 scheme_id=scheme_id,
                 scheme_name=scheme_name,
                 stage="CSV Write",
                 error=str(e)
                )

               progress.save_progress(
                mf_id=mf_id,
                last_index=index - 1,
                scheme_id=scheme_id,
                scheme_name=scheme_name,
                status="processing"
               )

               print(f"✗ CSV Error : {e} - main.py:319")

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

            print("\nExtracted Data:\n - main.py:341")
            print(result.model_dump_json(indent=4))

        scheme_repository.upsert(result)    

        # ----------------------------------------------
        # Fund Summary
        # ----------------------------------------------

        print("\n - main.py:350" + "=" * 80)
        print(f"✓ Completed Fund House : {fund_name} - main.py:351")
        print("= - main.py:352" * 80)

        last_index = -1

    # --------------------------------------------------
    # All Funds Finished
    # --------------------------------------------------

    progress.clear_progress()

    print("\n - main.py:362" + "=" * 80)
    print("ALL FUND HOUSES HAVE BEEN PROCESSED SUCCESSFULLY - main.py:363")
    print("No pending schemes remain. - main.py:364")
    print("= - main.py:365" * 80)
    return "ALL_COMPLETED"
    


if __name__ == "__main__":

    try:

      while True:

          status = main()

          if status == "API_KEYS_EXHAUSTED":

              DailyResetScheduler.wait()

          elif status == "ALL_COMPLETED":

              MonthlyScheduler.wait()

    # --------------------------------------------------
    # User Interrupted
    # --------------------------------------------------

    except KeyboardInterrupt:

        print("\n - main.py:392" + "=" * 80)
        print("PROGRAM INTERRUPTED BY USER - main.py:393")
        print("Progress has already been saved. - main.py:394")
        print("Restart the program to continue. - main.py:395")
        print("= - main.py:396" * 80)

    # --------------------------------------------------
    # File Permission Problems
    # --------------------------------------------------

    except PermissionError as e:

        print("\n - main.py:404" + "=" * 80)
        print("PERMISSION ERROR - main.py:405")
        print(str(e))
        print()
        print("Possible reasons: - main.py:408")
        print("CSV file is open. - main.py:409")
        print("Log file is locked. - main.py:410")
        print("No write permission. - main.py:411")
        print()
        print("Fix the issue and restart. - main.py:413")
        print("= - main.py:414" * 80)

    # --------------------------------------------------
    # Out of Memory
    # --------------------------------------------------

    except MemoryError:

        print("\n - main.py:422" + "=" * 80)
        print("OUT OF MEMORY - main.py:423")
        print()
        print("Possible reasons: - main.py:425")
        print("XML file too large. - main.py:426")
        print("Too many objects in memory. - main.py:427")
        print("System RAM exhausted. - main.py:428")
        print()
        print("Close other applications and restart. - main.py:430")
        print("= - main.py:431" * 80)

    # --------------------------------------------------
    # Any Unexpected Fatal Error
    # --------------------------------------------------

    except Exception as e:

        import traceback

        print("\n - main.py:441" + "=" * 80)
        print("UNEXPECTED FATAL ERROR - main.py:442")
        print(type(e).__name__)
        print(str(e))
        print("= - main.py:445" * 80)

        traceback.print_exc()