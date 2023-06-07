import whisper
import sys
from typing import Optional, Literal

# # this import is relative, because voice_backend.py is opened as subprocess
import config as CONFIG


import moviepy.editor as mp


def audio_length(file_path: str = CONFIG.AUDIO_PATH):
    duration = mp.AudioFileClip(file_path).duration
    print(f"{CONFIG.DURATION_MSG}{duration}")
    return duration


def file_to_audio(file_path: str):
    clip = mp.VideoFileClip(file_path)
    clip.audio.write_audiofile(CONFIG.AUDIO_PATH)


def transcribe_audio(
    audio_path: str,
    language: Optional[str] = None,
    task: Literal["transcribe", "translate"] = "transcribe",
):
    model: whisper.Whisper = whisper.load_model("tiny")
    decode_options: dict = {"language": language, "task": task}
    print(decode_options)
    model.transcribe(
        audio_path,
        verbose=True,
        word_timestamps=True,
        **decode_options,
    )


if __name__ == "__main__":
    if len(sys.argv) < 5:
        raise AssertionError("Expected 4 arguments: path to file, filetype, language, task")
    PATH = sys.argv[1]
    FILETYPE = sys.argv[2]
    LANGUAGE = sys.argv[3] if len(sys.argv[3]) else None
    TASK = sys.argv[4]

    if FILETYPE == "video":
        file_to_audio(PATH)
        PATH = CONFIG.AUDIO_PATH

    audio_length(PATH)
    print("TASK:", TASK, type(TASK), TASK == "translate")
    if not (TASK == "translate" or TASK == "transcribe"):
        raise AssertionError(f"Task must be 'transcribe' or 'translate', got {TASK}")
    transcribe_audio(PATH, LANGUAGE, TASK)
