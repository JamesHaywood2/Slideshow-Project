import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from Widgets import *
from tkinter import filedialog
from PIL import Image, ImageOps
import FileSupport as FP
import random

import time
import copy
import pprint as pp

temp_geometry = None

temp_geometry = None

class SlideshowPlayerStart(tb.Frame):
    def __init__(self, master):
        super().__init__(master)
        try:
            FP.initializeCache()
        except:
            print("Cache initialziation failed")
        tb.Style().theme_use(FP.getPreferences())
        self.master = master
        self.pack(expand=True, fill="both")
        self.label = tb.Label(self, text="Slideshow Player", font=("Arial", 24)).place(relx=0.5, rely=0.15, anchor="center")
        self.openProjectButton = tb.Button(self, text="Open Project", command=self.openProject).place(anchor="center", relx=0.5, rely=0.25)
        self.recentSlideshowList = RecentSlideshowList(self)
        self.recentSlideshowList.place(relx=0.5, rely=0.6, anchor="center", relwidth=0.8, relheight=0.5)

        #Set window size
        self.master.geometry("800x600")
        global temp_geometry 
        temp_geometry  = self.master.geometry()
        #Resizable window false
        self.master.resizable(False, False)

        #Bind double clicking the recentSlideshowList to open the project
        self.recentSlideshowList.tableView.view.bind("<Double-1>", self.openRecentProject)
        return
    
    def openRecentProject(self, event):
        #Get the selected item
        item = self.recentSlideshowList.tableView.view.selection()
        if len(item) == 0:
            return
        #Get the project path
        projectPath = self.recentSlideshowList.tableView.view.item(item, "values")[2]
        # print(f"Opening project: {projectPath}")
        #Open the project
        self.openProjectPath(projectPath)

    def openProject(self):
        """Loads the slideshow creator window with a project file. This will open an existing project."""
        #Create a SlideshowCreator object, destroy the current window, and pack the new window
        projectPath = filedialog.askopenfilename(filetypes=[("Slideshow Files", "*.pyslide")], multiple=False)
        if projectPath == "":
            return
        self.destroy()
        self.update_idletasks()
        self = SlideshowPlayer(self.master, projectPath=projectPath)
        self.pack(expand=True, fill="both")


    def openProjectPath(self, projectPath: str):
        """Loads the slideshow creator window with a project file. This will open an existing project."""
        #Create a SlideshowCreator object, destroy the current window, and pack the new window
        #check if the projectPath even exists
        try:
            with open(projectPath, "r"):
                pass
        except:
            projectPath = "New Project"
        #Check if it's a .pyslide file
        if not projectPath.endswith(".pyslide"):
            projectPath = "New Project"
        self.destroy()
        self.update_idletasks()
        self = SlideshowPlayer(self.master, projectPath=projectPath)
        self.pack(expand=True, fill="both")


