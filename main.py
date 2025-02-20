import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import crud
import schemas
from database_connection import get_db
from gpt_utils import get_ai_response
import re
import ast
from database_connection import  engine
import models
import pandas as pd

# Logging configuration
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,  # INFO, WARNING, ERROR
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

models.Base.metadata.create_all(engine)

def load_customers_from_csv(db: Session):
    """bank_sample.csv dosyasındaki verileri veritabanına aktarır."""
    df = pd.read_csv("bank_sample.csv")  # CSV dosyasını oku

    # Eğer daha önce yüklenmişse tekrar eklememek için kontrol et
    existing_customers = db.query(models.Customer).count()
    if existing_customers > 0:
        print("Müşteriler zaten veritabanına eklenmiş.")
        return

    for _, row in df.iterrows():
        customer_data = schemas.CustomerCreate(
            age=row["age"],
            job=row["job"],
            marital=row["marital"],
            education=row["education"],
            is_default=row["is_default"],
            balance=row["balance"],
            housing=row["housing"],
            loan=row["loan"],
            contact=row["contact"],
            call_day=row["call_day"],
            call_month=row["call_month"],
            duration=row["duration"],
            campaign=row["campaign"],
            pdays=row["pdays"],
            previous=row["previous"],
            poutcome=row["poutcome"],
            deposit=row["deposit"]
        )
        crud.create_customer(db, customer_data)  # CRUD fonksiyonunu kullanarak ekleyelim

    print("CSV verileri başarıyla veritabanına eklendi.")

@app.on_event("startup")
def startup_event():
    """FastAPI uygulaması başlarken çalışacak event."""
    db = next(get_db())  # Veritabanı bağlantısını al
    load_customers_from_csv(db)  # CSV'den verileri yükle
    db.close()  # Bağlantıyı kapat


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

            # Process operator parameters
            updated_params, operators = process_operator_params(condition_dict)

            print(f"Updated Params: {updated_params}")
            print(f"Operators: {operators}")

            result = crud.update_customer(db, updated_params, operators, update_dict)

            print(f"Update Result: {result}")


        elif method_name == "delete_customer":
            if not isinstance(params, dict):
                raise ValueError("Parameters should be a dictionary.")
    
            updated_params, operators = process_operator_params(params)

            customer = schemas.CustomerGet(**updated_params)
            result = crud.delete_customer(db, customer, operators)

        else:
            error_message = f"Unknown ORM method: {method_name}"
            logging.error(error_message)
            raise HTTPException(status_code=400, detail=error_message)

        # Log the successful
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

         **Input Query Format:**
         - Kullanıcı, veritabanı üzerinde işlem yapabilmek için doğal dilde bir sorgu girmelidir. 
         - Sorgular, bir veya birden fazla veritabanı işlemi (örneğin, müşteri ekleme, güncelleme, silme) içerebilir.
         - Örnek sorgular:
             1. "Ali adlı yeni müşteri ekle, 30 yaşında, işi mühendis."  
             2. "ID'si 5 olan müşterinin işi değişti, yeni iş: öğretmen."  
             3. "ID'si 10 olan müşteriyi sil."  
             4. "İşi mühendis ve 30 yaşındaki müşteriyi getir."  
             5. "Yaşı 30'dan küçük ve 'evli' olan tüm müşterilerin işini değiştir."  
             6. "15 yaşındaki müşterinin işini doktor olarak güncelle."  

         **Veritabanı Tabloları:**
         - Veritabanında `customers` adlı bir tablo bulunmaktadır ve aşağıdaki alanlara sahiptir:
             - id (Integer)
             - age (Integer)
             - job (String)
             - marital (String)
             - education (String)
             - is_default (String)
             - balance (Integer)
             - housing (String)
             - loan (String)
             - contact (String)
             - call_day (Integer)
             - call_month (String)
             - duration (Integer)
             - campaign (Integer)
             - pdays (Integer)
             - previous (Integer)
             - poutcome (String)
             - deposit (String)
    
    """

    try:
        # Take the ORM method from the AI model
        orm_method = get_ai_response(query)

        # ORM method processing
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