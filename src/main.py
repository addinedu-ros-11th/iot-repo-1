import sys
import os
from PyQt6.QtWidgets import QApplication

# src 폴더를 python path에 추가함
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.windows.main_window import MainWindow
from core.db_manager import DatabaseManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # db_manager는 이제 MainWindow 내부에서 초기화됨
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
