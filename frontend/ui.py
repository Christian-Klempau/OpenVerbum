# PyQt6 and related
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QProgressBar,
    QRadioButton,
    QComboBox,
    QCheckBox,
)
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QIcon

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
from enum import Enum, auto


class Task(Enum):
    TRANSCRIBE = auto()
    TRANSLATE = auto()


# Just used for typing
class G_CONFIG:
    LANGUAGES: list[str]


class TEXT:
    # File input
    SELECT_FILE_LABEL = "Select file"
    # buttons and it's labels
    NO_FILE_SELECTED = "No file selected..."
    OPEN_FILE_BUTTON = "Select file"
    PROCESS_FILE_BUTTON = "Process file"

    # info texts during processing
    INFO_DONE = "Done!"
    INFO_PROCESSING = "Processing..."

    # Downloading transcription
    DOWNLOAD_BUTTON = "Download ⬇"

    # Radio buttons
    TRANSCRIBE_RADIO = "X voice --> X text"
    TRANSLATE_RADIO = "X voice --> English text"

    # Language
    LANGUAGE_LABEL = "Choose language:"
    LANGUAGE_DEFAULT = "Spanish"
    AUTO_LANGUAGE = "automatic"
    LANGUAGE_ENGLISH = "English"

    # Task
    IS_TRANSLATE = "Translate"
    IS_TRANSCRIBE = "Transcribe"


class Signals(QObject):
    # progress tracking
    process_requested = pyqtSignal(str, str, str)
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
    def __init__(self, G_CONFIG: G_CONFIG):
        super().__init__()
        self.setGeometry(500, 200, 540, 450)
        self.setWindowTitle(CONFIG.WINDOW_TITLE)
        self.setWindowIcon(QIcon(CONFIG.WINDOW_ICON))
        self.G_CONFIG = G_CONFIG
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
        self.download_button.move(195, 350)
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
        self.info_label.move(150, 215)

        self.file_opener_button.clicked.connect(self.open_file)
        self.file_processor_button.clicked.connect(self.process_file)
        self.download_button.clicked.connect(self.save_file)

        self.transcribe_radio = QRadioButton(self)
        self.transcribe_radio.setText(TEXT.TRANSCRIBE_RADIO)
        self.transcribe_radio.move(50, 150)

        self.translate_radio = QRadioButton(self)
        self.translate_radio.setText(TEXT.TRANSLATE_RADIO)
        self.translate_radio.move(50, 180)

        self.choose_language_checkbox = QCheckBox(self)
        self.choose_language_checkbox.setText(TEXT.LANGUAGE_LABEL)
        self.choose_language_checkbox.move(300, 150)
        self.choose_language_checkbox.clicked.connect(self.handle_language_checkbox)

        self.translate_combo = QComboBox(self)
        self.translate_combo.move(300, 180)
        self.translate_combo.addItems(self.G_CONFIG.LANGUAGES)
        self.translate_combo.setEditable(True)
        self.translate_combo.setCurrentText(TEXT.LANGUAGE_DEFAULT)
        # self.translate_combo.setInsertPolicy(QComboBox.NoInsert)
        self.translate_combo.activated.connect(self.update_task_info)
        [
            widget.clicked.connect(self.update_task_info)
            for widget in [
                self.transcribe_radio,
                self.translate_radio,
                self.choose_language_checkbox,
            ]
        ]

        self.reset_labels()

    def update_task_info(self):
        current_task = self.get_current_task()

        is_specific_language = self.choose_language_checkbox.isChecked()

        origin_lang = (
            self.translate_combo.currentText() if is_specific_language else TEXT.AUTO_LANGUAGE
        )
        dest_lang = (
            TEXT.LANGUAGE_ENGLISH
            if current_task == Task.TRANSLATE
            else (
                self.translate_combo.currentText() if is_specific_language else TEXT.AUTO_LANGUAGE
            )
        )

        task = TEXT.IS_TRANSCRIBE if current_task == Task.TRANSCRIBE else TEXT.IS_TRANSLATE

        msg = f"{task}: {origin_lang} --> {dest_lang}"
        self.handle_info(msg, reset_other_labels=False, append_new_line=False)

    def handle_language_checkbox(self):
        lang_is_checked = self.choose_language_checkbox.isChecked()
        self.translate_combo.setEnabled(lang_is_checked)

    def fake_process(self):
        # For debugging, so you dont have to pick a file everytime
        self.signals.process_requested.emit("media/audio2.mp3")

    def reset_labels(self):
        # Resets the information labels and the progress bar
        set_text(self.progress_label, "")
        set_text(self.info_label, "")

        #
        self.update_task_info()

        # Resets the radio buttons
        self.translate_combo.setEnabled(False)
        self.choose_language_checkbox.setChecked(False)
        self.transcribe_radio.setChecked(True)

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
            TEXT.SELECT_FILE_LABEL,
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

    def get_current_task(self) -> Task:
        is_transcribe = self.transcribe_radio.isChecked()
        # For initial state or after reset_labels(), no box is checked so we have Transcribe
        is_transcribe = is_transcribe or not self.translate_radio.isChecked()

        if is_transcribe:
            return Task.TRANSCRIBE

        return Task.TRANSLATE

    def get_current_language(self) -> str | None:
        is_auto = not self.choose_language_checkbox.isChecked()
        curr_lang = self.translate_combo.currentText()

        return curr_lang if not is_auto else None

    def process_file(self):
        # Handles the click of "process" button
        self.signals.process_requested.emit(
            self.current_file,
            self.get_current_language(),
            self.get_current_task().name.lower(),
        )
        self.reset_labels()

    def handle_error(self, message: str):
        # Handles an error recieved from backend. Resets labels and sets the error message
        self.file_processor_button.setEnabled(False)
        self.reset_labels()
        set_text(self.info_label, f"❎ {message}", CONFIG.COLOR_ERROR)

    def handle_info(
        self, message: str, reset_other_labels: bool = True, append_new_line: bool = True
    ):
        # Adds a new line to the information label (green info lines)
        if not message:
            return

        old_message = self.info_label.text()
        if reset_other_labels:
            self.reset_labels()

        if append_new_line:
            msg = f"{old_message}\n☑ {message}"
        else:
            msg = f"\n☑ {message}"

        set_text(self.info_label, msg, CONFIG.COLOR_INFO)

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


def create_ui(G_CONFIG) -> Tuple[QApplication, MainWindow]:
    app = QApplication(sys.argv)

    apply_stylesheet(app, theme="dark_purple.xml")

    window = MainWindow(G_CONFIG)

    return app, window


def launch_ui(app, window) -> None:
    window.show()
    sys.exit(app.exec())
