from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLabel, QProgressBar
from PyQt5.QtCore import pyqtSignal, QObject

import sys
from typing import Tuple
import pathlib


class Signals(QObject):
    process_requested = pyqtSignal(str)
    process_error = pyqtSignal(str)
    process_info = pyqtSignal(str)
    process_done = pyqtSignal()
    advance_bar = pyqtSignal(int)


# sets the QLabel text, color and adjusts it's size
def set_text(label, text, color="black") -> QLabel:
    label.setText(text)
    label.setStyleSheet(f"color: {color};")
    label.adjustSize()
    return label


class TEXT:
    NO_FILE_SELECTED = "No file selected..."


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 200, 600, 300)
        self.setWindowTitle("Transcriber")

        self.signals = Signals()

        self.current_file = ""

        self.ERROR_COLOR = "red"
        self.INFO_COLOR = "green"

        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setGeometry(200, 105, 250, 20)

        self.file_opener_button = QPushButton(self)
        self.file_opener_button.setText("Open file")
        self.file_opener_button.move(50, 50)

        self.file_processor_button = QPushButton(self)
        self.file_processor_button.setText("Process file")
        self.file_processor_button.move(50, 100)

        self.opened_file_label = QLabel(self)
        self.opened_file_label.setText(TEXT.NO_FILE_SELECTED)
        self.opened_file_label.move(200, 50)

        self.info_label_first = QLabel(self)
        self.info_label_first.move(150, 150)

        self.info_labels = (self.info_label_first,)

        self.file_opener_button.clicked.connect(self.open_file)
        self.file_processor_button.clicked.connect(self.process_file)

    def reset_info_labels(self):
        [info_label.setText("") for info_label in self.info_labels]

    def open_file(self):
        self.reset_info_labels()
        self.opened_file_label.setText(TEXT.NO_FILE_SELECTED)
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
        if not message:
            return

        old_message = self.info_label_first.text()
        self.reset_info_labels()
        set_text(self.info_label_first, f"{old_message}\n{message}", self.INFO_COLOR)

    def advance_bar(self, value: int):
        print("ACA", value)
        self.progress.setValue(value)


def create_ui() -> Tuple[QApplication, MainWindow]:
    app = QApplication(sys.argv)
    window = MainWindow()
    return app, window


def launch_ui(app, window) -> None:
    window.show()
    sys.exit(app.exec_())
