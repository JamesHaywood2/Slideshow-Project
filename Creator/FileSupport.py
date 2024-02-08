import os
import random
from PIL import Image

def getJPEG(folderPath:str, recursive:bool=False):
    """
    Get all the JPEG files in the folder and its subfolders
    """
    if recursive:
        #Iterates through folder and subfolders with walk. The list of files is called filenames. It will then check filenames for .jpg or .jpeg files and add them to the list.
        files = [os.path.join(dirPath, f) for dirPath, dirNames, filenames in os.walk(folderPath) for f in filenames if os.path.splitext(f)[1] == '.jpg' or os.path.splitext(f)[1] == '.jpeg']
    else:
        #Same as above, but only for the folder
        files = [os.path.join(folderPath, f) for f in os.listdir(folderPath) if os.path.splitext(f)[1] == '.jpg' or os.path.splitext(f)[1] == '.jpeg']

    #replace the forward slashes with backslashes
    return [f.replace("\\", "/") for f in files]


#Get the base file name from a list of file paths
def removePath(files):
    """Removes the path from a list of filepaths and returns the base file names."""
    return [os.path.basename(f) for f in files]
    
#Return a random image from a list of files
def randomImage(files):
    """Returns a random image from a list of file paths."""
    return random.choice(files)

def removeExtension(files):
    """Removes the file extension from a list of file paths."""
    return [os.path.splitext(f)[0] for f in files]

def getBaseName(files):
    """Returns the base name of a list of file paths."""
    return [os.path.basename(f) for f in files]

class Slide:
    def __init__(self, imagePath:str):
        self.slideID: int = None
        self.imagePath: str = None
        self.imageName: str = None
        self.transition: transitionType = transitionType.DEFAULT
        self.transitionSpeed: int = 1

        #Check if the imagePath is a valid picture
        try:
            img = Image.open(imagePath)
            self.imagePath = imagePath
            self.imageName = removePath([self.imagePath])[0]
        except:
            # print(f"{imagePath} is not a valid image file.")
            self.imagePath = r"..\Slideshow-Project\MissingImage.png"
            self.imageName = "Error: Missing Image"


class transitionType:
    DEFAULT = "Default"
    FADE = "Fade"
    WIPEUP = "Wipe_Up"
    WIPEDOWN = "Wipe_Down"
    WIPELEFT = "Wipe_Left"
    WIPERIGHT = "Wipe_Right"

class Slideshow:
    def __init__(self, filePath:str=None):
        #Check if file exists
        if not os.path.exists(filePath):
            raise FileNotFoundError(f"File {filePath} not found.")
        self.__filePath: str = filePath #The file path of the slideshow file
        self.name = getBaseName([self.filePath])[0]
        self.__slides: list[Slide] = []
        self.__count: int = 0
        self.__playlist: Playlist = Playlist()
        self.manual: bool = False
        self.defaultSlideDuration: int = 5
        self.shuffle: bool = False
        self.loop: bool = False


    #Add a slide at an index
    def addSlide(self, slide:Slide, index:int=-1):
        """Will insert a slide at the index, then push the rest of the slides down one index.
        If the index is -1, it will append the slide to the end of the list."""
        if index == -1:
            self.slides.append(slide)
        else:
            self.slides.insert(index, slide)
        self.count += 1
    
    def removeSlide(self, slide:Slide):
        self.slides.remove(slide)
        self.count -= 1

    def getSlide(self, index:int):
        return self.slides[index]
    
    def getSlides(self):
        return self.slides
    
    def getSlideCount(self):
        return self.count
    
    def getPlaylist(self):
        return self.playlist
    

class Song:
    def __init__(self, songPath:str):
        self.filePath: str = None
        self.name: str = None
        self.duration: int = 0
        self.artist: str = None
        self.album: str = None

        #Check if the songPath is a valid song (.mp3, .mp4, .wav, .AAIF)
        try:
            #Check if the file exists
            if not os.path.exists(songPath):
                raise FileNotFoundError(f"File {songPath} not found.")
            #Check if the file is of a valid type
            if not os.path.splitext(songPath)[1] in ['.mp3', '.mp4', '.wav', '.AAIF']:
                raise FileNotFoundError(f"File {songPath} is not a valid song file.")
            self.filePath = songPath
            self.name = removePath([self.filePath])[0]
        except:
            # print(f"{songPath} is not a valid song file.")
            self.filePath = "Error: Missing Song"
            self.name = "Error: Missing Song"

        
class Playlist:
    def __init__(self):
        self.name: str = None
        self.__songs: list[Song] = []
        self.__count: int = 0
        self.__duration: int = 0
        self.shuffle: bool = False
        self.loop: bool = False

    def addSong(self, song:Song, index:int=-1):
        """Will insert a song at the index, then push the rest of the songs down one index.
        If the index is -1, it will append the song to the end of the list."""
        if index == -1:
            self.songs.append(song)
        else:
            self.songs.insert(index, song)
        self.count += 1
        #Update the duration

    def removeSong(self, song:Song):
        self.songs.remove(song)
        self.count -= 1
        #Update the duration
    