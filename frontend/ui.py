# PyQt5 and related
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QProgressBar,
    QSizePolicy,
)
from PyQt5.QtCore import pyqtSignal, QObject

# Material UI stylesheet
from qt_material import apply_stylesheet

# Locals
import frontend.config as CONFIG

# Other libraries
import os
import sys
from typing import Tuple
import pathlib
from shutil import copyfile


class Signals(QObject):
    # progress tracking
    process_requested = pyqtSignal(str)
    process_error = pyqtSignal(str)
    process_info = pyqtSignal(str)
    process_started = pyqtSignal()
    process_done = pyqtSignal(str)
    save_file = pyqtSignal(str)

    # progress bar
    advance_bar = pyqtSignal(int)


# sets the QLabel text, color and adjusts it's size
def set_text(label, text, color=CONFIG.COLOR_DEFAULT) -> QLabel:
    label.setText(text)
    label.setStyleSheet(f"color: {color};")
    label.adjustSize()
    label.setScaledContents(True)
    return label


class TEXT:
    # buttons and it's labels
    NO_FILE_SELECTED = "No file selected..."
    OPEN_FILE_BUTTON = "Select file"
    PROCESS_FILE_BUTTON = "Process file"

    # info texts during processing
    INFO_DONE = "Done!"
    INFO_PROCESSING = "Processing..."

    # Downloading transcription
    DOWNLOAD_BUTTON = "Download ⬇"


def get_info_button_style(primary_color, secondary_color):
    return (
        "QPushButton"
        "{"
        f"color: {primary_color};"
        f"border-color: {primary_color};"
        "}"
        "QPushButton::hover"
        "{"
        f"background-color: {primary_color};"
        "color: white;"
        "}"
        "QPushButton::disabled"
        "{"
        f"color: {secondary_color};"
        f"border-color: {secondary_color};"
        "};"
    )


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 200, 600, 300)
        self.setWindowTitle(CONFIG.WINDOW_TITLE)

        self.signals = Signals()

        self.current_file = ""
        self.transcription_path = ""

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setGeometry(200, 110, 250, 20)

        self.file_opener_button = QPushButton(self)
        self.file_opener_button.move(55, 50)
        self.file_opener_button.setText(TEXT.OPEN_FILE_BUTTON)

        self.file_processor_button = QPushButton(self)
        self.file_processor_button.move(50, 100)
        self.file_processor_button.setEnabled(False)
        self.file_processor_button.setText(TEXT.PROCESS_FILE_BUTTON)

        self.download_button = QPushButton(self)
        self.download_button.move(230, 227)
        self.download_button.setEnabled(False)
        self.download_button.setStyleSheet(
            get_info_button_style(CONFIG.COLOR_INFO, os.environ["QTMATERIAL_SECONDARYLIGHTCOLOR"])
        )
        self.download_button.setText(TEXT.DOWNLOAD_BUTTON)

        self.progress_label = QLabel(self)
        self.progress_label.move(320, 112)

        self.opened_file_label = QLabel(self)
        self.opened_file_label.move(200, 60)
        set_text(self.opened_file_label, TEXT.NO_FILE_SELECTED)

        self.info_label = QLabel(self)
        self.info_label.move(150, 150)

        self.file_opener_button.clicked.connect(self.open_file)
        self.file_processor_button.clicked.connect(self.process_file)
        self.download_button.clicked.connect(self.save_file)

        self.reset_labels()

    def fake_process(self):
        # For debugging, so you dont have to pick a file everytime
        self.signals.process_requested.emit("media/audio2.mp3")

    def reset_labels(self):
        # resets the information labels and the progress bar
        set_text(self.progress_label, "")
        [set_text(info_label, "") for info_label in (self.info_label,)]

    def block_buttons(self):
        # blocks opening and processing buttons
        self.file_opener_button.setEnabled(False)
        self.file_processor_button.setEnabled(False)
        self.download_button.setEnabled(False)

    def unblock_buttons(self):
        # Unblocks opening and processing buttons
        self.file_opener_button.setEnabled(True)
        self.file_processor_button.setEnabled(True)
        self.download_button.setEnabled(True)

    def open_file(self):
        # OS file opener handler, sets filename label and saves filepath if valid
        self.file_processor_button.setEnabled(False)
        self.reset_labels()
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select File",
            "",
        )
        if not file_path:
            set_text(self.opened_file_label, TEXT.NO_FILE_SELECTED)
            self.file_processor_button.setEnabled(False)
            return

        self.file_processor_button.setEnabled(True)
        set_text(self.opened_file_label, self._get_file_name_and_ext(file_path))
        self.current_file = file_path

    def _get_file_name_and_ext(self, file_path: str) -> str:
        # returns the filename with extension from the filepath
        return pathlib.Path(file_path).name

    def _get_file_name_alone(self, file_path: str) -> str:
        # returns the filename from the filepath
        return pathlib.Path(file_path).stem

    def save_file(self):
        save_file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            self._get_file_name_alone(self.current_file) + ".txt",
            "Text Files (*.txt)",
        )
        if not save_file_path:
            return

        if "." not in save_file_path and not save_file_path.endswith(".txt"):
            save_file_path += ".txt"

        copyfile(self.transcription_path, save_file_path)

    def process_file(self):
        # Handles the click of "process" button
        self.reset_labels()
        self.signals.process_requested.emit(self.current_file)

    def handle_error(self, message: str):
        # Handles an error recieved from backend. Resets labels and sets the error message
        self.file_processor_button.setEnabled(False)
        self.reset_labels()
        set_text(self.info_label, f"❎ {message}", CONFIG.COLOR_ERROR)

    def handle_info(self, message: str):
        # Adds a new line to the information label (green info lines)
        if not message:
            return

        old_message = self.info_label.text()
        self.reset_labels()
        set_text(self.info_label, f"{old_message}\n☑ {message}", CONFIG.COLOR_INFO)

    def advance_bar(self, value: int):
        # When called from backend, it updates the progress bar
        self.progress_bar.setValue(value)
        set_text(self.progress_label, f"{value}%")

    def start_process(self):
        # What happens when the backend starts a processing task
        self.handle_info(TEXT.INFO_PROCESSING)
        self.block_buttons()
        self.progress_bar.setValue(0)

    def finish_process(self, transcription_path: str):
        # What happens when the backend finishes a processing task
        self.transcription_path = transcription_path
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
