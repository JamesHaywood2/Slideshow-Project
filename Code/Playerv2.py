import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from Widgets import *
from tkinter import filedialog
import FileSupport as FP
import random

import time

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
        self.label = tb.Label(self, text="Slideshow Player", font=("Arial", 24))
        self.openProjectButton = tb.Button(self, text="Open Project", command=self.openProject)
        self.recentSlideshowList = RecentSlideshowList(self)

        self.label.place(relx=0.5, rely=0.15, anchor="center")
        self.openProjectButton.place(anchor="center", relx=0.5, rely=0.25)
        self.recentSlideshowList.place(relx=0.5, rely=0.6, anchor="center", relwidth=0.8, relheight=0.5)

        #Set window size
        self.master.geometry("800x600")
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
        print(f"Opening project: {projectPath}")
        #Open the project
        self.openProjectPath(projectPath)

    def openProject(self):
        file = filedialog.askopenfilenames(filetypes=[("SlideShow Files", "*.pyslide")], multiple=False)
        #If not file was selected, return. Effectively cancels.
        if not file:
            return
        self.destroy()
        self = SlideshowPlayer(self.master, projectPath=file[0])
        self.pack(expand=True, fill="both")

    def openProjectPath(self, projectPath: str):
        #Make sure the projectPath is valid
        try:
            with open(projectPath, "r"):
                pass
        except:
            projectPath = "New Project"
        #Make sure it's a .pyslide file
        if not projectPath.endswith(".pyslide"):
            projectPath = "New Project"
        self.destroy()
        self = SlideshowPlayer(self.master, projectPath=projectPath)
        self.pack(expand=True, fill="both")


