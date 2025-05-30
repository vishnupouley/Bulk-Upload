from pydantic import BaseModel
from datetime import date

class Users(BaseModel):
    user_id: str
    user_name: str
    email: str
    business_unit: str
    department: str
    date_of_joining: date
    mobile_number: str