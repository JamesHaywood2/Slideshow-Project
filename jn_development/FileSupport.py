import os
import random
from PIL import Image
import json

MissingImage = r"Slideshow-Project\Creator\MissingImage.png"

ProgramIcon = r"Slideshow-Project\Creator\Icon.ico"

ball = r"Slideshow-Project\Creator\ball.jpg"
ball2 = r"Slideshow-Project\Creator\ball2.png"


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

def getParentDir(files):
    """Returns the parent directory of a list of file paths."""
    return [os.path.dirname(f) for f in files]

def getUserCacheDir():
    """Print the user's AppData/Local/PySlideshow directory. This is where the program will store its cache files."""
    return os.path.join(os.getenv('LOCALAPPDATA'), "PySlideshow")

def initializeCache():
    """Initialize the cache directory. Creates it if it doesn't exist."""
    cacheDir = getUserCacheDir()
    if not os.path.exists(cacheDir):
        os.makedirs(cacheDir)

    #Make a user preferences file and a cache folder
    if not os.path.exists(os.path.join(cacheDir, "cache")):
        os.makedirs(os.path.join(cacheDir, "cache"))

    #Preference file can just be a text file containing the theme.
    if not os.path.exists(os.path.join(cacheDir, "preferences.txt")):
        with open(os.path.join(cacheDir, "preferences.txt"), 'w') as f:
            f.write("litera")

def updatePreferences(theme:str):
    """Update the user preferences file with the theme."""
    cacheDir = getUserCacheDir()
    with open(os.path.join(cacheDir, "preferences.txt"), 'w') as f:
        f.write(theme)

def getPreferences():
    """Get the user preferences from the preferences file."""
    #Check if the preferences file exists
    cacheDir = getUserCacheDir()
    if not os.path.exists(os.path.join(cacheDir, "preferences.txt")):
        initializeCache()
        return "litera"
    else:
        with open(os.path.join(cacheDir, "preferences.txt"), 'r') as f:
            return f.read().strip()

def clearCache():
    """Clear the cache folder."""
    cacheDir = os.path.join(getUserCacheDir(), "cache")
    for f in os.listdir(cacheDir):
        os.remove(os.path.join(cacheDir, f))
    print("Cache cleared.")

def resetPreferences():
    """Reset the preferences file to the default theme."""
    updatePreferences("litera")

class Slide:
    """
    Slide class. Contains the image path, transition type, and transition speed.\n
    WARNING:
    ------------------
    Be careful how you reference the contents of this class. Sometimes it is a dictionary, sometimes it is a Slide object.\n
    Just be aware of this when you are working with it.\n
    When accessing slides there's a difference between pre-existing slides loaded from a save and new slides created in the program with FP.Slide().\n
    Pre-existing slides get treated as dictonaries and need subscript notation because they are like key:value. EX slide['imagePath']\n
    New slides are treated as Slide objects and need dot notation because they are like objects. EX slide.imagePath\n
    As of 2/14/2024 when slides get added to the slideshow they SHOULD be converted to dictionaries. So by default try subscript if dealing with slides from Slideshow object.\n
    """
    def __init__(self, imagePath:str):
        self.slideID: int = None
        self.imagePath: str = None
        self.imageName: str = None
        self.transition: transitionType = transitionType.DEFAULT
        self.transitionSpeed: int = 2
        self.duration: int = 5

        #Check if the imagePath is a valid picture
        try:
            img = Image.open(imagePath)
            self.imagePath = imagePath
            self.imageName = removePath([self.imagePath])[0]
        except:
            # print(f"{imagePath} is not a valid image file.")
            self.imagePath = MissingImage
            self.imageName = "Error: Missing Image"

    def __str__(self) -> str:
        #Print __dict__ for debugging
        return str(self.__dict__)
        
class transitionType:
    '''Transition types enumeration for the slideshow'''
    DEFAULT = "Default"
    FADE = "Fade"
    WIPEUP = "Wipe_Up"
    WIPEDOWN = "Wipe_Down"
    WIPELEFT = "Wipe_Left"
    WIPERIGHT = "Wipe_Right"

