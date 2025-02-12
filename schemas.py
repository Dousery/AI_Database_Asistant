from pydantic import BaseModel
from typing import Optional

class CustomerBase(BaseModel):
    age: int
    job: str
    marital: str
    education: str
    is_default: str
    balance: int
    housing: str
    loan: str
    contact: str
    call_day: int
    call_month: str
    duration: int
    campaign: int
    pdays: int
    previous: int
    poutcome: str
    deposit: str

    class Config:
        orm_mode = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
