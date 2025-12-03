import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
import serial
import time

from_class = uic.loadUiType("/home/mj/dev_ws/IOT_프로젝트/GUI/pump.ui")[0]

class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Pump_1.clicked.connect(self.Pump1)
        self.Pump_2.clicked.connect(self.Pump2)
        self.Pump_3.clicked.connect(self.Pump3)
        self.Pump_4.clicked.connect(self.Pump4)
        self.Pump_5.clicked.connect(self.Pump5)
        self.Pump_6.clicked.connect(self.Pump6)

    # 선택 버튼 텍스트 출력
    def Pump1(self) :
        self.textEdit.setText("1번 펌프")
    def Pump2(self) :
        self.textEdit.setText("2번 펌프")
    def Pump3(self) :
        self.textEdit.setText("3번 펌프")
    def Pump4(self) :
        self.textEdit.setText("4번 펌프")
    def Pump5(self) :
        self.textEdit.setText("5번 펌프")
    def Pump6(self) :
        self.textEdit.setText("6번 펌프")

if __name__=="__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())
