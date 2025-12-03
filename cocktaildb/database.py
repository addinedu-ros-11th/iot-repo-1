import mysql.connector

class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': "aaaaaaa",
            'port':3306,
            'user': 'admin',       # DB 아이디
            'password': 'aaaaa', # DB 비번
            'database': 'wbb'
        }

    def get_connection(self):
        return mysql.connector.connect(**self.config)
    
    def get_menu_list(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT cocktail_id, name, price, description FROM cocktails"
            cursor.execute(query)
            result = cursor.fetchall() # 리스트 형태 [ {id:1, name:..}, {id:2...} ]
            return result
            
        except Exception as e:
            print(f"Menu Error: {e}")
            return []
        finally:
            if 'conn' in locals() and conn.is_connected(): conn.close()


    def get_cocktail_info(self, cid):
        """
        사용법: info = db.get_cocktail_info(1~5)
        결과값: {'name': 'Gin Tonic', 'price': 6000, 'recipe': [{'pin':2, 'ml':45}, ...]}
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

           # 칵테일 정보 반환 쿼리 
            query_info = "SELECT name, price, description FROM cocktails WHERE cocktail_id = %s"
            cursor.execute(query_info, (cid,))
            info = cursor.fetchone() # 결과: {'name': 'Gin & Tonic', 'price': 6000, ...}

            if not info:
                return None # 없는 칵테일 번호면 빈값 리턴

            # 레시피 테이블에서 재료+펌프 핀번호+재료양 반환 쿼리 
            query_recipe = """
                SELECT ingredient_name, pump_pin, amount_ml 
                FROM recipes 
                WHERE cocktail_id = %s
            """
            cursor.execute(query_recipe, (cid,))
            recipes = cursor.fetchall() 
            # 결과: [{'pump_pin': 2, 'amount_ml': 45}, {'pump_pin': 3, ...}]

            # 결과 취합
            result = {
                "id": cid,
                "name": info['name'],
                "price": info['price'],
                "desc": info['description'],
                "recipe": recipes  
            }
            
            return result

        except Exception as e:
            print(f"Info Error: {e}")
            return None
        finally:
            if conn and conn.is_connected(): conn.close()

   
    # 3. 유저 & 결제 관련 
   
    def get_user_by_rfid(self, uid):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE rfid_uid = %s"
            cursor.execute(query, (uid,))
            return cursor.fetchone()
        except Exception as e:
            print(f"User Error: {e}")
            return None
        finally:
            if 'conn' in locals() and conn.is_connected(): conn.close()

    def deduct_points(self, user_id, amount):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = "UPDATE users SET point_balance = point_balance - %s WHERE user_id = %s"
            cursor.execute(query, (amount, user_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Pay Error: {e}")
            return False
        finally:
            if 'conn' in locals() and conn.is_connected(): conn.close()
