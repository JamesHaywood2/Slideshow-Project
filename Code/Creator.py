import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from Widgets import *
from tkinter import filedialog
import Player as Player
import FileSupport as FP


# FP.file_check(path, RELATIVE_PROJECT_PATH)

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
        self.buttonFrame = tb.Frame(self)
        self.newProjectButton = tb.Button(self.buttonFrame, text="New Project", command=self.newProject)
        self.openProjectButton = tb.Button(self.buttonFrame, text="Open Project", command=self.openProject)
        self.recentSlideshowList = RecentSlideshowList(self)

        self.label.place(relx=0.5, rely=0.15, anchor="center")
        self.buttonFrame.place(relx=0.5, rely=0.25, anchor="center")
        self.newProjectButton.pack(padx=10, side="left")
        self.openProjectButton.pack(padx=10, side="right")
        self.recentSlideshowList.place(relx=0.5, rely=0.6, anchor="center", relwidth=0.8, relheight=0.5)

        #Set window size
        self.master.geometry("800x600")
        #Resizable window false
        self.master.resizable(False, False)

        #Set the size of recentSlideshowList to be 3/4 of the window width and 1/3 of the window height
        # self.recentSlideshowList.config(width=600, height=200)

        #Bind double clicking the recentSlideshowList to open the project
        self.recentSlideshowList.tableView.view.bind("<Double-1>", self.openRecentProject)

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

    def newProject(self):
        """Loads the slideshow creator window without a project file. This will create a new project."""
        #Create a SlideshowCreator object, destroy the current window, and pack the new window
        # folder = filedialog.askdirectory(mustexist=True)
        # if not folder:
        #     return
        self.destroy()
        self: SlideshowCreator = SlideshowCreator(self.master)
        self.pack(expand=True, fill="both")

    def openProject(self):
        """Loads the slideshow creator window with a project file. This will open an existing project."""
        #Create a SlideshowCreator object, destroy the current window, and pack the new window
        projectPath = filedialog.askopenfilename(filetypes=[("Slideshow Files", "*.pyslide")], multiple=False)
        if projectPath == "":
            return
        self.destroy()
        self = SlideshowCreator(self.master, projectPath=projectPath)
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
        self = SlideshowCreator(self.master, projectPath=projectPath)
        self.pack(expand=True, fill="both")
  
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
        master.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
        master.resizable(True, True)
        super().__init__(master, **kw)
        self.debug = debug
        #Check if the projectPath even exists
        try:
            open(projectPath, "r")
        except:
            projectPath = "New Project"
        self.slideshow = FP.Slideshow(projectPath)
        self.slideshow.load()
        FP.relative_project_path = self.slideshow.getSaveLocation()
        
        self.update_idletasks()
        try:
            FP.initializeCache()
        except:
            print("Cache initialziation failed")

        try:
            FP.updateSlideshowCacheList(self.slideshow.getSaveLocation())
        except:
            print("Failed to update the slideshow cache list")

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

        
        self.changeLayout(0)

        self.debugWindow: tk.Toplevel = None

        ########################
        ######  MENU BAR #######
        ########################

        #MenuFrame
        self.style = tb.Style()
        self.style.configure("custom.TFrame", background=self.style.colors.primary)
        self.menuFrame = tb.Frame(self, style="custom.TFrame")
        self.menuFrame.pack(side="top", fill="x")
        self.PanedWindow_Base.pack_forget()
        self.PanedWindow_Base.pack(expand=True, fill="both")

        #MenuButtons
        self.style.configure('TMenubutton', arrowsize=0, relief=FLAT, arrowpadding=0, font=("Arial", 10))
        self.projectMB = tb.Menubutton(self.menuFrame, text="Project", style="TMenubutton")
        self.projectMB.pack(side="left")
        self.fileMB = tb.Menubutton(self.menuFrame, text="File", style="TMenubutton")
        self.fileMB.pack(side="left")
        self.themeMB = tb.Menubutton(self.menuFrame, text="View", style="TMenubutton")
        self.themeMB.pack(side="left")

        #Project Menu
        self.projectMenu = tb.Menu(self.projectMB, tearoff=0)
        self.projectMenu.add_command(label="New Project", command=self.newProject)
        self.projectMenu.add_command(label="Open Project", command=self.openProject)
        self.projectMenu.add_separator()
        self.projectMenu.add_command(label="Save", command=self.save)
        self.projectMenu.add_command(label="Save As", command=self.saveAs)
        self.projectMenu.add_separator()
        self.projectMenu.add_command(label="Export Project", command=lambda: self.slideshow.exportToFolder(filedialog.askdirectory()))
        self.projectMenu.add_separator()
        self.projectMenu.add_command(label="Export to Player", command=self.exportToPlayer)
        self.projectMenu.add_separator()
        self.projectMenu.add_command(label="Exit", command=self.quit)
        self.projectMB.config(menu=self.projectMenu)

        #File Menu
        self.fileMenu = tb.Menu(self.fileMB, tearoff=0)
        self.fileMenu.add_command(label="Add file", command=self.addFile)
        self.fileMenu.add_command(label="Add folder", command=self.addFolder)
        self.fileMenu.add_separator()
        if self.mediaBucket:
            self.fileMenu.add_command(label="Revert addition", command=self.mediaBucket.undoAdd)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Open Cache", command=FP.openCacheFolder)
        self.fileMenu.add_command(label="Clear Cache", command=FP.clearCache)
        self.fileMB.config(menu=self.fileMenu)

        #Theme Menu
        self.themeMenu = tb.Menu(self.themeMB, tearoff=0)
        self.themeMenu.add_command(label="Theme Selector", command=self.ThemeSelector)
        self.themeMenu.add_separator()
        #Edit the style of the RadioButton so the indicator is different from the background
        layouts = [1, 2]
        self.layoutVar = tk.IntVar()
        self.themeMenu.add_radiobutton(label="Layout 1", command=lambda: self.changeLayout(1), variable=self.layoutVar, value=1, selectcolor=self.style.colors.get("selectfg"))
        self.themeMenu.add_radiobutton(label="Layout 2", command=lambda: self.changeLayout(2), variable=self.layoutVar, value=2, selectcolor=self.style.colors.get("selectfg"))
        self.layoutVar.set(1)
        self.themeMB.config(menu=self.themeMenu)

        self.projectMenu.config(background=self.style.colors.primary, foreground=self.style.colors.get("selectfg"))
        self.fileMenu.config(background=self.style.colors.primary, foreground=self.style.colors.get("selectfg"))
        self.themeMenu.config(background=self.style.colors.primary, foreground=self.style.colors.get("selectfg"))

        self.winWidth = self.master.winfo_width()
        self.winHeight = self.master.winfo_height()

        #Bind hitting escape to putting focus on the window
        self.bind_all("<Escape>", lambda event: self.master.focus_set())

        #Bind ctrl+s to save
        self.bind_all("<Control-s>", lambda event: self.save())
        self.bind_all("<Button-1>", lambda event: event.widget.focus_set())

        #Bind enter to the window
        self.bind("<Enter>", self.enterWindow)

        self.after_id = None
        #Will call redraw event once super quickly, and then bind it to the resize event
        self.update_idletasks()
        # self.update()
        self.after(66, self.redraw)

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

        if self.infoViewer:
            self.infoViewer.fillProjectInfo()
            self.infoViewer.fillSlideInfo()         
        return

    def changeLayout(self, layout: int):
        #Layout 1 has media bucket top left, imageViewer top right, infoframe bottom left, and slideReel bottom right
        #Layout 2 has the MediaBucket on the left, imageViewer in the center, and infoframe on the right and below all of that is the slideReel
        possible_layouts = [0,1, 2]
        if layout not in possible_layouts:
            return
        
        #Destroy the autoResize event
        if layout != 0 and self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
            print("AutoResize event turned off.")

        #Destroy the current widgets
        if layout != 0:
            self.mediaFrame.destroy()
            self.imageFrame.destroy()
            self.slideInfoFrame.destroy()
            self.reelFrame.destroy()


        if layout == 1 or layout == 0:
            self.mediaFrame = tb.Frame(self.PanedWindow_Top)
            self.PanedWindow_Top.add(self.mediaFrame)
            self.mediaBucket: MediaBucket = None

            self.imageFrame = tb.Frame(self.PanedWindow_Top)
            self.PanedWindow_Top.add(self.imageFrame)
            self.imageViewer: ImageViewer = None

            self.slideInfoFrame = tb.Frame(self.PanedWindow_Bottom)
            self.PanedWindow_Bottom.add(self.slideInfoFrame)
            self.infoViewer: InfoFrame = None

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

            self.update_idletasks()
        elif layout == 2:
            self.mediaFrame = tb.Frame(self.PanedWindow_Top)
            self.PanedWindow_Top.add(self.mediaFrame, stretch="always")
            self.mediaBucket: MediaBucket = None

            self.imageFrame = tb.Frame(self.PanedWindow_Top)
            self.PanedWindow_Top.add(self.imageFrame, stretch="always")
            self.imageViewer: ImageViewer = None

            self.slideInfoFrame = tb.Frame(self.PanedWindow_Top)
            self.PanedWindow_Top.add(self.slideInfoFrame, stretch="always")
            self.infoViewer: InfoFrame = None

            self.reelFrame = tb.Frame(self.PanedWindow_Bottom)
            self.PanedWindow_Bottom.add(self.reelFrame)
            self.slideReel: SlideReel = None

            #Sets the initial sizes for the PanedWindows
            #Maybe this isn't the best method for setting the initial sizes? Idk. If yall have a better method, let me know. - James
            win_width_start = self.master.winfo_screenwidth()//2
            win_height_start = self.master.winfo_screenheight()//2
            self.PanedWindow_Base.paneconfigure(self.PanedWindow_Top, height=win_height_start//10*7, minsize=180)
            self.PanedWindow_Base.paneconfigure(self.PanedWindow_Bottom, height=170, minsize=170)
            self.PanedWindow_Top.paneconfigure(self.mediaFrame, width=win_width_start//10*6, minsize=110)
            self.PanedWindow_Top.paneconfigure(self.imageFrame, width=win_width_start//10*3, minsize=100)
            self.PanedWindow_Top.paneconfigure(self.slideInfoFrame, width=win_width_start//10*6, minsize=100)
            self.PanedWindow_Bottom.paneconfigure(self.reelFrame, width=win_width_start//10*6, minsize=200)

            self.update_idletasks()

        #Initialize these widgets. They will probably have to be redrawn later though.
        self.infoViewer = InfoFrame(self.slideInfoFrame, slideshow=self.slideshow)
        self.infoViewer.pack(expand=True, fill="both")

        self.update_idletasks()

        #Create the ImageViewer object
        self.imageViewer = ImageViewer(self.imageFrame)
        self.imageViewer.pack(expand=True, fill="both")

        self.update_idletasks()

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

        self.update_idletasks()

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

        self.update_idletasks()

        if layout != 0:
            self.after(66, self.redraw)
        
    def enterWindow(self, event):
        self.style.configure("custom.TFrame", background=self.style.colors.primary)
        self.style.configure('TMenubutton', arrowsize=0, relief=FLAT, arrowpadding=0, font=("Arial", 10))
        self.projectMenu.config(background=self.style.colors.primary, foreground=self.style.colors.get("selectfg"))
        self.fileMenu.config(background=self.style.colors.primary, foreground=self.style.colors.get("selectfg"))
        self.themeMenu.config(background=self.style.colors.primary, foreground=self.style.colors.get("selectfg"))   
        return

    def newProject(self):
        #Basically destroy the current SlideshowCreator object and create a new one
        self.destroy()
        self = SlideshowCreator(self.master)
        self.pack(expand=True, fill="both")

    def openProject(self):
        print("Open Project")
        #Destroy the debug window
        path = filedialog.askopenfilename(filetypes=[("Slideshow Files", "*.pyslide")])
        if not path:
            return
        if self.debugWindow:
            self.debugWindow.destroy()


        #Destroy the menubar
        if self.menuFrame:
            print("Destroying menuFrame")
            self.menuFrame.destroy()

        #Destroy EVERYTHING child of the master window
        for widget in self.master.winfo_children():
            widget.destroy()
        
        self.pack_forget()
        self.update()

        self = SlideshowCreator(self.master, projectPath=path)
        self.pack(expand=True, fill="both")
        self.update_idletasks()
        print(f"New slideshow name: {self.slideshow.name}")
        

    def save(self):
        print("Save")
        self.slideshow.filesInProject = self.mediaBucket.files
        if self.slideshow.getSaveLocation() == "New Project":
            self.saveAs()
        else:
            self.slideshow.save()
            self.redraw()
            try:
                FP.updateSlideshowCacheList(self.slideshow.getSaveLocation())
            except:
                print("Failed to update the slideshow cache list")

            try:
                #Export the project to the cache
                self.slideshow.exportToCache()
            except:
                print("Failed to export the project to the cache")
        
    def saveAs(self):
        print("Save As")
        path = filedialog.asksaveasfilename(defaultextension=".pyslide", filetypes=[("Slideshow Files", "*.pyslide")])
        if not path:
            return
        print(f"Path: {path}")
        self.slideshow.filesInProject = self.mediaBucket.files
        self.slideshow.setSaveLocation(path)
        self.update_idletasks()
        self.slideshow.save()
        self.redraw()

    def exportToPlayer(self):
        #Save the project
        self.save()
        #Create a new top level window
        window = tb.Toplevel()
        # window.transient(self.master)
        window.title("Slideshow Player")
        window.geometry("800x600")
        window.resizable(True, True)
        #Create a new SlideshowPlayer object
        player = Player.SlideshowPlayer(window, projectPath=self.slideshow.getSaveLocation())
        player.pack(expand=True, fill="both")


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
        # themes = ["litera", "solar", "superhero", "darkly", "cyborg", "vapor", "cosmo", "flatly", "journal", "lumen", "minty", "pulse", "sandstone", "united", "yeti", "morph", "simplex", "cerculean"]
        themes = tb.Style().theme_names()
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
        self.style.theme_use(theme)

        self.panedWindowColor = self.style.colors.primary
        self.PanedWindow_Base.config(bg=self.panedWindowColor)
        self.PanedWindow_Top.config(bg=self.panedWindowColor)
        self.PanedWindow_Bottom.config(bg=self.panedWindowColor)
        self.style.configure("custom.TFrame", background=self.style.colors.primary)
        self.style.configure('TMenubutton', arrowsize=0, relief=FLAT, arrowpadding=0, font=("Arial", 10))
        self.projectMenu.config(background=self.style.colors.primary, foreground=self.style.colors.get("selectfg"))
        self.fileMenu.config(background=self.style.colors.primary, foreground=self.style.colors.get("selectfg"))
        self.themeMenu.config(background=self.style.colors.primary, foreground=self.style.colors.get("selectfg"))
        

        self.master.update_idletasks()
        # self.master.update()
        self.redraw()

    def quit(self):
        print("Quiting Creator...")
        self.master.quit()

if __name__ == "__main__":
    root = tb.Window()
    root.title("Slideshow Creator")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
    #minimum size
    root.minsize(600, 500)
    app = SlideshowCreatorStart(root)
    #User HOME directory
    usrDir = FP.getUserHome()
    testPath = usrDir + "\Pictures\cat\kitty.pyslide"
    # testPath = usrDir + "\OneDrive - uah.edu\CS499\TestSlideshow.pyslide"
    # app = SlideshowCreator(root, debug=False, projectPath=testPath)
    app.pack(expand=True, fill="both")

    app.mainloop()

