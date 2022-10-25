from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLabel
from PyQt5.QtCore import pyqtSignal, QObject

import sys
from typing import Tuple
import pathlib


class Signals(QObject):
    process_requested = pyqtSignal(str)
    process_error = pyqtSignal(str)
    process_info = pyqtSignal(str)


# sets the QLabel text, color and adjusts it's size
def set_text(label, text, color="black") -> QLabel:
    label.setText(text)
    label.setStyleSheet(f"color: {color};")
    label.adjustSize()
    return label


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 200, 600, 300)
        self.setWindowTitle("Transcriber")

        self.signals = Signals()

        self.current_file = ""

        self.ERROR_COLOR = "red"
        self.INFO_COLOR = "green"

        self.file_opener_button = QPushButton(self)
        self.file_opener_button.setText("Open file")
        self.file_opener_button.move(50, 50)

        self.file_processor_button = QPushButton(self)
        self.file_processor_button.setText("Process file")
        self.file_processor_button.move(50, 100)

        self.opened_file_label = QLabel(self)
        self.opened_file_label.setText("No file selected...")
        self.opened_file_label.move(200, 50)

        self.info_label_first = QLabel(self)
        self.info_label_first.move(150, 150)

        self.info_label_second = QLabel(self)
        self.info_label_second.move(150, 200)

        self.info_label_third = QLabel(self)
        self.info_label_third.move(150, 250)

        self.info_labels = (self.info_label_first, self.info_label_second, self.info_label_third)

        self.file_opener_button.clicked.connect(self.open_file)
        self.file_processor_button.clicked.connect(self.process_file)

    def reset_info_labels(self):
        [info_label.setText("") for info_label in self.info_labels]

    def open_file(self):
        self.reset_info_labels()
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "QFileDialog.getOpenFileName()",
            "",
        )
        self.opened_file_label.setText(pathlib.Path(file_path).name)
        self.current_file = file_path

    def process_file(self):
        self.signals.process_requested.emit(self.current_file)

    def handle_error(self, message: str):
        self.reset_info_labels()
        set_text(self.info_label_first, message, self.ERROR_COLOR)

    def handle_info(self, message: str):
        old_message = self.info_label_first.text()
        self.reset_info_labels()
        set_text(self.info_label_first, f"{old_message}\n{message}", self.INFO_COLOR)


def create_ui() -> Tuple[QApplication, MainWindow]:
    app = QApplication(sys.argv)
    window = MainWindow()
    return app, window


def launch_ui(app, window) -> None:
    window.show()
    sys.exit(app.exec_())
