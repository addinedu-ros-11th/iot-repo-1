import os
import sys

# Add src to path to allow imports when running directly
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '../../'))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from PyQt6.QtWidgets import QDialog, QApplication
from PyQt6 import uic
from core.serial_manager import SerialThread

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        # Load the UI file
        ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cocktail_GUI.ui'))
        uic.loadUi(ui_path, self)

        # List of progress bars in the UI
        self.progress_bars = [
            self.progressBar,
            self.progressBar_2,
            self.progressBar_3,
            self.progressBar_4,
            self.progressBar_5,
            self.progressBar_6
        ]

        # Initialize progress bars
        for bar in self.progress_bars:
            bar.setRange(0, 100)
            bar.setValue(0)

        # Serial Thread Configuration
        self.port = '/dev/ttyUSB0' # Make sure this matches your setup
        self.thread = SerialThread(self.port)
        self.thread.progress_update.connect(self.update_progress)
        self.thread.start()

    def update_progress(self, values):
        # Update each progress bar
        for i, value in enumerate(values):
            if i < len(self.progress_bars):
                self.progress_bars[i].setValue(value)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
