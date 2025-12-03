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


if __name__=="__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())