import random
from tkinter import *
import FileSupport as FP
import time
from Widgets import *
import json

# Create the root window
class player(tk.Tk):
    def __init__(self, slideshowPath: str = "New Project"):
        tk.Tk.__init__(self)
        self.title("Resizable Window")
        # self.iconbitmap(FP.ProgramIcon)
        #self.icon = PhotoImage(file="Slideshow-Project/Player/icon.ico")
        #self.iconphoto(self.icon)
        # Get the size of the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Should make the window half the size of the screen and centered
        self.geometry(f"{screen_width // 2}x{screen_height // 2}+{screen_width // 4}+{screen_height // 4}")

        # Project file stuff
        self.projectFile = dict
        #self.timer = 0
        self.slide_counter = 0

        # Base PanedWindow that holds everything. Takes up the whole window and should always be the same size as the window
        self.base = tk.PanedWindow(self, orient=tk.VERTICAL, bd=1, sashwidth=10)
        self.base.pack(expand=True, fill="both")

        # Add a slide to the canvas
        self.picture = ImageViewer(master=self)
        # Not anchoring to center
        self.picture.pack(expand=True, fill="y", anchor=CENTER)

        # Get the position of the window
        self.win_xPos = self.winfo_x()
        self.win_yPos = self.winfo_y()

        # resize after call variable.
        self.__resize_after = None

        # Bind the resize event to the on_resize function
        self.bind("<Configure>", self.on_resize)

        # MENU BAR
        self.menubar = MenuBar(self, self)
        self.config(menu=self.menubar)

    # Redraw the window when you open a SlideShow project
    def redrawWindow(self):
        # Update the project title
        self.title(self.projectFile['name'])
        # Redraw the preview image [imagePath]
        self.picture.imagePath = self.projectFile['_Slideshow__slides'][self.slide_counter]['imagePath']
        print(self.slide_counter)
        self.picture.redrawImage()
        # Redraw the slideReel

    # Debounce function. On_resize() gets called every <configure> event and creates a new after event.
    # If it gets called again, the after event gets cancelled and a new one is created.
    # If it doesn't it then calls the resize function.
    # This prevents the resize function from being spam and causing lag.
    def on_resize(self, event):
        if self.__resize_after:
            self.after_cancel(self.__resize_after)
        self.__resize_after = self.after(100, self.resize, event)

    def resize(self, event):
        # print("Resizing")
        self.update()
        self.win_width = self.winfo_width()
        self.win_height = self.winfo_height()

        # If canvas size has changed, redraw the image
        if self.picture.winfo_width() != self.picture.canvasWidth or self.picture.winfo_height() != self.picture.canvasHeight:
            self.picture.redrawImage()

    def openProject(self, path: str):
        self.projectFile = self.load(path)
        self.redrawWindow()
        #self.picture.redrawImage()

    def nextSlide_a(self):
        print("Time over")
        if self.projectFile['shuffle'] == False:
            if (self.slide_counter + 1) > len(self.projectFile['_Slideshow__slides']):
                self.slide_counter += 1
                self.after((self.projectFile['defaultSlideDuration'] * 1000), self.nextSlide_a())
                print("Going to next slide")
            elif self.projectFile['loop'] == True:
                self.slide_counter = 0
                self.after((self.projectFile['defaultSlideDuration'] * 1000), self.nextSlide_a())
                print("Looping")
            else:
                print("Slideshow over")
        else: #Not sure how shuffle should work with loop
            self.slide_counter = random.randint(0, len(self.projectFile['_Slideshow__slides']))
            self.after((self.projectFile['defaultSlideDuration'] * 1000), self.nextSlide_a())
        self.redrawWindow()

    # Set up manual advance buttons
    def nextSlide_m(self):
        if self.projectFile['shuffle'] == False:
            if (self.slide_counter + 1) > len(self.projectFile['_Slideshow__slides']):
                self.slide_counter += 1
            elif self.projectFile['loop'] == True:
                self.slide_counter = 0
        else:  # Not sure how shuffle should work with loop
            self.slide_counter = random.randint(0, len(self.projectFile['_Slideshow__slides']))
        self.redrawWindow()

    def load(self, __filePath):
        """
        Loads data from the JSON file into the slideshow.
        """
        # This could probably just be in the __init__ method. I don't know why I made it seperate, but I don't want to change it and see if it breaks anything. - James
        try:
            with open(__filePath, 'r') as f:
                # file_contents = f.read()
                # print(file_contents)
                data = json.load(f)
                return data

        except Exception as e:
            print(f"Error loading file: {str(e)}")
            # Basically if there is an error loading the file it's going to create a new slideshow.
            #self.__init__()



