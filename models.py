from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    job = Column(String)
    marital = Column(String)
    education = Column(String)
    is_default = Column(String)
    balance = Column(Integer)
    housing = Column(String)
    loan = Column(String)
    contact = Column(String)
    call_day = Column(Integer)
    call_month = Column(String)
    duration = Column(Integer)
    campaign = Column(Integer)
    pdays = Column(Integer)
    previous = Column(Integer)
    poutcome = Column(String)
    deposit = Column(String)