class SlideshowPlayer(tb.Frame):
    def __init__(self, master: tk.Tk, debug:bool= False, projectPath: str="New Project", geometry: str=None):
        self.quiting: bool = False
        self.closing: bool = False
        if geometry is not None:
            try:
                master.geometry(geometry)
            except:
                print("Invalid geometry")
        else:
            screen_width = master.winfo_screenwidth()
            screen_height = master.winfo_screenheight()
            master.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
        master.resizable(True, True) #Resizable window

        global temp_geometry 
        temp_geometry  = "800x600"

        # master.attributes("-fullscreen", True) #Fullscreen

        self.dummy = DummyWindow(master)

        master.overrideredirect(True)
        master.state("zoomed")
        master.update_idletasks()
        self.fullscreen:bool = True
        self.fullScreenToggleReady: bool = True

        #Bind escape to exit fullscreen
        master.bind("<Escape>", self.deactivateFullScreen)
        master.bind("<F11>", self.toggleFullScreen)
        master.bind("<Control-q>", self.quit)

        self.START = time.time()
        self.END = time.time()
        super().__init__(master)
        print("\nNEW SLIDESHOW PLAYER\n")
        self.master = master
        #Check if the projectPath even exists
        try:
            with open(projectPath, "r"):
                pass
        except:
            projectPath = "New Project"
        self.slideshow = FP.Slideshow(projectPath)
        self.slideshow.load()
        FP.relative_project_path = self.slideshow.getSaveLocation()
        try:
            FP.initializeCache()
        except:
            print("Cache initialziation failed")
        tb.Style().theme_use(FP.getPreferences())

        # pp.pprint(self.slideshow.__dict__)

        self.debug = debug

        #List of all the slides
        self.slideList: list[FP.Slide] = []
        try:
            self.slideList = self.slideshow.getSlides()
        except:
            print("Error loading slides")

        self.currentSlide:int = 0
        self.manual:bool = True #If false the slideshow will automatically advance to the next slide after a set time.
        self.isPaused: bool = True
        self.shuffleSlideshow:bool = False
        try:
            self.manual = self.slideshow.manual
        except:
            print("Error loading manual setting")

        try:
            self.shuffleSlideshow = self.slideshow.shuffle
        except:
            print("Error loading shuffle setting")

        #If loop setting is indefinite, then really nothing needs to be done.
        #If it is until_playlist_ends, then we need to do a check every time we move to a new song to see if the playlist is over.
        #If it is until_slideshow_ends, then we need to do a check every time we move to a new slide to see if the slideshow is over.
        try:
            self.loopSetting = self.slideshow.loopSettings
        except:
            print("Error loading loop setting")
            self.loopSetting = FP.loopSetting.INDEFINITE

        ######Playlist stuff######
        self.playlist:FP.Playlist = FP.Playlist() #Empty playlist``
        try:
            self.playlist = self.slideshow.getPlaylist()
        except:
            print("Error loading playlists")
        self.currentSong:int = 0
        self.shufflePlaylist:bool = False
        self.playlistExists:bool = False

        if len(self.playlist.songs) > 0:
            print("\nPlaylist found...\n")
            print(f"Playlist: \n{self.playlist.songs}")
            self.playlistExists = True
            try:
                self.shufflePlaylist = self.playlist.shuffle
            except:
                print("Error loading shuffle setting")
        else:
            print("\nNo Playlist was loaded...\n")

        ##### Shuffle stuff #####
        if self.shuffleSlideshow:
            #Randomize the order of the slides
            for slide in self.slideList:
                print(f"Slide: {slide['slideID']}")
            print("Shuffling slideshow")
            random.shuffle(self.slideList)
            for slide in self.slideList:
                print(f"Slide: {slide['slideID']}")
        if self.shufflePlaylist:
            random.shuffle(self.playlist.songs)
            # print("Shuffling playlist")

        # print(f"Playlist: \n{self.playlist.songs}")

        #Create AudioPlayer
        self.audioPlayer = FP.AudioPlayer()
        
        self.audioPlayerEnabled:bool = False
        #Do a test load of all the songs
        print("\nTest loading all songs...\n")
        for song in self.playlist.songs:
            print(f"Loading song: {song.name}")

            #Get the location of the file
            loc = FP.file_loc(song.filePath, FP.relative_project_path)
            if loc == 3:
                #File was just straight up not found anywhere. Remove it from the playlist.
                print(f"File not found: {song.name}")
                self.playlist.songs.remove(song)
                continue

            #If we did find the file, just go ahead and update the filepaths and stuff.
            newpath = FP.file_check(song.filePath, FP.relative_project_path)
            song.filePath = newpath
            song.name = os.path.basename(newpath)

            #Load the song into the audio player
            loaded = self.audioPlayer.loadSong(song)
            if loaded == -2:
                try:
                    cached_path = self.audioPlayer.rewriteWavto16Bit(song.filePath)
                    song.filePath = cached_path
                    song.name = os.path.basename(cached_path)
                except Exception as e:
                    print(f"Error rewriting song: {e}")
                    self.playlist.songs.remove(song)
                    continue
                #reload the song
                loaded = self.audioPlayer.loadSong(song)
            if loaded == -1:
                print(f"Error loading song: {song.name}")
                self.playlist.songs.remove(song)
        print("\nTest loading complete\n")

        #Load first song into the audio player
        if self.playlistExists:
            song = self.playlist.songs[self.currentSong]
            songLoaded:bool = False
            while songLoaded == False and len(self.playlist.songs) > 0:
                loaded = self.audioPlayer.loadSong(song)
                #Try to load a song into the audio player
                print(f"Loading song: {song.name} and loaded: {loaded}")
                if loaded == -1:
                    #If the song failed to load, remove it from the playlist and try the next song.
                    self.playlist.songs.pop(self.currentSong)
                    if self.currentSong < 0:
                        self.currentSong = 0
                    song = self.playlist.songs[self.currentSong]
                else:
                    songLoaded = True

            self.progressBarUpdater = None
            self.audioPlayerEnabled = True

        ########################
        ######   Layout  #######
        ########################
            
        if len(self.slideList) > 0:
            #Add an ImageViewer to the canvas
            self.imageViewer = ImageViewer(self)
            self.imageViewer.pack(expand=True, fill="both")
            self.imageViewer.autoResizeToggle()

            ######
            #Will call the create components method after the window is created and image viewer is packed.
            ######

        else:
            #If there are no slides/project is empty, display a message.
            self.emptyLabel = tb.Label(self, text="Error: No slides in project", font=("Comic Sans MS", 20))
            self.emptyLabel.place(relx=0.5, rely=0.5, anchor="center")
            #Button to open a new project
            self.openButton = tb.Button(self, text="Open Project", command=self.openProject)
            self.openButton.place(relx=0.5, rely=0.6, anchor="center")

        ########################
        ######  MENU BAR #######
        ########################
        self.update()
        #MenuFrame
        self.menuVisible: bool = False
        style = tb.Style()
        style.configure("custom.TFrame", background=style.colors.primary)
        self.menuFrame = tb.Frame(self, style="custom.TFrame")
        self.menuFrame.place(relx=0.5, anchor="n", relwidth=1)
        self.menuFrame.place_forget()

        #MenuButtons
        style.configure('TMenubutton', arrowsize=0, relief=FLAT, arrowpadding=0, font=("Arial", 10))
        self.fileMB = tb.Menubutton(self.menuFrame, text="Project", style="TMenubutton")
        self.fileMB.pack(side="left")
        self.fileMenu = tb.Menu(self.fileMB, tearoff=0)
        self.fileMenu.config(background=style.colors.primary, foreground=style.colors.get("selectfg"))
        self.fileMenu.add_command(label="Open", command=self.openProject)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.quit)
        self.fileMenu.add_command(label="Open Filles", command=self.printOpenFiles)
        self.fileMB.config(menu=self.fileMenu)

        style.configure('TCheckbutton', font=("Arial", 10), background=style.colors.primary, foreground=style.colors.get("selectfg"))
        #Create a checkbutton to toggle audio
        self.audioCheckbutton = tb.Checkbutton(self.menuFrame, style="TCheckbutton", text="Enable Audio", command=self.toggleAudio)
        self.audioCheckbutton.pack(side="left", padx=3)
        #Check if the audio player is enabled
        if self.playlistExists:
            self.audioCheckbutton.state(["!disabled"])
            self.audioCheckbutton.state(["!alternate"])
            self.audioCheckbutton.state(["selected"])
        else:
            self.audioCheckbutton.state(["disabled"])

        #Create a checkbutton to toggle fullscreen
        self.fullscreenCheckbutton = tb.Checkbutton(self.menuFrame, style="TCheckbutton", text="Fullscreen", command=self.toggleFullScreen)
        self.fullscreenCheckbutton.pack(side="left", padx=3)
        #Set the checkbutton to the correct state
        self.fullscreenCheckbutton.state(["!alternate"])
        self.fullscreenCheckbutton.state(["selected"])

        


        #After variable to keep track of slide changes.
        self.slideChangeAfter = None
        self.transition_checker = None

        #Bind a configure event to the window so we can create the components after the window is resized.
        self.bind("<Configure>", lambda e: self.createComponents())

        return
    
    def toggleAudio(self):
        self.pause(True)
        if self.audioPlayerEnabled:
            self.audioPlayerEnabled = False
            self.hideProgressBar()
        else:
            self.audioPlayerEnabled = True
        self.update()
        self.update_ProgressBar()
        self.showOverlay()
        return
    
    def printOpenFiles(self):
        print("\nOpen Files:\n")
        for f in FP.openFiles.keys():
            print(f)
        print(f"\nTotal: {len(FP.openFiles)}\n")
        return

    def renderImages(self):
        ###### PRE-RENDER THE IMAGES ######
        if len(self.slideList) > 0:
            print("\nRendering images...\n")
            canvas_width = self.imageViewer.canvasWidth
            canvas_height = self.imageViewer.canvasHeight
            #We want to get every slide image in the slideshow and prepare them for display.
            self.ImageMap = {} #Key: Slide number, name of the image file in the cache
            self.ImageList = {}
            max_width = -1
            max_height = -1
            for slide in self.slideList:
                #Open the image and convert it etc etc and resize it to the max canvas size.
                pth = FP.file_check(slide['imagePath'], FP.relative_project_path)
                try:
                    slideImage = Image.open(pth)
                except:
                    print(f"Error loading image: {pth}")
                    slideImage = Image.open(FP.MissingImage)

                #Open the files
                try:
                    f = open(pth, "rb")
                    FP.openFiles[pth] = f
                except:
                    print(f"Error opening file: {pth}")

                slideImage = ImageOps.exif_transpose(slideImage).convert("RGBA")
                slideImage.thumbnail((canvas_width, canvas_height), resample=Image.NEAREST, reducing_gap=3)
                #Add the image to the list
                self.ImageList[slide['slideID']] = slideImage

                #check if the image is the largest so far
                if slideImage.width > max_width:
                    max_width = slideImage.width
                if slideImage.height > max_height:
                    max_height = slideImage.height

            self.update_idletasks()

            #Create a background image at the size of the max image sizes and then paste the images in the center.
            #This is done so all images are the exact same size and transitions are consistent in positioning and stuff.
            for slide in self.slideList:
                i = slide['slideID']
                bg = Image.new("RGBA", (max_width, max_height), (255, 255, 255, 0))
                x, y = (bg.width - self.ImageList[i].width) // 2, (bg.height - self.ImageList[i].height) // 2
                bg.paste(self.ImageList[i], (x, y), self.ImageList[i])
                self.ImageMap[i] = bg
            
            #clear the ImageList
            self.ImageList = {}
            del self.ImageList
    
    def createComponents(self):
        #Unbind the configure event so it doesn't keep creating components. This method gets called once.
        self.unbind("<Configure>")
        self.update_idletasks()
        #Only construct the layout if the project is not empty of slides.
        # if len(self.slideList) > 0:
        #Add first slide to the ImageViewer
        if len(self.slideList) > 0:
            pth = FP.file_check(self.slideList[self.currentSlide]['imagePath'], FP.relative_project_path)
            print(f"First slide: {pth}")
            self.imageViewer.loadImage(pth)

            #Render the images
            self.renderImages()
        
        self.update_idletasks()

        #Add next and previous buttons using place.
        self.nextButton = tb.Button(self, text="Next", command=self.nextSlide)
        self.prevButton = tb.Button(self, text="Previous", command=self.prevSlide)
        self.pauseButton = tb.Button(self, text="Play", command=self.pause)

        #Add a slide counter in the top right corner
        self.slideMeterBroken: bool = False

        #Add a slide counter in the top right corner using a bootstrap meter
        #Go into ttkboostrap/widgets.py line 856 and change CUBIC to BICUBIC to get it to work
        try:
            if len(self.slideList) > 0:
                self.slideCounter = tb.Meter(self, 
                                     bootstyle="primary",
                                     metersize=100,
                                     textright=f"/{len(self.slideList)}",
                                     metertype="semi",
                                     amounttotal=len(self.slideList),
                                     amountused=self.currentSlide+1,
                                     stripethickness=0,)
            # self.slideCounter.place(relx=1, rely=0, anchor="ne")
        except:
            self.slideMeterBroken = True
            self.slideCounter = tb.Label(self, text=f"Slide {self.currentSlide+1}/{len(self.slideList)}")
            # self.slideCounter.place(relx=0.95, rely=0.05, anchor="center")
            #Throw an error message: f"Error: Slide meter broken. Please go into ttkboostrap/widgets.py line 856 and change CUBIC to BICUBIC to get it to work.\n Defaulting to label."
            print(f"\nError: Slide meter broken. Please go into ttkboostrap/widgets.py line 856 and change CUBIC to BICUBIC to get it to work.\n Defaulting to label.\n")
        
        if len(self.slideList) > 0:
            self.showButtons()
            self.showSlideCounter()

        if self.playlistExists:
            #Add a tb.Progressbar to the bottom of the screen
            self.progressBar = tb.Progressbar(self, orient="horizontal", mode="determinate")
            self.progressBar["value"] = 0
            self.progressBar_maxLabel = tb.Label(self, text="0:00", font=("Arial", 12))
            self.progressBar_progressLabel = tb.Label(self, text="0:00", font=("Arial", 12))
            self.songLabel = tb.Label(self, text=self.playlist.songs[self.currentSong].name, font=("Arial", 12))

            #Next song buttons should use Left and Right arrow characters
            self.nextSongButton = tb.Button(self, text="⮞", command=self.nextSong)
            self.previousSongButton = tb.Button(self, text="⮜", command=self.previousSong)

            if len(self.slideList) > 0:
                self.showProgressBar()
                self.update_ProgressBar()    
            
        self.master.bind("<Right>", lambda e: self.nextSlide())
        self.master.bind("<Left>", lambda e: self.prevSlide())
        self.master.bind("<space>", lambda e: self.pause())
        self.master.bind("<h>", lambda e: self.hideOverlay())
        self.mouse_after_id = None
        self.master.bind("<Motion>", self.motionEvent)

        #bind t to toggle pause the music, y to next song, u to previous song
        #Remove later just for testing right now
        self.master.bind("<t>", lambda e: self.pause())
        self.master.bind("<y>", lambda e: self.nextSong())
        self.master.bind("<r>", lambda e: self.previousSong())
        self.master.bind("<e>", lambda e: self.pause(True))

        self.master.bind("<Destroy>", self.close)
        self.master.protocol("WM_DELETE_WINDOW", self.quit)

    def motionEvent(self, event):
        #Get the mouse position
        x = event.x
        y = event.y
        # print(f"Mouse at: {x}, {y}")
        #If the mouse is at the top of the screen, show the menu
        try:
            if self.menuVisible == False and y < 10:
                self.menuFrame.place(relx=0.5, anchor="n", relwidth=1)
                self.menuVisible = True
            elif self.menuVisible == True and y > 30:
                self.menuFrame.place_forget()
                self.menuVisible = False
        except Exception as e:
            print(f"Error showing menu: {e}")
            
            
            
        #If there are no slides, return
        try:
            if len(self.slideList) == 0:
                return
        except:
            return
        self.showOverlay()
        if self.mouse_after_id:
            self.after_cancel(self.mouse_after_id)
        self.mouse_after_id = self.after(2500, self.hideOverlay)
        return
    
    

    def hideButtons(self):
        self.nextButton.place_forget()
        self.prevButton.place_forget()
        self.pauseButton.place_forget()
    
    def hideProgressBar(self):
        self.progressBar.place_forget()
        self.progressBar_maxLabel.place_forget()
        self.progressBar_progressLabel.place_forget()
        self.songLabel.place_forget()
        self.nextSongButton.place_forget()
        self.previousSongButton.place_forget()


    def hideOverlay(self):
        #Hide slide buttons
        self.hideButtons()
        self.slideCounter.place_forget()

        if self.playlistExists:
            self.hideProgressBar()
        
        self.master.bind("<h>", lambda e: self.showOverlay())
        self.config(cursor="none")
        return

    def showOverlay(self):
        #Show slide buttons
        self.showButtons()
        self.showSlideCounter()

        if self.playlistExists:
            self.showProgressBar()

        self.master.bind("<h>", lambda e: self.hideOverlay())
        self.config(cursor="")
        return
    
    def showProgressBar(self):
        if self.audioPlayerEnabled == False:
            return
        if self.fullscreen:
            self.progressBar_maxLabel.place(anchor="sw", relx=0.97, rely=1, relheight=0.02)
            self.progressBar.place(anchor="se", relx=0.97, rely=1, relwidth=0.83, relheight=0.02)
            self.progressBar_progressLabel.place(anchor="se", relx=0.14, rely=1, relheight=0.02)

            #Bottom left corner
            self.previousSongButton.place(anchor="sw", relx=0.01, rely=1, relwidth=0.05, relheight=0.025)
            self.nextSongButton.place(anchor="sw", relx=0.06, rely=1, relwidth=0.05, relheight=0.025)

            #height of previousSongButton
            y=float(self.previousSongButton.winfo_height()/self.master.winfo_height())
            self.songLabel.config(font=("Arial", 12))

            self.songLabel.place(anchor="sw", relx=0.01, rely=1-y)
        else:
            self.progressBar.place(relwidth=0.9, relheight=0.02, anchor="sw", relx=0.1, rely=1)
            self.progressBar_maxLabel.place(relx=1, rely=0.98, anchor="se")
            self.progressBar_progressLabel.place(relx=0.1, rely=0.98, anchor="sw")

            #Bottom left corner
            self.previousSongButton.place(anchor="se", relx=0.05, rely=1, relwidth=0.05)
            self.nextSongButton.place(anchor="se", relx=0.1, rely=1, relwidth=0.05)

            #height of previousSongButton
            y=float(self.progressBar.winfo_height()/self.master.winfo_height())
            x=float(self.progressBar_maxLabel.winfo_width()/self.master.winfo_width())


            songlabelWidth = (1-.6-.06-x) * self.master.winfo_width()
            if songlabelWidth < 200:
                self.songLabel.config(font=("Arial", 8))
            elif songlabelWidth < 300:
                self.songLabel.config(font=("Arial", 10))
            else:
                self.songLabel.config(font=("Arial", 12))
            self.songLabel.place(anchor="se", relx=1-x, rely=1-y)



    def showButtons(self):
        if self.audioPlayerEnabled:
            if self.fullscreen:
                #Center of screen
                self.pauseButton.place(anchor="s", relx=0.5, rely=0.980, relwidth=0.12)
                self.nextButton.place(anchor="s", relx=0.6, rely=0.980, relwidth=0.12)
                self.prevButton.place(anchor="s", relx=0.4, rely=0.980, relwidth=0.12)
            else:
                #Center of screen
                self.pauseButton.place(anchor="s", relx=0.5, rely=0.98, relwidth=0.12)
                self.nextButton.place(anchor="s", relx=0.6, rely=0.98, relwidth=0.12)
                self.prevButton.place(anchor="s", relx=0.4, rely=0.98, relwidth=0.12)
        else:
            if self.fullscreen:
                #Center of screen
                self.pauseButton.place(anchor="s", relx=0.5, rely=1, relwidth=0.12)
                self.nextButton.place(anchor="s", relx=0.6, rely=1, relwidth=0.12)
                self.prevButton.place(anchor="s", relx=0.4, rely=1, relwidth=0.12)
            else:
                #Center of screen
                self.pauseButton.place(anchor="s", relx=0.5, rely=1, relwidth=0.12)
                self.nextButton.place(anchor="s", relx=0.6, rely=1, relwidth=0.12)
                self.prevButton.place(anchor="s", relx=0.4, rely=1, relwidth=0.12)
                
        # if self.audioPlayerEnabled == False and self.manual == True:
        #     self.pauseButton.place_forget()

        # if len(self.slideList) < 2:
        #     self.nextButton.place_forget()
        #     self.prevButton.place_forget()
        #     if self.audioPlayerEnabled == False:
        #         self.pauseButton.place_forget()
            
    
    def showSlideCounter(self):
        if not self.slideMeterBroken:
            self.slideCounter.place(relx=1, rely=0, anchor="ne")
        else:
            self.slideCounter.place(relx=0.95, rely=0.05, anchor="center")

    def openProject(self):
        file = filedialog.askopenfilenames(filetypes=[("SlideShow Files", "*.pyslide")], multiple=False)
        #If not file was selected, return. Effectively cancels.
        if not file:
            return
        
        #Clear FP.openFiles
        for f in FP.openFiles.keys():
            FP.openFiles[f].close()
        
        #Destroy every child widget
        for widget in self.master.winfo_children():
            widget.destroy()

        if self.dummy:
            self.dummy.destroy()

        #Clear the ImageMap
        self.ImageMap = {}
        self.ImageList = {}
        self.slideList = []
        FP.openFiles = {}
        self.playlist = FP.Playlist()
        del self.slideshow
        del self.slideList
        del self.ImageMap
        del self.ImageList
        del self.playlist
        del self.dummy
        
        #Stop any loops
        try:
            if self.slideChangeAfter:
                self.after_cancel(self.slideChangeAfter)
        except:
            pass
        try:
            if self.progressBarUpdater:
                self.after_cancel(self.progressBarUpdater)
        except:
            pass
        try:
            if self.transition_checker:
                self.after_cancel(self.transition_checker)
        except:
            pass
        try:
            if self.mouse_after_id:
                self.after_cancel(self.mouse_after_id)
        except:
            pass

        self.pack_forget()
        self.destroy()
        self.update_idletasks()
 
        self = SlideshowPlayer(self.master, projectPath=file[0])
        self.pack(expand=True, fill="both")


    def checkTransition(self, imagePath: str):
        if self.imageViewer.transitioning:
            self.transition_checker = self.after(1, self.checkTransition, imagePath)
        else:
            #Once transitioning is complete, make sure the correct image is displayed.
            try:
                self.after_cancel(self.transition_checker)
            except:
                pass
            self.transition_checker = None
            self.END = time.time()

            #If the transition was default
            if self.slideList[self.currentSlide]['transition'] == FP.transitionType.DEFAULT:
                print(f"Transition took {(self.END - self.START) * 1000:.2f}ms and {self.imageViewer.frameCounter} frames.")
                print(f"Total transition time: {self.imageViewer.totalTransitionTime:.2f}ms")
            else:
                print(f"Transition took {(self.END - self.START) * 1000:.2f}ms and {self.imageViewer.frameCounter} frames.")
                print(f"Total transition time: {self.imageViewer.totalTransitionTime:.2f}ms")
                print(f"Averge frame time: {self.imageViewer.totalTransitionTime / self.imageViewer.frameCounter:.2f}ms")

            self.imageViewer.loadImagePIL(copy.deepcopy(self.ImageMap[self.slideList[self.currentSlide]['slideID']]))
            self.automaticNext()

    def nextSlide(self):
        print("")
        #Launch a motion event to show the overlay
        # self.event_generate("<Motion>")
        self.START = time.time()
        if self.imageViewer.transitioning:
            self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])
            return
        
        #Next slide is the slide we are going to. previous slide is the slide we are transitioning from (currently on)
        previousSlide = self.slideList[self.currentSlide]
        if self.currentSlide == len(self.slideList)-1 and self.loopSetting == FP.loopSetting.UNTIL_SLIDES_END:
            self.pause(True)
            return
        self.currentSlide = (self.currentSlide + 1) % len(self.slideList)
        nextSlide = self.slideList[self.currentSlide]

        #Print the canvas size
        print(f"Canvas size: {self.imageViewer.canvasWidth}x{self.imageViewer.canvasHeight}")



        #Gets the slide we're transitioning to and the previous slide.
        #Then gets the images and correctly sizes them.
        transition = nextSlide['transition']
        transitionSpeed = nextSlide['transitionSpeed'] * 1000
        # transitionSpeed = 10000

        previous_ID = previousSlide['slideID']
        next_ID = nextSlide['slideID']

        #Load from memory using deepcopy
        previousImage: Image = copy.deepcopy(self.ImageMap[previous_ID])
        nextImage: Image = copy.deepcopy(self.ImageMap[next_ID])

        print(f"Transitioning from {previous_ID} to {next_ID} with transition {transition} at speed {transitionSpeed}ms")
        #It will then execute the transition and do a constant check to see if the transition is complete.
        self.START = time.time()
        self.imageViewer.executeTransition(transition, transitionSpeed, endImg=nextImage, startImg=previousImage)
        self.imageViewer.after(10, self.checkTransition, nextSlide['imagePath'])
        print(f"Loaded {nextSlide['imagePath']} into viewer")


        #Update the slide counter
        if not self.slideMeterBroken:
            try:
                self.slideCounter.amountusedvar.set(self.currentSlide+1)
            except:
                self.slideMeterBroken = True
                print("Slide meter broken")
                try:
                    #Destroy the old meter
                    self.slideCounter.destroy()
                    self.slideCounter = tb.Label(self, text=f"Slide {self.currentSlide+1}/{len(self.slideList)}")
                    self.slideCounter.place(relx=0.95, rely=0.05, anchor="center")
                except:
                    print("Something is seriously wrong lmao")
        try:
            self.slideCounter.config(text=f"Slide {self.currentSlide+1}/{len(self.slideList)}")
        except:
            pass

        return
        
    def automaticNext(self):
        if not self.manual and not self.isPaused:
            #Automatic transitions
            if self.slideChangeAfter:
                self.after_cancel(self.slideChangeAfter)
            changeTime = self.slideList[self.currentSlide]['duration']
            #Clamp to range of 1-60 seconds
            if changeTime < 1:
                changeTime = 1
            elif changeTime > 60:
                changeTime = 60
            changeTime = int(changeTime * 1000)
            self.slideChangeAfter = self.after(changeTime, self.nextSlide)
            print(f"Next slide in {changeTime}ms")

        print(f"Current slide: {self.slideList[self.currentSlide]}\n")
        return
    
    def prevSlide(self):
        print("")
        # self.event_generate("<Motion>")
        self.START = time.time()
        #If a transition is in progress, cancel it and just load the image before returning.
        if self.imageViewer.transitioning:
            self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])
            return
        
        #Next slide is the slide we are going to. previous slide is the slide we are transitioning from (currently on)
        previousSlide = self.slideList[self.currentSlide]
        self.currentSlide = (self.currentSlide - 1) % len(self.slideList)
        nextSlide = self.slideList[self.currentSlide]
        
        reverseTransitionDict = {
            FP.transitionType.FADE: FP.transitionType.FADE,
            FP.transitionType.WIPELEFT: FP.transitionType.WIPERIGHT,
            FP.transitionType.WIPERIGHT: FP.transitionType.WIPELEFT,
            FP.transitionType.WIPEDOWN: FP.transitionType.WIPEUP,
            FP.transitionType.WIPEUP: FP.transitionType.WIPEDOWN,
            FP.transitionType.DEFAULT: FP.transitionType.DEFAULT
        }
            

        #Gets the slide we're transitioning to and the previous slide.
        #Then gets the images and correctly sizes them.
        transition = reverseTransitionDict[previousSlide['transition']]
        transitionSpeed = nextSlide['transitionSpeed']
        #Clamp to range of 0.5-10 seconds
        if transitionSpeed < 0.5:
            transitionSpeed = 0.5
        elif transitionSpeed > 10:
            transitionSpeed = 10
        transitionSpeed = int(transitionSpeed * 1000)

        previous_ID = previousSlide['slideID']
        next_ID = nextSlide['slideID']
        #Load from memory using deepcopy
        previousImage: Image = copy.deepcopy(self.ImageMap[previous_ID])
        nextImage: Image = copy.deepcopy(self.ImageMap[next_ID])

        print(f"Transitioning from {previous_ID} to {next_ID} with transition {transition} at speed {transitionSpeed}ms")

        #It will then execute the transition and do a constant check to see if the transition is complete.
        self.START = time.time()
        self.imageViewer.executeTransition(transition, transitionSpeed, endImg=nextImage, startImg=previousImage)
        self.checkTransition(nextSlide['imagePath'])

        #Update the slide counter
        if not self.slideMeterBroken:
            try:
                self.slideCounter.amountusedvar.set(self.currentSlide+1)
            except:
                self.slideMeterBroken = True
                print("Slide meter broken")
                try:
                    #Destroy the old meter
                    self.slideCounter.destroy()
                    self.slideCounter = tb.Label(self, text=f"Slide {self.currentSlide+1}/{len(self.slideList)}")
                    self.slideCounter.place(relx=0.95, rely=0.05, anchor="center")
                except:
                    print("Something is seriously wrong lmao")
        try:
            self.slideCounter.config(text=f"Slide {self.currentSlide+1}/{len(self.slideList)}")
        except:
            pass
        return
    
    def pause(self, paused:bool=None):
        #Will pause the music and slideshow.
        if paused is None:
            self.isPaused = not self.isPaused
        else:
            if paused:
                self.isPaused = True
            else:
                self.isPaused = False
                print("Resuming slideshow")


        print(f"Pausing state: {self.isPaused}")
        self.update_idletasks()

        if self.isPaused:
            print("Pausing slideshow")
            #Set slideshow to pause
            self.pauseButton.config(text="Play")
            if not self.manual: #If the slideshow is automatic transition and you pause, stop that transition.
                try:
                    self.after_cancel(self.slideChangeAfter)
                except:
                    pass
            self.update_idletasks()
            
            #Audio player
            if self.playlistExists and self.audioPlayerEnabled:
                #If the audio Player is playing, pause it.
                if self.audioPlayer.state == FP.AudioPlayer.State.PLAYING:
                    self.audioPlayer.pause()
        else: 
            print("Resuming slideshow")
            #Set slideshow to start playing
            self.pauseButton.config(text="Pause")
            self.automaticNext()
            
            self.update_idletasks()

            #Audio player
            if self.playlistExists and self.audioPlayerEnabled:
                #If the audio Player is paused, play it.
                if self.audioPlayer.state == FP.AudioPlayer.State.PAUSED:
                    self.audioPlayer.resume()
                elif self.audioPlayer.state == FP.AudioPlayer.State.STOPPED:
                    played = self.audioPlayer.play()
                    if played == -1:
                        self.nextSong()

        self.showOverlay()
        return
    
    def update_ProgressBar(self):
        if self.playlistExists:
            if self.audioPlayerEnabled == False:
                self.audioPlayer.stop()
                return
            #Update the progress bar
            progress = self.audioPlayer.getProgress()
            # print(f"Progress: {progress} / {self.audioPlayer.duration}")
            self.progressBar["value"] = progress
            self.progressBar['maximum'] = self.audioPlayer.duration
            self.progressBar_maxLabel.config(text=FP.formatTime(self.audioPlayer.duration))
            self.progressBar_progressLabel.config(text=FP.formatTime(self.audioPlayer.progress))


            #If the song is over, move to the next song.
            if self.audioPlayer.isFinished():
                self.nextSong()

            self.progressBarUpdater = self.after(120, self.update_ProgressBar)
            # print(f"Progress: {self.audioPlayer.getProgress()} / {self.audioPlayer.duration}")
        return
    
    def nextSong(self):
        if self.playlistExists:
            #Check and see if any songs are even in the playlist.
            if len(self.playlist.songs) == 0:
                print("No songs in playlist")
                self.playlistExists = False
                self.audioPlayerEnabled:bool = False
                return

            self.currentSong += 1
            #If we're at the end of the playlist, loop back to the beginning.
            if self.currentSong > len(self.playlist.songs)-1:
                #If the loop setting is until_playlist_ends, then stop the slideshow.
                if self.loopSetting == FP.loopSetting.UNTIL_PLAYLIST_ENDS:
                    self.pause(True)
                self.currentSong = 0
            song = self.playlist.songs[self.currentSong]
            #unload the current song
            # self.audioPlayer.stop()

            self.update_idletasks()
            if self.audioPlayer.loadSong(song) == -1:
                self.nextSong()
                # self.playlist.songs.pop(self.currentSong)
                # self.currentSong -= 1
                return
            else:
                self.songLabel.config(text=song.name)
                print(f"{song.name} loaded successfully")


            self.update_idletasks
            #If the slideshow is playing, play the song.
            if not self.isPaused:
                self.audioPlayer.play()
        return
    
    def previousSong(self):
        if self.playlistExists:
            #Check and see if any songs are even in the playlist.
            if len(self.playlist.songs) == 0:
                print("No songs in playlist")
                self.playlistExists = False
                self.audioPlayerEnabled:bool = False
                return

            self.currentSong -= 1
            #If we're at the beginning of the playlist, loop back to the end.
            if self.currentSong < 0:
                self.currentSong = len(self.playlist.songs)-1
            song = self.playlist.songs[self.currentSong]
            #unload the current song
            # self.audioPlayer.stop()

            self.update_idletasks()
            if self.audioPlayer.loadSong(song) == -1:
                #If the song failed to load, move to the next song and remove the current song from the playlist
                self.previousSong()
                # self.playlist.songs.pop(self.currentSong)
                # self.currentSong -= 1
                return
            else:
                self.songLabel.config(text=song.name)
                print(f"{song.name} loaded successfully")

            self.update_idletasks()
            #If the slideshow is playing, play the song.
            if not self.isPaused:
                self.audioPlayer.play()
        return
    
    def quit(self, event=None):
        if self.quiting:
            return
        print("\nQuitting Player...\n")
        self.quiting = True
        self.audioPlayer.stop()

        #Stop any loops
        try:
            if self.slideChangeAfter:
                self.after_cancel(self.slideChangeAfter)
        except:
            pass
        try:
            if self.progressBarUpdater:
                self.after_cancel(self.progressBarUpdater)
        except:
            pass
        try:
            if self.transition_checker:
                self.after_cancel(self.transition_checker)
        except:
            pass
        try:
            if self.mouse_after_id:
                self.after_cancel(self.mouse_after_id)
        except:
            pass

        self.dummy.close(False)
        self.master.destroy()
        self.update()
        return
    
    def close(self, event=None):
        if self.closing:
            return
        print("\nClosing...\n")
        self.closing = True
        self.audioPlayer.stop()
        #Close all open files
        for f in FP.openFiles.values():
            f.close()

        #Stop any loops
        try:
            if self.slideChangeAfter:
                self.after_cancel(self.slideChangeAfter)
        except:
            pass
        try:
            if self.progressBarUpdater:
                self.after_cancel(self.progressBarUpdater)
        except:
            pass
        try:
            if self.transition_checker:
                self.after_cancel(self.transition_checker)
        except:
            pass
        try:
            if self.mouse_after_id:
                self.after_cancel(self.mouse_after_id)
        except:
            pass

        self.dummy.close(False)
        self.update()
        self.destroy()
        return

    def toggleFullScreen(self, event=None):
        if self.fullScreenToggleReady:
            self.fullScreenToggleReady = False
            if self.fullscreen:
                self.deactivateFullScreen()
                self.fullscreenCheckbutton.state(["!selected"])
            else:
                self.activateFullScreen()
                self.fullscreenCheckbutton.state(["selected"])
        return

    def activateFullScreen(self, event=None):
        print("Activating fullscreen")
        self.fullscreenCheckbutton.state(["selected"])
        self.master.update()
        self.fullscreen = True
        global temp_geometry 
        temp_geometry = self.master.geometry()
        self.master.overrideredirect(True)
        self.master.state('zoomed')
        self.master.update()
        self.dummy.deiconify()
        self.master.update_idletasks()
        #Update the canvas size
        self.imageViewer.canvasWidth = self.master.winfo_width()
        self.imageViewer.canvasHeight = self.master.winfo_height()
        self.imageViewer.update_idletasks()
        self.renderImages()
        self.master.update()
        self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])
        self.master.update()
        self.hideOverlay()
        self.showOverlay()
        self.master.update_idletasks()
        self.after(50, self.__set_fullscreen_toggle_ready)

    def __set_fullscreen_toggle_ready(self):
        self.fullScreenToggleReady = True

    def deactivateFullScreen(self, event=None):
        print("Deactivating fullscreen")
        #Pause the slideshow
        self.pause(True)
        self.fullscreenCheckbutton.state(["!selected"])
        self.master.update()
        self.fullscreen = False
        self.master.overrideredirect(False)
        self.master.state('normal')
        self.update()
        self.dummy.withdraw()
        self.master.update_idletasks()
        global temp_geometry 
        self.master.geometry(temp_geometry )
        self.master.update()
        #Just load the image
        self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])
        self.master.update()
        self.hideOverlay()
        self.showOverlay()
        self.master.update_idletasks()
        self.after(50, self.__set_fullscreen_toggle_ready)

