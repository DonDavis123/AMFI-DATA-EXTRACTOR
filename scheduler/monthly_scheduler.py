import time
from datetime import datetime


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

        print("\n - monthly_scheduler.py:37" + "=" * 80)
        print("ALL FUNDS HAVE BEEN UPDATED - monthly_scheduler.py:38")
        print(f"Current Time : {now:%d%m%Y %H:%M:%S} - monthly_scheduler.py:39")
        print(f"Next Run     : {next_run:%d%m%Y %H:%M:%S} - monthly_scheduler.py:40")
        print("= - monthly_scheduler.py:41" * 80)

        while True:

            remaining = next_run - datetime.now()

            if remaining.total_seconds() <= 0:
                break

            days = remaining.days
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            seconds = remaining.seconds % 60

            print(
                f"\rSleeping : "
                f"{days}d "
                f"{hours:02}:{minutes:02}:{seconds:02}",
                end="",
                flush=True
            )

            time.sleep(1)

        print("\n - monthly_scheduler.py:65")
        print("= - monthly_scheduler.py:66" * 80)
        print("Monthly update starting... - monthly_scheduler.py:67")
        print("= - monthly_scheduler.py:68" * 80)