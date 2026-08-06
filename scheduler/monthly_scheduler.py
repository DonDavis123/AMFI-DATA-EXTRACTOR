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

        
        while True:

            remaining = next_run - datetime.now()

            if remaining.total_seconds() <= 0:
                break

            days = remaining.days
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            seconds = remaining.seconds % 60

            

            time.sleep(min(60, remaining.total_seconds()))

        system_logger.info(
         "Monthly update starting."
        )