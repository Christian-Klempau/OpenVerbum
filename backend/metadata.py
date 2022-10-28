import re
from threading import Thread
import subprocess
import os
from .config import DURATION_MSG
from typing import Callable


CLIP_DURATION: float = 0


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


class MetaData(Thread):
    def __init__(self, signals, file_path, file_type):
        super().__init__(daemon=True)
        self.signals = signals
        self.file_path = file_path
        self.file_type = file_type

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
                DURATION_MSG,
                lambda x: clip_duration_setter(float(x.split(":")[1].strip())),
                self.signals.process_info,
            ),
        )

    def run(self):

        cmd = [
            "python",
            "-u",
            os.path.join("backend", "processor.py"),
            self.file_path,
            self.file_type,
        ]

        self.signals.process_started.emit()

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        for io in p.stdout:
            self.handle_line(io)

        self.signals.process_done.emit()

    def handle_line(self, io):
        line: str = io.rstrip().decode("utf-8")

        for processor in self.processors:
            processor(line)

        progress_made = progress(line)
        if progress_made:
            my_progress = int(progress_made / CLIP_DURATION * 100)
            self.signals.advance_bar.emit(my_progress)
