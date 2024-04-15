import os
import sys
import time
from PIL import Image, ImageOps
import json

import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.aiff import AIFF
from mutagen.wave import WAVE
import soundfile as sf

# import pygame
from pygame import mixer
from enum import Enum


import contextlib
@contextlib.contextmanager
def supress_print():
    with open(os.devnull, 'w') as f:
        with contextlib.redirect_stdout(f):
            yield

def resource_path(relative_path):
    """Get the absolute path to the resource, works for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS # type: ignore
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ProgramIcon = resource_path(r"../Slideshow-Project/assets/icon.ico")

# MissingImage = resource_path(r"MissingImage.png")
# refreshIcon  = resource_path(r"refreshIcon.png")
# toolTipIcon  = resource_path(r"tooltip.png")

MissingImage = resource_path(r"../Slideshow-Project/assets/MissingImage.png")
refreshIcon  = resource_path(r"../Slideshow-Project/assets/refreshIcon.png")
toolTipIcon  = resource_path(r"../Slideshow-Project/assets/tooltip.png")



relative_project_path = ""
# FP.file_check(path, FP.reltaive_project_path)

def set_relative_project_path(path:str):
    global relative_project_path
    relative_project_path = path

openFiles = {}

def printOpenFiles():
    for f in openFiles:
        print(f)

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
    
#Take a str or list of str file paths and return their names without the file extension
def removeExtension(files):
    """Removes the file extension from a list of file paths."""
    if isinstance(files, list):
        return [os.path.splitext(f)[0] for f in files]
    else:
        return os.path.splitext(files)[0]

def getBaseName(files):
    """Returns the base name of a list of file paths.\n
    ex: C:/Users/James/Documents/Project1.txt -> Project1.txt
    """
    # print(files)
    return [os.path.basename(f) for f in files]

def getParentDir(files):
    """Returns the parent directory of a list of file paths.\n
    ex: C:/Users/James/Documents/Project1.txt -> C:/Users/James/Documents
    """
    return [os.path.dirname(f) for f in files]

def getUserHome():
    """Print the user's home directory. This is where the program will store its cache files."""
    return os.path.expanduser("~")

def getUserCacheDir():
    """Print the user's AppData/Local/PySlideshow directory. This is where the program will store its cache files."""
    return os.path.join(os.getenv('LOCALAPPDATA'), "PySlideshow") # type: ignore

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

    #RecentSlideshows file can just be a text file containing the file paths of the recent slideshows.
    if not os.path.exists(os.path.join(cacheDir, "RecentSlideshows.txt")):
        with open(os.path.join(cacheDir, "RecentSlideshows.txt"), 'w') as f:
            pass
    else:
        validateRecentSlideshows()

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
        
def getLastModified(fileName:str):
    """Get the last modified time of a file."""
    #Check if the file exists
    if not os.path.exists(fileName):
        return time.ctime(0)
    mod_time = os.path.getmtime(fileName)
    return time.ctime(mod_time)

def updateSlideshowCacheList(slideshowPath:str):
    print(f"Updating RecentSlideshows.txt with {slideshowPath}")
    #Get the cache directory
    cacheDir = getUserCacheDir()
    # #Convert the slideshowPath "\" to "/" for the cache file
    # slideshowPath = slideshowPath.replace("\\", "/")
    #Check if the RecentSlideshows.txt file exists
    cache_list_exists = False
    try: 
        cache_list_exists = os.path.exists(os.path.join(cacheDir, "RecentSlideshows.txt"))
    except:
        print("Error checking if RecentSlideshows.txt exists.")
    #If the file doesn't exist, initialize it
    if not cache_list_exists:
        initializeCache()
    
    file_exists = False
    try:
        file_exists = os.path.exists(slideshowPath)
    except:
        print("Error checking if slideshowPath exists.")
        
    if not file_exists:
        print(f"{slideshowPath} does not exist. from updateSlideshowCacheList()")
        return
    
    #Get the last modified time of the slideshow
    mod_time = getLastModified(slideshowPath)
    entry = f"{slideshowPath}${mod_time}"
    #Insert entry into the RecentSlideshows.txt file at the top
    with open(os.path.join(cacheDir, "RecentSlideshows.txt"), 'r') as f:
        slideshows = f.readlines()
        slideshows = [s.strip() for s in slideshows]
        if entry in slideshows:
            slideshows.remove(entry)
        slideshows.insert(0, entry)

    with open(os.path.join(cacheDir, "RecentSlideshows.txt"), 'w') as f:
        for s in slideshows:
            f.write(s + "\n")

    #Validate the recent slideshows list
    validateRecentSlideshows()



