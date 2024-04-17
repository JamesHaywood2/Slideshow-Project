import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import *
from Widgets import *
from tkinter import filedialog
import Player as Player
import FileSupport as FP
import SQLSaver as SQ

import pprint


# FP.file_check(path, RELATIVE_PROJECT_PATH)

class StartMenu(tb.Frame):
    """Start window for the Slideshow Creator but using the Database.\n
    This window will allow you to select a project, choose to delete it, rename it, open it, create a new one, whatever."""
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        try:
            FP.initializeCache()
        except:
            print("Cache initialziation failed")
        tb.Style().theme_use(FP.getPreferences())

        self.bind("<Configure>", self.create_widgets)


    def create_widgets(self, *args):
        """Creates the widgets for the start window."""
        #unbind the configure event
        self.unbind("<Configure>")
        self.label = tb.Label(self, text="Slideshow Creator", font=("Arial", 28, "bold"))
        self.label.place(relx=0.5, rely=0.1, anchor="s")

        self.slideshowList = SlideshowListDatabase(self)
        self.slideshowList.place(anchor="nw", relx=0.505, rely=0.1, relwidth=0.48, relheight=0.85)

        #Bind double clicking the recentSlideshowList to open the project
        # self.slideshowList.tableView.view.bind("<Double-1>", self.openProject)

        #Bind single clicking the recentSlideshowList to display the project info
        self.slideshowList.tableView.view.bind("<ButtonRelease-1>", self.displayProjectInfo)

        #Sort the tableview by the 3rd column (last modified)
        self.slideshowList.tableView.sort_column_data(cid=2, sort=1)

        #Labelframe for info
        self.infoFrame = tb.LabelFrame(self, text="Project Info", bootstyle="primary")
        self.infoFrame.place(anchor="ne", relx=0.495, rely=0.1, relwidth=0.48, relheight=0.6)

        self.scrollFrame = ScrollableFrame(self.infoFrame, orient="both", autohide=True)
        # self.Frame = ScrolledFrame(self.infoFrame, autohide=False)
        self.Frame = self.scrollFrame.scrollable_frame

        #Set the ScrolledFrame style to be red
        tb.Style().configure("test.TFrame", background="red")
        # self.infoFrame.config(style="test.TFrame")
        # self.config(style="test.TFrame")

        # Create a custom style for the bold labels
        tb.Style().configure("Bold.TLabel", font=("Arial", 14, "bold"))
        tb.Style().configure("value.TLabel", font=("Arial", 12))

        # Create the bold labels
        self.nameLabel = tb.Label(self.Frame, text="Name:", style="Bold.TLabel")
        self.idLabel = tb.Label(self.Frame, text="ID:", style="Bold.TLabel")
        self.modifiedLabel = tb.Label(self.Frame, text="Last Modified:", style="Bold.TLabel")

        self.nameLabel.grid(row=0, column=0)
        self.idLabel.grid(row=1, column=0)
        self.modifiedLabel.grid(row=2, column=0)

        self.nameValue = tb.Label(self.Frame, text="Name Value", style="value.TLabel")
        self.idValue = tb.Label(self.Frame, text="ID Value", style="value.TLabel")
        self.modifiedValue = tb.Label(self.Frame, text="Last Modified Value", style="value.TLabel")

        self.nameValue.grid(row=0, column=1, sticky="w")
        self.idValue.grid(row=1, column=1, sticky="w")
        self.modifiedValue.grid(row=2, column=1, sticky="w")


        self.tagFrame = ScrolledFrame(self.infoFrame, autohide=True)
        self.tagLabel = tb.Label(self.tagFrame, text="Tags:", style="Bold.TLabel")
        self.tagLabel.pack(fill="x", expand=True)

        self.update()
        buttonHeight = self.nameLabel.winfo_height() * 3

        #ScrollFrame houses the buttons
        self.scrollFrame.place(anchor="nw", relx=0, rely=0, relwidth=1, height=buttonHeight)
        self.scrollFrame.update_idletasks()
        relHeight = 1 - (self.scrollFrame.winfo_height() / (self.infoFrame.winfo_height()*0.9))
        self.tagFrame.place(anchor="nw", relx=0, y=self.scrollFrame.winfo_height(), relwidth=1, relheight=relHeight)


        self.tagBox = TagBox(self.tagFrame, tags=[], justDisplay=True)
        self.tagBox.pack(fill="both", expand=True)

        #Load the first entry if there is one
        if len(self.slideshowList.slideshows) > 0:
            #Get the very first entry in the list
            item = self.slideshowList.tableView.view.item(self.slideshowList.tableView.view.get_children()[0], "values")
            projectID = int(item[0])
            self.displayProjectInfo(projectID=projectID)

        #set the focus to the slideshowList
        self.slideshowList.tableView.view.focus_set()

        ########
        #Buttons:
        ########
        #new, open, rename, deleted, import, play

        #Convert a relative height of 0.205 to a pixel value
        height = self.winfo_height() * 0.25

        self.actionsFrame = tb.LabelFrame(self, text="Actions", bootstyle="primary")
        # self.actionsFrame.place(anchor="ne", relx=0.495, rely=0.7, relwidth=0.48, height=height)
        self.actionsFrame.place(anchor="se", relx=0.495, rely=0.95, relwidth=0.48, height=height)

        self.topFrame = tb.Frame(self.actionsFrame)
        self.topFrame.pack(expand=True, fill="both")
        self.bottomFrame = tb.Frame(self.actionsFrame)
        self.bottomFrame.pack(expand=True, fill="both")
        self.topFrame.update_idletasks()
        self.bottomFrame.update_idletasks()

        tb.Style().configure("Start.success.TButton", font=("Arial", 10))
        tb.Style().configure("Start.danger.TButton", font=("Arial", 10))
        tb.Style().configure("Start.info.TButton", font=("Arial", 10))
        tb.Style().configure("Start.TButton", font=("Arial", 10))

        #Button for new project, open project, rename project, delete project
        self.newProjectButton = tb.Button(self.topFrame, text="New Project", command=self.newProject, style="Start.success.TButton")
        self.openProjectButton = tb.Button(self.topFrame, text="Open Project", command=self.openProject, style="Start.TButton")
        self.renameProjectButton = tb.Button(self.topFrame, text="Rename Project", command=self.renameProject, style="Start.TButton")
        self.deleteProjectButton = tb.Button(self.topFrame, text="Delete Project", command=self.deleteProject, style="Start.danger.TButton")
        self.importButton = tb.Button(self.bottomFrame, text="Import", command=self.importFromFile, style="Start.TButton")
        self.playButton = tb.Button(self.bottomFrame, text="Play", command=self.openPlayer, style="Start.TButton")
        self.themesButton = tb.Button(self.bottomFrame, text="Themes", command=self.ThemeSelector, style="Start.info.TButton")
        self.actionsFrame.update_idletasks()

        xpad=5
        self.newProjectButton.pack(side="left", padx=xpad, pady=10)
        self.openProjectButton.pack(side="left", padx=xpad, pady=10)
        self.renameProjectButton.pack(side="left", padx=xpad, pady=10)
        self.deleteProjectButton.pack(side="left", padx=xpad, pady=10)
        self.importButton.pack(side="left", padx=xpad, pady=10)
        self.playButton.pack(side="left", padx=xpad, pady=10)
        self.themesButton.pack(side="left", padx=xpad, pady=10)

        self.topFrame.update_idletasks()
        self.bottomFrame.update_idletasks()

        self.defaultDeleteWidth = self.deleteProjectButton.winfo_width()
        self.defaultDeleteX = self.deleteProjectButton.winfo_x()

        #Scaled font size
        self.fontSize = 10
        self.resizeFont()

        #bind the configure event to the afterEvent function
        self.bind("<Configure>", lambda event: self.afterEvent(event, "<<Resize>>"))
        #bind custom event to resizeEvent
        self.bind("<<Resize>>", self.resizeEvent)
        self.after_id = {}
        self.after_id["<<Resize>>"] = None

    def afterEvent(self, event, event2=None):
        # print(event2)
        try:
            if self.after_id[event2]:
                self.after_cancel(self.after_id[event2])
                self.after_id[event2] = None
            else:
                #Generate an event for event2
                self.after_id[event2] = self.after(33, self.resizeEvent)
        except Exception as e:
            print(e)
        return
    
    def resizeFont(self):
        root.update_idletasks()

        #Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        width = root.winfo_width()
        height = root.winfo_height()

        width_scale = width / screen_width
        height_scale = height / screen_height

        #Scale the font size
        scaling_factor = width_scale
        new_fontsize = int(24 * scaling_factor)
        if new_fontsize < 10:
            self.fontSize = 10
            self.resizeButtons()
        else:
            self.fontSize = new_fontsize
            self.resizeButtons()
        # print(f"\nWidth Scale: {width_scale}, Height Scale: {height_scale}")
        # print(f"Font Size: {self.fontSize}")
        tb.Style().configure("Start.success.TButton", font=("Arial", self.fontSize))
        tb.Style().configure("Start.danger.TButton", font=("Arial", self.fontSize))
        tb.Style().configure("Start.info.TButton", font=("Arial", self.fontSize))
        tb.Style().configure("Start.TButton", font=("Arial", self.fontSize))
            
    def resizeButtons(self):
        #Check if the buttons were cut off width wise
        self.deleteProjectButton.update_idletasks()
        self.actionsFrame.update_idletasks()
        
        defaultxval = self.defaultDeleteX + self.defaultDeleteWidth
        #Action frame width
        actionsFrameWidth = self.actionsFrame.winfo_width()

        if defaultxval > actionsFrameWidth:
            #Shorten to "del"
            self.deleteProjectButton.config(text="Del")
            self.newProjectButton.config(text="New")
            self.openProjectButton.config(text="Open")
            self.renameProjectButton.config(text="Rename")
        else:
            self.deleteProjectButton.config(text="Delete Project")
            self.newProjectButton.config(text="New Project")
            self.openProjectButton.config(text="Open Project")
            self.renameProjectButton.config(text="Rename Project")


    def resizeEvent(self, event=None):
        self.after_id["<<Resize>>"] = None
        # print("Resizing")
        self.resizeFont()

        self.update_idletasks()
        win_height = self.winfo_height()

        actionsFrame_height = self.actionsFrame.winfo_height()
        slideshowList_height = self.slideshowList.winfo_height()

        height_available = slideshowList_height - actionsFrame_height
        rel_height = height_available / win_height
        self.infoFrame.place_configure(relheight=rel_height)

        #Resize the infoFrame
        self.infoFrame.update_idletasks()
        buttonHeight = self.nameLabel.winfo_height() * 3

        # self.scrollFrame.place(anchor="nw", relx=0, rely=0, relwidth=1, height=buttonHeight)
        self.scrollFrame.update_idletasks()
        relHeight = 1 - (self.scrollFrame.winfo_height() / (self.infoFrame.winfo_height()*0.9))
        self.tagFrame.place(anchor="nw", relx=0, y=self.scrollFrame.winfo_height(), relwidth=1, relheight=relHeight)
        
        return

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
        tb.Style().theme_use(theme)
        #Update the InfoLabels
        tb.Style().configure("Bold.TLabel", font=("Arial", 14, "bold"))
        tb.Style().configure("value.TLabel", font=("Arial", 12))
        self.update_idletasks()
        return
        

    def displayProjectInfo(self, event=None, projectID=None):
        print("Displaying Project Info")
        item = self.slideshowList.tableView.view.selection()

        if len(item) == 0:
            return
        
        if projectID == None:
            projectID = self.slideshowList.tableView.view.item(item, "values")[0]
            projectID = int(projectID)
        s = self.slideshowList.slideshows[projectID]
        projectID, name, date, tags, tagString = SlideshowListDatabase.slideshowInfo(s)

        #Update the labels
        self.nameValue.config(text=name)
        self.idValue.config(text=projectID)
        self.modifiedValue.config(text=date)
        self.tagBox.updateTags(tags)

    def newProject(self):
        print("New Project")
        # name = self.nameProjectDialog()
        # if name == None:
        #     return
        # print(f"Creating new project: {name}")
        self.destroy()
        self = SlideshowCreator(self.master, projectPath="New Project")
        self.pack(expand=True, fill="both")


    def openProject(self, event=None, projectID=None):
        if projectID == None:
            #Get the selected project ID
            item = self.slideshowList.tableView.view.selection()
            if len(item) == 0:
                return
            projectID = self.slideshowList.tableView.view.item(item, "values")[0]
            projectID = int(projectID)
            s = self.slideshowList.slideshows[projectID]
            projectID, name, date, tags, tagString = SlideshowListDatabase.slideshowInfo(s)
 
        self.destroy()
        self = SlideshowCreator(self.master, projectPath="", slideshowID=projectID)
        self.pack(expand=True, fill="both")
        SQ.updateLastModified(projectID)


    def renameProject(self):
        print("Rename Project")
        #Get the ID from the selected project
        item = self.slideshowList.tableView.view.selection()
        if len(item) == 0:
            return
        projectID = self.slideshowList.tableView.view.item(item, "values")[0]
        projectID = int(projectID)
        s = self.slideshowList.slideshows[projectID]
        projectID, oldName, date, tags, tagString = SlideshowListDatabase.slideshowInfo(s)
        name = self.nameProjectDialog()
        while name == oldName or name == "":
            name = self.nameProjectDialog(invalid=True)
        if name == None:
            return
        #Update the name in the database
        SQ.renameSlideshow(projectID, name)
        #Update the name in the list
        self.slideshowList.slideshows[projectID]["name"] = name
        self.slideshowList.tableView.view.item(item, values=[projectID, name, self.slideshowList.slideshows[projectID]["lastModified"], tagString])
        #update the infoFrame
        self.nameValue.config(text=name)
        self.update_idletasks()
        
    def deleteProject(self):
        #Get the ID from the selected project
        item = self.slideshowList.tableView.view.selection()
        if len(item) == 0:
            return
        projectID = self.slideshowList.tableView.view.item(item, "values")[0]
        projectID = int(projectID)
        s = self.slideshowList.slideshows[projectID]
        projectID, name, date, tags, tagString = SlideshowListDatabase.slideshowInfo(s)
        #Dialog box to confirm deletion
        if not Messagebox.yesno(title="Delete Project", message=f"Are you sure you want to delete the project {name}?"):
            return
        print(f"Deleting project {name}")
        #Delete the project from the database
        SQ.deleteSlideshow(projectID)
        
    
    def nameProjectDialog(self, invalid=False, ErrorMessage:str="Invalid name. Please enter a name for the project"):
        if invalid:
            name = Querybox.get_string(prompt=ErrorMessage, title="Name Project")
        else:
            name = Querybox.get_string(prompt="Enter a name for the project", title="Name Project")
        if name == "":
            return self.nameProjectDialog(invalid=True, ErrorMessage="Name cannot be blank. Please enter a name for the project")
        if SQ.sqlProtector(name):
            return self.nameProjectDialog(invalid=True, ErrorMessage="SQL Injection detected. Please enter a different name for the project")
        if SQ.checkNameExists(name):
            return self.nameProjectDialog(invalid=True, ErrorMessage="Name already exists. Please enter a different name for the project")
        return name
    
    def importFromFile(self):
        print("Import from File")
        #Open a file dialog to select a file
        file = filedialog.askopenfilename(filetypes=[("Slideshow Files", "*.pyslide")])
        if file == "":
            return
        #Get the base name of the file
        name = file.split("/")[-1]
        #Remove the extension
        name = name.split(".")[0]
        #Check if the name already exists
        if SQ.checkNameExists(name):
            name = self.nameProjectDialog(invalid=True, ErrorMessage="Name already exists. Please enter a different name for the project")
            if name == None:
                return
        #Save the file to the database
        self.destroy()
        self = SlideshowCreator(self.master, projectPath=file)
        self.pack(expand=True, fill="both")
        self.slideshow.name = name
        self.redraw()
        SQ.saveSlideshow(self.slideshow)
        

    def openPlayer(self, projectID=None):
        print("Open Player")
        if projectID == None:
            #Get the selected project ID
            item = self.slideshowList.tableView.view.selection()
            if len(item) == 0:
                return
            projectID = self.slideshowList.tableView.view.item(item, "values")[0]
            projectID = int(projectID)
            s = self.slideshowList.slideshows[projectID]
            projectID, name, date, tags, tagString = SlideshowListDatabase.slideshowInfo(s)

        #check that the project exists
        if not SQ.checkSlideshowExists(projectID):
            #Create a messagebox to say the project doesn't exist
            Messagebox.showinfo(title="Project does not exist", message="The project you are trying to open does not exist.")
            return
        #Open the player
        self.destroy()
        self = Player.SlideshowPlayer(self.master, projectID=projectID)
        self.pack(expand=True, fill="both")
        SQ.updateLastModified(projectID)

