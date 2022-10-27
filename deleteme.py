import moviepy.editor as mp
from math import ceil


def audio_length(file_path: str):
    duration = mp.AudioFileClip(file_path).duration
    return ceil(duration)


print(audio_length("audio.mp3"))
