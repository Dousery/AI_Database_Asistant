import psycopg2
import csv

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "bank"
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
    with open("bank_sample.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            cur.execute(
                """
                INSERT INTO customers (age, job, marital, education, is_default, balance, housing, loan, contact, 
                call_day, call_month, duration, campaign, pdays, previous, poutcome, deposit) VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """, row 
                )
    conn.commit()
    conn.close()
    print("Data has been written succesfully")


if __name__ == "__main__":
    csv_to_database()