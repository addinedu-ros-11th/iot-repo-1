import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def check_schema():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        cursor.execute("DESCRIBE recipes")
        for x in cursor:
            print(x)
        conn.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_schema()