def getRecentSlideshows() -> list[str]:
    """Get the list of recent slideshows from the cache folder."""
    cacheDir = getUserCacheDir()
    #Validate the recent slideshows list
    validateRecentSlideshows()
    #Check if the RecentSlideshows file exists
    if not os.path.exists(os.path.join(cacheDir, "RecentSlideshows.txt")):
        print(f"RecentSlideshows.txt does not exist in {cacheDir}. Creating it now.")
        with open(os.path.join(cacheDir, "RecentSlideshows.txt"), 'w') as f:
            pass
    else:
        #If the file exists, return the list of recent slideshows
        with open(os.path.join(cacheDir, "RecentSlideshows.txt"), 'r') as f:
            print("Reading RecentSlideshows.txt")
            slideshows = f.readlines()
            slideshows = [s.strip() for s in slideshows]
            for s in slideshows:
                #Check if it's empty
                if s == "":
                    slideshows.remove(s)
                    continue
                #Split the entry into the file path and the last modified time
                split = s.split("$")
                #Check if the split is valid
                if len(split) != 2:
                    slideshows.remove(s)
                    continue
                #Check if the file path is valid
                if not os.path.exists(split[0]):
                    slideshows.remove(s)
                    continue
            return slideshows
    return []
        
def validateRecentSlideshows():
    """Validate the recent slideshows list. Remove any invalid file paths from the list."""
    cacheDir = getUserCacheDir()
    #Check if the RecentSlideshows file exists
    cache_list_exists = False
    try: 
        cache_list_exists = os.path.exists(os.path.join(cacheDir, "RecentSlideshows.txt"))
    except:
        print("Error checking if RecentSlideshows.txt exists.")
    #If the file doesn't exist, initialize it
    if not cache_list_exists:
        initializeCache()
        #Since it didn't exist, there's nothing to validate.
        return

    #Get the list of recent slideshows
    entries = {}
    with open(os.path.join(cacheDir, "RecentSlideshows.txt"), 'r') as f:
        slideshows = f.readlines()
        slideshows = [s.strip() for s in slideshows]
        #Check if the list is empty
        if len(slideshows) == 0:
            return
        #Iterate through the list
        for s in slideshows:
            split = s.split("$")
            #Check if the split is valid
            if len(split) != 2:
                #If it's not valid, remove it from the list
                slideshows.remove(s)
                continue
            path = split[0]
            mod_time = split[1]
            #Check if already in the dictionary
            if path in entries:
                #If it is, check if the mod_time is newer
                if mod_time > entries[path]:
                    #If it is, update the mod_time
                    entries[path] = mod_time
            else:
                #If it's not in the dictionary, add it
                entries[path] = mod_time
        
        #Check if the file paths are valid
        for path in list(entries):
            if not os.path.exists(path):
                #If the file path is invalid, remove it from the list
                entries.pop(path)
        
        #Write the valid file paths back to the file
        with open(os.path.join(cacheDir, "RecentSlideshows.txt"), 'w') as f:
            for path in list(entries):
                f.write(f"{path}${entries[path]}\n")

def clearCache():
    """Clear the cache folder."""
    cacheDir = os.path.join(getUserCacheDir(), "cache")
    for f in os.listdir(cacheDir):
        os.remove(os.path.join(cacheDir, f))
    print("Cache cleared.")

def openCacheFolder():
    """Open the cache folder in explorer."""
    os.startfile(os.path.join(getUserCacheDir(), "cache"))

def resetPreferences():
    """Reset the preferences file to the default theme."""
    updatePreferences("litera")

def saveImageToCache(image:Image, name:str): # type: ignore
    """Save the image to the cache folder."""
    cacheDir = os.path.join(getUserCacheDir(), "cache")
    #Save the image to the cache folder
    image.save(os.path.join(cacheDir, name)) # type: ignore

def copyFileToCache(file:str):
    """Copy a file to the cache folder."""
    cacheDir = os.path.join(getUserCacheDir(), "cache")
    #Copy the file to the cache folder
    with open(file, 'rb') as f:
        with open(os.path.join(cacheDir, os.path.basename(file)), 'wb') as c:
            c.write(f.read())

def loadImageFromCache(name:str):
    """Load the image from the cache folder."""
    cacheDir = os.path.join(getUserCacheDir(), "cache")
    #Load the image from the cache folder
    return ImageOps.exif_transpose(Image.open(os.path.join(cacheDir, name)))

