import serial
import time
from PyQt6.QtCore import QThread, pyqtSignal, QMutex

class SerialManager(QThread):
    rfid_detected = pyqtSignal(str)   
    status_received = pyqtSignal(str) 

    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.mutex = QMutex()
        self.latest_response = None
        self.ser = None

    def run(self):
        """스레드 실행"""
        try:
            # 1. 포트 열기 (dsrdtr=True로 아두이노 리셋 유도)
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1, dsrdtr=True)
            print(f"✅ [Serial] 포트 열기 성공: {self.port}")
            
            # 2. 아두이노 확실하게 재부팅 시키기 (DTR 신호 조작)
            self.ser.dtr = False
            time.sleep(1)
            self.ser.dtr = True
            time.sleep(2) # 부팅 완료 대기 (2초)
            
            # [🔥 핵심 수정] 연결 직후 쌓여있는 쓰레기 데이터 싹 비우기
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            
            print("✅ [Serial] 버퍼 초기화 완료 & 아두이노 준비 끝! (Ready)")
            
        except Exception as e:
            print(f"❌ [Serial] 연결 실패: {e}")
            return

        self.running = True
        
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    # 데이터 읽기
                    raw = self.ser.readline()
                    # 깨진 글자(쓰레기 값)가 있어도 무시하고 변환
                    line = raw.decode('utf-8', errors='ignore').strip()
                    
                    if not line: continue
                    
                    # [디버깅 로그]
                    print(f"📥 [Arduino]: {line}")

                    # 1. RFID UID 감지
                    if line.startswith("UID:"): 
                        uid = line.replace("UID:", "").strip()
                        self.rfid_detected.emit(uid) 
                    
                    # 2. 메시지 감지
                    elif line.startswith("MSG:"):
                        msg = line.replace("MSG:", "").strip()
                        self.status_received.emit(msg)

                    else:
                        self.mutex.lock()
                        self.latest_response = line
                        self.mutex.unlock()
                        
            except Exception as e:
                print(f"⚠️ Read Error: {e}")
                time.sleep(1)
            
            time.sleep(0.01)

    # (나머지 함수들은 그대로 유지)
    def check_cup(self):
        if not self.ser: return True
        self.send_command("C")
        for _ in range(20):
            self.mutex.lock()
            resp = self.latest_response
            self.latest_response = None
            self.mutex.unlock()
            if resp == "CUP_YES": return True
            time.sleep(0.1)
        return True 

    def pour(self, pin, amount_ml):
        if not self.ser: return
        ms_per_ml = 50 
        duration_ms = amount_ml * ms_per_ml
        cmd = f"P:{pin}:{duration_ms}"
        self.status_received.emit(f"Pouring {amount_ml}ml (Pin {pin})...")
        self.send_command(cmd)

    def send_command(self, cmd):
        if self.ser:
            self.ser.write((cmd + '\n').encode())

    def stop(self):
        self.running = False
        self.wait()
        if self.ser:
            self.ser.close()