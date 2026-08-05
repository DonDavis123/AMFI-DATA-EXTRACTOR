import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


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

        print("\n - daily_reset_scheduler.py:37" + "=" * 80)
        print("ALL GEMINI API QUOTAS ARE EXHAUSTED - daily_reset_scheduler.py:38")
        print(f"Current Local Time : {local:%d%m%Y %H:%M:%S %Z} - daily_reset_scheduler.py:39")
        print(f"Current PT Time    : {pacific_now:%d%m%Y %H:%M:%S %Z} - daily_reset_scheduler.py:40")
        print(f"Quota Reset (PT)   : {next_midnight:%d%m%Y %H:%M:%S %Z} - daily_reset_scheduler.py:41")
        print(f"Resume Local Time  : {local_reset:%d%m%Y %H:%M:%S %Z} - daily_reset_scheduler.py:42")
        print("= - daily_reset_scheduler.py:43" * 80)

        while True:

            remaining = local_reset - datetime.now().astimezone()

            if remaining.total_seconds() <= 0:
                break

            total = int(remaining.total_seconds())

            days = total // 86400
            hours = (total % 86400) // 3600
            minutes = (total % 3600) // 60
            seconds = total % 60

            print(
                f"\rWaiting for Gemini quota reset : "
                f"{days}d "
                f"{hours:02}:{minutes:02}:{seconds:02}",
                end="",
                flush=True
            )

            time.sleep(1)

        print("\n - daily_reset_scheduler.py:69")
        print("= - daily_reset_scheduler.py:70" * 80)
        print("Gemini quota has been reset. - daily_reset_scheduler.py:71")
        print("Resuming processing... - daily_reset_scheduler.py:72")
        print("= - daily_reset_scheduler.py:73" * 80)