def checkCache(filepath:str):
    """Check if the file exists in the cache folder."""
    #Get the base file name
    baseName = os.path.basename(filepath)
    #Get the cache folder
    cacheFolder = os.path.join(getUserCacheDir(), "cache")
    #Check if the file exists in the cache folder
    if os.path.exists(os.path.join(cacheFolder, baseName)):
        return os.path.join(cacheFolder, baseName)
    else:
        return None

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
        self.slideID: int = None # type: ignore
        self.imagePath: str = None # type: ignore
        self.imageName: str = None # type: ignore
        self.transition: transitionType = transitionType.DEFAULT # type: ignore
        self.transitionSpeed: int = 1
        self.duration: int = 5
        self.slideDB_ID: int = None # type: ignore

        #Check if the imagePath is a valid picture
        try:
            img = Image.open(imagePath)
            self.imagePath = imagePath
            self.imageName = removePath([self.imagePath])[0]
            try:
                f = open(imagePath, 'rb')
                openFiles[imagePath] = f
            except:
                print(f"Error opening {imagePath} for locking.")
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

class loopSetting:
    """Loop settings enumeration for the slideshow\n 
    "Indefinietly", "Until Playlist Ends", "Until Slides End", "Sync with Playlist"""
    INDEFINITE = "Indefinite"
    UNTIL_PLAYLIST_ENDS = "Until Playlist Ends"
    UNTIL_SLIDES_END = "Until Slides End"
    SYNC_WITH_PLAYLIST = "Sync with Playlist"
    

