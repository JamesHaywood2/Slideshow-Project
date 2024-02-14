import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from Widgetsv2 import *
from tkinter import filedialog
from tkinter import dnd


class SlideshowCreatorStart(tb.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.create_widgets()

    def create_widgets(self):
        self.label = tb.Label(self, text="Slideshow Creator", font=("Arial", 24))
        self.label.pack()
        self.newProjectButton = tb.Button(self, text="New Project", command=self.newProject)
        self.newProjectButton.pack()
        self.openProjectButton = tb.Button(self, text="Open Project", command=self.openProject)
        self.openProjectButton.pack()

    def newProject(self):
        #Create a SlideshowCreator object, destroy the current window, and pack the new window
        self.destroy()
        self.creator = SlideshowCreator(self.master)
        self.creator.pack(expand=True, fill="both")

    def openProject(self):
        #Create a SlideshowCreator object, destroy the current window, and pack the new window
        projectPath = filedialog.askopenfilename(filetypes=[("Slideshow Files", "*.pyslide")])
        if not projectPath:
            return
        self.destroy()
        self.creator = SlideshowCreator(self.master, projectPath=projectPath)
        self.creator.pack(expand=True, fill="both")

    


class SlideshowCreator(tb.Frame):
    def __init__(self, master=None, debug: bool=False, projectPath: str="New Project", **kw):
        super().__init__(master, **kw)
        self.debug = debug
        self.slideshow = FP.Slideshow(projectPath)
        self.slideshow.load()
        self.update()

        
        ######################
        #LAYOUT SETUP
        ######################
        #The 3 PanedWindows that divide the window into 4 sections
        self.PanedWindow_Base = tk.PanedWindow(self, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=5, showhandle=True, bg="black")
        self.PanedWindow_Base.pack(expand=True, fill=tk.BOTH)

        self.PanedWindow_Top = tk.PanedWindow(self.PanedWindow_Base, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5, showhandle=True, bg="red")
        self.PanedWindow_Base.add(self.PanedWindow_Top, stretch="first")
        self.PanedWindow_Bottom = tk.PanedWindow(self.PanedWindow_Base, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5, showhandle=True, bg="blue")
        self.PanedWindow_Base.add(self.PanedWindow_Bottom, stretch="last")

        self.mediaFrame = tb.Frame(self.PanedWindow_Top)
        self.PanedWindow_Top.add(self.mediaFrame)

        self.imageFrame = tb.Frame(self.PanedWindow_Top)
        self.PanedWindow_Top.add(self.imageFrame)

        self.slideInfoFrame = tb.Frame(self.PanedWindow_Bottom)
        self.PanedWindow_Bottom.add(self.slideInfoFrame)

        self.reelFrame = tb.Frame(self.PanedWindow_Bottom)
        self.PanedWindow_Bottom.add(self.reelFrame)

        #Sets the initial sizes for the PanedWindows
        #Maybe this isn't the best method for setting the initial sizes? Idk. If yall have a better method, let me know. - James
        win_width_start = self.master.winfo_screenwidth()//2
        win_height_start = self.master.winfo_screenheight()//2
        self.PanedWindow_Base.paneconfigure(self.PanedWindow_Top, height=win_height_start//10*7, minsize=win_height_start//10*3)
        self.PanedWindow_Base.paneconfigure(self.PanedWindow_Bottom, height=win_height_start//10*3, minsize=win_height_start//10*3)
        self.PanedWindow_Top.paneconfigure(self.mediaFrame, width=win_width_start//10*6, minsize=win_width_start//10*3)
        self.PanedWindow_Top.paneconfigure(self.imageFrame, width=win_width_start//10*4, minsize=win_width_start//10*3)
        self.PanedWindow_Bottom.paneconfigure(self.slideInfoFrame, width=win_width_start//10*3, minsize=win_width_start//10*4)
        self.PanedWindow_Bottom.paneconfigure(self.reelFrame, width=win_width_start//10*7, minsize=win_width_start//10*4)

        #Initialize these widgets. They will probably have to be redrawn later though.
        self.slideInfoButton = tb.Button(self.slideInfoFrame, text="Slide Info")
        self.slideInfoButton.pack()

        #Create the ImageViewer object
        self.imageViewer = ImageViewer(self.imageFrame)
        self.imageViewer.pack(expand=True, fill="both")

        self.slideReel = SlideReel(self.reelFrame, slideshow=self.slideshow)
        self.slideReel.pack(expand=True, fill="both")
        self.slideReel.linkPreviewer(self.imageViewer)

        #Mediabucket
        self.mediaBucket = MediaBucket(self.mediaFrame, slideshow=self.slideshow)
        self.mediaBucket.linkPreviewer(self.imageViewer)
        self.mediaBucket.linkReel(self.slideReel)
        self.mediaBucket.pack(expand=True, fill="both")

        self.DebugWindow()

        #Menubar
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)
        self.projectMenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Project", menu=self.projectMenu)
        self.projectMenu.add_command(label="New Project", command=self.newProject)
        self.projectMenu.add_command(label="Open Project", command=self.openProject)
        self.projectMenu.add_separator()
        self.projectMenu.add_command(label="Save", command=self.save)
        self.projectMenu.add_command(label="Save As", command=self.saveAs)
        self.projectMenu.add_separator()
        self.projectMenu.add_command(label="Exit", command=self.quit)

        self.fileMenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="Add file", command=self.addFile)
        self.fileMenu.add_command(label="Add folder", command=self.addFolder)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Revert addition", command=self.mediaBucket.undoAdd)
        self.fileMenu.add_command(label="Debug", command=self.DebugWindow)


    def redraw(self):
        self.imageViewer.redrawImage()
        self.mediaBucket.fillBucket()
        self.slideReel.fillReel()

    def AppStart(self):
        app.mainloop()

    def DebugWindow(self):
        if self.debug == False:
            return
        self.debugWindow = tk.Toplevel()
        self.debugWindow.title("Debug Window")
        self.debugWindow.geometry("400x800")

        #Print size buttons
        self.winSizeButton = tb.Button(self.debugWindow, text="Print Window Size", command=lambda: print(f"Window size: {self.master.winfo_width()}x{self.master.winfo_height()}"))
        self.winSizeButton.pack()
        self.topPaneSizeButton = tb.Button(self.debugWindow, text="Print Top Pane Size", command=lambda: print(f"Top Pane size: {self.PanedWindow_Top.winfo_width()}x{self.PanedWindow_Top.winfo_height()}"))
        self.topPaneSizeButton.pack()
        self.bottomPaneSizeButton = tb.Button(self.debugWindow, text="Print Bottom Pane Size", command=lambda: print(f"Bottom Pane size: {self.PanedWindow_Bottom.winfo_width()}x{self.PanedWindow_Bottom.winfo_height()}"))
        self.bottomPaneSizeButton.pack()

        self.mediaFrameSizeButton = tb.Button(self.debugWindow, text="Print Media Frame Size", command=lambda: print(f"Media Frame size: {self.mediaFrame.winfo_width()}x{self.mediaFrame.winfo_height()}"))
        self.mediaFrameSizeButton.pack()
        self.mediaBucketSizeButton = tb.Button(self.debugWindow, text="Print Media Bucket Size", command=lambda: print(f"Media Bucket size: {self.mediaBucket.winfo_width()}x{self.mediaBucket.winfo_height()}"))
        self.mediaBucketSizeButton.pack()
        self.mediaBucketFillButton = tb.Button(self.debugWindow, text="Fill Media Bucket", command=self.mediaBucket.fillBucket)
        self.mediaBucketFillButton.pack()
        self.mediaBucketContentButton = tb.Button(self.debugWindow, text="Print Media Bucket Content", command=lambda: print(self.mediaBucket.files))
        self.mediaBucketContentButton.pack()


        self.imageFrameSizeButton = tb.Button(self.debugWindow, text="Print Image Frame Size", command=lambda: print(f"Image Frame size: {self.imageFrame.winfo_width()}x{self.imageFrame.winfo_height()}"))
        self.imageFrameSizeButton.pack()

        self.slideInfoFrameSizeButton = tb.Button(self.debugWindow, text="Print Slide Info Frame Size", command=lambda: print(f"Slide Info Frame size: {self.slideInfoFrame.winfo_width()}x{self.slideInfoFrame.winfo_height()}"))
        self.slideInfoFrameSizeButton.pack()

        self.reelFrameSizeButton = tb.Button(self.debugWindow, text="Print Reel Frame Size", command=lambda: print(f"Reel Frame size: {self.reelFrame.winfo_width()}x{self.reelFrame.winfo_height()}"))
        self.reelFrameSizeButton.pack()
        self.reelSizeButton = tb.Button(self.debugWindow, text="Print Reel Size", command=lambda: print(f"Reel size: {self.slideReel.winfo_width()}x{self.slideReel.winfo_height()}"))
        self.reelSizeButton.pack()
        self.reelFillButton = tb.Button(self.debugWindow, text="Fill Reel", command=self.slideReel.fillReel)
        self.reelFillButton.pack()
        self.reelCountButton = tb.Button(self.debugWindow, text="Print Reel Count", command=lambda: print(f"Reel count: {len(self.slideReel.slides)}"))
        self.slideListButton = tb.Button(self.debugWindow, text="Print Slide List", command=lambda: print(self.slideshow.printSlides()))
        self.slideListButton.pack()

        self.imageViewerSizeButton = tb.Button(self.debugWindow, text="Print ImageViewer Size", command=lambda: print(f"ImageViewer size: {self.imageViewer.winfo_width()}x{self.imageViewer.winfo_height()}"))
        self.imageViewerSizeButton.pack()

        self.slideshowsButton = tb.Button(self.debugWindow, text="Print Slideshows", command=lambda: print(self.slideshow))
        self.slideshowsButton.pack()

    def newProject(self):
        #Basically destroy the current SlideshowCreator object and create a new one
        self.destroy()
        self.creator = SlideshowCreator(self.master)
        self.creator.pack(expand=True, fill="both")

    def openProject(self):
        print("Open Project")
        #Destroy the debug window
        path = filedialog.askopenfilename(filetypes=[("Slideshow Files", "*.pyslide")])
        if not path:
            return
        self.debugWindow.destroy()
        self.destroy()
        self.creator = SlideshowCreator(self.master, projectPath=path, debug=True)
        self.creator.pack(expand=True, fill="both")
        self.update()
        print(self.creator.slideshow)

    def save(self):
        print("Save")
        self.slideshow.filesInProject = self.mediaBucket.files
        if self.slideshow.getSaveLocation() == "New Project":
            self.saveAs()
        else:
            self.slideshow.save()
        

    def saveAs(self):
        print("Save As")
        path = filedialog.asksaveasfilename(defaultextension=".pyslide", filetypes=[("Slideshow Files", "*.pyslide")])
        if not path:
            return
        print(f"Path: {path}")
        self.slideshow.filesInProject = self.mediaBucket.files
        self.slideshow.setSaveLocation(path)
        self.slideshow.save()


    def addFile(self):
        print("Adding Image")
        file = filedialog.askopenfilenames(multiple=True, filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if not file:
            return
        #Check if the file is valid
        if file:
            print(f"File: {file}")
            self.mediaBucket.addFile(file)
            self.slideshow.filesInProject = self.mediaBucket.files

    def addFolder(self):
        print("Adding Folder")
        folder = filedialog.askdirectory()
        if not folder:
            return
        if folder:
            print(f"Folder: {folder}")
            self.mediaBucket.addFolder(folder)
            self.slideshow.filesInProject = self.mediaBucket.files

    def quit(self):
        self.master.quit()

if __name__ == "__main__":
    root = tb.Window()
    root.title("Slideshow Creator")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
    app = SlideshowCreatorStart(root)
    # app = SlideshowCreator(root, debug=True, projectPath=r"C:\Users\JamesH\Pictures\cat\kitty.pyslide")
    app.pack(expand=True, fill="both")
    app.mainloop()

