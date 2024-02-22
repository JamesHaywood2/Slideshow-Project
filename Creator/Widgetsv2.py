import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *
import FileSupport as FP
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from copy import deepcopy

updateRate = 100 #Milliseconds
    
class ScrollableFrame(tk.Frame):
    """
    A frame that can be scrolled vertically or horizontally.
    From https://blog.teclado.com/tkinter-scrollable-frames/
    """
    def __init__(self, container, orient: str="both", autohide:bool = True, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.orient = orient
        self.autohide = autohide

        horiz = False
        vert = False
        if orient == "both":
            horiz = True
            vert = True
        if orient == "horizontal":
            horiz = True
        if orient == "vertical":
            vert = True

        if horiz == False and vert == False:
            horiz = True
            vert = True

        if vert:
            self.scrollbar = tb.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        if horiz:
            self.scrollbar_h = tb.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # Get the size of the scrollableFrame
        height = self.canvas.winfo_height()

        self.canvasWindow = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        if vert:
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
        if horiz:
            self.canvas.configure(xscrollcommand=self.scrollbar_h.set)

        try:
            self.scrollbar_h.pack(side="bottom", fill="x")
            # self.scrollbar_h.grid(row=11, column=0, sticky="ew")
        except:
            pass
        try:
            self.scrollbar.pack(side="right", fill="y")
            # self.scrollbar.grid(row=0, column=11, sticky="ns")
        except:
            pass

        self.canvas.pack(side="left", fill="both", expand=True)
        # self.canvas.grid(row=0, column=0, sticky="nsew")

        self.verticle = vert
        self.horizontal = horiz
        if self.autohide:
            self.hideScrollBar()
            pass
        

        self.bind("<Enter>", self.bindMouseWheel)
        self.bind("<Leave>", self.unbindMouseWheel)

    def bindMouseWheel(self, event):
        self.showScrollBar()
        if self.verticle:
            self.scrollbar.bind_all("<MouseWheel>", self.onMouseWheel)
        if self.horizontal:
            self.scrollbar_h.bind_all("<MouseWheel>", self.onMouseWheel)
        return
    
    def unbindMouseWheel(self, event):
        self.hideScrollBar()
        try:
            self.scrollbar.unbind_all("<MouseWheel>")
        except:
            pass
        try:
            self.scrollbar_h.unbind_all("<MouseWheel>")
        except:
            pass
        return
    
    def onMouseWheel(self, event):
        #Prefer the verticle scrolling over the horizontal scrolling
        #Could probably set it to change based on the last scrollbar that was used with the mouse, but I dont see the need. - James
        if self.verticle:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.horizontal:
            self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        return
    
    def hideScrollBar(self):
        #Hiding horizontal scrollbar doesn't work. It's a byproduct of using pack. May be able to fix it by using grid, but I couldn't figure it out. - James

        #Unpack the scrollbar
        # try:
        #     self.scrollbar_h.pack_forget()
        #     # self.scrollbar_h.grid_remove()
        # except:
        #     pass
        try:
            self.scrollbar.pack_forget()
            # self.scrollbar.grid_remove()
        except:
            pass

    def showScrollBar(self):
        #Hiding horizontal scrollbar doesn't work. It's a byproduct of using pack. May be able to fix it by using grid, but I couldn't figure it out. - James
        #Another potential fix is to essentially repack the widget. This "works" but causes the widget to kinda flicker. Didn't like it. - James

        #pack remove the canvas, then pack the scrollbars, then pack the canvas
        # self.canvas.pack_forget()
        # self.canvas.grid_remove()
        # try:
        #     self.scrollbar_h.pack(side="bottom", fill="x")
        #     # self.scrollbar_h.grid()
        # except:
        #     pass
        try:
            self.scrollbar.pack(side="right", fill="y")
            # self.scrollbar.grid()
        except:
            pass
        # self.canvas.pack(side="left", fill="both", expand=True)
        # self.canvas.grid()
        return
    
    def recenterCanvasWindow(self):
        #Get the size of the scrollableFrame
        height = self.canvas.winfo_height()
        # print(f"Scrollable Frame Height: {height}")
        self.canvasWindow = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        return

class ImageViewer(tb.Canvas):
    """
    ImageViewer is a canvas that resizes and displays an image. It also has a label that displays the name of the image.

    loadImage(imagePath:str) - Loads an image into the ImageViewer
    redrawImage() - Redraws the image on the canvas. Called when canvas is resized.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvasWidth = self.winfo_width()
        self.canvasHeight = self.winfo_height()

        self.imagePath = None
        #Initially there is no image.
        self.imagePath = None
        self.imagePIL = None
        self.image = None
        self.canvasImage = None

        #Label on the canvas that says the name of the image
        self.imageLabel = self.create_text(10, 10, anchor="nw", text="", font=("Arial", 16), fill="#FF1D8E")

        #bind a configure event to the canvas
        self.autoResize: bool = False
        self.after_id = None
        # self.autoResizeToggle(False)
        return

    def autoResizeToggle(self, state: bool=True):
        if state:
            print("ImageViewer: Auto resizing enabled")
            self.autoResize = True
            self.after_id = None
            self.bind("<Configure>", self.afterEvent)
            return
        else:
            print("ImageViewer: Auto resizing disabled")
            self.autoResize = False
            self.after_id = None
            self.unbind("<Configure>")
            return

    def afterEvent(self, event):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(updateRate, self.redrawImage)
        return

    def loadImage(self, imagePath:str):
        #Clear the canvas
        self.delete("all")
        #Test if the file is a valid image file
        try:
            img = Image.open(imagePath)
            self.imagePath = imagePath
            self.imagePIL = img
            #Delete & replace old label
            self.imageLabel = self.create_text(10, 10, anchor="nw", text=FP.removeExtension(FP.removePath([self.imagePath]))[0], font=("Arial", 16), fill="#FF1D8E")
            print(f"Loaded {imagePath} into ImageViewer")
        except:
            print(f"{imagePath} is not a valid image file.")
            self.imagePath = FP.MissingImage
            img = Image.open(self.imagePath)
            self.imagePIL = img
            print(f"Loaded {imagePath} into ImageViewer as Missing Image")

        #Resize the image while using the aspect ratio
        self.imagePIL.thumbnail((self.canvasWidth, self.canvasHeight))
        self.image = ImageTk.PhotoImage(self.imagePIL)
        self.canvasImage = self.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
        self.redrawImage()
        return

    def redrawImage(self):
        print("Redrawing Image")
        #Return early if there is no image
        if self.imagePath == None:
            self.delete("all")
            return

        #Get the size of the canvas
        self.canvasWidth = self.winfo_width()
        self.canvasHeight = self.winfo_height()
        # print(f"Current Window Size: {event.width}x{event.height}")
        # print(f"Canvas Size: {self.canvasWidth}x{self.canvasHeight}")
        #Clear the canvas
        self.delete("all")
        #Resize the image while using the aspect ratio
        img = Image.open(self.imagePath)
        self.imagePIL = img
        self.imagePIL.thumbnail((self.canvasWidth, self.canvasHeight))
        self.image = ImageTk.PhotoImage(self.imagePIL)
        self.canvasImage = self.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
        self.imageLabel = self.create_text(10, 10, anchor="nw", text=FP.removeExtension(FP.removePath([self.imagePath]))[0], font=("Arial", 16), fill="#FF1D8E")

        if self.imagePath == FP.MissingImage:
            self.after(3000, self.setBlankImage)
        return

    def printCanvasSize(self):
        self.canvasWidth = self.canvas.winfo_width()
        self.canvasHeight = self.canvas.winfo_height()
        print(f"Canvas Size: {self.canvasWidth}x{self.canvasHeight}")
        return

    def setBlankImage(self):
        print("Setting Blank Image")
        self.imagePath = None
        self.redrawImage()
        return

class FileIcon(tk.Frame):
    """
    FileIcon is a frame that contains a canvas and a label. The canvas displays the image and the label displays the name of the image.\n
    It has some drag and drop functionality.\n
    NOTE:
    --------------------
    This is specifically for FILES in the media bucket. Intended functionality is to be able to drag and drop files into the ImageViewer and SlideReel.\n
    In order for it to do that you currently need to link it to the ImageViewer and SlideReel.\n
    This is done in the SlideshowCreator object when those things get created.\n
    There may be a way to do this without linking them together using the drop coordinates, but idk how to do that and this works. - James\n

    - openImage(event) - Opens the image set in the imagepath with the default program for that file type. Called when the user double clicks the icon.\n
    - clickIcon(event) - Called when the user clicks the icon. If the icon is linked to an ImageViewer, it will load the image into the viewer.
    Called specifically when you release the mouse button while on the icon.\n
    - pickup(event) - Called when the user clicks the icon. Assuming the file is not missing, it will bind pressed mouse movement to dragIconStart.\n
    - dragIconStart(event) - Called when the user moves the mouse while clicking the icon. If the mouse moves a certain distance away from initial click, it will bind the mouse movement to dragIcon.\n
    - dragIcon(event) - Creates a borderless transparent TopLevel window containing the image and binds it to the mouse. \n
    - dropIcon(event) - Called when the user releases the mouse button when dragging the icon. Will destroy the popup and reset the bindings.\n

    Drag-and-drop flowchart:
    --------------------
    click on icon=pickup() -> move mouse a certain distance=dragIconStart() -> move mouse=dragIcon() -> release mouse=dropIcon()\n
    
    """
    def __init__(self, master, imagepath: str=None, **kwargs):
        super().__init__(master, **kwargs)
        self.width = 100
        self.height = 140
        self.configure(width=self.width, height=self.height)
        self.pack_propagate(False)

        self.canvasWidth = 100
        self.canvasHeight = 100
        self.canvas = tk.Canvas(self, width=self.canvasWidth, height=self.canvasHeight)
        self.canvas.pack(expand=True, fill="both")

        try:
            self.name = FP.removeExtension(FP.removePath([imagepath]))[0]
        except:
            self.name = "Error: Missing Image"
        nameCutoff: int = 20
        fn = self.name[:nameCutoff] + "..." if len(self.name) > nameCutoff else self.name
        self.label = tb.Label(self, text=fn, font=("Arial", 12), bootstyle="default", justify="center", wraplength=90)
        self.label.pack(expand=False, fill="none", anchor="center")

        self.missing: bool = False
        #Test if the file is a valid image file
        try:
            img = Image.open(imagepath)
            self.imagepath = imagepath
            self.__imagePIL = img
        except:
            print(f"{imagepath} is not a valid image file.")
            self.missing = True
            img = Image.open(FP.MissingImage)
            self.__imagePIL = img
        self.__imagePIL.thumbnail((self.canvasWidth, self.canvasHeight))
        self.image = ImageTk.PhotoImage(self.__imagePIL)
        self.canvasImage = self.canvas.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image, anchor=tk.CENTER)

        self.linkedViewer: ImageViewer = None
        self.linkedReel: SlideReel = None
        self.linkedInfo: InfoFrame = None
        self.linkedBucket: MediaBucket = None

        #Event binding
        self.canvas.bind("<Double-Button-1>", self.openImage)
        self.canvas.bind("<Enter>", self.hoverEnter)
        self.canvas.bind("<Leave>", self.hoverLeave)
        self.__hover: bool = False
        self.canvas.bind("<ButtonRelease-1>", self.clickIcon)
        self.canvas.bind("<Button-1>", self.pickup)
        self.__startX: int = 0
        self.__startY: int = 0
        self.popup: tk.Toplevel = None

    def openImage(self, event):
        os.startfile(self.imagepath)
        return

    def hoverEnter(self, event):
        self.__hover = True
        self.configure(relief=tk.SUNKEN, borderwidth=2)
        return

    def hoverLeave(self, event):
        self.__hover = False
        self.configure(relief=tk.FLAT, borderwidth=0)
        return

    def clickIcon(self, event):
        # print(f"Clicked on {self.name}")
        if self.linkedViewer != None:
            #Load image into the viewer
            self.linkedViewer.loadImage(self.imagepath)

        #Probably put info in the InfoFrame here
        if self.linkedInfo != None:
            self.linkedInfo.loadIcon(self)
        else:
            print(f"No InfoFrame linked to {self.name}")
        return
     
    def pickup(self, event):
        # print(f"Click at {event.x}, {event.y} on {self.name}")
        self.__startX = event.x
        self.__startY = event.y
        #If missing image, don't allow dragging
        if self.missing == True:
            return
        self.canvas.bind("<B1-Motion>", self.dragIconStart)
        return

    def dragIconStart(self, event):
        #Begin dragging after the mouse has moved a certain distance. Once it does, change the binding to dragIcon
        distance = 15
        if abs(event.x - self.__startX) > distance or abs(event.y - self.__startY) > distance:
            self.canvas.unbind("<B1-Motion>")
            self.canvas.bind("<B1-Motion>", self.dragIcon)
        return

    def dragIcon(self, event):
        #Check if the popup exists. If it does move it to the mouse position
        if self.popup:
            self.popup.geometry(f"+{event.x_root}+{event.y_root}")

            #Check and see if the user is hovering over a divider. If they are, highlight the divider
            for divider in self.linkedReel.dividers:
                x: int = divider.winfo_rootx()
                y: int = divider.winfo_rooty()
                w: int = divider.winfo_width()
                h: int = divider.winfo_height()
                if event.x_root > x and event.x_root < x+w and event.y_root > y and event.y_root < y+h:
                    if (type(self) == SlideIcon):
                        #If the slideID is within two of the divider index, return early.
                        distance: int = abs(self.slide['slideID'] - (divider.index//2))
                        if divider.index//2 > self.slide['slideID']:
                            distance -= 1
                        # print(f"Distance: {distance}")
                        if distance == 0:
                            return

                    divider.label.configure(text=" ", bootstyle="inverse-default")
                else:
                    divider.label.configure(text="", bootstyle="default")
            return

        else:
            #Create the popup which is a borderless transparent TopLevel window containing the image
            self.popup = tk.Toplevel()
            self.popup.overrideredirect(True)
            self.popup.geometry(f"{self.canvasWidth}x{self.canvasHeight}+{event.x_root}+{event.y_root}")
            self.popup.attributes("-transparentcolor", "white")
            self.popup.attributes("-topmost", True)
            self.popup.wm_attributes("-alpha", 0.8)

            #Create the canvas in the popup
            self.popupCanvas = tk.Canvas(self.popup, width=self.canvasWidth, height=self.canvasHeight)
            self.popupCanvas.pack()
            self.popupImage = ImageTk.PhotoImage(self.__imagePIL)
            self.popupCanvas.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.popupImage)

            #Bind the popup to the mouse
            self.popup.bind("<B1-Motion>", self.dragIcon)
            self.canvas.bind("<ButtonRelease-1>", self.dropIcon)
            return

    def dropIcon(self, event):
        print(f"Dropped at {event.x}, {event.y}")
        self.popup.destroy()
        self.popup = None
        self.canvas.bind("<Button-1>", self.pickup)
        self.canvas.unbind("<B1-Motion>")
        self.canvas.bind("<ButtonRelease-1>", self.clickIcon)

        
        #check if the user has dropped the icon into the previewer. If they have, load the image
        if self.linkedViewer:
            x = self.linkedViewer.winfo_rootx()
            y = self.linkedViewer.winfo_rooty()
            w = self.linkedViewer.winfo_width()
            h = self.linkedViewer.winfo_height()
            if event.x_root > x and event.x_root < x+w and event.y_root > y and event.y_root < y+h:
                self.linkedViewer.loadImage(self.imagepath)
                self.linkedViewer.redrawImage()

        #If the user dropped the icon into the slide reel, add the image to the slideshow
        if self.linkedReel:
            #Check if the dividers exist.
            if len(self.linkedReel.dividers) > 0:
                for divider in self.linkedReel.dividers:
                    divider.reset()
                    x = divider.winfo_rootx()
                    y = divider.winfo_rooty()
                    w = divider.winfo_width()
                    h = divider.winfo_height()
                    if event.x_root > x and event.x_root < x+w and event.y_root > y and event.y_root < y+h:
                        print(f"Adding {self.imagepath} to the slideshow at index {divider.index//2}")
                        self.linkedReel.addSlide(self.imagepath, (divider.index//2))
                        return

            x = self.linkedReel.winfo_rootx()
            y = self.linkedReel.winfo_rooty()
            w = self.linkedReel.winfo_width()
            h = self.linkedReel.winfo_height()
            if event.x_root > x and event.x_root < x+w and event.y_root > y and event.y_root < y+h:
                # print(f"Adding {self.imagepath} to the slideshow")
                self.linkedReel.addSlide(self.imagepath)
        return

class IconDivider(tb.Frame):
    def __init__(self, master, index:int, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=20, height=150)
        self.pack_propagate(False)
        self.label = tb.Label(self, text="", font=("Arial", 12), bootstyle="default")
        self.label.pack(expand=True, fill="both")
        self.index: int = index

        #Bind click
        self.label.bind("<ButtonRelease-1>", self.clickDivider)


    def clickDivider(self, event):
        print(f"Clicked on divider {self.index}")
        return

    def reset(self):
        self.label.configure(text="", bootstyle="default")
        self.configure(relief=tk.FLAT, borderwidth=0)
        return

class SlideIcon(FileIcon):
    """
    SlideIcon litteraly just a FileIcon but with the extra slide attribute. It's used in the SlideReel.\n
    Will probably need to redo drag and drop functionality specifically for this depending on how we want to organize the slides.\n
    Since it acts just like a FileIcon there is some wierd interactions with the SlideReel. Will fix later.\n
    """
    def __init__(self, master, imgPath: str, **kwargs):
        super().__init__(master, imgPath, **kwargs)
        self.slide: FP.Slide = FP.Slide(imgPath)

    def setSlide(self, slide: FP.Slide):
        self.slide = slide
        return
    
    def dropIcon(self, event):
        print(f"Dropped at {event.x}, {event.y}")
        self.popup.destroy()
        self.popup = None
        self.canvas.bind("<Button-1>", self.pickup)
        self.canvas.unbind("<B1-Motion>")
        self.canvas.bind("<ButtonRelease-1>", self.clickIcon)

        #Set the dividers back to normal
        for divider in self.linkedReel.dividers:
            divider.configure(relief=tk.FLAT, borderwidth=0)
            divider.label.configure(text="", bootstyle="default")

        #check if the user has dropped the icon into the previewer. If they have, load the image
        if self.linkedViewer:
            x = self.linkedViewer.winfo_rootx()
            y = self.linkedViewer.winfo_rooty()
            w = self.linkedViewer.winfo_width()
            h = self.linkedViewer.winfo_height()
            if event.x_root > x and event.x_root < x+w and event.y_root > y and event.y_root < y+h:
                self.linkedViewer.loadImage(self.imagepath)
                self.linkedViewer.redrawImage()

        if self.linkedReel:
            #Check if the dividers exist.
            if len(self.linkedReel.dividers) > 0:
                for divider in self.linkedReel.dividers:
                    divider.reset()
                    x = divider.winfo_rootx()
                    y = divider.winfo_rooty()
                    w = divider.winfo_width()
                    h = divider.winfo_height()


                    #If they dropped the icon onto a divider, move the slide icon to that index.
                    if event.x_root > x and event.x_root < x+w and event.y_root > y and event.y_root < y+h:
                        slideID = self.slide['slideID']
                        self.linkedReel.slideshow.moveSlide(slideID, divider.index//2)
                        self.update_idletasks()
                        self.after(33, self.linkedReel.fillReel)
        return




class InfoFrame(tb.Frame):
    def __init__(self, master, slideshow: FP.Slideshow = None, **kwargs):
        super().__init__(master, **kwargs)
        self.slideshow: FP.Slideshow = slideshow

        #Notebook for different tabs: Slide/Image info and Project Info.
        self.notebook = tb.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        #Scrollable Frame for the slide info
        self.slideInfoFrame = ScrollableFrame(self.notebook, orient="both")
        self.notebook.add(self.slideInfoFrame, text="Slide Info")

        #Scrollable Frame for the project info
        self.projectInfoFrame = ScrollableFrame(self.notebook, orient="both")
        self.notebook.add(self.projectInfoFrame, text="Project Info")

        self.__defaultDurationTemp = self.slideshow.defaultSlideDuration

        self.image: bool = False #If True, display the image info. If False, display the slide info.
        self.__icon = None #This will be the icon that was clicked on to open the info frame.

        self.fillProjectInfo()
        self.fillSlideInfo()
        self.notebook.select(1)
        return

    def fillProjectInfo(self):
        if self.slideshow == None:
            return
        
        #Clear the project info frame
        for widget in self.projectInfoFrame.scrollable_frame.winfo_children():
            widget.destroy()
        
        #Grid layout for the project info
        self.nameLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Name: ", font=("Arial", 12))
        self.nameLabel.grid(row=0, column=0, columnspan=3, sticky="w")
        self.name = tb.Label(self.projectInfoFrame.scrollable_frame, text=self.slideshow.name, font=("Arial", 12))
        self.name.grid(row=0, column=3, columnspan=10, sticky="w")

        self.countLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Slide Count: ", font=("Arial", 12))
        self.countLabel.grid(row=1, column=0, columnspan=3, sticky="w")
        self.count = tb.Label(self.projectInfoFrame.scrollable_frame, text=str(len(self.slideshow.getSlides())), font=("Arial", 12))
        self.count.grid(row=1, column=3, columnspan=10, sticky="w")

        self.pathLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Path: ", font=("Arial", 12))
        self.pathLabel.grid(row=2, column=0, columnspan=3,sticky="w")
        self.path = tb.Label(self.projectInfoFrame.scrollable_frame, text=self.slideshow.getSaveLocation(), font=("Arial", 12))
        self.path.grid(row=2, column=3, sticky="w", columnspan=4)

        self.defaultSlideDurationLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Default Slide Duration: ", font=("Arial", 12))
        self.defaultSlideDurationLabel.grid(row=3, column=0, columnspan=3, sticky="w")
        # self.setDurationButton = tb.Button(self.projectInfoFrame.scrollable_frame, text="Set", command=self.setDefaultDuration, takefocus=0)
        # self.setDurationButton.grid(row=3, column=3, sticky="w")
        self.defaultSlideDuration = tb.Entry(self.projectInfoFrame.scrollable_frame, font=("Arial", 12), state=tk.NORMAL, takefocus=0)
        self.defaultSlideDuration.config(width=7)
        self.defaultSlideDuration.insert(0, self.slideshow.defaultSlideDuration)
        self.defaultSlideDuration.grid(row=3, column=3, sticky="w")

        self.defaultSlideDuration.bind("<FocusIn>", self.onDefaultDurationFocusIn)
        self.defaultSlideDuration.bind("<FocusOut>", self.onDefaultDurationFocusOut)
        
        self.slideShuffleLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Slide Shuffle: ", font=("Arial", 12))
        self.slideShuffleLabel.grid(row=4, column=0, columnspan=3, sticky="w")
        self.slideShuffle = tb.Checkbutton(self.projectInfoFrame.scrollable_frame, style="Roundtoggle.Toolbutton")
        self.slideShuffle.grid(row=4, column=3, sticky="w")

        self.loopLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Loop: ", font=("Arial", 12))
        self.loopLabel.grid(row=5, column=0, columnspan=3, sticky="w")
        self.loop = tb.Checkbutton(self.projectInfoFrame.scrollable_frame, style="Roundtoggle.Toolbutton")
        self.loop.grid(row=5, column=3, sticky="w")

        #Separator
        self.separator = tb.Separator(self.projectInfoFrame.scrollable_frame, orient="horizontal")
        self.separator.grid(row=6, column=0, columnspan=10, sticky="ew", pady=10)

        self.PlaylistLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Playlist: ", font=("Arial", 12))
        self.PlaylistLabel.grid(row=7, column=0, columnspan=3, sticky="w")
        self.PlaylistName = tb.Label(self.projectInfoFrame.scrollable_frame, text="None", font=("Arial", 12))
        self.PlaylistName.grid(row=7, column=2, columnspan=1,sticky="w")

        self.playlistDurationLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Duration: ", font=("Arial", 12))
        self.playlistDurationLabel.grid(row=8, column=0, columnspan=3, sticky="w")
        self.playlistDuration = tb.Label(self.projectInfoFrame.scrollable_frame, text="0:00", font=("Arial", 12))
        self.playlistDuration.grid(row=8, column=2, columnspan=1, sticky="w")

        #Add shuffle and loop buttons.


        self.tree_frame = tb.Frame(self.projectInfoFrame.scrollable_frame)
        self.tree_frame.grid(row=9, column=1, columnspan=9, rowspan=7, sticky="w")

        #Scrollbar for the treeview
        tree_scrollbar = tb.Scrollbar(self.tree_frame, orient="vertical")
        tree_scrollbar.pack(side="right", fill="y")

        # self.tree_frame = ScrolledFrame(self.projectInfoFrame.scrollable_frame, style="primary.TFrame", autohide=True)
        # self.tree_frame.grid(row=9, column=0, columnspan=10, rowspan=7, sticky="w")

        self.playlistTree = tb.Treeview(self.tree_frame, columns=("Name", "Order"), show="headings", selectmode="browse")
        self.playlistTree.heading("Name", text="Name")
        self.playlistTree.heading("Order", text="Order")
        self.playlistTree.column("Name", anchor="w", minwidth=100, width=150)
        self.playlistTree.column("Order", anchor="w", minwidth=50, width=100)
        self.playlistTree.pack(expand=True, fill="both")

        tree_scrollbar.config(command=self.playlistTree.yview)

        #Buttons to move a song up, down, or remove it from the playlist
        self.moveUpButton = tb.Button(self.projectInfoFrame.scrollable_frame, text="/\\", command=self.playListMoveUp, takefocus=0)
        self.moveUpButton.grid(row=10, column=0, sticky="e", padx=5)
        self.addSongButton = tb.Button(self.projectInfoFrame.scrollable_frame, text="+", command=self.playListAdd, takefocus=0, style="success.TButton")
        self.addSongButton.grid(row=11, column=0, sticky="e", padx=5)
        self.removeSongButton = tb.Button(self.projectInfoFrame.scrollable_frame, text="X", command=self.playListRemove, takefocus=0, style="danger.TButton")
        self.removeSongButton.grid(row=12, column=0, sticky="e", padx=5)
        self.moveDownButton = tb.Button(self.projectInfoFrame.scrollable_frame, text="\\/", command=self.playListMoveDown, takefocus=0)
        self.moveDownButton.grid(row=13, column=0, sticky="e", padx=5)

        #Empty space to pad the bottom of grid
        self.emptySpace = tb.Label(self.projectInfoFrame.scrollable_frame, text="", font=("Arial", 12))
        self.emptySpace.grid(row=17, column=0, columnspan=10, sticky="w")
        return

    def playListMoveUp(self):
        return

    def playListMoveDown(self):
        return

    def playListRemove(self):
        return

    def playListAdd(self):
        return

    def setDefaultDuration(self):
        #Check if it is a valid number.
        try:
            float(self.defaultSlideDuration.get())
        except:
            print("Invalid input for slide duration.")
            self.defaultSlideDuration.delete(0, tk.END)
            self.defaultSlideDuration.insert(0, self.__defaultDurationTemp)

            #Set the outline to red
            self.defaultSlideDuration.config(style="danger.TEntry")
            return
        
        #No errors
        self.defaultSlideDuration.config(style="TEntry")
        # print(f"Slide Duration: {self.defaultSlideDuration.get()}")
        self.slideshow.defaultSlideDuration = self.defaultSlideDuration.get()
        self.__defaultDurationTemp = self.slideshow.defaultSlideDuration
        self.winfo_toplevel().focus_set()
        return
    
    def onDefaultDurationFocusIn(self, event):
        # self.defaultSlideDuration.config(state=tk.NORMAL)
        print("Slide Duration Focused In")
        self.defaultSlideDuration.bind("<Return>", lambda event: self.setDefaultDuration())
        #Bind escape to unfocus the entry
        self.defaultSlideDuration.bind("<Escape>", lambda event: self.focus_set())
        return
    
    def onDefaultDurationFocusOut(self, event):
        # self.defaultSlideDuration.config(state=tk.DISABLED)
        print("Slide Duration Focused Out")
        self.defaultSlideDuration.unbind("<Return>")
        self.defaultSlideDuration.unbind("<Escape>")
        #Reset the entry
        self.defaultSlideDuration.delete(0, tk.END)
        self.defaultSlideDuration.insert(0, self.__defaultDurationTemp)

        #Change style to normal
        # self.defaultSlideDuration.config(style="TEntry", bootstyle="normal")
        return
    
    def fillSlideInfo(self):
        if self.slideshow == None:
            return
        
        #Clear the project info frame
        for widget in self.slideInfoFrame.scrollable_frame.winfo_children():
            widget.destroy()


        #If the icon is an image, display the image info. If it is a slide, display the slide info.
        if type(self.__icon) == SlideIcon:
            icon: SlideIcon = self.__icon
        elif type(self.__icon) == FileIcon:
            icon: FileIcon = self.__icon
        else:
            print(f"FillSlideInfo: Invalid icon type. {type(self.__icon)}")
            label = tb.Label(self.slideInfoFrame.scrollable_frame, text="Select an image or slide to view info.", font=("Arial", 12))
            label.grid(row=0, column=0, columnspan=2, sticky="w")
            return

        #Grid layout for the slide info
        self.nameLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Name: ", font=("Arial", 12))
        self.nameLabel.grid(row=0, column=0, columnspan=2, sticky="w")
        self.name = tb.Label(self.slideInfoFrame.scrollable_frame, text=icon.name, font=("Arial", 12))
        self.name.grid(row=0, column=3, sticky="w")

        #imagePath
        self.imagePathLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Image Path: ", font=("Arial", 12))
        self.imagePathLabel.grid(row=1, column=0, columnspan=2,sticky="w")
        self.imagePath = tb.Label(self.slideInfoFrame.scrollable_frame, text=icon.imagepath, font=("Arial", 12))
        self.imagePath.grid(row=1, column=3, sticky="w", columnspan=4)

        if self.image:
            #Change the notebook tab text to "Image Info"
            self.notebook.tab(0, text="Image Info")
            #Button for adding image to the slideshow
            self.addSlideButton = tb.Button(self.slideInfoFrame.scrollable_frame, text="Add Slide", command=self.addSlide, takefocus=0, style="success.TButton")
            self.addSlideButton.grid(row=2, column=0, sticky="w")
            #Button to remove image from the project.
            self.removeImageButton = tb.Button(self.slideInfoFrame.scrollable_frame, text="Remove Image", command=self.removeImage, takefocus=0, style="danger.TButton")
            self.removeImageButton.grid(row=2, column=1, sticky="w")
            return
            
        icon: SlideIcon = self.__icon
        self.notebook.tab(0, text="Slide Info")

        #Slide info we need:
        #Position/ID
        #Duration to show slide for
        #transition speed (maybe just have this be static??)
        #Transition type
        #Preview transition.

        #Slide ID
        self.slideIDLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Slide ID: ", font=("Arial", 12))
        self.slideIDLabel.grid(row=2, column=0, columnspan=2, sticky="w")
        self.slideID = tb.Label(self.slideInfoFrame.scrollable_frame, text=str(icon.slide['slideID']), font=("Arial", 12))
        self.slideID.grid(row=2, column=3, sticky="w")

        return

    def addSlide(self):
        print(self.__icon.imagepath)
        self.__icon.linkedReel.addSlide(self.__icon.imagepath)
        return

    def removeImage(self):
        print(self.__icon.imagepath)
        self.__icon.linkedBucket.removeFile(self.__icon.imagepath)
        return


    def loadIcon(self, icon):
        if type(icon) == SlideIcon:
            self.image = False
            self.__icon = icon
        elif type(icon) == FileIcon:
            self.image = True
            self.__icon = icon
        else:
            print("Error loading Icon into InfoFrame: Invalid icon type.")

        self.fillSlideInfo()
        return

class SlideReel(tk.Frame):
    """
    SlideReel is a frame that contains the SlideReel widget. Consists of a scrollable frame that contains SlideIcons.\n
    Must be initialized with a Slideshow object. SlideshowCreator object should give it one even if its a new project.\n
    - loadProject(project: FP.Slideshow) - Loads a project into the SlideReel\n
    - fillReel() - Should draw the slides from the project into SlideIcons. If called again will delete then redraw the icons. Use to update.\n
    - addSlide(imagePath:str, index:int=-1) - Creates a slide object from the image path and adds it to the slideshow object by calling Slideshow.addSlide(). Will then redraw.\n

    """
    def __init__(self, master, slideshow: FP.Slideshow, **kwargs):
        super().__init__(master, **kwargs)
        self.addStack = []
        self.slideshow: FP.Slideshow = slideshow
        self.previewer: ImageViewer = None 
        self.infoFrame: InfoFrame = None
        self.slides: list[FP.Slide] = self.slideshow.getSlides() #Pretty sure this is a reference to the slideshow object so it should update automatically.
        self.dividers: list[IconDivider] = []

        #Horizontal Scrollable Frame
        self.scrollFrame = ScrollableFrame(self, orient="horizontal")
        self.scrollFrame.pack(expand=True, fill="both")

        self.prevSlideList: list[FP.Slide] = deepcopy(self.slides)

        #bind a configure event to the canvas
        self.autoResize: bool = False
        self.after_id = None
        # self.autoResizeToggle(True)
        return

    def autoResizeToggle(self, state: bool=True):
        if state:
            print("SlideReel: AutoResize Enabled")
            self.autoResize = True
            self.after_id = None
            self.bind("<Configure>", self.afterEvent)
        else:
            print("SlideReel: AutoResize Disabled")
            self.autoResize = False
            self.after_id = None
            self.unbind("<Configure>")
        return

    def afterEvent(self, event):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(updateRate, self.refreshReel)
        return
    
    def linkPreviewer(self, previewer: ImageViewer):
        self.previewer = previewer
        return
    
    def linkInfoFrame(self, info: InfoFrame):
        self.infoFrame = info
        return
    
    def refreshReel(self):
        #If the slides have not changed at all, just redraw them, which is faster as it doesn't require creating new SlideIcons.
        #Recenter the scrollable frame
        # self.scrollFrame.recenterCanvasWindow()
        print("Refreshing the reel")

        #If they have changed redraw the entire widget.
        if self.slides == self.prevSlideList and len(self.slides) > 0 and len(self.scrollFrame.scrollable_frame.winfo_children()) > 0:
            print(f"No change in slides. {len(self.slides)} == {len(self.prevSlideList)}")
            self.redrawReel()
            return
        else:
            self.prevSlideList = deepcopy(self.slides)
            self.fillReel()
            return

    #fillReel just takes the slides and puts them in the scrollable frame IN ORDER
    def fillReel(self):
        print("Filling the reel")
        # print(self.slideshow.printSlides())

        #First of all pack forget everything in the scrollable frame
        for slide in self.scrollFrame.scrollable_frame.winfo_children():
            slide.destroy()

        #Clear the dividers
        for divider in self.dividers:
            divider.destroy()

        self.dividers = []

        i = 0
        #Every slide in the slideReel is made into a slideIcon.
        for slide in self.slides:
            #If accessing using subscript doesn't work try using dot notation
            try:
                imgPath = slide["imagePath"]
            except:
                imgPath = slide.imagePath

            divider = IconDivider(self.scrollFrame.scrollable_frame, i)
            divider.grid(row=0, column=i, padx=0, pady=10, sticky="w")
            self.dividers.append(divider)
            i += 1

            slideIcon = SlideIcon(self.scrollFrame.scrollable_frame, imgPath)
            slideIcon.label.configure(text=f"Slide {i//2}")
            slideIcon.linkedViewer = self.previewer
            slideIcon.linkedReel = self
            slideIcon.linkedInfo = self.infoFrame
            slide['slideID'] = i//2
            slideIcon.slide = slide
            slideIcon.grid(row=0, column=i, padx=0, pady=10, sticky="w")
            i += 1

        divider = IconDivider(self.scrollFrame.scrollable_frame, i)
        divider.grid(row=0, column=i, padx=0, pady=10, sticky="w")
        self.dividers.append(divider)
        return

    def redrawReel(self):
        print(f"Redrawing the reel")
        #Ungrid the dividers and slideIcons
        children = self.scrollFrame.scrollable_frame.winfo_children()
        for child in children:
            child.grid_remove()
        
        self.update_idletasks()
        for child in children:
            #If ANY child is a SlideIcon, test if it has a slideID. If it does we good. If it doesn't then something is wrong and we should call fillReel.
            if type(child) == SlideIcon:
                if child.slide['slideID'] == None:
                    print("Redraw Error: SlideID is None")
                    self.fillReel()
                    return
            child.grid()


        #Regrid the dividers and slideIcons

    def addSlide(self, imagePath:str, index:int=-1):
        #First check if there is a slideshow object. If there isn't there isn't a point in adding a slide.
        if self.slideshow == None:
            print("\n\nNo slideshow object to add slide to.")
            return

        #Add the slide to the slideshow object
        slide = FP.Slide(imagePath)
        # print("\n")
        # print(f"Adding slide for {imagePath}")
        self.slideshow.addSlide(slide, index)
        self.fillReel()
        return

class MediaBucket(tb.Frame):
    """
    Media bucket is a frame that contains the media bucket widget. It basically consists of a scrollable frame from tkBootstrap that contains file icons.\n
    In order to work properly, it needs to be linked to an ImageViewer and a SlideReel. This is done in the SlideshowCreator object when those things get created.\n
    If called without a slideshow project as an input it should just default to a blank bucket.\n
    There is functionality for a sort of undo feature? Basically when files get added to the bucket the entire addition is pushed onto a stack. When the undo is called it pops the last addition off the stack and removes it from the bucket.\n
    
    - fillBucket() - Fills the bucket with files stored in the files list. Effectively redraws the bucket.\n
    - loadProject(project: FP.Slideshow) - Loads all images in a project into the bucket.\n
    - addFile(file:str) - Adds a file to the bucket. Will then redraw the bucket.\n
    - addFolder(folder:str) - Basically same functionality as addFile.\n
    WARNING: Adds the files recursively meaning it will find all the images in a directory and subdirectories.\n
    - undoAdd() - Removes the last addition from the bucket. Will then redraw the bucket.\n
    - removeFile(file:str) - Removes a file from the bucket. Will then redraw the bucket.\n
    """
    def __init__(self, master, slideshow: FP.Slideshow="New Project", **kwargs):
        super().__init__(master, **kwargs)
        self.files: list[str] = []
        self.icons: list[FileIcon] = []
        #Keeps track of files added to the bucket. Used for undoing.
        self.addStack = []
        self.previewer: ImageViewer = None
        self.reel: SlideReel = None
        self.infoFrame: InfoFrame = None
        self.project: FP.Slideshow = slideshow
        # self.files = self.project.filesInProject

        #Label for the project
        self.projectLabel = tb.Label(self, text=self.project.name, font=("Arial", 16), bootstyle="inverse-info")
        self.projectLabel.pack(fill="x", anchor="nw")

        #Frame for the icons
        self.iconFrame: ScrolledFrame = ScrolledFrame(self, autohide=True)
        self.iconFrame.pack(expand=True, fill="both")


        #FileIcons are 100x130
        self.columnCount: int = 0

        self.loadProject(slideshow) 
        #bind a configure event to the canvas
        self.autoResize: bool = False
        self.after_id = None
        # self.autoResizeToggle(True)

    def autoResizeToggle(self, state: bool=True):
        if state:
            print("MediaBucket: AutoResize Enabled")
            self.autoResize = True
            self.after_id = None
            self.bind("<Configure>", self.afterEvent)
            return
        else:
            print("MediaBucket: AutoResize Disabled")
            self.autoResize = False
            self.after_id = None
            self.unbind("<Configure>")
            return
    
    def afterEvent(self, event):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(updateRate, self.fillBucket)
        return

    def linkPreviewer(self, previewer: ImageViewer):
        self.previewer = previewer
        return
    
    def linkReel(self, reel: SlideReel):
        self.reel = reel
        return
    
    def linkInfoFrame(self, info: InfoFrame):
        self.infoFrame = info
        return

    def removeDuplicates(self):
        self.files = list(dict.fromkeys(self.files))
        return

    def fillBucket(self):
        print("Filling Bucket")
        # print(f"{self.project.name} has {len(self.files)} files in it.")
        self.projectLabel.config(text=self.project.name)

        #Remove duplicates
        self.removeDuplicates()

        #find the number of columns
        width = self.winfo_width()
        #Only even attempt to fill the bucket if the width is greater than like 10. If it's less than 10 the window probably doesn't exist yet.
        if width < 10:
            print("Width too small\n")
            return

        #Icons should be 100 wide with 3 pixels of padding on each side
        columnCount = width // 106
        filecount = len(self.files)

        #If the column count is the same as before, don't do anything
        if columnCount == self.columnCount and len(self.icons) == filecount:
            return
        self.columnCount = columnCount
        
        for icon in self.iconFrame.winfo_children():
            icon.destroy()

        #If there are no files, add buttons to add files
        # print(f"Files in bucket: {len(self.files)}")
        if len(self.files) == 0:
            print("No files in the bucket")
            #Create buttons to add files
            addFileButton = tb.Button(self.iconFrame, text="Add File", command=lambda: self.addFile(filedialog.askopenfilenames(multiple=True, filetypes=[("Image Files", "*.jpg *.jpeg *.png")])))
            addFileButton.pack()
            addFolderButton = tb.Button(self.iconFrame, text="Add Folder", command=lambda: self.addFolder(filedialog.askdirectory()))
            addFolderButton.pack()
            return

        #Create the icons
        i=0
        j=0
        for file in self.files:
            icon = FileIcon(self.iconFrame, file)
            icon.linkedViewer = self.previewer
            icon.linkedReel = self.reel
            icon.linkedInfo = self.infoFrame
            icon.linkedBucket = self
            icon.grid(row=i, column=j, padx=3, pady=3)
            self.icons.append(icon)
            j += 1
            if j >= self.columnCount:
                j = 0
                i += 1
        return
          
    def loadProject(self, project: FP.Slideshow):
        """Given a project object it will load all the files in the project into the bucket."""
        self.files = project.filesInProject
        self.projectLabel.config(text=project.name)
        self.fillBucket()
        return

    def addFile(self, file):
        """
        Given an imagePath, it will add the image to the bucket.
        """
        files = []
        #Sometimes the input is a string or like a tuple. This is to catch that.
        if type(file) == str:
            # print(f"Adding {file} to the bucket")
            self.files.append(file)
            files.append(file)
        elif type(file) == tuple:
            # print(f"Adding tuple {file} to the bucket")
            for f in file:
                print(f)
                self.files.append(f)
                files.append(f)
        else:
            print(f"Invalid file type: {type(file)}")
            return
        #Remove last entry in tempstack
        self.addStack.append(files)
        self.fillBucket()
        return
    
    def addFolder(self, folder):
        """
        Given a folderPath it will add all the images it finds within the folder and subfolders to the bucket.
        """
        files = []
        if type(folder) == str:
            files = FP.getJPEG(folder, True) #Recursively get all the files in the folder
        elif type(folder) == tuple:
            for f in folder:
                files.extend(FP.getJPEG(f, True))
        else:
            print(f"Expected string or tuple of strings. Got {type(folder)}")
            return
        self.addStack.append(files)
        self.files.extend(files)
        self.fillBucket()
        return
    
    def undoAdd(self):
        """Pops the last addition off the stack and removes it from the bucket."""
        if len(self.addStack) > 0:
            last = self.addStack.pop()
            if type(last) == str:
                self.files.remove(last)
            else:
                for f in last:
                    self.files.remove(f)
        self.fillBucket()
        return
    
    def removeFile(self, file):
        """
        Removes a file from the bucket.\n
        """
        #Removing a file from the bucket should also probably give a warning or something if the file is used in a slideshow.
        self.files.remove(file)
        self.fillBucket()
        return
    
    def verifyFile(self, file):
        """
        Checks if the file is in the bucket. If it is, returns True. If it isn't, returns False.
        """
        if file in self.files:
            return True
        else:
            return False
    
