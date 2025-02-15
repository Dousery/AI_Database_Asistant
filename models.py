from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    age = Column(Integer, nullable=True)
    job = Column(String, nullable=True)
    marital = Column(String, nullable=True)
    education = Column(String, nullable=True)
    is_default = Column(String, nullable=True)
    balance = Column(Integer, nullable=True)
    housing = Column(String, nullable=True)
    loan = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    call_day = Column(Integer, nullable=True)
    call_month = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)
    campaign = Column(Integer, nullable=True)
    pdays = Column(Integer, nullable=True)
    previous = Column(Integer, nullable=True)
    poutcome = Column(String, nullable=True)
    deposit = Column(String, nullable=True)
