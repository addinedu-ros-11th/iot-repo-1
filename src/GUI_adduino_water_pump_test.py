import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
import serial
import time

from_class = uic.loadUiType("/home/mj/dev_ws/IOT_프로젝트/GUI/Button_Relay_Pump.ui")[0]

class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 아두이노 시리얼 연결
        self.ser = serial.Serial('/dev/ttyACM0', 9600)
        time.sleep(2)

        # 버튼 클릭 이벤트 연결
        self.Pump_1.clicked.connect(lambda: self.runPump("P1"))
        self.Pump_2.clicked.connect(lambda: self.runPump("P2"))
        self.Pump_3.clicked.connect(lambda: self.runPump("P3"))
        self.Pump_4.clicked.connect(lambda: self.runPump("P4"))
        self.Pump_5.clicked.connect(lambda: self.runPump("P5"))
        self.Pump_6.clicked.connect(lambda: self.runPump("P6"))

    # 공통 펌프 실행 함수
    def runPump(self, pump_cmd):
        pump_number = pump_cmd[1]
        self.textEdit.setText(f"{pump_number}번 펌프 동작")
        send_cmd = (pump_cmd + "\n").encode()
        self.ser.write(send_cmd)
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())