import whisper
import sys

# # this import is relative, because processor.py is opened as subprocess
import config as CONFIG

PATH = sys.argv[1]
FILETYPE = sys.argv[2]


import moviepy.editor as mp


def audio_length(file_path: str = CONFIG.AUDIO_PATH):
    duration = mp.AudioFileClip(file_path).duration
    print(f"{CONFIG.DURATION_MSG}{duration}")
    return duration


def file_to_audio(file_path: str):
    clip = mp.VideoFileClip(file_path)
    clip.audio.write_audiofile(CONFIG.AUDIO_PATH)


def transcribe_audio(audio_path: str):
    model = whisper.load_model("tiny")
    model.transcribe(audio_path, verbose=True)


if FILETYPE == "video":
    file_to_audio(PATH)
    PATH = CONFIG.AUDIO_PATH

audio_length(PATH)
transcribe_audio(PATH)
sys.exit(0)
