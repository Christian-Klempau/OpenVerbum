# Locals
import os
import re
import subprocess
from threading import Thread
from typing import Callable, Literal
import sys

# Backend
import backend.config as CONFIG
from backend.utils import find_file_type, is_media_file

CLIP_DURATION: float = 0

VERBOSE = True


def is_build() -> bool:
    """
    NOTE: Returns True if inside PyInstaller executable, else False
    We need this because PyInstaller creates a temp folder and stores path in _MEIPASS
    In that temp folder lives the voice_backend.py file and utils.py file
    Normally (running as script, not as build), we just import it from backend/voice_backend.py
    """
    return hasattr(sys, "_MEIPASS")


# https://stackoverflow.com/questions/56564441/best-way-to-call-subprocess-scripts-in-a-python-exe
def resource_path(relative_path):
    # sys._MEIPASS is the temp folder where PyInstaller stores the files
    # when running as build, not as script
    if is_build():
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def clip_duration_setter(value: float):
    global CLIP_DURATION
    CLIP_DURATION = value
    return ""


def process_startswith(starter: str, parser: Callable, signal):
    def func(msg):
        if not msg.strip().startswith(starter):
            return

        parsed_msg = parser(msg)
        signal.emit(parsed_msg)

    return func


def progress(string) -> int:
    match = re.match(r"\[[^\]]*]", string)
    if not match:
        return 0

    string = match.group(0)
    # strings look like this: [00:03.500 --> 00:04.500]
    # we want only the second time (00:04.500)
    # and convert it to seconds (60 * minutes + seconds, ignoring the ms)
    remove = ("[", "]", "-->")
    for char in remove:
        string = string.replace(char, "")
    string.strip()
    string = string.split("  ")[1]

    def format_to_seconds(time):
        hours, seconds = time.split(":")
        seconds = seconds.split(".")[0]
        return 60 * int(hours) + int(seconds)

    return format_to_seconds(string)


class VoiceProcessor:
    def __init__(self, signals):
        self.signals = signals

        self.processors = (
            process_startswith(
                "MoviePy - Writing audio in",
                lambda _: "Extracting audio...",
                self.signals.process_info,
            ),
            process_startswith(
                "Detecting language:",
                lambda _: "Detecting language...",
                self.signals.process_info,
            ),
            process_startswith(
                "Detected language:",
                lambda x: x.lower().capitalize(),
                self.signals.process_info,
            ),
            process_startswith(
                CONFIG.DURATION_MSG,
                lambda x: clip_duration_setter(float(x.split(":")[1].strip())),
                self.signals.process_info,
            ),
        )

    def process_file(
        self, file_path: str, language: str | None, task: Literal["transcribe", "translate"]
    ) -> None:
        file_type = find_file_type(file_path)

        if not is_media_file(file_path):
            self.signals.process_error.emit(
                f"File not supported (use {', '.join(CONFIG.ACCEPTED_FILE_TYPES)} files)"
            )
            return

        transcription_task = Thread(
            target=self.run, daemon=True, args=(file_path, file_type, language, task)
        )
        transcription_task.start()

    def run(
        self,
        file_path: str,
        file_type: str,
        language: str | None,
        task: Literal["transcribe", "translate"],
    ) -> None:
        # See the note at is_build()
        voice_backend_path = (
            resource_path("voice_backend.py")
            if is_build()
            else os.path.join("backend", "voice_backend.py")
        )
        cmd = [
            "python",
            "-u",
            voice_backend_path,
            file_path,
            file_type,
            language,
            task,
        ]

        self.signals.process_started.emit()

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        with open(CONFIG.OUTPUT_FILE, "w") as output_file:
            for line in p.stdout:
                if VERBOSE:
                    print(line.decode("utf-8").rstrip())
                self.handle_line(output_file, line)

        self.signals.process_done.emit(CONFIG.OUTPUT_FILE)

    def handle_line(self, output_file, line):
        line: str = line.rstrip().decode("utf-8")

        for processor in self.processors:
            processor(line)

        progress_made = progress(line)
        if progress_made:
            self.write_transcript(output_file, line)
            my_progress = int(progress_made / CLIP_DURATION * 100)
            self.signals.advance_bar.emit(my_progress)

    def write_transcript(self, output_file, line: str):
        line = line.split("]")[1].strip()
        output_file.write(line + "\n")
