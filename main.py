from fund_provider import FundProvider
from dotenv import load_dotenv
load_dotenv()
from ai_services.ai_service import GeminiAI
#from csv_service_disabled import CsvService
from logger import Logger
from progress import ProgressTracker
from processors.xml_manager import XmlManager
from scheduler.daily_reset_scheduler import DailyResetScheduler
from scheduler.monthly_scheduler import MonthlyScheduler
from scheme_details_service import SchemeDetailsRepository
scheme_repository = SchemeDetailsRepository()
logger = Logger()
provider = FundProvider()
ai = GeminiAI()
 #csv_service = CsvService()
    
progress = ProgressTracker()
optimizer = XmlManager()
    
    


def main():

    

    # --------------------------------------------------
    # Load Previous Progress
    # --------------------------------------------------

    saved_progress = progress.load_progress()

    last_mf_id = None
    last_index = -1

    if saved_progress:

        last_mf_id = saved_progress["mf_id"]
        last_index = saved_progress["last_index"]
        

        print("\nPrevious progress found. - main.py:43")
        print(f"Resume Fund ID : {last_mf_id} - main.py:44")
        print(f"Resume Index   : {last_index + 1} - main.py:45")

    else:

        print("\nNo previous progress found. - main.py:49")
        print("Starting from first fund. - main.py:50")

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

        print("\n - main.py:78")
        print("= - main.py:79" * 80)
        print(f"Fund House : {fund_name} - main.py:80")
        print(f"MF ID      : {mf_id} - main.py:81")
        print("= - main.py:82")

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

            print(f"Unable to fetch schemes : {e} - main.py:102")

            continue

        if not schemes:

            print("No schemes found. - main.py:108")
            continue

        print(f"Total Schemes : {len(schemes)} - main.py:111")

        # ----------------------------------------------
        # Resume Index
        # ----------------------------------------------

        if mf_id == last_mf_id:

            start_index = last_index + 1

        else:

            start_index = 0

        if start_index >= len(schemes):

            print("This fund is already completed. - main.py:127")
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

            print("\n - main.py:150" )
            print(f"Scheme {index + 1}/{len(schemes)} - main.py:151")
            print(f"Scheme ID   : {scheme_id} - main.py:152")
            print(f"Scheme Name : {scheme_name} - main.py:153")
            

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

                print("✓ XML Downloaded - main.py:171")

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

                print(f"✗ XML Error : {e} - main.py:191")

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

                print(f"✗ XML Optimizer Error : {e} - main.py:230")

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

                print("✓ Gemini Success - main.py:248")

            except RuntimeError as e:

                if str(e) == "ALL API KEYS ARE EXHAUSTED":

                    print("\n - main.py:254" + "=" )
                    print("Gemini quota exhausted. - main.py:255")
                    
                    print("= - main.py:257" )

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

                print(f"✗ Gemini Error : {e} - main.py:290")

                continue

            # ------------------------------------------
            # Scheme details
            # ------------------------------------------
            try:

              # csv_service.append(result)
               scheme_repository.upsert(result)    

               #print("✓ Data written to CSV. - main.py:300")
               print("✓ Scheme details updated. - main.py:303")

            except Exception as e:

               logger.log_error(
                 mf_id=mf_id,
                 scheme_id=scheme_id,
                 scheme_name=scheme_name,
                 stage="Scheme Details",
                 error=str(e)
                )

               progress.save_progress(
                mf_id=mf_id,
                last_index=index - 1,
                scheme_id=scheme_id,
                scheme_name=scheme_name,
                status="processing"
               )

               print(f"✗ Scheme details : {e} - main.py:323")

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

            print("\nExtracted Data:\n - main.py:345")
            print(result.model_dump_json(indent=4))

        #scheme_repository.upsert(result)    

        # ----------------------------------------------
        # Fund Summary
        # ----------------------------------------------

        print("\n - main.py:354")
        print(f"✓ Completed Fund House : {fund_name} - main.py:355")
        print("= - main.py:356" )

        last_index = -1

    # --------------------------------------------------
    # All Funds Finished
    # --------------------------------------------------

    progress.clear_progress()

    print("\n - main.py:366" )
    print("ALL FUND HOUSES HAVE BEEN PROCESSED SUCCESSFULLY - main.py:367")
    print("No pending schemes remain. - main.py:368")
    print("= - main.py:369" )
    return "ALL_COMPLETED"
    


if __name__ == "__main__":
    

    try:

      while True:

          status = main()

          if status == "API_KEYS_EXHAUSTED":

              DailyResetScheduler.wait()

          elif status == "ALL_COMPLETED":

              MonthlyScheduler.wait()
              try:
              
                 logger.clear_error_log()
              except Exception as e:
                  print("Failed to clear the log - main.py:394")   

    # --------------------------------------------------
    # User Interrupted
    # --------------------------------------------------

    except KeyboardInterrupt:

        print("\n - main.py:402"  )
        print("PROGRAM INTERRUPTED BY USER - main.py:403")
        print("Progress has already been saved. - main.py:404")
        print("Restart the program to continue. - main.py:405")
        print("= - main.py:406" )

    # --------------------------------------------------
    # File Permission Problems
    # --------------------------------------------------

    except PermissionError as e:

        print("\n - main.py:414" + "=" )
        print("PERMISSION ERROR - main.py:415")
        print(str(e))
        print()
        print("Possible reasons: - main.py:418")
        print("issues with scheme_details file - main.py:419")
        print("Log file is locked. - main.py:420")
        print("No write permission. - main.py:421")
        print()
        print("Fix the issue and restart. - main.py:423")
        print("= - main.py:424" )

    # --------------------------------------------------
    # Out of Memory
    # --------------------------------------------------

    except MemoryError:

        print("\n - main.py:432" + "=" )
        print("OUT OF MEMORY - main.py:433")
        print()
        print("Possible reasons: - main.py:435")
        print("XML file too large. - main.py:436")
        print("Too many objects in memory. - main.py:437")
        print("System RAM exhausted. - main.py:438")
        print()
        print("Close other applications and restart. - main.py:440")
        print("= - main.py:441" )

    # --------------------------------------------------
    # Any Unexpected Fatal Error
    # --------------------------------------------------

    except Exception as e:

        import traceback

        print("\n - main.py:451" + "=" )
        print("UNEXPECTED FATAL ERROR - main.py:452")
        print(type(e).__name__)
        print(str(e))
        print("= - main.py:455" )

        traceback.print_exc()