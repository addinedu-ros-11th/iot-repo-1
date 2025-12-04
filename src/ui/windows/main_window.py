import os
import sys

# 직접 실행 시 import를 위해 src 경로를 추가함
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '../../'))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from PyQt6.QtWidgets import QDialog, QApplication, QListView, QInputDialog, QLineEdit, QMessageBox, QLabel, QPushButton
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6 import uic
from core.serial_manager import SerialThread
from core.db_manager import DatabaseManager

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager(host="wbb.c70a028eoyhm.ap-northeast-2.rds.amazonaws.com",
                                         user="sm",
                                         password="----",
                                         database="wbb")
        self.db_manager.connect()
        # UI 파일을 로드함
        ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cocktail_GUI.ui'))
        uic.loadUi(ui_path, self)

        # 칵테일 메뉴 로드
        self.load_cocktail_menu()
        
        # 원료 라벨 로드
        self.load_ingredient_labels()

        # 탭 위젯 설정
        self.tabWidget = self.findChild(object, 'tabWidget')
        self.previous_tab_index = 0
        self.tabWidget.currentChanged.connect(self.check_admin_access)

        # UI의 프로그레스 바 목록임
        self.progress_bars = [
            self.progressBar,
            self.progressBar_2,
            self.progressBar_3,
            self.progressBar_4,
            self.progressBar_5,
            self.progressBar_6
        ]

        # 경고 라벨 목록 (UI 파일에 해당 이름의 QLabel이 있어야 함)
        self.tank_warnings = [
            self.findChild(QLabel, f"tank_{i}_warn") for i in range(1, 7)
        ]

        self.listView = self.findChild(QListView, 'listView')
        self.list_model = QStandardItemModel()
        self.listView.setModel(self.list_model)

        # 프로그레스 바를 초기화함
        for bar in self.progress_bars:
            bar.setRange(0, 100)
            bar.setValue(0)

        # 주문 버튼 연결
        self.order_buttons = [
            self.findChild(QPushButton, 'pushButton'),
            self.findChild(QPushButton, 'pushButton_2'),
            self.findChild(QPushButton, 'pushButton_3'),
            self.findChild(QPushButton, 'pushButton_4'),
            self.findChild(QPushButton, 'pushButton_5')
        ]
        
        for i, btn in enumerate(self.order_buttons):
            if btn:
                btn.clicked.connect(lambda checked, idx=i: self.select_cocktail(idx))

        self.selected_cocktail_label = self.findChild(QLabel, "label_3")
        self.selected_price_label = self.findChild(QLabel, "label_4")

        # Serial Thread Configuration
        self.port_sensor = '/dev/ttyUSB0' # Make sure this matches your setup
        self.thread_sensor = SerialThread(self.port_sensor)
        self.thread_sensor.progress_update.connect(self.update_progress)
        self.thread_sensor.start()


        # self.port_pump = '/dev/ttyUSB1' # Make sure this matches your setup
        # self.thread_pump = SerialThread(self.port_pump)
        # self.thread_pump.progress_update.connect(self.update_progress)
        # self.thread_pump.start()

        self.port_RFID = '/dev/ttyUSB2' # 설정과 일치하는지 확인해야 함
        self.thread_RFID = SerialThread(self.port_RFID)
        self.thread_RFID.progress_update.connect(self.handle_rfid_reading)
        self.thread_RFID.start()

    def handle_rfid_reading(self, data):
        # 데이터가 RFID 태그 문자열을 포함하는 리스트라고 가정함
        if not data:
            return
        
        rfid_tag = str(data[0]).strip()
        print(f"RFID Detected: {rfid_tag}")
        
        # 이전 결과를 지움
        self.list_model.clear()
        
        # 데이터베이스를 조회함
        # TODO: 실제 스키마에 맞게 테이블명 'users'와 컬럼 'rfid'를 수정해야 함
        query = "SELECT * FROM users WHERE rfid = %s"
        result = self.db_manager.fetch_query(query, (rfid_tag,))
        
        if result:
            for row in result:
                # 찾은 사용자의 모든 컬럼을 표시함
                display_text = " | ".join([f"{k}: {v}" for k, v in row.items()])
                item = QStandardItem(display_text)
                self.list_model.appendRow(item)
        else:
            self.list_model.appendRow(QStandardItem("User not found"))

    def check_admin_access(self, index):
        # 관리자 탭(인덱스 1)으로 이동하려는 경우
        if index == 1:
            password, ok = QInputDialog.getText(self, '관리자 인증', '비밀번호를 입력하세요:', QLineEdit.EchoMode.Password)
            if ok and password == '1234':
                # 비밀번호가 맞으면 탭 변경 허용 및 현재 인덱스 업데이트
                self.previous_tab_index = index
            else:
                # 비밀번호가 틀리거나 취소하면 경고 메시지 표시 및 이전 탭으로 복귀
                if ok: # 취소가 아닌 경우에만 경고 표시
                    QMessageBox.warning(self, '접근 거부', '비밀번호가 올바르지 않습니다.')
                
                # 시그널 차단 후 탭 복귀 (재귀 호출 방지)
                self.tabWidget.blockSignals(True)
                self.tabWidget.setCurrentIndex(self.previous_tab_index)
                self.tabWidget.blockSignals(False)
        else:
            # 다른 탭으로 이동하는 경우 현재 인덱스 업데이트
            self.previous_tab_index = index

    def load_cocktail_menu(self):
        """데이터베이스에서 칵테일 메뉴를 불러와 UI를 업데이트함."""
        query = "SELECT name, price FROM cocktails LIMIT 5"
        result = self.db_manager.fetch_query(query)

        if result:
            for i, row in enumerate(result):
                # 라벨 위젯 찾기 (cocktail01 ~ cocktail05, price01 ~ price05)
                name_label = self.findChild(QLabel, f"cocktail{i+1:02d}")
                price_label = self.findChild(QLabel, f"price{i+1:02d}")

                if name_label:
                    name_label.setText(str(row['name']))
                
                if price_label:
                    price_label.setText(f"{row['price']}원")
        else:
            print("칵테일 메뉴를 불러오지 못했습니다.")

    def load_ingredient_labels(self):
        """데이터베이스에서 원료 정보를 불러와 컵 라벨을 업데이트함."""
        # 펌프 핀(2~7)에 해당하는 원료 이름을 가져옴
        # DISTINCT를 사용하여 중복 제거 (같은 핀에 같은 재료가 여러 레시피에 쓰일 수 있음)
        query = "SELECT DISTINCT pump_pin, ingredient_name FROM recipes WHERE pump_pin BETWEEN 2 AND 7"
        result = self.db_manager.fetch_query(query)

        # 라벨 매핑 (펌프 핀 -> UI 위젯 이름)
        # Pump 2 -> cup1
        # Pump 3 -> cup2
        # Pump 4 -> cup3
        # Pump 5 -> cup4
        # Pump 6 -> cup5
        # Pump 7 -> cup6
        pin_to_label = {
            2: 'cup1',
            3: 'cup2',
            4: 'cup3',
            5: 'cup4',
            6: 'cup5',
            7: 'cup6'
        }

        if result:
            for row in result:
                pin = row['pump_pin']
                name = row['ingredient_name']
                
                if pin in pin_to_label:
                    label_name = pin_to_label[pin]
                    label = self.findChild(QLabel, label_name)
                    if label:
                        label.setText(name)
        else:
            print("원료 정보를 불러오지 못했습니다.")

    def select_cocktail(self, index):
        """주문 버튼 클릭 시 선택된 칵테일 정보를 업데이트함."""
        # 칵테일 이름과 가격 라벨 찾기
        name_label = self.findChild(QLabel, f"cocktail{index+1:02d}")
        price_label = self.findChild(QLabel, f"price{index+1:02d}")

        if name_label and self.selected_cocktail_label:
            self.selected_cocktail_label.setText(name_label.text())
        
        if price_label and self.selected_price_label:
            # "5000원" 형식에서 숫자만 추출하거나 그대로 사용
            # 요구사항: "클릭한 버튼의 해당되는 가격으로 변할 수 있게"
            self.selected_price_label.setText(price_label.text())

    def update_progress(self, values):
        # 각 프로그레스 바를 업데이트함
        for i, value in enumerate(values):
            if i < len(self.progress_bars):
                self.progress_bars[i].setValue(value)
            
            # 탱크 잔량 경고 처리
            if i < len(self.tank_warnings):
                label = self.tank_warnings[i]
                if label: # 라벨이 존재하는 경우에만
                    if value <= 10:
                        label.setText("부족")
                        label.setStyleSheet("color: red; font-weight: bold;")
                    else:
                        label.setText("")
                        label.setStyleSheet("")


       

    def closeEvent(self, event):
        if hasattr(self, 'thread_sensor'):
            self.thread_sensor.stop()
        if hasattr(self, 'thread_RFID'):
            self.thread_RFID.stop()
        self.db_manager.disconnect()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
