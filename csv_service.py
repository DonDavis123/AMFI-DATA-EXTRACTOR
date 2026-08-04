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

        # --------------------------------------------------
        # Create CSV if it doesn't exist
        # --------------------------------------------------

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
            data_rows = rows[1:]

            # ------------------------------------------
            # Build ISIN Lookup
            # ------------------------------------------

            isin_to_index = {}

            for index, row in enumerate(data_rows):

                if len(row) < 2:
                    continue

                isin = row[1].strip().upper()

                if not isin:
                    continue

                if isin in isin_to_index:

                    raise ValueError(
                        f"Duplicate ISIN already exists in CSV: {isin}"
                    )

                isin_to_index[isin] = index

            inserted = 0
            updated = 0

            # ------------------------------------------
            # Insert / Update Records
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

                # ----------------------------------
                # Update Existing Record
                # ----------------------------------

                if isin in isin_to_index:

                    row_index = isin_to_index[isin]

                    data_rows[row_index] = record

                    updated += 1

                # ----------------------------------
                # Insert New Record
                # ----------------------------------

                else:

                    data_rows.append(record)

                    isin_to_index[isin] = len(data_rows) - 1

                    inserted += 1

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

            print("\n - csv_service.py:167" + "=" * 80)
            print("CSV Updated Successfully - csv_service.py:168")
            print(f"Inserted : {inserted} - csv_service.py:169")
            print(f"Updated  : {updated} - csv_service.py:170")
            print(f"Total Rows : {len(data_rows)} - csv_service.py:171")
            print("= - csv_service.py:172" * 80)

        # ----------------------------------------------
        # File Open
        # ----------------------------------------------

        except PermissionError:

            print("\n - csv_service.py:180" + "=" * 80)
            print("ERROR - csv_service.py:181")
            print("Unable to write to funds.csv. - csv_service.py:182")
            print("The CSV file is currently open. - csv_service.py:183")
            print("Please close the file and run again. - csv_service.py:184")
            print("= - csv_service.py:185" * 80)

            raise

        # ----------------------------------------------
        # Unexpected Errors
        # ----------------------------------------------

        except Exception as e:

            print("\n - csv_service.py:195" + "=" * 80)
            print(f"CSV Write Failed : {e} - csv_service.py:196")
            print("= - csv_service.py:197" * 80)

            raise