class DummyWindow(tb.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master = master
        
        self.title("PySlide Viewer")
        #Alpha to 0
        self.attributes("-alpha", 0)
        self.geometry("700x700")
        

        self.master = master

        #The idea here is that when you do overrideredirect(True) and state("zoomed") on the master window, the dummy window will be "visible" so it's still on the taskbar.

        #Bind focus in event for the dummy window to focus the master window
        self.bind("<FocusIn>", self.focusIn)

        self.protocol("WM_DELETE_WINDOW", lambda: self.close(True))

    def close(self, quit: bool):
        print("\nClosing dummy window...\n")
        self.update()
        self.destroy()
        if quit:
            self.master.destroy()
        return


    def focusIn(self, event):
        #Bring the master window to the front
        self.master.lift()
        #Focus the master window
        self.master.focus_set()


    def toggleFullScreen(self, event=None):
        if self.fullScreenToggleReady:
            self.fullScreenToggleReady = False
            if self.fullscreen:
                self.deactivateFullScreen()
                self.fullscreenCheckbutton.state(["!selected"])
            else:
                self.activateFullScreen()
                self.fullscreenCheckbutton.state(["selected"])
        return

    def activateFullScreen(self, event=None):
        print("Activating fullscreen")
        self.fullscreenCheckbutton.state(["selected"])
        self.master.update()
        self.fullscreen = True
        global temp_geometry 
        temp_geometry = self.master.geometry()
        self.master.overrideredirect(True)
        self.master.state('zoomed')
        self.master.update()
        self.dummy.deiconify()
        self.master.update_idletasks()
        #Update the canvas size
        self.imageViewer.canvasWidth = self.master.winfo_width()
        self.imageViewer.canvasHeight = self.master.winfo_height()
        self.imageViewer.update_idletasks()
        self.renderImages()
        self.master.update()
        self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])
        self.master.update()
        self.hideOverlay()
        self.showOverlay()
        self.master.update_idletasks()
        self.after(50, self.__set_fullscreen_toggle_ready)

    def __set_fullscreen_toggle_ready(self):
        self.fullScreenToggleReady = True

    def deactivateFullScreen(self, event=None):
        print("Deactivating fullscreen")
        #Pause the slideshow
        self.pause(True)
        self.fullscreenCheckbutton.state(["!selected"])
        self.master.update()
        self.fullscreen = False
        self.master.overrideredirect(False)
        self.master.state('normal')
        self.update()
        self.dummy.withdraw()
        self.master.update_idletasks()
        global temp_geometry 
        self.master.geometry(temp_geometry )
        self.master.update()
        #Just load the image
        self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])
        self.master.update()
        self.hideOverlay()
        self.showOverlay()
        self.master.update_idletasks()
        self.after(50, self.__set_fullscreen_toggle_ready)

class DummyWindow(tb.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master = master
        
        self.title("PySlide Viewer")
        #Alpha to 0
        self.attributes("-alpha", 0)
        self.geometry("700x700")
        

        self.master = master

        #The idea here is that when you do overrideredirect(True) and state("zoomed") on the master window, the dummy window will be "visible" so it's still on the taskbar.

        #Bind focus in event for the dummy window to focus the master window
        self.bind("<FocusIn>", self.focusIn)

        self.protocol("WM_DELETE_WINDOW", lambda: self.close(True))

    def close(self, quit: bool):
        print("\nClosing dummy window...\n")
        self.update()
        self.destroy()
        if quit:
            self.master.quit()
        return


    def focusIn(self, event):
        #Bring the master window to the front
        self.master.lift()
        #Focus the master window
        self.master.focus_set()



if __name__ == "__main__":
    root = tb.Window()
    root.title("Slideshow Viewer")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
    #minimum size
    root.minsize(600, 500)
    # app = SlideshowPlayer(root, projectPath=r"C:\Users\JamesH\OneDrive - uah.edu\CS499\TestImages3\Kitty.pyslide")
    app = SlideshowPlayerStart(root)
    app.pack(expand=True, fill="both")

    app.mainloop()

    