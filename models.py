from typing import List
from pydantic import BaseModel, Field


class FundRow(BaseModel):
    fund_name: str
    isin: str
    fund_type: str

    riskometer_at_launch: str = ""
    riskometer_as_on_date: str = ""
    category: str = ""
    description: str = ""

    fund_manager_name: List[str] = Field(
        default_factory=list
    )


class FundExtraction(BaseModel):
    funds: List[FundRow]