class SlideshowPlayer(tb.Frame):
    def __init__(self, master, debug:bool= False, projectPath: str="New Project"):
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        master.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
        master.resizable(True, True) #Resizable window
        master.attributes("-fullscreen", True) #Fullscreen
        #Bind escape to exit fullscreen
        master.bind("<Escape>", lambda e: self.quit())

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


        # self.shuffleSlideshow:bool = True
        ##### Shuffle stuff #####
        if self.shuffleSlideshow:
            #Randomize the order of the slides
            random.shuffle(self.slideList)
            print("Shuffling slideshow")
        if self.shufflePlaylist:
            random.shuffle(self.playlist.songs)
            print("Shuffling playlist")

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
        self.transition_checker = None

        #Bind a configure event to the window so we can create the components after the window is resized.
        self.bind("<Configure>", lambda e: self.createComponents())
        return
    
    def createComponents(self):
        #Unbind the configure event so it doesn't keep creating components.
        self.unbind("<Configure>")
        self.update_idletasks()
        #Only construct the layout if the project is not empty of slides.
        if len(self.slideList) > 0:
            
            #Add first slide to the ImageViewer
            self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])

            ###### PRE-RENDER THE IMAGES ######
            screen_height = self.master.winfo_screenheight()
            screen_width = self.master.winfo_screenwidth()
            canvas_width = self.imageViewer.canvasWidth
            canvas_height = self.imageViewer.canvasHeight
            #We want to get every slide image in the slideshow and prepare them for display.
            self.ImageList = {} #Key: Slide number, name of the image file in the cache
            for slide in self.slideList:
                # print(f"Loading image: {slide['imagePath']} for slide {slide['slideID']}")
                try:
                    slideImage = Image.open(slide['imagePath']).convert("RGBA")
                    #Resize the image to fit the canvas size.
                    slideImage.thumbnail((canvas_width, canvas_height), resample=Image.NEAREST, reducing_gap=None)
                except:
                    print(f"Error loading image: {slide['imagePath']}")

                try:
                    #Background will be a transparent square fit to the canvas size.
                    #Background will insure that every image is the same size and dimensions.
                    bg = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))
                except:
                    print("Error creating background")

                try:
                    x, y = (bg.width - slideImage.width) // 2, (bg.height - slideImage.height) // 2
                    #Paste the image onto the background
                    bg.paste(slideImage, (x, y), slideImage)      
                except:
                    print("Error pasting image onto background")
                    print(f"Slide image dimensions: {slideImage.size}")
                    print(f"Background dimensions: {bg.size}")
                    quit()

                #Generate a name for the image
                name = f"{FP.removeExtension(self.slideshow.name)}__{slide['slideID']}_{slide['transition']}_{FP.removeExtension(slide['imageName'])}.png"
                # print(f"Saving image to cache: {name}")
                #Save the image to the cache
                FP.saveImageToCache(bg, name)
                #Add the image to the ImageList
                self.ImageList[slide['slideID']] = name

            #Add next and previous buttons using place.
            self.nextButton = tb.Button(self, text="Next", command=self.nextSlide)
            self.nextButton.place(relx=0.8, rely=0.85, anchor="center")
            self.prevButton = tb.Button(self, text="Previous", command=self.prevSlide)
            self.prevButton.place(relx=0.2, rely=0.85, anchor="center")

            #Pause button
            self.pauseButton = tb.Button(self, text="Play", command=self.pause)
            self.pauseButton.place(relx=0.5, rely=0.85, anchor="center")

            #Add a slide counter in the top right corner
            self.slideMeterBroken: bool = False
            # self.slideCounter = tb.Label(self, text=f"Slide {self.currentSlide+1}/{len(self.slideList)}")
            # self.slideCounter.place(relx=0.95, rely=0.05, anchor="center")

            #Add a slide counter in the top right corner using a bootstrap meter
            #Go into ttkboostrap/widgets.py line 856 and change CUBIC to BICUBIC to get it to work
            try:
                self.slideCounter = tb.Meter(self, 
                                         bootstyle="primary",
                                         metersize=100,
                                         textright=f"/{len(self.slideList)}",
                                         metertype="semi",
                                         amounttotal=len(self.slideList),
                                         amountused=self.currentSlide+1,
                                         stripethickness=0,)
                self.slideCounter.place(relx=1, rely=0, anchor="ne")
            except:
                self.slideMeterBroken = True
                self.slideCounter = tb.Label(self, text=f"Slide {self.currentSlide+1}/{len(self.slideList)}")
                self.slideCounter.place(relx=0.95, rely=0.05, anchor="center")
                #Throw an error message: f"Error: Slide meter broken. Please go into ttkboostrap/widgets.py line 856 and change CUBIC to BICUBIC to get it to work.\n Defaulting to label."
                print(f"\nError: Slide meter broken. Please go into ttkboostrap/widgets.py line 856 and change CUBIC to BICUBIC to get it to work.\n Defaulting to label.\n")


            if self.playlistExists:
                #Add a music player (probably gonna be a widegt)
                pass


        # self.hideOverlay()
        # self.master.bind("<Enter>", lambda e: self.showOverlay())
        # self.master.bind("<Leave>", lambda e: self.hideOverlay())
        self.master.bind("<Right>", lambda e: self.nextSlide())
        self.master.bind("<Left>", lambda e: self.prevSlide())
        self.master.bind("<space>", lambda e: self.pause())
        self.master.bind("<h>", lambda e: self.hideOverlay())
        self.mouse_after_id = None
        self.master.bind("<Motion>", lambda e: self.motionEvent())



    def motionEvent(self):
        self.showOverlay()
        if self.mouse_after_id:
            self.after_cancel(self.mouse_after_id)
        self.mouse_after_id = self.after(2500, self.hideOverlay)
        return

    def hideOverlay(self):
        #Hide slide buttons
        self.nextButton.place_forget()
        self.prevButton.place_forget()
        self.pauseButton.place_forget()
        self.slideCounter.place_forget()
        
        self.master.bind("<h>", lambda e: self.showOverlay())
        self.config(cursor="none")
        return

    def showOverlay(self):
        #Show slide buttons
        self.nextButton.place(relx=0.8, rely=0.85, anchor="center")
        self.prevButton.place(relx=0.2, rely=0.85, anchor="center")
        self.pauseButton.place(relx=0.5, rely=0.85, anchor="center")
        if not self.slideMeterBroken:
            self.slideCounter.place(relx=1, rely=0, anchor="ne")
        else:
            self.slideCounter.place(relx=0.95, rely=0.05, anchor="center")

        self.master.bind("<h>", lambda e: self.hideOverlay())
        self.config(cursor="")
        return

    def openProject(self):
        file = filedialog.askopenfilenames(filetypes=[("SlideShow Files", "*.pyslide")], multiple=False)
        #If not file was selected, return. Effectively cancels.
        if not file:
            return
        self.destroy()
        self = SlideshowPlayer(self.master, projectPath=file[0])
        self.pack(expand=True, fill="both")

    def checkTransition(self, imagePath: str):
        if self.imageViewer.transitioning:
            self.transition_checker = self.after(100, self.checkTransition, imagePath)
        else:
            #Once transitioning is complete, make sure the correct image is displayed.
            try:
                self.after_cancel(self.transition_checker)
            except:
                pass
            self.transition_checker = None
            self.END = time.time()
            print(f"Transition took {self.END - self.START} seconds and {self.imageViewer.frameCounter} frames.")
            print(f"Transition complete, reloading the image to be safe. ")
            # self.imageViewer.loadImagePIL(self.ImageList[self.slideList[self.currentSlide]['slideID']])
            self.imageViewer.loadImage(imagePath)
            self.imageViewer.loadImagePIL(FP.loadImageFromCache(self.ImageList[self.slideList[self.currentSlide]['slideID']]))
            self.automaticNext()

    def nextSlide(self):
        print("")
        #Launch a motion event to show the overlay
        self.event_generate("<Motion>")
        self.START = time.time()
        if self.imageViewer.transitioning:
            self.imageViewer.cancelTransition()
            # self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])
            # self.imageViewer.loadImagePIL(self.ImageList[self.slideList[self.currentSlide]['slideID']])
            # self.imageViewer.loadImagePIL(FP.loadImageFromCache(self.ImageList[self.slideList[self.currentSlide]['slideID']]))
            return

        self.currentSlide += 1
        if self.currentSlide > len(self.slideList)-1:
            self.currentSlide = 0
            nextSlide = self.slideList[0]
            previousSlide = self.slideList[-1]
        else:
            nextSlide = self.slideList[self.currentSlide]
            previousSlide = self.slideList[self.currentSlide-1]

        #Gets the slide we're transitioning to and the previous slide.
        #Then gets the images and correctly sizes them.
        transition = nextSlide['transition']
        transitionSpeed = nextSlide['transitionSpeed'] * 1000
        # previousImage = previousSlide['imagePath']
        # previousImage = Image.open(previousImage)
        # nextImage = nextSlide['imagePath']
        # nextImage = Image.open(nextImage)
        # nextImage.thumbnail((self.imageViewer.canvasWidth, self.imageViewer.canvasHeight), resample=Image.NEAREST, reducing_gap=None)
        # previousImage.thumbnail((self.imageViewer.canvasWidth, self.imageViewer.canvasHeight), resample=Image.NEAREST, reducing_gap=None)

        previous_ID = previousSlide['slideID']
        next_ID = nextSlide['slideID']
        previousImage = FP.loadImageFromCache(self.ImageList[previous_ID])
        nextImage = FP.loadImageFromCache(self.ImageList[next_ID])

        print(f"Transitioning from {previous_ID} to {next_ID} with transition {transition} at speed {transitionSpeed}ms")

        #It will then execute the transition and do a constant check to see if the transition is complete.
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
        
    def automaticNext(self):
        if not self.manual and not self.isPaused:
            #Automatic transitions
            if self.slideChangeAfter:
                self.after_cancel(self.slideChangeAfter)
            changeTime = self.slideList[self.currentSlide]['duration'] * 1000
            self.slideChangeAfter = self.after(changeTime, self.nextSlide)
            print(f"Next slide in {changeTime}ms")

        print(f"Current slide: {self.slideList[self.currentSlide]}")
        return
    
    def prevSlide(self):
        print("")
        self.event_generate("<Motion>")
        self.START = time.time()
        #If a transition is in progress, cancel it and just load the image before returning.
        if self.imageViewer.transitioning:
            self.imageViewer.cancelTransition()
            self.imageViewer.loadImage(self.slideList[self.currentSlide]['imagePath'])
            return
        
        self.currentSlide -= 1
        if self.currentSlide < 0:
            nextSlide = self.slideList[-1]
            previousSlide = self.slideList[0]
            self.currentSlide = len(self.slideList)-1
        else:
            nextSlide = self.slideList[self.currentSlide]
            previousSlide = self.slideList[self.currentSlide+1]

        def reverseTransition(transition:str):
            if transition == FP.transitionType.FADE:
                return FP.transitionType.FADE
            elif transition == FP.transitionType.WIPELEFT:
                return FP.transitionType.WIPERIGHT
            elif transition == FP.transitionType.WIPERIGHT:
                return FP.transitionType.WIPELEFT
            elif transition == FP.transitionType.WIPEDOWN:
                return FP.transitionType.WIPEUP
            elif transition == FP.transitionType.WIPEUP:
                return FP.transitionType.WIPEDOWN
            else:
                return FP.transitionType.DEFAULT

        #Gets the slide we're transitioning to and the previous slide.
        #Then gets the images and correctly sizes them.
        transition = reverseTransition(previousSlide['transition'])
        transitionSpeed = nextSlide['transitionSpeed'] * 1000
        # previousImage = previousSlide['imagePath']
        # previousImage = Image.open(previousImage)
        # nextImage = nextSlide['imagePath']
        # nextImage = Image.open(nextImage)
        # previousImage.thumbnail((self.imageViewer.canvasWidth, self.imageViewer.canvasHeight), resample=Image.NEAREST, reducing_gap=None)
        # nextImage.thumbnail((self.imageViewer.canvasWidth, self.imageViewer.canvasHeight), resample=Image.NEAREST, reducing_gap=None)

        previous_ID = previousSlide['slideID']
        next_ID = nextSlide['slideID']
        previousImage = FP.loadImageFromCache(self.ImageList[previous_ID])
        nextImage = FP.loadImageFromCache(self.ImageList[next_ID])

        print(f"Transitioning from {previous_ID} to {next_ID} with transition {transition} at speed {transitionSpeed}ms")

        #It will then execute the transition and do a constant check to see if the transition is complete.
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
            self.automaticNext()

        self.showOverlay()
        return
    

if __name__ == "__main__":
    root = tb.Window()
    root.title("Slideshow Viewer")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
    #minimum size
    root.minsize(600, 500)
    # app = SlideshowPlayer(root)
    app = SlideshowPlayerStart(root)
    app.pack(expand=True, fill="both")

    app.mainloop()

    