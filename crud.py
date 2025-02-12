from sqlalchemy.orm import Session
from models import Customer

# Müşteri verisini alma
def get_customer_by_attributes(db: Session, **attributes):
    query = db.query(Customer)
    
    for key, value in attributes.items():
        query = query.filter(getattr(Customer, key) == value)
    
    return query.all()

# Müşteri oluşturma
def create_customer(db: Session, customer_data: dict):
    db_customer = Customer(**customer_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# Müşteri güncelleme (birden fazla müşteri)
def update_customers(db: Session, customer_data: dict, **attributes):
    query = db.query(Customer)
    
    for key, value in attributes.items():
        query = query.filter(getattr(Customer, key) == value)
    
    customers = query.all()
    
    if customers:
        for customer in customers:
            for key, value in customer_data.items():
                setattr(customer, key, value)
        db.commit()
        return customers
    return None

# Müşteri silme (birden fazla müşteri)
def delete_customers(db: Session, **attributes):
    query = db.query(Customer)
    
    for key, value in attributes.items():
        query = query.filter(getattr(Customer, key) == value)
    
    customers = query.all()
    
    if customers:
        for customer in customers:
            db.delete(customer)
        db.commit()
        return {"message": f"{len(customers)} customers deleted"}
    return None