from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Veritabanı bağlantı URL'si
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy motorunu oluştur
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM modelleri için temel sınıf
Base = declarative_base()

# Veritabanı bağlantısı sağlayan fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()