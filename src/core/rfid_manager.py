import time
import serial
from PyQt6.QtCore import QThread, pyqtSignal

class RfidThread(QThread):
    rfid_detected = pyqtSignal(str)

    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.ser = None

    def run(self):
        """RFID 전용 시리얼 스레드"""
        try:
            self.ser = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1,
                dsrdtr=True  # 자동 리셋
            )
            print(f"✅ Serial Open: {self.port}")

            # 아두이노 리셋을 위한 DTR 조작
            self.ser.dtr = False
            time.sleep(1)
            self.ser.dtr = True
            time.sleep(2)

            # 연결 직후 쓰레기 데이터 제거
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

            print("✅ Ready. Waiting for RFID...\n")

        except Exception as e:
            print(f"❌ Serial connection failed: {e}")
            return

        self.running = True

        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    raw = self.ser.readline()
                    line = raw.decode("utf-8", errors="ignore").strip()

                    if not line:
                        continue

                    print(f"📥 [Arduino] {line}")

                    # ====== RFID UID 감지 ======
                    if line.startswith("UID:"):
                        uid = line.replace("UID:", "").strip()
                        self.rfid_detected.emit(uid)

            except Exception as e:
                print(f"⚠️ Read Error: {e}")
                time.sleep(0.1)

            time.sleep(0.01)

    def stop(self):
        self.running = False
        self.wait()
        if self.ser:
            self.ser.close()
            print("🔌 Serial Closed")
