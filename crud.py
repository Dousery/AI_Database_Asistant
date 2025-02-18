from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
import models
import re
import schemas
from fastapi import HTTPException

# 🔹 Koşul ayrıştırma fonksiyonu (">30" → (">", 30))
def parse_condition(value):
    match = re.match(r"([><]=?)(\d+)", str(value).strip())
    if match:
        operator, number = match.groups()
        return operator, int(number)  # Sayıyı integer olarak döndür
    return None, value  # Eğer koşul değilse olduğu gibi bırak

import re

def get_customer(db: Session, customer: schemas.CustomerGet, operators: dict = None):
    query = db.query(models.Customer)
    parameters = customer.model_dump(exclude_unset=True)
    
    if operators is None:
        operators = {}

    for key, value in parameters.items():
        print(f"Processing column: {key}, value: {value}")  # Aşama 1: Parametrelerin sütunları ve değerlerini yazdırıyoruz
        column_attr = getattr(models.Customer, key)

        # Operatörlü koşul kontrolü
        if key in operators:
            operator = operators[key]  # Operatör parametreden alınıyor
            print(f"Found operator for {key}: {operator}")  # Aşama 2: Operatör bulunduysa yazdırıyoruz
            
            if operator == '>':
                query = query.filter(column_attr > value)
                print(f"Added filter: {key} > {value}")
            elif operator == '<':
                query = query.filter(column_attr < value)
                print(f"Added filter: {key} < {value}")
            elif operator == '>=':
                query = query.filter(column_attr >= value)
                print(f"Added filter: {key} >= {value}")
            elif operator == '<=':
                query = query.filter(column_attr <= value)
                print(f"Added filter: {key} <= {value}")
            elif operator == '!=':
                query = query.filter(column_attr != value)
                print(f"Added filter: {key} != {value}")
        else:
            # Eğer operatör belirtilmemişse basit eşitlik kontrolü yapılır
            query = query.filter(column_attr == value)
            print(f"Added filter: {key} == {value}")  # Aşama 3: Operatörsüz eşitlik kontrolü

    print(f"Final query: {query}")  # Aşama 4: Final sorguyu yazdırıyoruz
    return query.all()


# Create new customer
def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump(exclude_unset=True))
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, condition_dict: dict, operators: dict, update_dict: dict):
    query = db.query(models.Customer)
    
    if operators is None:
        operators = {}
    
    # Koşulları sorguya ekleme
    for key, value in condition_dict.items():
        column_attr = getattr(models.Customer, key)
        operator = operators.get(key, '==')
        
        if operator == '>':
            query = query.filter(column_attr > value)
        elif operator == '<':
            query = query.filter(column_attr < value)
        elif operator == '>=':
            query = query.filter(column_attr >= value)
        elif operator == '<=':
            query = query.filter(column_attr <= value)
        elif operator == '!=':
            query = query.filter(column_attr != value)
        else:
            query = query.filter(column_attr == value)
    
    customers_to_update = query.all()
    
    if not customers_to_update:
        print("No customers found matching the given conditions.")
        return []
    
    try:
        # Güncelleme işlemi
        for customer in customers_to_update:
            for key, value in update_dict.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
        
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error updating customers: {e}")
        return None
    
    return query.all()