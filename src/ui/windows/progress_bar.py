import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QProgressBar, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from get_serial import SerialReader

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
                    # Split the line by whitespace
                    parts = line.split()
                    # We expect at least 6 values
                    if len(parts) >= 6:
                        values = []
                        for i in range(6):
                            values.append(int(parts[i]))
                        self.progress_update.emit(values)
                    else:
                        print(f"Insufficient data: {line}")
                except ValueError:
                    print(f"Invalid data received: {line}")
            time.sleep(0.01)

        self.reader.close()

    def stop(self):
        self.running = False
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino Serial Progress Bar (6 Channels)")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.label = QLabel("Waiting for data...")
        self.main_layout.addWidget(self.label)

        # Horizontal layout for progress bars
        self.bars_layout = QHBoxLayout()
        self.main_layout.addLayout(self.bars_layout)

        self.progress_bars = []
        for i in range(6):
            bar = QProgressBar()
            bar.setOrientation(Qt.Orientation.Vertical)
            bar.setRange(0, 100) # Adjust range if needed (e.g., 0-1023 for analogRead)
            bar.setValue(0)
            self.bars_layout.addWidget(bar)
            self.progress_bars.append(bar)

        # Serial Thread Configuration
        # Replace '/dev/ttyUSB0' with your actual port
        self.port = '/dev/ttyUSB0' 
        self.thread = SerialThread(self.port)
        self.thread.progress_update.connect(self.update_progress)
        self.thread.start()

    def update_progress(self, values):
        # Update label with all values
        self.label.setText(f"Values: {values}")
        
        # Update each progress bar
        for i, value in enumerate(values):
            if i < len(self.progress_bars):
                # Ensure value is within range
                # If your values are 0-1023, you might want to map them to 0-100
                # or change the range of the progress bar.
                # For now, assuming 0-100 or clamping.
                # clamped_value = max(0, min(100, value)) 
                self.progress_bars[i].setValue(value)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