class Slideshow:
    """
    Slideshow class. Contains the file path, project name, list of slides, song playlist, etc. \n
    WARNING:
    ------------------
    Be careful how you reference slides (and songs too I guess) from a Slideshow object. They can be a dictionary or a Slide object.\n
    Just be aware of this when you are working with it. As of 2/14/2024 it should be a dictionary MOST of the time.\n
    """
    def __init__(self, filePath:str="New Project"):
        #Check if file exists
        if not os.path.exists(filePath):
            self.name = "Missing Path"
        self.__filePath: str = filePath #The file path of the slideshow file
        self.name = getBaseName([self.__filePath])[0]
        self.__slides: list[Slide] = []
        self.__count: int = 0
        self.__playlist: Playlist = Playlist()
        self.manual: bool = False
        self.defaultSlideDuration: int = 5
        self.shuffle: bool = False
        self.loop: bool = False
        self.filesInProject: list[str] = [] #This is a list of all the files in the project folder. Not necessarily a list of slides.

    #Add a slide at an index
    def addSlide(self, slide:Slide, index:int=-1):
        """
        Will insert a slide at the index, then push the rest of the slides down one index.
        If the index is -1, it will append the slide to the end of the list.
        NOTE:
        ------------------
        The slide object that gets added is a dictionary. Use subscript notation to access it. EX slide['imagePath']
        """
        # print(f"Adding slide at index {index}")
        
        #convert Slide to dict
        slide = slide.__dict__
        #IMPORTANT: Basically, when it was adding new slides it was adding them as a Slide object. Pre-existing slides were as a dictionary.
        #This caused a lot of issues. This should fix it by converting them all to dictionaries. Reference slides with subscript notation.

        if index == -1:
            self.__slides.append(slide)
        else:
            self.__slides.insert(index, slide)

        #Make slideID the index of the slide in the list
        for i, slide in enumerate(self.__slides):
            slide['slideID'] = i
        self.__count += 1
        self.printSlides()

    def printSlides(self):
        """Just prints a list of slides in the slideshow. For debugging."""
        print(f"Slide count: {self.__count}")
        print(f"Slide list:")
        for slide in self.__slides:
            print(slide)
        print("\n")
    
    #Haven't tested.
    def removeSlide(self, slide:Slide):
        self.__slides.remove(slide)
        self.__count -= 1

    def swapSlides(self, index1:int, index2:int):
        """
        Swap the slides at index1 and index2.
        """
        self.__slides[index1], self.__slides[index2] = self.__slides[index2], self.__slides[index1]
        #Update the slideID
        for i, slide in enumerate(self.__slides):
            slide['slideID'] = i

    def moveSlide(self, index:int, newIndex:int):
        """
        Move the slide at index to newIndex.
        """
        #If the newIndex is greater than the index, subtract 1. Otherwise just use the newIndex.
        if newIndex > index:
            newIndex -= 1

        slide = self.__slides.pop(index)
        self.__slides.insert(newIndex, slide)
        print(f"Moved slide from {index} to {newIndex}")
        #Update the slideID
        for i, slide in enumerate(self.__slides):
            slide['slideID'] = i

    #Haven't tested. Should work
    def getSlide(self, index:int):
        return self.__slides[index]
    
    def getSlides(self):
        """
        Returns a list of slides. Use subscript notation to access the slides. EX slide['imagePath'] if dot notation doesn't work.
        """
        return self.__slides
    
    def getSlideCount(self):
        return self.__count
    
    def getPlaylist(self):
        return self.__playlist
    
    def getSaveLocation(self):
        return self.__filePath
    
    def setSaveLocation(self, filePath:str):
        """
        Used to set the file path of the slideshow. Only used when creating a new slideshow or saving as.
        """
        self.__filePath = filePath
        self.name = getBaseName([self.__filePath])[0]
    
    def save(self):
        """
        Save the slideshow to a file by dumping the __dict__ to a json file.
        """
        print(f"Saving slideshow to {self.__filePath}\n{self}")
        with open(self.__filePath, 'w') as f:
            #Basically it's going to dump the __dict__ to a JSON file. If it encounters another object it's going to dump that object's __dict__ to the JSON file as well.
            json.dump(self.__dict__, f, default=lambda o: o.__dict__, indent=4)

    def load(self):
        """
        Loads data from the JSON file into the slideshow.
        """
        #This could probably just be in the __init__ method. I don't know why I made it seperate, but I don't want to change it and see if it breaks anything. - James
        #If the slideshow is new just skip checking and seeing if you can load it.
        if self.name == "New Project":
            self.__init__()
            return


        try:
            with open(self.__filePath, 'r') as f:
                data = json.load(f)
                self.__dict__.update(data)
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            #Basically if there is an error loading the file it's going to create a new slideshow.
            self.__init__()
    
    def __str__(self) -> str:
        """Print definition for debugging."""
        #Print __dict__ for debugging
        return str(self.__dict__)
    

class Song:
    #SEE SLIDE CLASS FOR REFERENCE.
    #SEE METHOD USED TO ADD SLIDES TO SLIDESHOW FOR REFERENCE.
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
            self.__songs.append(song)
        else:
            self.__songs.insert(index, song)
        self.__count += 1
        #Update the duration

    def removeSong(self, song:Song):
        self.__songs.remove(song)
        self.__count -= 1
        #Update the duration
    