class Slideshow:
    """
    Slideshow class. Contains the file path, project name, list of slides, song playlist, etc. \n
    WARNING:
    ------------------
    Be careful how you reference slides (and songs too I guess) from a Slideshow object. They can be a dictionary or a Slide object.\n
    Just be aware of this when you are working with it. As of 2/14/2024 it should be a dictionary MOST of the time.\n
    """
    def __init__(self, filePath:str="New Project", **kw):
        self.__filePath: str = filePath #The file path of the slideshow file
        #if the filepath is an existing file, get the name of the file without the extension
        if os.path.exists(filePath):
            self.name = getBaseName([self.__filePath])[0]
        else:
            self.name = "New Project"
        self.slides: list[Slide] = []
        self.__count: int = 0
        self.playlist: Playlist = Playlist()
        self.loopSettings: str = loopSetting.INDEFINITE
        self.manual: bool = False
        self.shuffle: bool = False
        self.filesInProject: list[str] = [] #This is a list of all the files in the project folder. Not necessarily a list of slides.
        self.tags: list[str] = [] #This is a list of tags for the project. Used for searching.

        self.slideshowID: int = None # type: ignore

        #if the file path exists, open it.
        if os.path.exists(filePath):
            try:
                f = open(filePath, 'r')
                openFiles[filePath] = f
                print(f"Opened {filePath}")
            except:
                print(f"Error opening {filePath}")
            self.loadFromFile()
        else:
            print("New project created.")

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
        slide = slide.__dict__ # type: ignore
        #IMPORTANT: Basically, when it was adding new slides it was adding them as a Slide object. Pre-existing slides were as a dictionary.
        #This caused a lot of issues. This should fix it by converting them all to dictionaries. Reference slides with subscript notation.

        if index == -1:
            self.slides.append(slide)
        else:
            self.slides.insert(index, slide)

        #Make slideID the index of the slide in the list
        for i, slide in enumerate(self.slides):
            try:
                slide['slideID'] = i
            except:
                slide.slideID = i
        self.__count += 1
        self.printSlides()

    def printSlides(self):
        """Just prints a list of slides in the slideshow. For debugging."""
        print(f"Slide count: {self.__count}")
        print(f"Slide list:")
        for slide in self.slides:
            print(slide)
        print("\n")
    
    def removeSlide(self, slide:Slide):
        print(slide)
        try:
            id = slide['slideID']
        except:
            id = slide.slideID
        print(f"Removing slide {id}")
        try:
            imgPth = slide['imagePath']
        except:
            imgPth = slide.imagePath
        try:
            openFiles[imgPth].close()
            del openFiles[imgPth]
        except:
            print(f"Error closing {imgPth}")
        self.slides.remove(slide)
        self.__count -= 1

    def moveSlide(self, index:int, newIndex:int):
        """
        Move the slide at index to newIndex.
        """
        #If the newIndex is greater than the index, subtract 1. Otherwise just use the newIndex.
        if newIndex > index:
            newIndex -= 1

        slide = self.slides.pop(index)
        self.slides.insert(newIndex, slide)
        print(f"Moved slide from {index} to {newIndex}")
        #Update the slideID
        for i, slide in enumerate(self.slides):
            try:
                slide['slideID'] = i
            except:
                slide.slideID = i

    #Haven't tested. Should work
    def getSlide(self, index:int):
        return self.slides[index]
    
    def getSlides(self):
        """
        Returns a list of slides. Use subscript notation to access the slides. EX slide['imagePath'] if dot notation doesn't work.
        """
        return self.slides
    
    def getSlideCount(self):
        self.__count = len(self.slides)
        return self.__count
    
    def getPlaylist(self):
        """Returns the playlist object. If a song is missing it will remove it from the playlist."""
        print(f"\nGetting playlist for {self.name}...")
        # print(self.playlist)
        #If the playlist is a disctionary, convert it to a Playlist object.
        if isinstance(self.playlist, dict):
            playlist = Playlist()
            playlist.__dict__.update(self.playlist)
            self.playlist = playlist
        
        #Convert the songs to Song objects
        for i, song in enumerate(self.playlist.songs):
            if isinstance(song, dict):
                try:
                    s = Song(file_check(song['filePath'], relative_project_path))
                    s.__dict__.update(song)
                    self.playlist.songs[i] = s
                except:
                    print(f"Error loading song {song['filePath']}")
                    self.playlist.songs.pop(i)

                #Open the file and lock it
                try:
                    f = open(song['filePath'], 'rb')
                    openFiles[song['filePath']] = f
                except:
                    print(f"Error opening {song['filePath']} for locking in Slideshow.getPlaylist()")

        return self.playlist
    
    def getSaveLocation(self):
        return self.__filePath
    
    def setSaveLocation(self, filePath:str):
        """
        Used to set the file path of the slideshow. Only used when creating a new slideshow or saving as.
        """
        self.__filePath = filePath
    
    def save(self):
        """
        Save the slideshow to a file by dumping the __dict__ to a json file.
        """
        print(f"Saving slideshow to {self.__filePath}")
        # print(self)

        for file in self.filesInProject:
            fileExtension = file.split(".")[-1]
            validExtensions = ["jpg", "jpeg", "png"]
            if fileExtension not in validExtensions:
                #remove the file from the list
                self.filesInProject.remove(file)

        with open(self.__filePath, 'w') as f:
            #Basically it's going to dump the __dict__ to a JSON file. If it encounters another object it's going to dump that object's __dict__ to the JSON file as well.
            json.dump(self.__dict__, f, default=lambda o: o.__dict__, indent=4)
            openFiles[self.__filePath] = f

        updateSlideshowCacheList(self.__filePath)

    def loadFromFile(self):
        """
        Loads data from the JSON file into the slideshow.
        """
        #This could probably just be in the __init__ method. I don't know why I made it seperate, but I don't want to change it and see if it breaks anything. - James
        #If the slideshow is new just skip checking and seeing if you can load it.
        if self.name == "New Project":
            print("New project detected.")
            return
        
        #Save the filepath and name to a temp variable
        tempPath = self.__filePath
        tempName = self.name

        try:
            with open(self.__filePath, 'r') as f:
                data = json.load(f)
                self.__dict__.update(data)
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            #Basically if there is an error loading the file it's going to create a new slideshow.
            self.__init__()

        for file in self.filesInProject:
            fileExtension = file.split(".")[-1]
            validExtensions = ["jpg", "jpeg", "png"]
            if fileExtension not in validExtensions:
                #remove the file from the list
                self.filesInProject.remove(file)
                continue

        #Restore the file path and name
        #Basically if you have a slideshow file and it has changed name or location it's going to act as if it's it's in the old location. We want the current ones.
        self.__filePath = tempPath
        self.name = tempName

        #rename self.__slides to self.slides if it exists
        if '_Slideshow__slides' in self.__dict__: # type: ignore
            print("Renaming __slides to slides.")
            self.slides = self.__slides # type: ignore
            self.__dict__.pop('_Slideshow__slides')

        set_relative_project_path(self.__filePath)

    def __str__(self) -> str:
        """Print definition for debugging."""
        #Print __dict__ for debugging
        return str(self.__dict__)
    
    def exportToCache(self):
        """Export all project files to the cache folder."""
        self.save()
        #Project files include self.filesInProject and the songs in the playlist.
        #Go through all filesInProject and export them to the cache folder.
        for file in self.filesInProject:
            #Check if the file exists in the cache folder
            if checkCache(file) == None:
                #If it doesn't exist, save it to the cache folder
                try:
                    copyFileToCache(file)
                except:
                    print(f"Error copying {file} to cache folder.")

        #Go through all the songs in the playlist and export them to the cache folder.
        for song in self.playlist.songs:
            #Check if the song exists in the cache folder
            if checkCache(song.filePath) == None:
                #If it's not yet in the cache, save a copy of the audio file to the cache folder
                try:
                    copyFileToCache(song.filePath)
                except:
                    print(f"Error copying {song.filePath} to cache folder.")

        #Go through all the slides in the slideshow and export them to the cache folder.
        for slide in self.slides:
            #Check if the slide exists in the cache folder
            if checkCache(slide['imagePath']) == None:
                #If it's not yet in the cache, save a copy of the image to the cache folder
                try:
                    copyFileToCache(slide['imagePath'])
                except:
                    print(f"Error copying {slide['imagePath']} to cache folder.")


    # def exportToFolder(self, folderPath:str):
    #     """Export all project files to a folder named exported_assets_{projectName} to the project folder."""
    #     self.save()
    #     if not os.path.exists(folderPath):
    #         #Create a folder in the project folder called exported_assets_{projectName}
    #         projectFolder = os.path.dirname(self.__filePath)
    #         exportFolder = os.path.join(projectFolder, f"exported_assets_{removeExtension(self.name)}")
    #     else:
    #         exportFolder = os.path.join(folderPath, f"exported_assets_{removeExtension(self.name)}")

    #     #Get the current time
    #     currentTime = time.strftime("_%Y-%m-%d_%H-%M-%S")
    #     exportFolder += currentTime
            
    #     if not os.path.exists(exportFolder):
    #         os.makedirs(exportFolder)
        
    #     #Export all the files in the project folder to the export folder
    #     for file in self.filesInProject:
    #         #Copy the file to the export folder
    #         img = Image.open(file)
    #         img.save(os.path.join(exportFolder, os.path.basename(file)))

    #     #Export all the songs in the playlist to the export folder
    #     for song in self.playlist.songs:
    #         #Copy the song to the export folder
    #         f = open(song.filePath, 'rb')
    #         with open(os.path.join(exportFolder, os.path.basename(song.filePath)), 'wb') as c:
    #             c.write(f.read())
    #         f.close()

    #     #Export all the slides in the slideshow to the export folder
    #     for slide in self.slides:
    #         #Copy the slide to the export folder
    #         img = Image.open(slide['imagePath'])
    #         img.save(os.path.join(exportFolder, os.path.basename(slide['imagePath'])))

    #     #Finally, copy the slideshow file to the export folder
    #     saveLoc = self.getSaveLocation()
    #     newSaveLoc = os.path.join(exportFolder, os.path.basename(saveLoc))
    #     self.setSaveLocation(newSaveLoc)
    #     self.save()
    #     self.setSaveLocation(saveLoc)

    def exportToFolder(self, filePath:str):
        """Export all project files to a folder named exported_assets_{projectName} to the project folder."""
        if not os.path.exists(filePath):
            #Create a folder in the project folder called exported_assets_{projectName}
            projectFolder = os.path.dirname(self.__filePath)
            exportFolder = os.path.join(projectFolder, f"exported_project_{removeExtension(self.name)}")
        else:
            exportFolder = os.path.join(filePath, f"exported_project_{removeExtension(self.name)}")

        #Get the current time
        currentTime = time.strftime("_%Y-%m-%d_%H-%M-%S")
        exportFolder += currentTime

        tempName = self.name
        self.name = getBaseName([exportFolder])[0]
            
        if not os.path.exists(exportFolder):
            os.makedirs(exportFolder)
        
        #Export all the files in the project folder to the export folder
        for file in self.filesInProject:
            #Copy the file to the export folder
            img = Image.open(file)
            img.save(os.path.join(exportFolder, os.path.basename(file)))

        #Export all the songs in the playlist to the export folder
        for song in self.playlist.songs:
            #Copy the song to the export folder
            f = open(song.filePath, 'rb')
            with open(os.path.join(exportFolder, os.path.basename(song.filePath)), 'wb') as c:
                c.write(f.read())
            f.close()

        #Export all the slides in the slideshow to the export folder
        for slide in self.slides:
            #Copy the slide to the export folder
            try:
                path = slide['imagePath']
            except:
                path = slide.imagePath
            img = Image.open(path)
            img.save(os.path.join(exportFolder, os.path.basename(path)))

        #Finally, copy the slideshow file to the export folder
        saveLoc = self.getSaveLocation()
        newSaveLoc = os.path.join(exportFolder, self.name)
        self.setSaveLocation(newSaveLoc + ".pyslide")
        self.save()
        self.name = tempName
        self.setSaveLocation(saveLoc)


