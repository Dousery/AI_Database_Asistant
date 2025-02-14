from sqlalchemy.orm import Session
import models
import schemas

# Müşteri verisini alma
def get_customer_by_attributes(db: Session, customer: schemas.CustomerGet):
    query = db.query(models.Customer)
    parameters = customer.model_dump(exclude_unset=True)

    for key, value in parameters.items():
        query = query.filter(getattr(models.Customer, key) == value)
    
    return query.all()

# Müşteri oluşturma
def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump(exclude_unset=True))
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# Müşteri güncelleme (birden fazla müşteri)
def update_customers(db: Session, customer: schemas.CustomerUpdate):
    query = db.query(models.Customer)
    parameters = customer.model_dump(exclude_unset=True)
    
    for key, value in parameters.items():
        query = query.filter(getattr(models.Customer, key) == value)
    
    customers = query.all()
    
    if customers:
        for customer in customers:
            for key, value in parameters.items():
                setattr(customer, key, value)
        db.commit()
        return customers
    return None

# Müşteri silme (birden fazla müşteri)
def delete_customers(db: Session, customer: schemas.CustomerUpdate):
    query = db.query(models.Customer)
    parameters = customer.model_dump(exclude_unset=True)
    
    for key, value in parameters.items():
        query = query.filter(getattr(models.Customer, key) == value)
    
    customers = query.all()
    
    if customers:
        for customer in customers:
            db.delete(customer)
        db.commit()
        return {"message": f"{len(customers)} customers deleted"}
    return None