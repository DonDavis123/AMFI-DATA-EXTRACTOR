import os
import json


class SchemeDetailsRepository:

    def __init__(self):

        self.folder = "scheme_details"

        self.file_path = os.path.join(
            self.folder,
            "scheme_details.json"
        )

        os.makedirs(self.folder, exist_ok=True)

    # --------------------------------------------------
    # Insert / Update
    # --------------------------------------------------

    def upsert(self, extraction):

        # ----------------------------------------------
        # Load Existing JSON
        # ----------------------------------------------

        if os.path.exists(self.file_path):

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as file:

                try:
                    records = json.load(file)

                except json.JSONDecodeError:
                    records = {}

        else:

            records = {}

        inserted = 0
        updated = 0

        # ----------------------------------------------
        # Insert / Update By ISIN
        # ----------------------------------------------

        for fund in extraction.funds:

            if not fund.isin:
                continue

            isin = fund.isin.strip().upper()

            if not isin:
                continue

            if isin == "NOT AVAILABLE":
                continue

            record = {
                "fund_name": fund.fund_name.strip(),
                "isin": isin,
                "fund_type": fund.fund_type.strip(),
                "riskometer_at_launch": fund.riskometer_at_launch.strip(),
                "riskometer_as_on_date": fund.riskometer_as_on_date.strip(),
                "category": fund.category.strip(),
                "description": fund.description.strip(),
                "fund_manager_name": fund.fund_manager_name.strip()
            }

            if isin in records:

                records[isin] = record
                updated += 1

            else:

                records[isin] = record
                inserted += 1

        # ----------------------------------------------
        # Save JSON
        # ----------------------------------------------

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                records,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\n - scheme_details_service.py:104" + "=" * 80)
        print("Scheme Details Updated Successfully - scheme_details_service.py:105")
        print(f"Inserted : {inserted} - scheme_details_service.py:106")
        print(f"Updated  : {updated} - scheme_details_service.py:107")
        print(f"Total    : {len(records)} - scheme_details_service.py:108")
        print("= - scheme_details_service.py:109" * 80)