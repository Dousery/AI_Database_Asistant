import psycopg2
import csv

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "Bank"
DB_USER = "postgres"
DB_PASS = "12345"
DB_PORT = "5432"

def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def csv_to_database():
    conn = connect_db()
    cur = conn.cursor()
    with open("data.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            cur.execute(
                """
                INSERT INTO bank_data (age, job, marital, education, default, balance, housing, loan, contact, 
                day, month, duration, campaign, pdays, previous, poutcome, deposit) VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """, row 
                )
    conn.commit()
    conn.close()