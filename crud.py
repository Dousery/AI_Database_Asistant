from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
import models
import re
import schemas
from fastapi import HTTPException

# Function to parse conditions for filters, like '>', '<', '>=', etc.
def parse_condition(value):
    match = re.match(r"([><]=?)(\d+)", str(value).strip())
    if match:
        operator, number = match.groups()
        return operator, int(number) 
    return None, value 

# Function to apply filters to a query based on parameters and operators
def apply_filters(query, model, parameters, operators):
    for key, value in parameters.items():
        print(f"Processing column: {key}, value: {value}")
        column_attr = getattr(model, key)
        
        if key in operators:
            operator = operators[key]
            print(f"Found operator for {key}: {operator}")
            
            # Apply filters based on the operator
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
            print(f"Added filter: {key} == {value}")
    return query

# Function to get a list of customers based on the specified conditions
def get_customer(db: Session, customer: schemas.CustomerGet, operators: dict = None):
    query = db.query(models.Customer) # Start a query on the Customer model
    parameters = customer.model_dump(exclude_unset=True)
    operators = operators or {}
    query = apply_filters(query, models.Customer, parameters, operators)
    
    print(f"Final query: {query}")
    
    return query.all()

# Function to create a new customer in the database
def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump(exclude_unset=True))
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# Function to delete a customer from the database
def delete_customer(db: Session, customer: schemas.CustomerDelete, operators: dict = None):
    query = db.query(models.Customer)
    parameters = customer.model_dump(exclude_unset=True)

    try:
        customers_to_delete = query.all()
    except Exception as e:
        db.rollback()
        print(f"Error fetching customers to delete: {e}")
        return []
    
    if customers_to_delete:
        try:
            for customer in customers_to_delete:
                db.delete(customer)
            db.commit()
            print(f"Deleted {len(customers_to_delete)} customers.")
        except Exception as e:
            db.rollback()
            print(f"Error during deletion process: {e}")
            return []
    else:
        print("No customers found for deletion.")
    
    return customers_to_delete

# Function to update customer information based on given conditions
def update_customer(db: Session, condition_dict: dict, operators: dict, update_dict: dict):
    query = db.query(models.Customer)
    operators = operators or {}
    query = apply_filters(query, models.Customer, condition_dict, operators)
    
    customers_to_update = query.all()
    
    if not customers_to_update:
        print("No customers found matching the given conditions.")
        return []
    
    try:
        for customer in customers_to_update:
            for key, value in update_dict.items():
                if hasattr(customer, key):   # Check if the customer has the given attribute
                    setattr(customer, key, value)  # Update the attribute value
        db.commit()
        
        updated_customers = db.query(models.Customer).filter(models.Customer.id.in_([customer.id for customer in customers_to_update])).all()

        for customer in updated_customers:
            print(f"Updated customer: {customer}")

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error updating customers: {e}") # Log the error
        return None
    
    return updated_customers