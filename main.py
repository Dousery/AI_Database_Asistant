import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import crud
import schemas
from database_connection import get_db
from gpt_utils import get_ai_response
import re

# 📌 Logging yapılandırması
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,  # INFO, WARNING, ERROR
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

import re
import ast
import logging
from fastapi import HTTPException

def process_orm_method(orm_method: str, db: Session):
    """
    GPT'den gelen ORM metodunu işler ve uygun CRUD işlemini gerçekleştirir.
    """
     # Baştaki ve sondaki backtick ve tırnakları temizle
    orm_method = orm_method.strip().strip("`").strip("'").strip('"')

    match = re.match(r'(\w+)\((.*)\)', orm_method.strip())
    
    if not match:
        error_message = f"Invalid ORM method format: {orm_method}"
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    method_name, params_str = match.groups()

    try:
        # Parametreleri güvenli şekilde dönüştür
        if params_str:
            params = ast.literal_eval(params_str)
        else:
            params = {}

        if method_name == "create_customer":
            if not isinstance(params, dict):
                raise ValueError("Parameters should be a dictionary.")
            customer = schemas.CustomerCreate(**params)
            result = crud.create_customer(db, customer)

        elif method_name == "get_customer_by_attributes":
            if not isinstance(params, dict):
                raise ValueError("Parameters should be a dictionary.")
            customer = schemas.CustomerGet(**params)
            result = crud.get_customer_by_attributes(db, customer)

        elif method_name == "update_customer":
            if not isinstance(params, tuple) or len(params) != 2:
                raise ValueError("update_customer should have two parameters: (id, update_dict).")
            
            customer_id, update_dict = params
            if not isinstance(customer_id, int) or not isinstance(update_dict, dict):
                raise ValueError("Invalid parameters for update_customer.")

            old_values = schemas.CustomerFilter(id=customer_id)
            new_values = schemas.CustomerUpdate(**update_dict)
            result = crud.update_customers(db, old_values, new_values)

        elif method_name == "delete_customer":
            if isinstance(params, dict):
                customer = schemas.CustomerFilter(**params)
            elif isinstance(params, int):
                customer = schemas.CustomerFilter(id=params)
            else:
                raise ValueError("Invalid parameter type for delete_customer.")
            
            result = crud.delete_customers(db, customer)

        else:
            error_message = f"Unknown ORM method: {method_name}"
            logging.error(error_message)
            raise HTTPException(status_code=400, detail=error_message)

        # Başarıyla çalıştıysa logla
        logging.info(f"Successfully executed: {orm_method}")
        return result

    except (SyntaxError, ValueError) as e:
        error_message = f"Error processing ORM method '{orm_method}': {str(e)}"
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)


@app.post("/process-query/", responses={400: {"description": "Invalid ORM Method or Processing Error"}})
async def process_query(query: str, db: Session = Depends(get_db)):
    """
    Doğal dil sorgusunu işler, ORM metodunu çalıştırır ve sonucu döndürür.
    """
    try:
        # GPT'den ORM metodunu al
        orm_method = get_ai_response(query)

        # ORM metodunu işle
        result = process_orm_method(orm_method, db)
        
        return {
            "query": query,
            "orm_method": orm_method,
            "result": result
        }
    
    except HTTPException as e:
        error_detail = e.detail
        logging.error(f"Query processing error: {error_detail}")
        return JSONResponse(
            status_code=400,
            content={
                "query": query,
                "orm_method": orm_method,
                "detail": error_detail
            }
        )
    
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logging.critical(error_message)  # Ciddi hatalar için CRITICAL seviyesi
        return JSONResponse(
            status_code=500,
            content={
                "query": query,
                "detail": "Internal Server Error. Please check logs."
            }
        )