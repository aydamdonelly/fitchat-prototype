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
    date: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'), description="Date of the activity log in YYYY-MM-DD format")
    
class UserData(BaseModel):
    first_name: Optional[str] = Field(description="name of the user")
    age: Optional[str] = Field(description="age of the user")
    gender: Optional[str] = Field(description="gender of the user")
    height: Optional[int] = Field(description="height in cm")
    
class Message(BaseModel):
    time: Optional[datetime] = Field(default_factory=datetime.now, description="time of the message")
    base_message: BaseMessage = Field(description="message")
        
class User(BaseModel):
    paid: bool = Field(default=False, description="paid user")
    day: int = Field(default=0, description="day of the user")
    user_data: UserData = Field(default_factory=UserData, description="user data")
    activity_log: Optional[DatedActivityLog] = Field(description="activity log")
    messages: list[Message] = Field(default_factory=list, description="messages")
