import os
import csv


class CsvService:

    def __init__(self):

        self.output_folder = "output"
        self.file_path = os.path.join(
            self.output_folder,
            "funds.csv"
        )

        os.makedirs(self.output_folder, exist_ok=True)

        if not os.path.exists(self.file_path):

            with open(
                self.file_path,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Fund Name",
                    "ISIN",
                    "Fund Type",
                    "Riskometer At Launch",
                    "Riskometer As On Date",
                    "Category",
                    "Description",
                    "Fund Manager Name"
                ])

    # --------------------------------------------------
    # Insert / Update
    # --------------------------------------------------

    def append(self, extraction):

        try:

            # ------------------------------------------
            # Read Existing CSV
            # ------------------------------------------

            with open(
                self.file_path,
                "r",
                newline="",
                encoding="utf-8"
            ) as file:

                reader = csv.reader(file)
                rows = list(reader)

            header = rows[0]

            # -------------------------------------------------
            # Dictionary keyed by ISIN
            # Automatically removes duplicate ISINs
            # -------------------------------------------------

            records = {}

            duplicate_count = 0

            for row in rows[1:]:

                if len(row) < 2:
                    continue

                isin = row[1].strip().upper()

                if not isin:
                    continue

                if isin in records:
                    duplicate_count += 1
                    print(f"Duplicate ISIN repaired : {isin} - csv_service.py:84")

                records[isin] = row

            inserted = 0
            updated = 0

            # ------------------------------------------
            # Insert / Update
            # ------------------------------------------

            for fund in extraction.funds:

                if not fund.isin:
                    continue

                isin = fund.isin.strip().upper()

                if not isin:
                    continue

                if isin == "NOT AVAILABLE":
                    continue

                record = [
                    fund.fund_name.strip(),
                    isin,
                    fund.fund_type.strip(),
                    fund.riskometer_at_launch.strip(),
                    fund.riskometer_as_on_date.strip(),
                    fund.category.strip(),
                    fund.description.strip(),
                    fund.fund_manager_name.strip()
                ]

                if isin in records:

                    records[isin] = record
                    updated += 1

                else:

                    records[isin] = record
                    inserted += 1

            # ------------------------------------------
            # Sort records
            # ------------------------------------------

            data_rows = sorted(
                records.values(),
                key=lambda row: row[1]
            )

            # ------------------------------------------
            # Rewrite CSV
            # ------------------------------------------

            with open(
                self.file_path,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow(header)
                writer.writerows(data_rows)

            # ------------------------------------------
            # Logs
            # ------------------------------------------

            print("\n - csv_service.py:158")
            print("CSV Updated Successfully - csv_service.py:159")
            print(f"Inserted          : {inserted} - csv_service.py:160")
            print(f"Updated           : {updated} - csv_service.py:161")
            print(f"Duplicate Removed : {duplicate_count} - csv_service.py:162")
            print(f"Total Rows        : {len(data_rows)} - csv_service.py:163")
            print("= - csv_service.py:164" * 80)

        except PermissionError:

            print("\n - csv_service.py:168" + "=" * 80)
            print("Unable to write to funds.csv - csv_service.py:169")
            print("Close the CSV file and try again. - csv_service.py:170")
            print("= - csv_service.py:171" * 80)

            raise

        except Exception as e:

            print("\n - csv_service.py:177" + "=" * 80)
            print(f"CSV Write Failed : {e} - csv_service.py:178")
            print("= - csv_service.py:179" * 80)

            raise