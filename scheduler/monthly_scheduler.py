import time
from datetime import datetime
from system_logger import SystemLogger


system_logger = SystemLogger.get_logger()


class MonthlyScheduler:
    """
    Sleep until the first day of the next month.
    """

    @staticmethod
    def wait():

        now = datetime.now()

        if now.month == 12:

            next_run = datetime(
                year=now.year + 1,
                month=1,
                day=1,
                hour=0,
                minute=0,
                second=0
            )

        else:

            next_run = datetime(
                year=now.year,
                month=now.month + 1,
                day=1,
                hour=0,
                minute=0,
                second=0
            )

        # Calculate exact time remaining until next month
        remaining = (next_run - datetime.now()).total_seconds()

        if remaining > 0:
            time.sleep(remaining)

        system_logger.info(
            "Monthly update starting."
        )