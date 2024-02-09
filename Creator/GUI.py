import tkinter as tk
import FileSupport as IS
from Widgets import *


#Create the root window
class Window:
    def __init__(self, root, slideshowPath:str="New Project"):
        #Project file stuff
        self.projectFile: FP.Slideshow = FP.Slideshow()

        self.root = root
        self.root.title("Resizable Window")
        #Get the size of the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        #Should make the window half the size of the screen and centered
        self.root.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
        
        #Base PanedWindow that holds everything. Takes up the whole window and should always be the same size as the window
        self.base = tk.PanedWindow(self.root, orient=tk.VERTICAL, bd=1, sashwidth=10)
        self.base.pack(expand=True, fill="both")

        #Top PanedWindow that houses media bucket and preview. 
        self.top = tk.PanedWindow(self.base, orient=tk.HORIZONTAL, bd=1, sashwidth=10)
        self.base.add(self.top, stretch="first")

        #Create the media and preview frames
        self.media = tk.Frame(self.top)
        self.top.add(self.media)
        self.preview = tk.Frame(self.top)
        self.top.add(self.preview)

        #Bottom frame that houses slide information and slide reel
        self.bottom = tk.PanedWindow(self.base, orient=tk.HORIZONTAL, bd=1, sashwidth=10)
        self.base.add(self.bottom)

        #Slide information
        self.slideInfo = tk.Frame(self.bottom, bg="blue")
        self.bottom.add(self.slideInfo)

        #Slide Reel
        self.slideReel = tk.Frame(self.bottom, bg="red")
        self.bottom.add(self.slideReel)

        
        #Get the size of the window
        self.root.update()
        self.win_width = self.root.winfo_width()
        self.win_height = self.root.winfo_height()

        #Sets the initial size of the PanedWindows
        self.base.paneconfigure(self.top, height=self.win_height//10*7, minsize=self.win_height//10*3)
        self.base.paneconfigure(self.bottom, height=self.win_height//10*3, minsize=self.win_height//10*3)
        self.top.paneconfigure(self.preview, width=self.win_width//10*6, minsize=self.win_width//10*3)
        self.top.paneconfigure(self.media, width=self.win_width//10*4, minsize=self.win_width//10*3)
        self.bottom.paneconfigure(self.slideInfo, width=self.win_width//10*3, minsize=self.win_width//10*3)
        self.bottom.paneconfigure(self.slideReel, width=self.win_width//10*7, minsize=self.win_width//10*3)

        #Add an ImagePreview to the preview frame
        self.previewImage = PreviewImage(self.preview)
        
        #Label frame
        self.titleFrame = tk.Frame(self.media, bg="grey")
        self.titleFrame.pack(fill=tk.X)
        #Add a label in the media frame that lists the Project Title
        self.projectTitle = tk.Label(self.titleFrame, text=self.projectFile.name, font=("Arial", 12), bg="grey")
        self.projectTitle.pack(fill=tk.NONE, anchor="w")
        #Add a FileViewer to the media frame
        self.fileViewer = FileViewer(self.media)
        self.fileViewer.pack(fill=tk.BOTH, expand=True)
        self.fileViewer.linkPreviewer(self.previewImage)


        #Get the position of the window
        self.win_xPos = self.root.winfo_x()
        self.win_yPos = self.root.winfo_y()

        #resize after call variable.
        self.__resize_after = None

        #Bind the resize event to the on_resize function
        self.root.bind("<Configure>", self.on_resize)

        #MENU BAR
        self.menubar = MenuBar(self.root, self)
        self.root.config(menu=self.menubar)


        self.root.mainloop()


    #Redraw the window when you open a SlideShow project
    def redrawWindow(self):
        #Update the project title
        self.projectTitle.config(text=self.projectFile.name)
        #Update the fileViewer
        self.fileViewer.imageList = self.projectFile.filesInProject

        #Redraw the file viewer
        self.fileViewer.propogateList()
        #Redraw the preview image
        self.previewImage.redrawImage()
        #Here we would also redraw the slideInfo and slideReel


    #Debounce function. On_resize() gets called every <configure> event and creates a new after event.
    #If it gets called again, the after event gets cancelled and a new one is created.
    #If it doesn't it then calls the resize function.
    #This prevents the resize function from being spam and causing lag.
    def on_resize(self, event):
        if self.__resize_after:
            self.root.after_cancel(self.__resize_after)
        self.__resize_after = self.root.after(100, self.resize, event)
        
    def resize(self, event):
        # print("Resizing")
        self.root.update()
        self.win_width = self.root.winfo_width()
        self.win_height = self.root.winfo_height()
        
        #If canvas size has changed, redraw the image
        if self.previewImage.canvas.winfo_width() != self.previewImage.canvasWidth or self.previewImage.canvas.winfo_height() != self.previewImage.canvasHeight:
            self.previewImage.redrawImage()

        #If media has changed size update the file viewer
        if self.fileViewer.parentHeight != self.media.winfo_height() or self.fileViewer.parentWidth != self.media.winfo_width():
            #Check and remove any duplicate items in the fileViewer
            self.fileViewer.propogateList()
            self.fileViewer.parentHeight = self.media.winfo_height()
            self.fileViewer.parentWidth = self.media.winfo_width()

class MenuBar(tk.Menu):
    def __init__(self, parent, GUI):
        tk.Menu.__init__(self, parent)
        self.parent = parent
        self.GUI = GUI
        fileMenu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="New", command=self.newFile)
        fileMenu.add_command(label="Open", command=self.openFile)
        fileMenu.add_command(label="Save", command=self.saveFile)
        fileMenu.add_command(label="Save As", command=self.saveAsFile)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.winfo_toplevel().quit)

        projectMenu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Project", menu=projectMenu)
        projectMenu.add_command(label="Add Image", command=self.addImage)
        projectMenu.add_command(label="Add Folder", command=self.addFolder)
        projectMenu.add_command(label="Revert add", command=self.GUI.fileViewer.revertList)
        projectMenu.add_command(label="Save and Export to Viewer", command=self.saveAndExport)

        #Debug Menu
        debugMenu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Debug", menu=debugMenu)
        debugMenu.add_command(label="Print Preview Slide", command=self.printPreviewSize)
        debugMenu.add_command(label="Redraw Image", command=self.redrawImage)
        debugMenu.add_command(label="Print Media Size", command=self.printMediaSize)
        debugMenu.add_command(label="Print Window Size", command=self.printWindowSize)
        debugMenu.add_command(label="Print Slide Info Size", command=self.printSlideInfoSize)
        debugMenu.add_command(label="Print Slide Reel Size", command=self.printSlideReelSize)
        debugMenu.add_command(label="Print Slideshow Info", command=self.printSlideshowInfo)

    def newFile(self):
        print("New Project")
        self.GUI.projectFile = FP.Slideshow()
        self.GUI.redrawWindow()


    def openFile(self):
        print("Open Project")
        file = filedialog.askopenfilenames(filetypes=[("SlideShow Files", "*.pyslide")], multiple=False)
        print(f"File: {file}")
        if file:
            self.GUI.projectFile = FP.Slideshow(file[0])
            self.GUI.projectFile.load()
            self.GUI.redrawWindow()
            

    def saveFile(self):
        print("Save Project")
        self.GUI.projectFile.filesInProject = self.GUI.fileViewer.imageList
        #All other attributes should already be part of the object
        #Check if the project has a save location
        if self.GUI.projectFile.getSaveLocation() == "New Project":
            self.saveAsFile()
        else:
            self.GUI.projectFile.save()

    def saveAsFile(self):
        print("Save Project As...")
        #Select a folder to save the project to
        path = filedialog.asksaveasfilename(initialfile="New Project", filetypes=[("SlideShow Files", "*.pyslide")], defaultextension=".pyslide")
        self.GUI.projectFile.name = FP.getBaseName([path])[0]
        #Append .pyslide to the end of the file
        print(f"Path: {path}")
        self.GUI.projectFile.filesInProject = self.GUI.fileViewer.imageList
        self.GUI.projectFile.setSaveLocation(path)
        #Save the project to the file
        self.GUI.projectFile.save()
        #redraw the window
        self.GUI.redrawWindow()


    def addImage(self):
        print("Add Image")
        file = filedialog.askopenfilenames(multiple=True, filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        #Check if the file is valid
        if file:
            print(f"File: {file}")
            self.GUI.fileViewer.addFile(file)
            self.GUI.projectFile.filesInProject = self.GUI.fileViewer.imageList

    def addFolder(self):
        print("Add Folder")
        path = filedialog.askdirectory()
        #Check if the path is valid
        if path:
            print(f"Path: {path}")
            self.GUI.fileViewer.addFolder(path)
            self.GUI.projectFile.filesInProject = self.GUI.fileViewer.imageList
            
    def saveAndExport(self):
        print("Save and Export")

    #Debug Functions
    def printPreviewSize(self):
        print(f"Preview Size: {self.GUI.preview.winfo_width()}x{self.GUI.preview.winfo_height()}")

    def redrawImage(self):
        self.GUI.previewImage.redrawImage()
    
    def printMediaSize(self):
        print(f"Media Size: {self.GUI.media.winfo_width()}x{self.GUI.media.winfo_height()}")

    def printWindowSize(self):
        print(f"Window Size: {self.parent.winfo_width()}x{self.parent.winfo_height()}")

    def printSlideInfoSize(self):
        print(f"Slide Info Size: {self.GUI.slideInfo.winfo_width()}x{self.GUI.slideInfo.winfo_height()}")
    
    def printSlideReelSize(self):
        print(f"Slide Reel Size: {self.GUI.slideReel.winfo_width()}x{self.GUI.slideReel.winfo_height()}")

    def printSlideshowInfo(self):
        print(f"Slideshow Info: {self.GUI.projectFile.__dict__}")


#Create the window
root = tk.Tk()
#Change the icon
root.iconbitmap(r"Creator\icon.ico")

app = Window(root)
