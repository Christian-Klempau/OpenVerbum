import whisper
import moviepy.editor as mp
import sys

# this import is relative, because processor.py is opened as subprocess
from config import AUDIO_PATH

PATH = sys.argv[1]
FILETYPE = sys.argv[2]


def file_to_audio(file):
    clip = mp.VideoFileClip(file)
    clip.audio.write_audiofile(AUDIO_PATH)


def transcribe_audio(audio_path):
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_path, verbose=True)
    return result["text"]


if FILETYPE == "video":
    file_to_audio(PATH)
    PATH = AUDIO_PATH

transcribe_audio(AUDIO_PATH)
sys.exit(0)
