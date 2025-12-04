import time
from PyQt6.QtCore import QThread, pyqtSignal
from utils.get_serial import SerialReader

class SerialThread(QThread):
    progress_update = pyqtSignal(list)

    def __init__(self, port, baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.reader = None

    def run(self):
        self.reader = SerialReader(self.port, self.baudrate)
        
        while self.running:
            line = self.reader.read_line()
            if line:
                try:
                    # 공백으로 라인을 분리함
                    parts = line.split()
                    # 6개의 값을 예상함
                    if len(parts) == 6:
                        values = []
                        for i in range(6):
                            values.append(int(parts[i]))
                        self.progress_update.emit(values)
                except ValueError:
                    print(f"Invalid data received: {line}")
            time.sleep(0.01)
            

        self.reader.close()

    def stop(self):
        self.running = False
        self.wait()

class PumpSerialThread(QThread):
    progress_update = pyqtSignal(str) # Log messages

    def __init__(self, port, baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.reader = None

    def run(self):
        self.reader = SerialReader(self.port, self.baudrate)
        
        while self.running:
            line = self.reader.read_line()
            if line:
                self.progress_update.emit(f"[PUMP] {line}")
            time.sleep(0.01)

        self.reader.close()

    def send_command(self, command):
        if self.reader:
            self.reader.write(command + '\n')

    def stop(self):
        self.running = False
        self.wait()
