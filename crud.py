from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
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

def get_customer_by_attributes(db: Session, customer: schemas.CustomerGet, operators: dict = None):
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


def update_customer(db: Session, condition_dict: dict, update_dict: dict):
    try:
        # Get all customers that match the conditions
        customers = db.query(models.Customer).filter_by(**condition_dict).all()
        
        if not customers:
            raise HTTPException(status_code=404, detail="No customers found matching the conditions.")

        # Update all customers that match the conditions
        for customer in customers:
            for key, value in update_dict.items():
                # Eğer operatörlü bir değer ise
                if isinstance(value, tuple) and len(value) == 2:
                    operator, number = value
                    column_attr = getattr(customer, key)
                    
                    if operator == '>':
                        if getattr(customer, key) <= number:
                            setattr(customer, key, number)
                    elif operator == '<':
                        if getattr(customer, key) >= number:
                            setattr(customer, key, number)
                    elif operator == '>=':
                        if getattr(customer, key) < number:
                            setattr(customer, key, number)
                    elif operator == '<=':
                        if getattr(customer, key) > number:
                            setattr(customer, key, number)
                else:
                    setattr(customer, key, value)

        # Commit the changes
        db.commit()

        # Get the updated customer records
        updated_customers = db.query(models.Customer).filter_by(**condition_dict).all()

        return updated_customers

    except Exception as e:
        db.rollback()  # Rollback the transaction if an error occurs
        raise HTTPException(status_code=500, detail=f"An error occurred at update process: {str(e)}")