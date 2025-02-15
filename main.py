from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import models
import schemas
from database_connection import get_db, engine
from gpt_utils import get_ai_response
import re

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def process_orm_method(orm_method: str, db: Session):
    """
    GPT'den gelen ORM metodunu işler ve uygun CRUD işlemini gerçekleştirir
    """
    # Metod adı ve parametreleri ayıkla
    match = re.match(r'(\w+)\((.*)\)', orm_method.strip())
    if not match:
        raise HTTPException(status_code=400, detail="Invalid ORM method format")
    
    method_name, params_str = match.groups()
    
    try:
        # Metoda göre işlem yap
        if method_name == "create_customer":
            # create_customer({'age': 30, 'job': 'mühendis'}) formatını işle
            params = eval(params_str)
            customer = schemas.CustomerCreate(**params)
            return crud.create_customer(db, customer)
            
        elif method_name == "get_customer_by_attributes":
            # get_customer_by_attributes(age=30, job='mühendis') formatını işle
            params = eval(f"dict({params_str})")
            customer = schemas.CustomerGet(**params)
            return crud.get_customer_by_attributes(db, customer)
            
        elif method_name == "update_customer":
            # update_customer(5, {'job': 'öğretmen'}) formatını işle
            id_str, update_dict_str = params_str.split(',', 1)
            customer_id = int(id_str.strip())
            update_dict = eval(update_dict_str.strip())
            
            old_values = schemas.CustomerFilter(id=customer_id)
            new_values = schemas.CustomerUpdate(**update_dict)
            return crud.update_customers(db, old_values, new_values)
            
        elif method_name == "delete_customer":
            # delete_customer(10) veya delete_customer({'job': 'mühendis'}) formatını işle
            params = eval(params_str)
            if isinstance(params, dict):
                customer = schemas.CustomerFilter(**params)
            else:
                customer = schemas.CustomerFilter(id=params)
            return crud.delete_customers(db, customer)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {method_name}")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing query: {str(e)}")

@app.post("/process-query/")
async def process_query(query: str, db: Session = Depends(get_db)):
    """
    Doğal dil sorgusunu işler ve uygun CRUD işlemini gerçekleştirir
    """
    try:
        # GPT'den ORM metodunu al
        orm_method = get_ai_response(query)
        
        # ORM metodunu işle ve sonucu döndür
        result = process_orm_method(orm_method, db)
        
        return {
            "query": query,
            "orm_method": orm_method,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))