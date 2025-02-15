from pydantic import BaseModel
from typing import Optional

class CustomerBase(BaseModel):
    id: Optional[int] = None
    age: Optional[int] = None
    job: Optional[str] = None
    marital: Optional[str] = None
    education: Optional[str] = None
    is_default: Optional[str] = None
    balance: Optional[int] = None
    housing: Optional[str] = None
    loan: Optional[str] = None
    contact: Optional[str] = None
    call_day: Optional[int] = None
    call_month: Optional[str] = None
    duration: Optional[int] = None
    campaign: Optional[int] = None
    pdays: Optional[int] = None
    previous: Optional[int] = None
    poutcome: Optional[str] = None
    deposit: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerFilter(CustomerBase):
    id: Optional[int] = None

class CustomerGet(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    
    class Config:
        from_attributes = True