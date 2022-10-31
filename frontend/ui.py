# PyQt5 and related
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLabel, QProgressBar
from PyQt5.QtCore import pyqtSignal, QObject

from qt_material import apply_stylesheet

# Locals
import frontend.config as CONFIG

# Other libraries
import sys
from typing import Tuple
import pathlib


class Signals(QObject):
    # progress tracking
    process_requested = pyqtSignal(str)
    process_error = pyqtSignal(str)
    process_info = pyqtSignal(str)
    process_started = pyqtSignal()
    process_done = pyqtSignal()

    # progress bar
    advance_bar = pyqtSignal(int)


# sets the QLabel text, color and adjusts it's size
def set_text(label, text, color=CONFIG.COLOR_DEFAULT) -> QLabel:
    label.setText(text)
    label.setStyleSheet(f"color: {color};")
    label.adjustSize()
    return label


class TEXT:
    # buttons and it's labels
    NO_FILE_SELECTED = "No file selected..."
    OPEN_FILE_BUTTON = "Open file"
    PROCESS_FILE_BUTTON = "Process file"

    # info texts during processing
    INFO_DONE = "Done!"
    INFO_PROCESSING = "Processing..."


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 200, 600, 300)
        self.setWindowTitle(CONFIG.WINDOW_TITLE)

        self.signals = Signals()

        self.current_file = ""

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setGeometry(200, 110, 250, 20)

        self.file_opener_button = QPushButton(self)
        self.file_opener_button.move(60, 50)
        self.file_opener_button.setText(TEXT.OPEN_FILE_BUTTON)

        self.file_processor_button = QPushButton(self)
        self.file_processor_button.move(50, 100)
        self.file_processor_button.setEnabled(False)
        self.file_processor_button.setText(TEXT.PROCESS_FILE_BUTTON)

        self.progress_label = QLabel(self)
        self.progress_label.move(320, 112)

        self.opened_file_label = QLabel(self)
        self.opened_file_label.move(200, 60)
        set_text(self.opened_file_label, TEXT.NO_FILE_SELECTED)

        self.info_label = QLabel(self)
        self.info_label.move(150, 150)

        self.file_opener_button.clicked.connect(self.open_file)
        self.file_processor_button.clicked.connect(self.process_file)

        self.reset_labels()

    def fake_process(self):  # TODO: REMOVE THIS
        self.signals.process_requested.emit("media/audio2.mp3")

    def reset_labels(self):
        set_text(self.progress_label, "")
        [set_text(info_label, "") for info_label in (self.info_label,)]

    def block_buttons(self):
        self.file_opener_button.setEnabled(False)
        self.file_processor_button.setEnabled(False)

    def unblock_buttons(self):
        self.file_opener_button.setEnabled(True)
        self.file_processor_button.setEnabled(True)

    def open_file(self):
        self.file_processor_button.setEnabled(False)
        self.reset_labels()
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "QFileDialog.getOpenFileName()",
            "",
        )
        if not file_path:
            set_text(self.opened_file_label, TEXT.NO_FILE_SELECTED)
            self.file_processor_button.setEnabled(False)
            return

        self.file_processor_button.setEnabled(True)
        self.opened_file_label.setText(pathlib.Path(file_path).name)
        self.current_file = file_path

    def process_file(self):
        self.signals.process_requested.emit(self.current_file)

    def handle_error(self, message: str):
        self.file_processor_button.setEnabled(False)
        self.reset_labels()
        set_text(self.info_label, f"❎ {message}", CONFIG.COLOR_ERROR)

    def handle_info(self, message: str):
        if not message:
            return

        old_message = self.info_label.text()
        self.reset_labels()
        set_text(self.info_label, f"{old_message}\n☑ {message}", CONFIG.COLOR_INFO)

    def advance_bar(self, value: int):
        self.progress_bar.setValue(value)
        set_text(self.progress_label, f"{value}%")

    def start_process(self):
        self.handle_info(TEXT.INFO_PROCESSING)
        self.block_buttons()
        self.progress_bar.setValue(0)

    def finish_process(self):
        self.handle_info(TEXT.INFO_DONE)
        self.unblock_buttons()
        self.progress_bar.setValue(100)


def create_ui() -> Tuple[QApplication, MainWindow]:
    app = QApplication(sys.argv)

    apply_stylesheet(app, theme="dark_purple.xml")

    window = MainWindow()
    return app, window


def launch_ui(app, window) -> None:
    window.show()
    sys.exit(app.exec_())
