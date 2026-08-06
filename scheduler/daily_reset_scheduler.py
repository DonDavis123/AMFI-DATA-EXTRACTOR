import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from system_logger import SystemLogger

system_logger = SystemLogger.get_logger()


class DailyResetScheduler:
    """
    Wait until Gemini free-tier quota resets
    (Midnight Pacific Time).
    """

    @staticmethod
    def wait():

        pacific = ZoneInfo("America/Los_Angeles")
        local = datetime.now().astimezone()

        pacific_now = local.astimezone(pacific)

        # ---------------------------------------
        # Next Midnight (Pacific Time)
        # ---------------------------------------

        next_midnight = (
            pacific_now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            + timedelta(days=1)
        )

        # Convert to user's local timezone
        local_reset = next_midnight.astimezone(local.tzinfo)
        system_logger.warning(
           f"All Gemini API keys exhausted. Waiting until {next_midnight:%Y-%m-%d %H:%M:%S %Z} for quota reset."
        )
        
        while True:

            remaining = local_reset - datetime.now().astimezone()

            if remaining.total_seconds() <= 0:
                break

            total = int(remaining.total_seconds())

            days = total // 86400
            hours = (total % 86400) // 3600
            minutes = (total % 3600) // 60
            seconds = total % 60

           

            time.sleep(1)

        system_logger.info(
               "Gemini quota reset reached. Resuming processing."
        )