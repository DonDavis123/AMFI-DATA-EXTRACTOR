import requests


class FundProvider:

    def __init__(self):

        # ----------------------------------------------------
        # Master List (Do not modify frequently)
        # ----------------------------------------------------

        self.fund_directory = {
            "360 ONE Mutual Fund": 62,
            "Abakkus Mutual Fund": 85,
            "Aditya Birla Sun Life Mutual Fund": 3,
            "Angel One Mutual Fund": 80,
            "Axis Mutual Fund": 53,
            "Bajaj Finserv Mutual Fund": 75,
            "Bandhan Mutual Fund": 48,
            "Bank of India Mutual Fund": 46,
            "Baroda BNP Paribas Mutual Fund": 4,
            "Canara Robeco Mutual Fund": 32,
            "Capitalmind Mutual Fund": 81,
            "Choice Mutual Fund": 84,
            "DSP Mutual Fund": 6,
            "Edelweiss Mutual Fund": 47,
            "Franklin Templeton Mutual Fund": 27,
            "Groww Mutual Fund": 63,
            "HDFC Mutual Fund": 9,
            "Helios Mutual Fund": 76,
            "HSBC Mutual Fund": 37,
            "ICICI Prudential Mutual Fund": 20,
            "IL&FS Mutual Fund (IDF)": 65,
            "Invesco Mutual Fund": 42,
            "ITI Mutual Fund": 70,
            "Jio BlackRock Mutual Fund": 82,
            "JM Financial Mutual Fund": 16,
            "Kotak Mahindra Mutual Fund": 17,
            "LIC Mutual Fund": 18,
            "Mahindra Manulife Mutual Fund": 69,
            "Mirae Asset Mutual Fund": 45,
            "Motilal Oswal Mutual Fund": 55,
            "Navi Mutual Fund": 54,
            "Nippon India Mutual Fund": 21,
            "NJ Mutual Fund": 73,
            "Old Bridge Mutual Fund": 78,
            "PGIM India Mutual Fund": 58,
            "PPFAS Mutual Fund": 64,
            "quant Mutual Fund": 13,
            "Quantum Mutual Fund": 41,
            "Samco Mutual Fund": 74,
            "SBI Mutual Fund": 22,
            "Shriram Mutual Fund": 67,
            "Sundaram Mutual Fund": 33,
            "Tata Mutual Fund": 25,
            "Taurus Mutual Fund": 26,
            "Trust Mutual Fund": 72,
            "Unifi Mutual Fund": 79,
            "Union Mutual Fund": 61,
            "UTI Mutual Fund": 28,
            "The Wealth Company Mutual Fund": 83,
            "WhiteOak Capital Mutual Fund": 71,
            "Zerodha Mutual Fund": 77,
        }

        # ----------------------------------------------------
        # ONLY THESE AMCs WILL BE PROCESSED
        # ----------------------------------------------------

        self.selected_funds = [
            
            85,
            3,
            80,
            53,
            75,
            48,
            46,
            4,
            32,
            81,
            84,
            6,
            47,
            27,
            63,
            9,
            76,
            37,
            20,
            65,
            42,
            70,
            82,
            16,
            17,
            18,
            69,
            45,
            55,
            54,
            21,
            73,
            78,
            58,
            64,
            13,
            41,
            74,
            22,
            67,
            33,
            25,
            26,
            72,
            79,
            61,
            28,
            83,
            71,
            77
        ]

    # ----------------------------------------------------
    # Returns ONLY selected fund houses
    # ----------------------------------------------------

    def get_all_funds(self):

        funds = []

        for mf_id in self.selected_funds:

            for fund_name, directory_id in self.fund_directory.items():

                if directory_id == mf_id:

                    funds.append(
                        {
                            "mf_id": mf_id,
                            "fund_name": fund_name,
                        }
                    )

                    break

        return funds

    # ----------------------------------------------------
    # Returns schemes of one fund house
    # ----------------------------------------------------

    def get_scheme_list(self, mf_id):

        url = "https://www.amfiindia.com/api/populate-scheme"

        response = requests.get(
            url,
            params={"MF_ID": mf_id},
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        schemes = []

        for item in data:

            schemes.append(
                {
                    "scheme_id": str(item["scheme_id"]),
                    "scheme_name": item["scheme_name"],
                }
            )

        return schemes

    # ----------------------------------------------------
    # Download SSD XML
    # ----------------------------------------------------

    def download_xml(self, scheme_id):

        url = f"https://portal.amfiindia.com/spages/SSD_{scheme_id}.xml"

        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.text