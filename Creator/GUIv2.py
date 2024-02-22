import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from Widgetsv2 import *
from tkinter import filedialog


class SlideshowCreatorStart(tb.Frame):
    """Start window for the Slideshow Creator. This window will have two buttons: New Project and Open Project."""
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.create_widgets()
        try:
            FP.initializeCache()
        except:
            print("Cache initialziation failed")
        tb.Style().theme_use(FP.getPreferences())

    def create_widgets(self):
        """Creates the widgets for the start window."""
        self.label = tb.Label(self, text="Slideshow Creator", font=("Arial", 24))
        self.label.pack(anchor="center", expand=True)
        self.buttonFrame = tb.Frame(self)
        self.buttonFrame.pack(anchor="center", expand=True, fill="both")
        self.newProjectButton = tb.Button(self.buttonFrame, text="New Project", command=self.newProject)
        self.newProjectButton.pack(anchor="center", pady=10)
        self.openProjectButton = tb.Button(self.buttonFrame, text="Open Project", command=self.openProject)
        self.openProjectButton.pack(anchor="center", pady=10)

    def newProject(self):
        """Loads the slideshow creator window without a project file. This will create a new project."""
        #Create a SlideshowCreator object, destroy the current window, and pack the new window
        # folder = filedialog.askdirectory(mustexist=True)
        # if not folder:
        #     return
        self.destroy()
        self.creator: SlideshowCreator = SlideshowCreator(self.master)
        self.creator.pack(expand=True, fill="both")

    def openProject(self):
        """Loads the slideshow creator window with a project file. This will open an existing project."""
        #Create a SlideshowCreator object, destroy the current window, and pack the new window
        projectPath = filedialog.askopenfilename(filetypes=[("Slideshow Files", "*.pyslide")])
        if not projectPath:
            return
        self.destroy()
        self.creator = SlideshowCreator(self.master, projectPath=projectPath)
        self.creator.pack(expand=True, fill="both")
  