class Song:
    #SEE SLIDE CLASS FOR REFERENCE.
    #SEE METHOD USED TO ADD SLIDES TO SLIDESHOW FOR REFERENCE.
    def __init__(self, songPath:str):
        self.filePath: str = None
        self.name: str = None
        self.duration: int = 0
        self.fileType: str = None
        self.duration: int = 0

        self.songDB_ID: int = None

        #Check if the songPath is a valid song (.mp3, .mp4, .wav, .AAIF)
        try:
            #Check if the file exists
            if not os.path.exists(songPath):
                raise FileNotFoundError(f"File {songPath} not found.")
            #Check if the file is of a valid type
            if not os.path.splitext(songPath)[1] in ['.mp3', '.mp4', '.wav', '.aiff']:
                raise FileNotFoundError(f"File {songPath} is not a valid song file.")
            self.filePath = songPath
            self.name = removePath([self.filePath])[0]
        except:
            # print(f"{songPath} is not a valid song file.")
            self.filePath = "Error: Missing Song"
            self.name = "Error: Missing Song"
            return
        
        #Get the duration of the song
        fileType = os.path.splitext(self.filePath)[1]
        # print(f"filepath: {self.filePath}, fileType: {fileType}")
        audio = None
        try:
            if fileType == ".mp3":
                audio = MP3(self.filePath)
            elif fileType == ".wav":
                audio = WAVE(self.filePath)
            elif fileType == ".mp4":
                audio = MP4(self.filePath)
            elif fileType == ".aiff":
                audio = AIFF(self.filePath)
        except Exception as e:
            print(f"Error loading {self.filePath} at Song Object Creation. Trying generic load")
            print("Error: ", e)
            try:
                audio = mutagen.File(self.filePath)
            except:
                print(f"Error loading generic audio file {self.filePath}.")
                return

        self.fileType = fileType
        self.duration = int(audio.info.length)

    def __str__(self) -> str:
        """Print definition for debugging."""
        #Print the object as a readable string
        return str(self.__dict__)
    
    def __repr__(self) -> str:
        """Print definition for debugging."""
        #Print the object as a readable string
        return str(self.__dict__)
    
