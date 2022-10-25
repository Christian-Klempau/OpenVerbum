import re
from PyQt5.QtCore import QThread
from threading import Thread
import time


def startswith(starter):
    def func(string):
        if not string.strip().startswith(starter):
            return ""
        return string

    return func


def regex(regex):
    def func(string):
        match = re.match(regex, string)
        if not match:
            return ""
        return match.group(0)

    return func


FUNC_PAIRS = [
    (
        startswith("MoviePy - Writing audio in"),
        lambda _: "Extracting audio...",
    ),
    (
        startswith("MoviePy - Done"),
        lambda _: "Done extracting audio",
    ),
    (
        startswith("Detecting language:"),
        lambda _: "Detecting language...",
    ),
    (
        startswith("Detected language:"),
        lambda x: x.lower().capitalize(),
    ),
    (
        regex(r"\[[^\]]*]"),
        lambda x: f"REGEX: {x}",
    ),
]


class MyThread(Thread):
    def run(self):
        for i in range(10):
            print(i)
            time.sleep(1)


class MetaData:
    def __init__(self, signals, file_path, file_type):
        self.signals = signals
        self.file_path = file_path
        self.file_type = file_type

        self.process()

    def process(self):
        t = MyThread()
        t.start()
        # cmd = ["python", os.path.join("backend", "processor.py"), self.file_path, self.file_type]

        # p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        # while p.stdout.readable():
        #     line = p.stdout.readline()

        #     if not line:
        #         break

        #     print(line.strip())

        # p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        # for io in p.stdout:
        #     self.handle_line(io)

        print("DONE!")

    def handle_line(self, io):
        line: str = io.rstrip().decode("utf-8")

        print("-->")

        for detector, executor in FUNC_PAIRS:
            found = detector(line)
            if found:
                result = executor(found)
                print(result)
                # self.signals.process_info.emit(result)
