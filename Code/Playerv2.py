import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from Widgets import *
from tkinter import filedialog
import FileSupport as FP


class SlideshowPlayer(tb.Frame):
    def __init__(self, master, debug:bool= False, projectPath: str="New Project"):
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
        try:
            FP.initializeCache()
        except:
            print("Cache initialziation failed")
        tb.Style().theme_use(FP.getPreferences())

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
        self.loopSlideshow:bool = False
        self.shuffleSlideshow:bool = False
        try:
            self.manual = self.slideshow.manual
            print(f"Manual: {self.manual}")
        except:
            print("Error loading manual setting")

        try:
            self.loopSlideshow = self.slideshow.loop
            print(f"Loop Slideshow: {self.loopSlideshow}")
        except:
            print("Error loading loop setting")
        try:
            self.shuffleSlideshow = self.slideshow.shuffle
            print(f"Shuffle Slideshow: {self.shuffleSlideshow}")
        except:
            print("Error loading shuffle setting")

        ######Playlist stuff
        self.playlist: list[FP.Playlist] = []
        try:
            self.playlist = self.slideshow.getPlaylist()
        except:
            print("Error loading playlists")
        self.currentSong:int = 0
        self.shufflePlaylist:bool = False
        self.loopPlaylist:bool = False
        self.playlistExists:bool = False
        if len(self.playlist.songs) > 0:
            print("Playlist exists")
            self.playlistExists = True
            try:
                self.shufflePlaylist = self.playlist.shuffle
                print(f"Shuffle Playlist: {self.shufflePlaylist}")
            except:
                print("Error loading shuffle setting")
            try:
                self.loopPlaylist = self.playlist.loop
                print(f"Loop Playlist: {self.loopPlaylist}")
            except:
                print("Error loading loop setting")

        ########################
        ######   Layout  #######
        ########################

        #Only construct the layout if the project is not empty of slides.
        if len(self.slideList) > 0:
            #Add an ImageViewer to the canvas
            self.imageViewer = ImageViewer(self)
            self.imageViewer.pack(expand=True, fill="both")
            #Add first slide to the ImageViewer
            self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])
            self.imageViewer.autoResizeToggle()

            #Add next and previous buttons using place.
            self.nextButton = tb.Button(self, text="Next", command=self.nextSlide)
            self.nextButton.place(relx=0.8, rely=0.85, anchor="center")
            self.prevButton = tb.Button(self, text="Previous", command=self.prevSlide)
            self.prevButton.place(relx=0.2, rely=0.85, anchor="center")

            #Pause button
            self.pauseButton = tb.Button(self, text="Play", command=self.pause)
            self.pauseButton.place(relx=0.5, rely=0.85, anchor="center")

            #Add a slide counter in the top right corner
            self.slideCounter = tb.Label(self, text=f"Slide {self.currentSlide+1}/{len(self.slideList)}")
            self.slideCounter.place(relx=0.95, rely=0.05, anchor="center")

            if self.playlistExists:
                #Add a music player (probably gonna be a widegt)
                pass

            
            # self.hideOverlay()
            self.master.bind("<Enter>", lambda e: self.showOverlay())
            self.master.bind("<Leave>", lambda e: self.hideOverlay())
            self.master.bind("<Right>", lambda e: self.nextSlide())
            self.master.bind("<Left>", lambda e: self.prevSlide())
            self.master.bind("<space>", lambda e: self.pause())
            self.master.bind("<h>", lambda e: self.hideOverlay())


        ########################
        ######  MENU BAR #######
        ########################
        self.menuBar = tb.Menu(self)
        self.master.config(menu=self.menuBar)
        #Only two menus: Open and exit
        self.fileMenu = tb.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Open", command=self.openProject)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.quit)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)


        #After variable to keep track of slide changes.
        self.slideChangeAfter = None
        return

    def hideOverlay(self):
        #Hide slide buttons
        self.nextButton.place_forget()
        self.prevButton.place_forget()
        self.pauseButton.place_forget()
        self.slideCounter.place_forget()
        
        self.master.bind("<h>", lambda e: self.showOverlay())
        return

    def showOverlay(self):
        #Show slide buttons
        self.nextButton.place(relx=0.8, rely=0.85, anchor="center")
        self.prevButton.place(relx=0.2, rely=0.85, anchor="center")
        self.pauseButton.place(relx=0.5, rely=0.85, anchor="center")
        self.slideCounter.place(relx=0.95, rely=0.05, anchor="center")

        self.master.bind("<h>", lambda e: self.hideOverlay())
        return

    def openProject(self):
        file = filedialog.askopenfilenames(filetypes=[("SlideShow Files", "*.pyslide")], multiple=False)
        #If not file was selected, return. Effectively cancels.
        if not file:
            return
        self.destroy()
        self = SlideshowPlayer(self.master, projectPath=file[0])
        self.pack(expand=True, fill="both")

    def nextSlide(self):
        self.currentSlide += 1
        if self.currentSlide > len(self.slideList)-1:
            self.currentSlide = 0
        self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])

        #Update the slide counter
        self.slideCounter.config(text=f"Slide {self.currentSlide+1}/{len(self.slideList)}")
        
        if not self.manual and not self.isPaused:
            if self.slideChangeAfter:
                self.after_cancel(self.slideChangeAfter)
            changeTime = self.slideList[self.currentSlide]['duration'] * 1000
            self.slideChangeAfter = self.after(changeTime, self.nextSlide)

        print(f"Current slide: {self.slideList[self.currentSlide]}")
        return
    
    def prevSlide(self):
        self.currentSlide -= 1
        if self.currentSlide < 0:
            self.currentSlide = len(self.slideList)-1
        self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])

        #Update the slide counter
        self.slideCounter.config(text=f"Slide {self.currentSlide+1}/{len(self.slideList)}")
        return
    
    def pause(self):
        #Will pause the music and slideshow.
        self.isPaused = not self.isPaused #Toggle the pause state
        print(f"Pausing state: {self.isPaused}")
        self.update_idletasks()
        if self.isPaused:
            #Set slideshow to pause
            self.pauseButton.config(text="Play")
            if not self.manual: #If the slideshow is automatic transition and you pause, stop that transition.
                self.after_cancel(self.slideChangeAfter)
        else: 
            #Set slideshow to start playing
            self.pauseButton.config(text="Pause")
            if not self.manual:
                changeTime = self.slideList[self.currentSlide]['duration'] * 1000
                self.slideChangeAfter = self.after(changeTime, self.nextSlide)
        return
    

if __name__ == "__main__":
    root = tb.Window()
    root.title("Slideshow Viewer")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
    #minimum size
    root.minsize(600, 500)
    app = SlideshowPlayer(root)
    app.pack(expand=True, fill="both")

    app.mainloop()

    