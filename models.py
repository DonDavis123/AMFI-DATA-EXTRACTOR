from typing import List
from pydantic import BaseModel


class FundRow(BaseModel):
    fund_name: str
    isin: str
    fund_type: str

    riskometer_at_launch: str = ""
    riskometer_as_on_date: str = ""
    category: str = ""
    description: str = ""
    fund_manager_name: str = ""
    


class FundExtraction(BaseModel):
    funds: List[FundRow]