def formatTime(seconds:int):
    """Format the time in seconds to a string."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

class Playlist:
    def __init__(self):
        # self.name: str = None
        self.songs: list[Song] = []
        self.__count: int = 0
        self.__duration: int = 0
        self.shuffle: bool = False

    def addSong(self, song:str, index:int=-1):
        """Will insert a song at the index, then push the rest of the songs down one index.
        If the index is -1, it will append the song to the end of the list."""
        newSong = Song(song)
        #Check if the song is valid
        if Song == -1:
            return
        #Check if the song already exists in the playlist
        for s in self.songs:

            if s.filePath == newSong.filePath:
                print(f"{newSong} already exists in the playlist.")
                return

        if index == -1:
            self.songs.append(newSong)
        else:
            self.songs.insert(index, newSong)
        self.__count += 1
        #Update the duration
        self.validate()

        #Try to save the song to the cache folder
        try:
            copyFileToCache(song)
        except:
            print(f"Error copying {song} to cache folder.")

    def removeSong(self, song:Song):
        print(type(song))
        print(self.songs)
        self.songs.remove(song)
        self.__count -= 1
        #Update the duration
        self.validate()

    def validate(self):
        #Just update values.
        self.__count = len(self.songs)
        self.__duration = 0
        for song in self.songs:
            #If song is a dictionary, convert it to a Song object.
            if isinstance(song, dict):
                s = Song(song['filePath'])
                s.__dict__.update(song)
                song = s
            self.__duration += song.duration
            # print(f"{song.name} - {formatTime(song.duration)}")
        # print(f"Playlist duration: {formatTime(self.__duration)}")
            
    def getDuration(self):
        return self.__duration
    
    def moveSongUp(self, index:int):
        """Move the song at index up one index."""
        if index > 0:
            self.songs[index], self.songs[index-1] = self.songs[index-1], self.songs[index]

    def moveSongDown(self, index:int):
        """Move the song at index down one index."""
        if index < self.__count - 1:
            self.songs[index], self.songs[index+1] = self.songs[index+1], self.songs[index]

    def __str__(self) -> str:
        """Print definition for debugging."""
        #Print __dict__ for debugging
        return str(self.__dict__)

class AudioPlayer:
    """
    First create an AudioPlayer object. Then load a song into the player with load_song().\n
    You can then play the song with play(), pause it with pause(), resume it with resume(), or stop it with stop().\n
    """
    class State(Enum):
        """
        UNLOADED: No song is loaded into the player.\n
        FAILED_TO_LOAD: The song failed to load.\n
        STOPPED: The song is stopped and at the very beginning.\n
        PLAYING: The song is currently playing.\n
        PAUSED: The song is paused.\n
        """
        UNLOADED = 0
        FAILED_TO_LOAD = 1
        STOPPED = 2
        PLAYING = 3
        PAUSED = 4

    def __init__(self) -> None:
        #Initialize pygame mixer
        mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
        # pygame.init()
        mixer.init()

        self.current_song: Song = None
        self.duration = 0
        self.progress = 0
        self.state = AudioPlayer.State.UNLOADED

    def isFinished(self):
        # print(f"Song progress: {formatTime(self.progress)} / {formatTime(self.duration)} and state: {self.state}")
        if self.state == AudioPlayer.State.PAUSED or mixer.music.get_busy() or self.state == AudioPlayer.State.STOPPED:
            # print("Song is not finished.")
            return False
        else:
            # print("Song is finished.")
            return True
        
    def get_bit_depth(self, wav_file):

        #Check if the file exists
        if not os.path.exists(wav_file):
            return None

        with sf.SoundFile(wav_file, 'r') as f:
            bit_depth = f.subtype
            if 'PCM_' in bit_depth:
                bit_depth = bit_depth.split('_')[-1]  # Extracting the bit depth from subtype
                if bit_depth.isdigit():  # Check if it's a digit
                    return int(bit_depth)
        return None

    def loadSong(self, song, rewriteWav:bool=False):
        print(f"\nAttempting to load song {song}...\n")
        #song must either be a path to a file or a Song object
        if isinstance(song, Song):
            self.current_song = song
        elif isinstance(song, str):
            self.current_song = Song(song)
            if self.current_song == -1:
                self.state = AudioPlayer.State.FAILED_TO_LOAD
                print(f"Failed to create song object for {song}.")
                return -1
        else:
            print("Invalid song type. Must be a path to a file or a Song object.")
            self.state = AudioPlayer.State.FAILED_TO_LOAD
            return -1

        if self.current_song.fileType == ".wav":
            #Check if the bit depth is 16

            bit_depth = self.get_bit_depth(file_check(self.current_song.filePath, relative_project_path))
            if bit_depth is not None:
                # print("Bit depth:", bit_depth)
                pass
            else:
                print("Error: Failed to get bit depth, file was not 16-bit.")

                return -2

        try:
            mixer.music.load(file_check(self.current_song.filePath, relative_project_path))
            print(f"Loaded {self.current_song.name}")
        except Exception as e:
            print(f"Failed to load song in loadsong() with mixer.music.load(). Song {self.current_song.filePath} failed to load.")
            print("Error: ", e)
            self.state = AudioPlayer.State.FAILED_TO_LOAD
            return -1
        self.state = AudioPlayer.State.STOPPED
        self.progress = 0
        self.duration = self.current_song.duration
        return 0
    
    def rewriteWavto16Bit(self, wav_file):
        data, samplerate = sf.read(wav_file)
        cachedWavPath = os.path.join(getUserCacheDir(), "cache", os.path.basename(wav_file))
        sf.write(cachedWavPath, data, samplerate, subtype='PCM_16')

        #Update the song object
        self.current_song = Song(cachedWavPath)

        return cachedWavPath


    def unloadSong(self):
        #If the song is unloaded or failed to load, don't do anything.
        if self.state == AudioPlayer.State.UNLOADED or self.state == AudioPlayer.State.FAILED_TO_LOAD:
            return -1
        try:
            mixer.music.unload()
        except Exception as e:
            print(f"Failed to unload song {self.current_song.filePath}.")
            print("Error: ", e)
            return -1
        print(f"Unloaded {self.current_song.name}")
        self.state = AudioPlayer.State.UNLOADED
        self.progress = 0
        self.duration = 0

    def play(self):
        print(f"\nAttempting to play song {self.current_song.name}...\n")
        #Song must be stopped for play to do anything.
        if self.state != AudioPlayer.State.STOPPED:
            if self.state == AudioPlayer.State.FAILED_TO_LOAD:
                print(f"Song state was failed to load. Cannot play {self.current_song.filePath}.")
                return -1
            elif self.state == AudioPlayer.State.PLAYING:
                print(f"Song is already playing. Cannot play {self.current_song.filePath}.")
                return -1
            elif self.state == AudioPlayer.State.PAUSED:
                print(f"Song is currently paused. Use resume() to continue playing. Cannot play {self.current_song.filePath}.")
                return -1
            elif self.state == AudioPlayer.State.UNLOADED:
                print(f"No song loaded. Use load_song() to load a song. Cannot play {self.current_song.filePath}.")
                return -1
            
        try:
            mixer.music.play()
            self.state = AudioPlayer.State.PLAYING
            print(f"Playing {self.current_song.name}")
        except Exception as e:
            print(f"Failed to play song {self.current_song.filePath}.")
            print("Error: ", e)
            self.state = AudioPlayer.State.FAILED_TO_LOAD
            return -1

    def pause(self):
        if self.state == AudioPlayer.State.PLAYING:
            try:
                mixer.music.pause()
                self.state = AudioPlayer.State.PAUSED
            except Exception as e:
                print(f"Failed to pause song {self.current_song.filePath}.")
                print("Error: ", e)
                return -1
            print(f"{self.current_song.name} paused.")
        else:
            print(f"{self.current_song.name} is not playing.")
            return -1

    def resume(self):
        if self.state == AudioPlayer.State.PAUSED:
            try:
                mixer.music.unpause()
                self.state = AudioPlayer.State.PLAYING
            except Exception as e:
                print(f"Failed to resume song {self.current_song.filePath}.")
                print("Error: ", e)
                return -1
            print(f"{self.current_song.name} resumed.")
        else:
            print(f"{self.current_song.name} is not paused.")
            return -1

    def stop(self):
        if self.state == AudioPlayer.State.PLAYING or self.state == AudioPlayer.State.PAUSED:
            try:
                mixer.music.stop()
                self.state = AudioPlayer.State.STOPPED
                self.progress = 0
            except Exception as e:
                print(f"Failed to stop song {self.current_song.filePath}.")
                print("Error: ", e)
                return -1
            print(f"{self.current_song.name} stopped.")
        else:
            print(f"{self.current_song.name} is not playing or paused.")
            return -1

    def togglePause(self):
        if self.state == AudioPlayer.State.PLAYING:
            self.pause()
            print("Song paused.")
        elif self.state == AudioPlayer.State.PAUSED:
            self.resume()
            print("Song resumed.")
        else:
            print("Song is not playing or paused.")

    def getProgress(self):
        if self.state != AudioPlayer.State.UNLOADED and self.state != AudioPlayer.State.FAILED_TO_LOAD:
            self.progress = mixer.music.get_pos() / 1000
        else:
            self.progress = 0

        if self.progress > self.duration:
            self.progress = self.duration
        if self.progress < 0:
            self.progress = 0
        return self.progress
            
        
        
def file_check(file_path:str, project_path:str=None):
    """Check if a file exists in the project folder, cache folder, or the file path.\n
    Player and Creator should set FP.relative_project_path when they load a project file so use that.\n
    """
    #Check if the file exists at the file path
    # print(f"Checking full path: {file_path}")
    if os.path.exists(file_path):
        # print(f"Found {file_path} at full path.")
        return file_path
    
    #Check if the file exists in the project folder
    if project_path != None:
        project_folder = os.path.dirname(project_path)
        path = os.path.join(project_folder, os.path.basename(file_path))
        # print(f"Checking project folder: {path}")
        if os.path.exists(path):
            # print(f"Found {path} in project folder.")
            return os.path.join(path)
        
    #Check if the file exists in the cache folder
    cache_folder = os.path.join(getUserCacheDir(), "cache")
    path = os.path.join(cache_folder, os.path.basename(file_path))
    # print(f"Checking cache: {path}")
    if os.path.exists(path):
        # print(f"Found {path} in cache folder.")
        return os.path.join(path)
    
    print(f"file_check: File {file_path} not found.")
    return MissingImage

def file_loc(file_path:str, project_path:str=None):
    """Check if a file exists in the project folder, cache folder, or the file path.\n
    Return where the file is located.\n
    0 = Full path\n
    1 = Project folder\n
    2 = Cache folder\n
    3 = Missing\n
    """
    #Check if the file exists at the file path
    # print(f"Checking full path: {file_path}")
    if os.path.exists(file_path):
        # print(f"Found {file_path} at full path.")
        return 0
    
    #Check if the file exists in the project folder
    if project_path != None:
        project_folder = os.path.dirname(project_path)
        path = os.path.join(project_folder, os.path.basename(file_path))
        # print(f"Checking project folder: {path}")
        if os.path.exists(path):
            # print(f"Found {path} in project folder.")
            return 1
        
    #Check if the file exists in the cache folder
    cache_folder = os.path.join(getUserCacheDir(), "cache")
    path = os.path.join(cache_folder, os.path.basename(file_path))
    # print(f"Checking cache: {path}")
    if os.path.exists(path):
        # print(f"Found {path} in cache folder.")
        return 2
    
    # print(f"file_loc: File {file_path} not found.")
    return 3