class MenuBar(tk.Menu):
    def __init__(self, parent, GUI):
        tk.Menu.__init__(self, parent)
        self.parent = parent
        self.GUI = GUI
        fileMenu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="File", menu=fileMenu)
        #fileMenu.add_command(label="New", command=self.newFile)
        fileMenu.add_command(label="Open", command=self.openFile)
        #fileMenu.add_command(label="Save", command=self.saveFile)
        #fileMenu.add_command(label="Save As", command=self.saveAsFile)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.winfo_toplevel().quit)

        #projectMenu = tk.Menu(self, tearoff=0)
        #self.add_cascade(label="Project", menu=projectMenu)
        #projectMenu.add_command(label="Add Image", command=self.addImage)
        #projectMenu.add_command(label="Add Folder", command=self.addFolder)
        #projectMenu.add_command(label="Revert add", command=self.GUI.fileViewer.revertList)
        #projectMenu.add_command(label="Save and Export to Viewer", command=self.saveAndExport)

        # Debug Menu
        debugMenu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Debug", menu=debugMenu)
        debugMenu.add_command(label="Print Preview Slide", command=self.printPreviewSize)
        debugMenu.add_command(label="Redraw Image", command=self.redrawImage)
        debugMenu.add_command(label="Print Media Size", command=self.printMediaSize)
        debugMenu.add_command(label="Print Window Size", command=self.printWindowSize)
        debugMenu.add_command(label="Print Slide Info Size", command=self.printSlideInfoSize)
        debugMenu.add_command(label="Print Slide Reel Size", command=self.printSlideReelSize)
        debugMenu.add_command(label="Print Slideshow Info", command=self.printSlideshowInfo)
        debugMenu.add_command(label="Redraw Window", command=self.GUI.redrawWindow)

    '''
    def newFile(self):
        print("New Project")
        self.GUI.projectFile = FP.Slideshow()
        self.GUI.redrawWindow()
    '''

    def openFile(self):
        print("Open Project")
        file = filedialog.askopenfilenames(filetypes=[("SlideShow Files", "*.pyslide")], multiple=False)
        # print(f"File: {file}")
        if file:
            self.GUI.openProject(file[0])
            if self.GUI.projectFile['manual'] == False:
                self.GUI.after((self.GUI.projectFile['defaultSlideDuration'] * 1000), self.GUI.nextSlide_a())

            #self.GUI.projectFile = FP.Slideshow(file[0])
            #self.GUI.projectFile.load()
            #self.GUI.redrawWindow()

    # Debug Functions
    def printPreviewSize(self):
        print(f"Preview Size: {self.GUI.preview.winfo_width()}x{self.GUI.preview.winfo_height()}")

    def redrawImage(self):
        self.GUI.Image.redrawImage()

    def printMediaSize(self):
        print(f"Media Size: {self.GUI.media.winfo_width()}x{self.GUI.media.winfo_height()}")

    def printWindowSize(self):
        print(f"Window Size: {self.parent.winfo_width()}x{self.parent.winfo_height()}")

    def printSlideInfoSize(self):
        print(f"Slide Info Size: {self.GUI.slideInfo.winfo_width()}x{self.GUI.slideInfo.winfo_height()}")

    def printSlideReelSize(self):
        print(f"Slide Reel Size: {self.GUI.slideReel.winfo_width()}x{self.GUI.slideReel.winfo_height()}")

    def printSlideshowInfo(self):
        print(f"Slideshow Info: {self.GUI.projectFile.getSlides()} and count: {self.GUI.projectFile.getSlideCount()}")

# Main

root = player()
root.mainloop()