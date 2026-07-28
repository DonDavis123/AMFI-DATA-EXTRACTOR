import os
from datetime import datetime


class Logger:

    def __init__(self):

        self.log_folder = "logs"
        self.log_file = os.path.join(self.log_folder, "errors.log")

        os.makedirs(self.log_folder, exist_ok=True)

    def log_error(
        self,
        mf_id,
        scheme_id,
        scheme_name,
        stage,
        error
    ):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = (
            f"[{timestamp}]\n"
            f"MF ID        : {mf_id}\n"
            f"Scheme ID    : {scheme_id}\n"
            f"Scheme Name  : {scheme_name}\n"
            f"Stage        : {stage}\n"
            f"Error        : {error}\n"
            f"{'-'*80}\n"
        )

        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(message)

    def log_success(
        self,
        mf_id,
        scheme_id,
        scheme_name
    ):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = (
            f"[{timestamp}] SUCCESS | "
            f"MF_ID={mf_id} | "
            f"Scheme_ID={scheme_id} | "
            f"{scheme_name}\n"
        )

        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(message)