class SlideshowCreator(tb.Frame):
    """
    The main application frame. Contains four main sections: MediaBucket, ImageViewer, SlideInfo, and SlideReel.\n
    MediaBucket: Contains all the media files that are in the project folder or added later.\n
    ImageViewer: Previews an image.\n
    SlideInfo: Contains the slide information.\n
    SlideReel: Contains all the slides in the project.

    redraw(): Redraws the ImageViewer, MediaBucket, and SlideReel. 
    """
    def __init__(self, master=None, projectPath: str="New Project", slideshowID:int = None, **kw):
        master.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
        master.resizable(True, True)
        super().__init__(master, **kw)
        #Check if the projectPath even exists
        openFromPath = False
        try:
            open(projectPath, "r")
            openFromPath = True
        except:
            projectPath = "New Project"
        self.slideshow = FP.Slideshow(projectPath)

        if slideshowID != None and SQ.checkSlideshowExists(slideshowID) and not openFromPath:
            self.slideshow = SQ.loadSlideshow(slideshowID)
            print("\nOpening project from ID")
        else:
            if openFromPath:
                print("\nOpening project from path")
            else:
                print("\nCreating new project")


        pprint.pprint(self.slideshow.__dict__)


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

    # def openProject(self):
    #     print("Open Project")
    #     path = filedialog.askopenfilename(filetypes=[("Slideshow Files", "*.pyslide")])
    #     if not path:
    #         return

    #     #Destroy the menubar
    #     if self.menuFrame:
    #         print("Destroying menuFrame")
    #         self.menuFrame.destroy()

    #     #Destroy EVERYTHING child of the master window
    #     for widget in self.master.winfo_children():
    #         widget.destroy()
        
    #     self.pack_forget()
    #     self.update()

    #     self = SlideshowCreator(self.master, projectPath=path)
    #     self.pack(expand=True, fill="both")
    #     self.update_idletasks()
    #     print(f"New slideshow name: {self.slideshow.name}")

    def openProject(self):
        print("Open Project")
        #Message box asking for confirmation
        if not Messagebox.yesno(title="Open Project", message="Are you sure you want to open a new project?"):
            return
        #Message box asking if you want to save the current project
        if Messagebox.yesno(title="Save Project", message="Would you like to save the current project?"):
            self.save()

        #Destroy the menubar
        if self.menuFrame:
            print("Destroying menuFrame")
            self.menuFrame.destroy()

        #Destroy EVERYTHING child of the master window
        for widget in self.master.winfo_children():
            widget.destroy()

        self.pack_forget()
        self.update()

        self = StartMenu(self.master)
        self.pack(expand=True, fill="both")
        self.update_idletasks()


    def save(self):
        print("Save")
        #Check if the project has a save location
        saveLocation = self.slideshow.getSaveLocation()
        if saveLocation == "New Project" or saveLocation == "Saved To Database":
            if self.slideshow.name == "New Project":
                name = self.nameProjectDialog()
                if name == None:
                    return
                self.slideshow.name = name
            SQ.saveSlideshow(self.slideshow)
        else:
            print(f"Save Location: {saveLocation}")
            SQ.saveSlideshow(self.slideshow, fromFile=True)

        self.update_idletasks()
        self.redraw()
        return True

        
    # def saveAs(self):
    #     """Effectively saves the project to a file."""
    #     print("Save As")
    #     path = filedialog.asksaveasfilename(defaultextension=".pyslide", filetypes=[("Slideshow Files", "*.pyslide")])
    #     if not path:
    #         return
    #     print(f"Path: {path}")
    #     self.slideshow.filesInProject = self.mediaBucket.files
    #     self.slideshow.setSaveLocation(path)
    #     self.update_idletasks()
    #     self.slideshow.save()
    #     self.redraw()

    def saveAs(self):
        """Effectively just changes the name of the project and erases the ID and saves it."""
        print("Save As")
        name = self.nameProjectDialog()
        if name == None:
            return
        self.slideshow.name = name
        self.slideshow.slideshowID = None
        self.save()
        return
        
        

    def renameProject(self, name=None):
        #ttkbootstrap Querybox get_string
        if name == None:
            name = self.nameProjectDialog()
        if name == None:
            return False
        self.slideshow.name = name
        self.redraw()
        self.save()
        return True
    
    def nameProjectDialog(self, invalid=False, ErrorMessage:str="Invalid name. Please enter a name for the project"):
        if invalid:
            name = Querybox.get_string(prompt=ErrorMessage, title="Name Project")
        else:
            name = Querybox.get_string(prompt="Enter a name for the project", title="Name Project")
        if name == "":
            return self.nameProjectDialog(invalid=True, ErrorMessage="Name cannot be blank. Please enter a name for the project")
        if SQ.sqlProtector(name):
            return self.nameProjectDialog(invalid=True, ErrorMessage="SQL Injection detected. Please enter a different name for the project")
        if SQ.checkNameExists(name):
            return self.nameProjectDialog(invalid=True, ErrorMessage="Name already exists. Please enter a different name for the project")
        return name
        

    def exportToPlayer(self):
        #Save the project
        self.save()
        #Create a new top level window
        window = tb.Toplevel()
        # window.transient(self.master)
        window.title("Slideshow Player")
        window.geometry("800x600")
        window.resizable(True, True)
        #Get the slideshowID
        projectID = self.slideshow.slideshowID
        #Create a new SlideshowPlayer object
        player = Player.SlideshowPlayer(window, projectID=projectID)
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
    #User HOME directory
    usrDir = FP.getUserHome()
    # testPath = usrDir + "\Pictures\cat\kitty.pyslide"
    # testPath = usrDir + "\OneDrive - uah.edu\CS499\TestSlideshow.pyslide"
    # app = SlideshowCreator(root, projectPath=testPath)

    # app = SlideshowCreatorStart(root)
    app = StartMenu(root)
    app.pack(expand=True, fill="both")

    app.mainloop()

