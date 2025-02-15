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

# Tüm parametrelerin eşleşip eşleşmediğini kontrol eden yardımcı fonksiyon
def check_all_parameters_match(customer_obj, parameters):
    for key, value in parameters.items():
        if getattr(customer_obj, key) != value:
            return False
    return True

# Müşteri güncelleme (birden fazla müşteri)
def update_customers(db: Session, old_values: schemas.CustomerFilter, new_values: schemas.CustomerUpdate):
    query = db.query(models.Customer)
    filter_params = old_values.model_dump(exclude_unset=True)
    update_params = new_values.model_dump(exclude_unset=True)
    
    # İlk filtrelemeyi yap
    for key, value in filter_params.items():
        query = query.filter(getattr(models.Customer, key) == value)
    
    customers = query.all()
    matched_customers = []
    
    if customers:
        for customer in customers:
            # Tüm parametrelerin eşleşip eşleşmediğini kontrol et
            if check_all_parameters_match(customer, filter_params):
                # Yeni değerleri güncelle
                for key, value in update_params.items():
                    setattr(customer, key, value)
                matched_customers.append(customer)
        
        if matched_customers:
            db.commit()
            return matched_customers
    return None

# Müşteri silme (birden fazla müşteri)
def delete_customers(db: Session, customer: schemas.CustomerFilter):
    query = db.query(models.Customer)
    parameters = customer.model_dump(exclude_unset=True)
    
    # İlk filtrelemeyi yap
    for key, value in parameters.items():
        query = query.filter(getattr(models.Customer, key) == value)
    
    customers = query.all()
    matched_customers = []
    
    if customers:
        for customer in customers:
            # Tüm parametrelerin eşleşip eşleşmediğini kontrol et
            if check_all_parameters_match(customer, parameters):
                db.delete(customer)
                matched_customers.append(customer)
        
        if matched_customers:
            db.commit()
            return {"message": f"{len(matched_customers)} customers deleted"}
    return None