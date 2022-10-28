import whisper
import sys

# # this import is relative, because processor.py is opened as subprocess
from config import AUDIO_PATH, DURATION_MSG

PATH = sys.argv[1]
FILETYPE = sys.argv[2]


import moviepy.editor as mp


def audio_length(file_path: str = AUDIO_PATH):
    duration = mp.AudioFileClip(file_path).duration
    print(f"{DURATION_MSG}{duration}")
    return duration


def file_to_audio(file_path: str):
    clip = mp.VideoFileClip(file_path)
    clip.audio.write_audiofile(AUDIO_PATH)


def transcribe_audio(audio_path: str):
    model = whisper.load_model("tiny")
    model.transcribe(audio_path, verbose=True)


if FILETYPE == "video":
    file_to_audio(PATH)
    PATH = AUDIO_PATH

audio_length(PATH)
transcribe_audio(PATH)
sys.exit(0)
