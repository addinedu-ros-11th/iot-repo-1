import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic

# ui 파일 연결 - 코드 파일과 같은 폴더 내에 위치해야함
from_class = uic.loadUiType("/home/mj/dev_ws/IOT_프로젝트/GUI/Button_Relay.ui")[0]

# GUI 화면
class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # POWER ON / OFF    
        self.isPowerON = True
        self.btnpower.clicked.connect(self.clickpower)

        # 비상 정지 / 부져 ON / OFF
        self.isEStopON = True
        self.enstop.clicked.connect(self.clickestop)

    def clickpower(self) :
        if self.isPowerON == False :
            self.btnpower.setText("Power ON")
            self.isPowerON = True

        else :
            self.btnpower.setText("Power OFF")
            self.isPowerON = False

    def clickestop(self) :
        if self.isEStopON == False :
            self.enstop.setText("E - Stop")
            self.isEStopON = True

        else :
            self.enstop.setText("Buzzer OFF")
            self.isEStopON = False

# python Main 함수        
if __name__=="__main__":
    app = QApplication(sys.argv)    # 프로그램 실행
    myWindows = WindowClass()       # 화면 클래스 생성
    myWindows.show()                # 프로그램 화면 보이기 

    sys.exit(app.exec())            # 프로그램 종료까지 동작시킴