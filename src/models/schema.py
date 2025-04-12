import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class HrResponseDP(BaseModel):
    date: Optional[date] = None
    time: str
    heartrate: int = Field(alias='value')
    data_insert_timestamp: Optional[datetime] = None 

class HeartrateResponseList(BaseModel):
    dataset: List[HrResponseDP]

    def to_dataframe(self) -> pd.DataFrame:
        # Convert entire model to dict, including nested models
        data_dict = self.model_dump()
        # Create DataFrame directly from dataset
        return pd.DataFrame(data_dict['dataset'])
    
class HeartrateResponse(BaseModel):
    activities: dict = Field(alias='activities-heart-intraday')