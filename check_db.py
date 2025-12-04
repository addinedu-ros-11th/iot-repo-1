import mysql.connector

def check_schema():
    try:
        conn = mysql.connector.connect(
            host="wbb.c70a028eoyhm.ap-northeast-2.rds.amazonaws.com",
            user="sm",
            password="123",
            database="wbb"
        )
        cursor = conn.cursor()
        cursor.execute("DESCRIBE cocktails")
        for x in cursor:
            print(x)
        conn.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_schema()
