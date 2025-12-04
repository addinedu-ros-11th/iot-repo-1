import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
import serial
import time
import mysql.connector 

from_class = uic.loadUiType("/home/mj/dev_ws/IOT_프로젝트/GUI/SQL_GUI_adduin_Button_Relay_Pump_test.ui")[0]

class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # MY SQL 연결
        try :
            self.db = mysql.connector.connect(
                host = "wbb.c70a028eoyhm.ap-northeast-2.rds.amazonaws.com",
                port = 3306,
                user = "mj",
                password = "123",
                database = "wbb"
            )
            self.cur = self.db.cursor()
            self.textEdit.setText("✅ DB 연결 성공")

        except mysql.connector.Error as e :
            self.db = None
            self.cur = None
            self.textEdit.setText(f"❌ DB 연결 실패: {e}")            

        # GUI 버튼을 칵테일 메뉴와 연결
        self.btnGinTonic.clicked.connect(lambda: self.makeCocktail("Gin & Tonic"))
        self.btnSomaek.clicked.connect(lambda: self.makeCocktail("Somaek"))
        self.btnOrangeTree.clicked.connect(lambda: self.makeCocktail("Orange Tree"))
        self.btnGinCoke.clicked.connect(lambda: self.makeCocktail("Gin Coke"))
        self.btnDiesel.clicked.connect(lambda: self.makeCocktail("Diesel"))

        # 아두이노 시리얼 연결
        self.ser = serial.Serial('/dev/ttyACM0', 9600)
        time.sleep(2)

        # POWER ON / OFF    
        self.isPowerON = False
        self.btnpower.clicked.connect(self.clickpower)

        # 비상 정지 / 부져 ON / OFF
        self.isEStopON = False
        self.enstop.clicked.connect(self.clickestop)

        # 버튼 클릭 이벤트 연결
        self.Pump_1.clicked.connect(lambda: self.runPump("P1"))
        self.Pump_2.clicked.connect(lambda: self.runPump("P2"))
        self.Pump_3.clicked.connect(lambda: self.runPump("P3"))
        self.Pump_4.clicked.connect(lambda: self.runPump("P4"))
        self.Pump_5.clicked.connect(lambda: self.runPump("P5"))
        self.Pump_6.clicked.connect(lambda: self.runPump("P6"))

    def clickpower(self):
        if self.isPowerON == False:
            self.btnpower.setText("Power OFF")
            self.ser.write(b"P_ON\n")
            self.isPowerON = True
            self.enablePumps(True)
        else :
            self.btnpower.setText("Power ON")
            self.ser.write(b"P_OFF\n")
            self.isPowerON = False
            self.enablePumps(False)

    def clickestop(self):
        if self.isEStopON == False:
            self.enstop.setText("Buzzer OFF")
            self.ser.write(b"BZ_ON\n")
            self.isEStopON = True

            # 릴레이도 동시에 OFF (긴급정지 효과)
            self.ser.write(b"P_OFF\n")

            # GUI Power 버튼도 OFF 상태로 동기화
            self.btnpower.setText("Power ON")
            self.isPowerON = False
        else :
            self.enstop.setText("E - Stop")
            self.ser.write(b"BZ_OFF\n")
            self.isEStopON = False

    # 공통 펌프 실행 함수
    def runPump(self, pump_cmd):
        pump_number = pump_cmd[1]
        self.textEdit.setText(f"{pump_number}번 펌프 동작")
        send_cmd = (pump_cmd + "\n").encode()
        self.ser.write(send_cmd)
    
    def enablePumps(self, enable):
        self.Pump_1.setEnabled(enable)
        self.Pump_2.setEnabled(enable)
        self.Pump_3.setEnabled(enable)
        self.Pump_4.setEnabled(enable)
        self.Pump_5.setEnabled(enable)
        self.Pump_6.setEnabled(enable)

    # cocktail_id 가져오는 함수
    def getCocktailID(self, cocktail_name):
        sql = "SELECT cocktail_id FROM cocktails WHERE name=%s"
        self.cur.execute(sql, (cocktail_name,))
        result = self.cur.fetchone()
        return result[0] if result else None
    
    # 레시피 조회 함수
    def getRecipes(self, cocktail_id):
        sql = "SELECT pump_pin, amount_ml FROM recipes WHERE cocktail_id=%s"
        self.cur.execute(sql, (cocktail_id,))
        return self.cur.fetchall()   # 예: [(2,45), (3,120)]

    # 펌프 동작 함수
    def runPumpFromDB(self, pump_pin, amount_ml):
        run_time = amount_ml * 50    # ml → ms 변환

        # DB pump_pin(2,3,4,5,6,7) -> Arduino 펌프 번호(1~6) 매핑
        pump_map = {
            2: 1,   # 2번 핀 → 1번 펌프
            3: 2,   # 3번 핀 → 2번 펌프
            4: 3,   # 4번 핀 → 3번 펌프
            5: 4,   # 5번 핀 → 4번 펌프
            6: 5,   # 6번 핀 → 5번 펌프
            7: 6,   # 7번 핀 → 6번 펌프
        }

        pump_num = pump_map.get(pump_pin)
        if pump_num is None:
            self.textEdit.append(f"⚠ 알 수 없는 pump_pin: {pump_pin}")
            return

        cmd = f"PUMP,{pump_num},{run_time}\n"
        self.ser.write(cmd.encode())

        self.textEdit.append(f"펌프 {pump_num} (DB pin {pump_pin}) : {amount_ml}ml → {run_time}ms 동작")
        time.sleep(0.1)


    # makeCocktail 함수
    def makeCocktail(self, cocktail_name):

        # 1) 칵테일 ID 가져오기
        cocktail_id = self.getCocktailID(cocktail_name)
        if cocktail_id is None:
            self.textEdit.setText("칵테일 정보를 찾을 수 없습니다.")
            return
        
        # 2) 해당 칵테일 레시피 가져오기
        recipes = self.getRecipes(cocktail_id)
        if not recipes:
            self.textEdit.setText("레시피가 존재하지 않습니다.")
            return
        
        self.textEdit.setText(f"{cocktail_name} 제조 시작...")

        # 3) 재료 순서대로 펌프 실행
        for pump_pin, amount_ml in recipes:
            self.runPumpFromDB(pump_pin, amount_ml)

        self.textEdit.append("제조 완료!")

if __name__=="__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())