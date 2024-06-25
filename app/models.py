from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional
from datetime import date

class DailyProgress(BaseModel):
    # date of the progreess (automatically set to today using datetime)
    date: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))
    calories: Optional[int] = Field(description="calories consumed today")
    steps: Optional[int] = Field(description="steps taken today")
    weight: Optional[float] = Field(description="weight in kg")
    protein: Optional[float] = Field(description="grams of protein consumed today")