from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional
from datetime import datetime
from langchain_core.messages import BaseMessage


class ActivityLog(BaseModel):
    calories: Optional[int] = Field(description="Total calories consumed today")
    steps: Optional[int] = Field(description="Number of steps taken today")
    weight: Optional[float] = Field(description="Current body weight in kilograms")
    protein: Optional[float] = Field(description="Total grams of protein consumed today")
    
class DatedActivityLog(ActivityLog):
    date: datetime = Field()
    
class UserData(BaseModel):
    first_name: Optional[str] = Field(description="name of the user")
    age: Optional[int] = Field(description="age of the user")
    gender: Optional[str] = Field(description="gender of the user, should be male or female")
    height: Optional[int] = Field(description="height in cm")
    
class Message(BaseModel):
    time: Optional[datetime] = Field(default_factory=datetime.now)
    base_message: BaseMessage = Field()
        
class User(BaseModel):
    paid: bool = Field(default=False)
    day: int = Field(default=0, description="Used to track how many days the user has been using the app")
    user_data: UserData = Field(default_factory=UserData)
    dated_activity_logs: list[DatedActivityLog] = Field(default_factory=list)
    messages: list[Message] = Field(default_factory=list)