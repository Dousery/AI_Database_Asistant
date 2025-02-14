from  fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database_connection import SessionLocal, engine, get_db
from gpt_utils import get_ai_response

models.Base.metadata.create_all(bind=engine)

app = FastAPI()




query = input("Query: ")
response = get_ai_response(query)
print(response)







@app.post("/customers/")
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, customer=customer)

