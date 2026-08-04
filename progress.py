import os
import json


class ProgressTracker:

    def __init__(self):

        self.log_folder = "logs"
        self.file_path = os.path.join(
            self.log_folder,
            "progress.json"
        )

        os.makedirs(self.log_folder, exist_ok=True)

    def save_progress(
        self,
        mf_id,
        last_index,
        scheme_id,
        scheme_name,
        status
    ):

        data = {
            "mf_id": mf_id,
            "last_index": last_index,
            "scheme_id": scheme_id,
            "scheme_name": scheme_name,
            "status": status
        }

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_progress(self):

        if not os.path.exists(self.file_path):
            return None

        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def clear_progress(self):

        if os.path.exists(self.file_path):
            os.remove(self.file_path)