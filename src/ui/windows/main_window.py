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
from core.rfid_manager import RfidThread
from core.cocktaildb import DatabaseManager

class MainWindow(QDialog):
    # State Constants
    STATE_IDLE = "대기 중"
    STATE_WAITING_TAG = "태그 대기"
    STATE_PAYMENT_WAIT = "결제 대기"
    STATE_MAKING = "제조 중"
    STATE_DONE = "제조 완료"

    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
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
        # Serial Thread Configuration
        # self.port_sensor = '/dev/ttyUSB0' # Make sure this matches your setup
        # self.thread_sensor = SerialThread(self.port_sensor)
        # self.thread_sensor.progress_update.connect(self.update_progress)
        # self.thread_sensor.start()


        # self.port_pump = '/dev/ttyUSB1' # Make sure this matches your setup
        # self.thread_pump = SerialThread(self.port_pump)
        # self.thread_pump.progress_update.connect(self.update_progress)
        # self.thread_pump.start()

        self.port_RFID = '/dev/ttyACM0' # 설정과 일치하는지 확인해야 함
        self.thread_RFID = RfidThread(self.port_RFID)
        self.thread_RFID.rfid_detected.connect(self.handle_rfid_reading)
        self.thread_RFID.start()

        # 초기 상태 설정
        self.current_state = self.STATE_IDLE
        self.update_status(self.STATE_IDLE)

        # RFID 중복 방지 변수
        self.last_rfid_time = 0
        self.last_rfid_tag = None

    def update_status(self, state):
        self.current_state = state
        status_label = self.findChild(QLabel, "status")
        if status_label:
            status_label.setText(state)
            
            # 상태에 따른 스타일 변경 (선택 사항)
            if state == self.STATE_IDLE:
                status_label.setStyleSheet("color: black;")
            elif state == self.STATE_MAKING:
                status_label.setStyleSheet("color: blue; font-weight: bold;")
            elif state == self.STATE_DONE:
                status_label.setStyleSheet("color: green; font-weight: bold;")

    def handle_rfid_reading(self, rfid_tag):
        import time
        current_time = time.time()
        
        # 2초 내에 같은 태그가 들어오면 무시 (Debounce)
        if rfid_tag == self.last_rfid_tag and (current_time - self.last_rfid_time) < 2.0:
            return

        self.last_rfid_tag = rfid_tag
        self.last_rfid_time = current_time

        print(f"RFID Detected: {rfid_tag}")
        
        # 이전 결과를 지움
        self.list_model.clear()
        
        # 1. 상태 확인 (칵테일이 선택되었는지)
        # STATE_WAITING_TAG 상태에서만 RFID 인식 처리
        if self.current_state != self.STATE_WAITING_TAG:
             # 대기 중이거나 이미 결제 진행 중이면 무시
             return

        # 2. 상태 변경: 결제 대기 (이 상태에서는 추가 태그 인식 안됨)
        self.update_status(self.STATE_PAYMENT_WAIT)

        # 3. 사용자 조회
        query_user = "SELECT * FROM users WHERE rfid_uid = %s"
        users = self.db_manager.fetch_query(query_user, (rfid_tag,))
        
        if not users:
            self.list_model.appendRow(QStandardItem("User not found"))
            QMessageBox.warning(self, '오류', '등록되지 않은 사용자입니다.')
            self.reset_to_idle() # 등록되지 않은 경우 초기화
            return

        user = users[0]
        user_balance = user.get('point_balance', 0) 
        user_name = user.get('user_name', 'Unknown')

        # 'label_5' 업데이트 (사용자 이름 및 잔액 표시)
        user_info_label = self.findChild(QLabel, "label_5")
        if user_info_label:
            user_info_label.setText(f"{user_name}님 | 잔액: {user_balance}원")

        # 4. 선택된 칵테일 가격 확인
        price_text = self.selected_price_label.text()
        if not price_text or "원" not in price_text:
             self.reset_to_idle()
             return

        try:
            cocktail_price = int(price_text.replace("원", "").strip())
        except ValueError:
             self.list_model.appendRow(QStandardItem("Invalid price format."))
             self.reset_to_idle()
             return

        # 5. 결제 확인 팝업
        reply = QMessageBox.question(self, '결제 확인', 
                                     f"{user_name}님, {cocktail_price}원을 결제하시겠습니까?\n현재 잔액: {user_balance}원",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # 6. 잔액 확인 및 결제
            if user_balance >= cocktail_price:
                new_balance = user_balance - cocktail_price
                
                # DB 업데이트
                update_query = "UPDATE users SET point_balance = %s WHERE rfid_uid = %s"
                self.db_manager.execute_query(update_query, (new_balance, rfid_tag))
                
                # UI 업데이트
                self.list_model.appendRow(QStandardItem(f"Payment Success!"))
                self.list_model.appendRow(QStandardItem(f"User: {user_name}"))
                self.list_model.appendRow(QStandardItem(f"Paid: {cocktail_price}원"))
                self.list_model.appendRow(QStandardItem(f"Remaining Balance: {new_balance}원"))
                
                # 'label_5' 업데이트 (결제 후 잔액)
                if user_info_label:
                    user_info_label.setText(f"{user_name}님 | 잔액: {new_balance}원")
                
                # 결제 성공 팝업
                QMessageBox.information(self, '결제 완료', f"결제가 완료되었습니다.\n남은 잔액: {new_balance}원")

                # 제조 시작
                self.start_making_process()
            else:
                self.list_model.appendRow(QStandardItem("Insufficient Funds!"))
                QMessageBox.warning(self, '잔액 부족', f"잔액이 부족합니다.\n현재 잔액: {user_balance}원\n필요 금액: {cocktail_price}원")
                self.reset_to_idle() # 잔액 부족 시 초기화
        else:
            self.list_model.appendRow(QStandardItem("Payment Cancelled"))
            self.reset_to_idle() # 취소 시 초기화

    def start_making_process(self):
        """칵테일 제조 프로세스 시뮬레이션"""
        self.update_status(self.STATE_MAKING)
        
        # 실제 펌프 제어 로직이 들어갈 곳
        # 여기서는 간단히 타이머를 사용하여 제조 완료를 시뮬레이션함
        # QTimer.singleShot을 사용하여 UI 스레드를 차단하지 않음
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, self.finish_making_process) # 3초 후 완료

    def finish_making_process(self):
        self.update_status(self.STATE_DONE)
        QMessageBox.information(self, '제조 완료', '칵테일 제조가 완료되었습니다! 맛있게 드세요.')
        
        # 잠시 후 대기 상태로 복귀
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.reset_to_idle)

    def reset_to_idle(self):
        self.update_status(self.STATE_IDLE)
        # 선택된 칵테일 정보 초기화 등 필요 시 추가
        if self.selected_cocktail_label:
            self.selected_cocktail_label.setText("-")
        if self.selected_price_label:
            self.selected_price_label.setText("-")
        
        # label_5 초기화 (원래 문구로 복구)
        user_info_label = self.findChild(QLabel, "label_5")
        if user_info_label:
            user_info_label.setText("카드를 터치하여 결제를 진행하세요")

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
            
        # 상태 업데이트: 태그 대기
        self.update_status(self.STATE_WAITING_TAG)

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
