import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import crud
import schemas
from database_connection import get_db
from gpt_utils import get_ai_response
import re

# Logging configuration
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


import re

def process_operator_params(params: dict) -> dict:
    """
    Operatörlü parametreleri işleyip, operatörleri çıkarıp güncellenmiş parametreler döner.
    Operatörler, sadece veritabanı sorgusunda kullanılmak üzere saklanır.
    """
    updated_params = {}
    operators = {}  

    for key, value in params.items():
        print(f"Processing key: {key}, value: {value}")  
        
        if isinstance(value, str) and re.match(r'(>|<|>=|<=)\d+', value):
            operator, number = re.match(r'(>|<|>=|<=)(\d+)', value).groups()
            print(f"Found operator: {operator}, number: {number}")  
            updated_params[key] = int(number)  
            operators[key] = operator 
        else:
            updated_params[key] = value
            print(f"No operator, directly added: {key}: {value}") 

    print(f"Updated parameters: {updated_params}") 
    print(f"Operators: {operators}")  
    return updated_params, operators


def process_orm_method(orm_method: str, db: Session):
    """
    GPT'den gelen ORM metodunu işler ve uygun CRUD işlemini gerçekleştirir.
    """
     # Remove quotes and backticks
    orm_method = orm_method.strip().strip("`").strip("'").strip('"')

    match = re.match(r'(\w+)\((.*)\)', orm_method.strip())
    
    if not match:
        error_message = f"Invalid ORM method format: {orm_method}"
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    method_name, params_str = match.groups()

    try:
        # Convert the parameters string to a dictionary
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
    
            # Operatörlü parametreleri işle
            updated_params, operators = process_operator_params(params)

            customer = schemas.CustomerGet(**updated_params)
            result = crud.get_customer(db, customer, operators)

        elif method_name == "update_customer":
            if len(params) != 2:
                raise ValueError("Update requires two dictionaries: condition and update fields.")
    
            condition_dict = params[0]  # Condition dictionary
            update_dict = params[1]     # Update dictionary

            print(f"Condition Dictionary: {condition_dict}")
            print(f"Update Dictionary: {update_dict}")

            # Operatörlü parametreleri işle
            updated_params, operators = process_operator_params(condition_dict)

            print(f"Updated Params: {updated_params}")
            print(f"Operators: {operators}")

            result = crud.update_customer(db, updated_params, operators, update_dict)

            print(f"Update Result: {result}")


        elif method_name == "delete_customer":
            if not isinstance(params, dict):
                raise ValueError("Parameters should be a dictionary.")
    
            # Operatörlü parametreleri işle
            updated_params, operators = process_operator_params(params)

            customer = schemas.CustomerGet(**updated_params)
            result = crud.delete_customer(db, customer, operators)

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
        logging.critical(error_message)  # Critical level for unexpected errors
        return JSONResponse(
            status_code=500,
            content={
                "query": query,
                "detail": "Internal Server Error. Please check logs."
            }
        )