class SlideshowCreator(tb.Frame):
    """
    The main application frame. Contains four main sections: MediaBucket, ImageViewer, SlideInfo, and SlideReel.\n
    MediaBucket: Contains all the media files that are in the project folder or added later.\n
    ImageViewer: Previews an image.\n
    SlideInfo: Contains the slide information.\n
    SlideReel: Contains all the slides in the project.

    DebugWindow(): Creates a debug window that has a bunch of buttons that do debug stuff.
    redraw(): Redraws the ImageViewer, MediaBucket, and SlideReel. 
    """
    def __init__(self, master=None, debug: bool=False, projectPath: str="New Project", **kw):
        super().__init__(master, **kw)
        self.debug = debug
        self.slideshow = FP.Slideshow(projectPath)
        self.slideshow.load()
        try:
            FP.initializeCache()
        except:
            print("Cache initialziation failed")
        tb.Style().theme_use(FP.getPreferences())

        ######################
        #LAYOUT SETUP
        ######################
        #The 3 PanedWindows that divide the window into 4 sections
        self.PanedWindow_Base = tk.PanedWindow(self, orient=tk.VERTICAL)
        self.PanedWindow_Base.pack(expand=True, fill=tk.BOTH)

        self.PanedWindow_Top = tk.PanedWindow(self.PanedWindow_Base, orient=tk.HORIZONTAL)
        self.PanedWindow_Bottom = tk.PanedWindow(self.PanedWindow_Base, orient=tk.HORIZONTAL)
        self.PanedWindow_Base.add(self.PanedWindow_Top, stretch="always")
        self.PanedWindow_Base.add(self.PanedWindow_Bottom, stretch="middle")

        #panedWindow color
        self.panedWindowColor = tb.Style().colors.primary
        self.PanedWindow_Base.config(bg=self.panedWindowColor)
        self.PanedWindow_Top.config(bg=self.panedWindowColor)
        self.PanedWindow_Bottom.config(bg=self.panedWindowColor)

        # #PanedWindow Options
        self.PanedWindow_Base.config(sashrelief=tk.FLAT, sashwidth=4, showhandle=False, opaqueresize=False, bd=0)
        self.PanedWindow_Top.config(sashrelief=tk.FLAT, sashwidth=6, showhandle=False, opaqueresize=False, bd=0)
        self.PanedWindow_Bottom.config(sashrelief=tk.FLAT, sashwidth=6, showhandle=False, opaqueresize=False, bd=0)


        self.mediaFrame = tb.Frame(self.PanedWindow_Top)
        self.PanedWindow_Top.add(self.mediaFrame)
        self.mediaBucket: MediaBucket = None

        self.imageFrame = tb.Frame(self.PanedWindow_Top)
        self.PanedWindow_Top.add(self.imageFrame)
        self.imageViewer: ImageViewer = None

        self.slideInfoFrame = tb.Frame(self.PanedWindow_Bottom)
        self.PanedWindow_Bottom.add(self.slideInfoFrame)
        self.slideInfoButton: InfoFrame = None

        self.reelFrame = tb.Frame(self.PanedWindow_Bottom)
        self.PanedWindow_Bottom.add(self.reelFrame)
        self.slideReel: SlideReel = None

        #Sets the initial sizes for the PanedWindows
        #Maybe this isn't the best method for setting the initial sizes? Idk. If yall have a better method, let me know. - James
        win_width_start = self.master.winfo_screenwidth()//2
        win_height_start = self.master.winfo_screenheight()//2
        self.PanedWindow_Base.paneconfigure(self.PanedWindow_Top, height=win_height_start//10*7, minsize=180)
        self.PanedWindow_Base.paneconfigure(self.PanedWindow_Bottom, height=win_height_start//10*3, minsize=170)
        self.PanedWindow_Top.paneconfigure(self.mediaFrame, width=win_width_start//10*6, minsize=130)
        self.PanedWindow_Top.paneconfigure(self.imageFrame, width=win_width_start//10*4, minsize=100)
        self.PanedWindow_Bottom.paneconfigure(self.slideInfoFrame, width=win_width_start//10*4, minsize=300)
        self.PanedWindow_Bottom.paneconfigure(self.reelFrame, width=win_width_start//10*6, minsize=200)

        #Initialize these widgets. They will probably have to be redrawn later though.
        self.infoViewer = InfoFrame(self.slideInfoFrame, slideshow=self.slideshow)
        self.infoViewer.pack(expand=True, fill="both")

        #Create the ImageViewer object
        self.imageViewer = ImageViewer(self.imageFrame)
        self.imageViewer.pack(expand=True, fill="both")

        self.slideReel = SlideReel(self.reelFrame, slideshow=self.slideshow)
        self.slideReel.pack(expand=True, fill="both", side="bottom")
        try:
            self.slideReel.linkPreviewer(self.imageViewer)
        except:
            print("No imageViewer to link to")
        try:
            self.slideReel.linkInfoFrame(self.infoViewer)
        except:
            print("No infoViewer to link to")

        #Mediabucket
        self.mediaBucket = MediaBucket(self.mediaFrame, slideshow=self.slideshow)
        self.mediaBucket.pack(expand=True, fill="both")
        try:
            self.mediaBucket.linkPreviewer(self.imageViewer)
        except:
            print("No imageViewer to link to")
        try:
            self.mediaBucket.linkReel(self.slideReel)
        except:
            print("No slideReel to link to")
        try:
            self.mediaBucket.linkInfoFrame(self.infoViewer)
        except:
            print("No infoViewer to link to")

        self.debugWindow: tk.Toplevel = None

        #Menubar
        self.menubar = tb.Menu(self.master)
        self.master.config(menu=self.menubar)
        self.projectMenu = tb.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Project", menu=self.projectMenu)
        self.projectMenu.add_command(label="New Project", command=self.newProject)
        self.projectMenu.add_command(label="Open Project", command=self.openProject)
        self.projectMenu.add_separator()
        self.projectMenu.add_command(label="Save", command=self.save)
        self.projectMenu.add_command(label="Save As", command=self.saveAs)
        self.projectMenu.add_separator()
        self.projectMenu.add_command(label="Exit", command=self.quit)

        self.fileMenu = tb.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="Add file", command=self.addFile)
        self.fileMenu.add_command(label="Add folder", command=self.addFolder)
        self.fileMenu.add_separator()
        if self.mediaBucket:
            self.fileMenu.add_command(label="Revert addition", command=self.mediaBucket.undoAdd)
        self.fileMenu.add_command(label="Debug", command=self.DebugWindow)

        self.themeMenu = tb.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Theme", menu=self.themeMenu)
        self.themeMenu.add_command(label="Theme Selector", command=self.ThemeSelector)

        self.winWidth = self.master.winfo_width()
        self.winHeight = self.master.winfo_height()

        self.after_id = None
        #Will call redraw event once super quickly, and then bind it to the resize event
        self.update_idletasks()
        self.after(33, self.redraw)

    def afterEvent(self, event):
        if self.after_id:
            self.after_cancel(self.after_id)
        else:
            #First time the window is resized, turn off the autoResize
            print("\n", "Window starting to change size. Widget autoResize turned off.")
            if self.imageViewer:
                self.imageViewer.autoResizeToggle(False)
            if self.mediaBucket:
                self.mediaBucket.autoResizeToggle(False)
            if self.slideReel:
                self.slideReel.autoResizeToggle(False)
        self.after_id = self.after(500, self.redraw)
        return


    def redraw(self):
        """
        Redraws the ImageViewer, MediaBucket, and SlideReel.\n
        Basically the SlideshowCreator object gets made and creates all the other widgets, but it doesn't actually exist in a window yet.\n
        This means all the widgets are sized to like 1x1 pixels. These functions will resize them to fit the new window properly.\n
        Possibly not necesary as the widgets themselves should call their own redraw functions when they are resized. - James
        """
        print("\nWindow changed size. Turning on autoResize for widgets.")
        self.after_id = None
        self.bind("<Configure>", self.afterEvent)

        if self.imageViewer:
            self.imageViewer.redrawImage()
            self.imageViewer.autoResizeToggle(True)

        if self.mediaBucket:
            self.mediaBucket.fillBucket()
            self.mediaBucket.autoResizeToggle(True)

        if self.slideReel:
            self.slideReel.refreshReel()
            self.slideReel.autoResizeToggle(True)

        return

        


    def DebugWindow(self):
        self.debugWindow = tk.Toplevel()
        self.debugWindow.transient(self.master)
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
        if self.mediaBucket:
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
        if self.slideReel:
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
        if self.debugWindow:
            self.debugWindow.destroy()
        self.destroy()
        self.creator = SlideshowCreator(self.master, projectPath=path)
        self.creator.pack(expand=True, fill="both")
        self.update_idletasks()
        print(self.creator.slideshow)

    def save(self):
        print("Save")
        self.slideshow.filesInProject = self.mediaBucket.files
        if self.slideshow.getSaveLocation() == "New Project":
            self.saveAs()
        else:
            self.slideshow.save()
            self.redraw()
        
    def saveAs(self):
        print("Save As")
        path = filedialog.asksaveasfilename(defaultextension=".pyslide", filetypes=[("Slideshow Files", "*.pyslide")])
        if not path:
            return
        print(f"Path: {path}")
        self.slideshow.filesInProject = self.mediaBucket.files
        self.slideshow.setSaveLocation(path)
        self.slideshow.save()
        self.redraw()

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

    def ThemeSelector(self):
        window = tb.Toplevel()
        window.transient(self.master)
        window.title("Theme Selector")
        window.geometry("400x400")
        #Get the theme currently used by the program.
        currentTheme: str = self.master.tk.call("ttk::style", "theme", "use")
        print(f"Current Theme: {currentTheme}")
        selectedTheme: str = currentTheme
        
        #Current theme label
        currentThemeLabel = tb.Label(window, text=f"Current Theme: {currentTheme}")
        currentThemeLabel.pack(pady=10)

        #Label for the currently selected theme
        selectedThemeLabel = tb.Label(window, text=f"Selected Theme: {selectedTheme}")
        selectedThemeLabel.pack(pady=10)

        def saveTheme(theme: str):
            nonlocal currentTheme
            currentTheme = theme
            currentThemeLabel.config(text=f"Current Theme: {currentTheme}")
            FP.updatePreferences(theme)

        #save theme button
        saveThemeButton = tb.Button(window, text="Save Theme", command=lambda: saveTheme(selectedTheme))
        saveThemeButton.pack(pady=10)

        #List of themes in TTKBootstrap
        #https://ttkbootstrap.readthedocs.io/en/latest/themes/
        themes = ["litera", "solar", "superhero", "darkly", "cyborg", "vapor", "cosmo", "flatly", "journal", "lumen", "minty", "pulse", "sandstone", "united", "yeti", "morph", "simplex", "cerculean"]
        #combobox for the themes
        themeList = tb.Combobox(window, values=themes)
        themeList.pack(expand=False, fill="none", pady=10)
        themeList.set(selectedTheme)

        def changeTheme(theme: str):
            nonlocal selectedTheme
            selectedTheme = theme
            selectedThemeLabel.config(text=f"Selected Theme: {theme}")
            self.changeTheme(theme)

        themeList.bind("<<ComboboxSelected>>", lambda event: changeTheme(themeList.get()))

        #Bind closing the window to changing the theme to the currentTheme
        def on_closing():
            self.changeTheme(currentTheme)
            window.destroy()
        window.protocol("WM_DELETE_WINDOW", on_closing)


    def changeTheme(self, theme: str):
        print(f"Changing theme to {theme}")
        tb.Style().theme_use(theme)

        self.panedWindowColor = tb.Style().colors.primary
        self.PanedWindow_Base.config(bg=self.panedWindowColor)
        self.PanedWindow_Top.config(bg=self.panedWindowColor)
        self.PanedWindow_Bottom.config(bg=self.panedWindowColor)

        self.master.update_idletasks()
        self.master.update()
        self.redraw()

    def quit(self):
        self.master.quit()

if __name__ == "__main__":
    root = tb.Window()
    root.title("Slideshow Creator")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
    #minimum size
    root.minsize(600, 500)
    # app = SlideshowCreatorStart(root)
    app = SlideshowCreator(root, debug=False, projectPath=r"C:\Users\JamesH\Pictures\cat\kitty.pyslide")
    # app = SlideshowCreator(root, debug=False, projectPath=r"C:\Users\flami\OneDrive - uah.edu\CS499\TestSlideshow.pyslide")
    app.pack(expand=True, fill="both")

    app.mainloop()
