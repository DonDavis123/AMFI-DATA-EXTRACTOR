from fund_provider import FundProvider
from dotenv import load_dotenv
load_dotenv()
from ai_services.ai_service import GeminiAI
#from csv_service_disabled import CsvService
from system_logger import SystemLogger
from logger import Logger
from progress import ProgressTracker
from processors.xml_manager import XmlManager
from scheduler.daily_reset_scheduler import DailyResetScheduler
from scheduler.monthly_scheduler import MonthlyScheduler
from scheme_details_service import SchemeDetailsRepository
system_logger = SystemLogger.get_logger()
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
        

        system_logger.info("Previous progress loaded.")
       

    else:

        system_logger.info("No previous progress found. Starting from first fund.")

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

            system_logger.error(f"Unable to fetch scheme list for MF {mf_id}: {e}")

            continue

        if not schemes:

            system_logger.warning(f"No schemes found for MF {mf_id}.")
            continue

       

        # ----------------------------------------------
        # Resume Index
        # ----------------------------------------------

        if mf_id == last_mf_id:

            start_index = last_index + 1

        else:

            start_index = 0

        if start_index >= len(schemes):

          
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

               

            except RuntimeError as e:

                if str(e) == "ALL API KEYS ARE EXHAUSTED":

                    system_logger.critical("All Gemini API keys exhausted.")
                    
                   

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

                
                continue

            # ------------------------------------------
            # Scheme details
            # ------------------------------------------
            try:

              # csv_service.append(result)
               scheme_repository.upsert(result)    

               #print("✓ Data written to CSV. - main.py:300")
               

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

           
        #scheme_repository.upsert(result)    

        # ----------------------------------------------
        # Fund Summary
        # ----------------------------------------------

       
        
      

        last_index = -1

    # --------------------------------------------------
    # All Funds Finished
    # --------------------------------------------------

    progress.clear_progress()

    system_logger.info("All fund houses processed successfully.")
    system_logger.info("Application finished successfully.")
    return "ALL_COMPLETED"
    


if __name__ == "__main__":
    

    try:

      system_logger.info("Application started.")
      print("Application started - main.py:366")
      while True:

          status = main()

          if status == "API_KEYS_EXHAUSTED":

              DailyResetScheduler.wait()

          elif status == "ALL_COMPLETED":

              MonthlyScheduler.wait()
              try:
              
                 logger.clear_error_log()
              except Exception as e:
                  system_logger.error(f"Failed to clear error log: {e}")  

    # --------------------------------------------------
    # User Interrupted
    # --------------------------------------------------

    except KeyboardInterrupt:

       system_logger.warning("Application interrupted by user.")

    # --------------------------------------------------
    # File Permission Problems
    # --------------------------------------------------

    except PermissionError as e:

        system_logger.critical(f"Permission error: {e}")

    # --------------------------------------------------
    # Out of Memory
    # --------------------------------------------------

    except MemoryError:

        system_logger.critical("Out of memory.")

    # --------------------------------------------------
    # Any Unexpected Fatal Error
    # --------------------------------------------------

    except Exception as e:

        

        system_logger.exception("Unexpected fatal error.")