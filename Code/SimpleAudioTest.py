import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from Widgets import *
import FileSupport as FP

import simpleaudio as sa
import numpy

import pydub

# import mutagen
# from mutagen.mp3 import MP3
# from mutagen.mp4 import MP4
# from mutagen.aiff import AIFF
# from mutagen.wave import WAVE


app = tb.Window()

app.title('Test')
app.geometry('800x600')

# #Set a theme for the app
style = tb.Style()
style.theme_use('solar')




class TestApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.audio = None
        self.wave_obj = None
        self.play_obj = None
        self.paused = False

        #Button to open a file
        self.openButton = tb.Button(self, text = 'Open', command = self.openFile)
        self.openButton.pack()

        #Button to play the song
        self.playButton = tb.Button(self, text = 'Play', command = self.playSong)
        self.playButton.pack()

        #Button to pause the song
        self.pauseButton = tb.Button(self, text = 'Pause', command = self.pauseSong)
        self.pauseButton.pack()

        #Button to stop the song
        self.stopButton = tb.Button(self, text = 'Stop', command = self.stopSong)
        self.stopButton.pack()

        self.progressButton = tb.Button(self, text = 'Get Progress', command = self.getProgress)
        self.progressButton.pack()

        #Label to display the song
        self.songLabel = tb.Label(self, text = 'Song Name: ')
        self.songLabel.pack()
        self.songDuration = tb.Label(self, text = 'Duration: ')
        self.songDuration.pack()

        #Progress label
        self.progressLabel = tb.Label(self, text = 'Progress: xxx/xxx')
        self.progressLabel.pack()
    
    def openFile(self):
        filetypes = [("Audio Files", "*.mp3 *.wav *.aiff")]
        file = filedialog.askopenfile(filetypes=filetypes, title="Select a song to add to the playlist")

        if file == None:
            return
    
        song = FP.Song(file.name)
   
        #Get the duration of the song
        fileType = file.name.split('.')[-1]
        audio = None
        audioData = None
        audio = pydub.AudioSegment.from_file(file.name, format=fileType)
        self.wave_obj = sa.WaveObject(audio.raw_data, audio.channels, audio.sample_width, audio.frame_rate)

        self.songLabel['text'] = 'Song Name: ' + song.name
        self.songDuration['text'] = 'Duration: ' + str(audio.duration_seconds) + ' seconds'
        self.audio = audio

    def playSong(self):
        if self.wave_obj == None:
            return

        self.play_obj = self.wave_obj.play()

    def pauseSong(self):
        if self.play_obj == None:
            return

        if self.paused:
            self.play_obj.resume()
            self.paused = False
            self.pauseButton['text'] = 'Pause'
        else:
            self.play_obj.pause()
            self.paused = True
            self.pauseButton['text'] = 'Resume'

    def stopSong(self):
        if self.play_obj == None:
            return

        self.play_obj.stop()
        self.play_obj = None
        self.paused = False
        self.pauseButton['text'] = 'Pause'

    def getProgress(self):
        if self.play_obj == None:
            return
        
        #Get the progress of the song
        progress = self.audio.duration_seconds * self.play_obj.get_time() / 1000
        
        


if __name__ == '__main__':
    app = TestApp(master=app)
    app.mainloop()
        