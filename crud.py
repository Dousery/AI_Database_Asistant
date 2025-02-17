from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
import models
import schemas
from fastapi import HTTPException

# Get customer ınformation
def get_customer_by_attributes(db: Session, customer: schemas.CustomerGet):
    query = db.query(models.Customer)
    parameters = customer.model_dump(exclude_unset=True)
    
    for key, value in parameters.items():
        query = query.filter(getattr(models.Customer, key) == value)
    
    return query.all()

# Create new customer
def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump(exclude_unset=True))
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


# Update existing customer
def update_customer(db: Session, condition_dict: dict, update_dict: dict):
    try:
        # Get all customers that match the conditions
        customers = db.query(models.Customer).filter_by(**condition_dict).all()
        
        if not customers:
            raise HTTPException(status_code=404, detail="No customers found matching the conditions.")

        # Update all customers that match the conditions
        for customer in customers:
            for key, value in update_dict.items():
                setattr(customer, key, value) 

        # Commit the changes
        db.commit()

        # Get the updated customer records
        updated_customers = db.query(models.Customer).filter_by(**condition_dict).all()

        return updated_customers

    except Exception as e:
        db.rollback()  # Rollback the transaction if an error occurs
        raise HTTPException(status_code=500, detail=f"An error occurred at update process: {str(e)}")
