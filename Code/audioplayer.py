import mutagen
from mutagen.mp3 import MP3
from mutagen.aiff import AIFF
from mutagen.wave import WAVE

from pygame import mixer
from enum import Enum


class AudioPlayer:
    class State(Enum):
        STOPPED = 0
        PLAYING = 1
        PAUSED = 2

    def __init__(self) -> None:
        #Initialize pygame mixer
        mixer.init()

        self.current_song = None
        self.current_song_length = None
        self.state = AudioPlayer.State.STOPPED

    def load_song(self, song):
        #song must either be a path to a file or a
        
        

        
