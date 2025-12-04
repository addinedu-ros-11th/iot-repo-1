import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# .env 파일 로드
load_dotenv()

class DatabaseManager:
    def __init__(self, host=None, user=None, password=None, database=None):
        self.host = host or os.getenv("DB_HOST")
        self.user = user or os.getenv("DB_USER")
        self.password = password or os.getenv("DB_PASSWORD")
        self.database = database or os.getenv("DB_NAME")
        self.connection = None

    def connect(self):
        """MySQL 데이터베이스에 연결함."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                return True
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """MySQL 데이터베이스 연결을 해제함."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def execute_query(self, query, params=None):
        """쿼리(INSERT, UPDATE, DELETE)를 실행함."""
        if not self.connection or not self.connection.is_connected():
            print("Not connected to database.")
            return None

        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
            return cursor
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            cursor.close()

    def fetch_query(self, query, params=None):
        """SELECT 쿼리를 실행하고 결과를 반환함."""
        if not self.connection or not self.connection.is_connected():
            print("Not connected to database.")
            return None

        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error fetching data: {e}")
            return None
        finally:
            cursor.close()