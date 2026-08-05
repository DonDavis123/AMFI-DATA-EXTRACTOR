import os
import json

import boto3
from botocore.exceptions import ClientError


class SchemeDetailsRepository:

    def __init__(self):

        # --------------------------------------------------
        # DigitalOcean Spaces Configuration
        # --------------------------------------------------

        self.bucket = os.getenv("DO_SPACES_BUCKET")
        self.endpoint = os.getenv("DO_SPACES_ENDPOINT")
        self.region = os.getenv("DO_SPACES_REGION")
        self.access_key = os.getenv("DO_SPACES_KEY")
        self.secret_key = os.getenv("DO_SPACES_SECRET")

        required = {
            "DO_SPACES_BUCKET": self.bucket,
            "DO_SPACES_ENDPOINT": self.endpoint,
            "DO_SPACES_REGION": self.region,
            "DO_SPACES_KEY": self.access_key,
            "DO_SPACES_SECRET": self.secret_key,
        }

        missing = [
            key
            for key, value in required.items()
            if not value
        ]

        if missing:

            raise RuntimeError(
                f"Missing environment variables: {', '.join(missing)}"
            )

        # --------------------------------------------------
        # File Information
        # --------------------------------------------------

        self.folder = "scheme_details"
        self.filename = "scheme_details.json"

        self.object_key = (
            f"{self.folder}/{self.filename}"
        )

        # --------------------------------------------------
        # DigitalOcean Spaces Client
        # --------------------------------------------------

        self.client = boto3.client(
            "s3",
            region_name=self.region,
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    # ==================================================
    # Insert / Update
    # ==================================================

    def upsert(self, extraction):

        records = self._load_json()

        inserted = 0
        updated = 0

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
                "riskometer_at_launch":
                    fund.riskometer_at_launch.strip(),
                "riskometer_as_on_date":
                    fund.riskometer_as_on_date.strip(),
                "category": fund.category.strip(),
                "description": fund.description.strip(),
                "fund_manager_name":
                    fund.fund_manager_name.strip()

            }

            if isin in records:

                records[isin] = record
                updated += 1

            else:

                records[isin] = record
                inserted += 1

        self._save_json(records)

        print("\n - scheme_details_service.py:117")
        print("SCHEME DETAILS UPDATED SUCCESSFULLY - scheme_details_service.py:118")
        print(f"Inserted : {inserted} - scheme_details_service.py:119")
        print(f"Updated  : {updated} - scheme_details_service.py:120")
        print(f"Total    : {len(records)} - scheme_details_service.py:121")
        print("= - scheme_details_service.py:122")

    # ==================================================
    # Load JSON From DigitalOcean Spaces
    # ==================================================

    def _load_json(self):

        try:

            response = self.client.get_object(
                Bucket=self.bucket,
                Key=self.object_key
            )

            content = (
                response["Body"]
                .read()
                .decode("utf-8")
            )

            print(
                "Loaded existing "
                "scheme_details.json"
            )

            return json.loads(content)

        except ClientError as e:

            error_code = (
                e.response["Error"]["Code"]
            )

            if error_code == "NoSuchKey":

                print(
                    "scheme_details.json "
                    "not found."
                )

                print(
                    "Creating a new file..."
                )

                return {}

            elif error_code in (

                "AccessDenied",
                "InvalidAccessKeyId",
                "SignatureDoesNotMatch",
                "NoSuchBucket",

            ):

                raise RuntimeError(
                    f"DigitalOcean Spaces Error: "
                    f"{error_code}"
                )

            raise

        except json.JSONDecodeError:

            print(
                "Invalid JSON found."
            )

            print(
                "Starting with empty data."
            )

            return {}

    # ==================================================
    # Upload JSON To DigitalOcean Spaces
    # ==================================================

    def _save_json(self, records):

        json_string = json.dumps(

            records,

            indent=4,
            ensure_ascii=False

        )

        self.client.put_object(

            Bucket=self.bucket,
            Key=self.object_key,
            Body=json_string.encode("utf-8"),
            ContentType="application/json"

        )

        print(
            f"Uploaded to "
            f"{self.bucket}/"
            f"{self.object_key}"
        )