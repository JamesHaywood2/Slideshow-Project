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
    Based on https://blog.teclado.com/tkinter-scrollable-frames/
    ---------------------
    Options:
    - container: The parent container for the frame
    - orient: "both", "horizontal", "vertical" - Which scrollbars to display
    - autohide: True/False - Whether or not to hide the scrollbars when the mouse is not over the frame
    ---------------------

    """
    def __init__(self, container, orient: str="both", autohide:bool = True, *args, **kwargs):
        #Scrollable Frame is a frame that houses a canvas and two scrollbars.
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="white")
        self.orient = orient
        self.autohide = autohide

        #It's going to check which scrollbar it needs to display.
        horiz = False
        vert = False
        orient_options = ["both", "horizontal", "vertical"]
        if orient not in orient_options:
            print(f"Invalid orientation. Defaulting to both. Options are {orient_options}")
            orient = "both"
        if orient == "both":
            horiz = True
            vert = True
        if orient == "horizontal":
            horiz = True
        if orient == "vertical":
            vert = True
        
        #If both are false something has gone wrong. Default to both.
        if horiz == False and vert == False:
            horiz = True
            vert = True

        self.verticle: bool = vert
        self.horizontal: bool = horiz

        if vert:
            self.scrollbar = tb.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        if horiz:
            self.scrollbar_h = tb.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas)

        #Whenever something is added to the scrollable frame (or removed), it changes sizes. Sroll region must be updated.
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvasWindow = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        if vert:
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.scrollbar.grid(row=0, column=1, sticky="ns")
        if horiz:
            self.canvas.configure(xscrollcommand=self.scrollbar_h.set)
            self.scrollbar_h.grid(row=1, column=0, sticky="ew")

        #Wait until they have been gridded to the frame
        self.update_idletasks()
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.hideVertical = False
        self.hideHorizontal = False

        #If autohide is on, bind show/hide scrollbars to the mouse entering and leaving the frame
        if self.autohide:
            self.bind("<Enter>", self.show_scrollbars)
            self.bind("<Leave>", self.hide_scrollbars)
            self.hide_scrollbars(None)

        self.update_idletasks()
        #Whenever the frame changes size, we should resize the canvas so it fits the frame properly.
        self.bind("<Configure>", self.resizeCanvas)
        self.canvas.bind("<Enter>", self.hoverEnter)
        self.canvas.bind("<Leave>", self.hoverLeave)

    def resizeCanvas(self, event):
        #The new size is the parent frame's new size.
        canvasWidth = self.winfo_width()
        canvasHeight = self.winfo_height()

        #Basically we want the canvas to be as big as it can be while fitting in the parent frame. If there are scrollbars then it needs to be slightly smaller to make room for them.
        #Even if autohide is off, the scrollbars will be hidden if they aren't required.
        if self.verticle:
                #If the canvas is tall enough to display the entire scrollable frame, then the scrollbar should be hidden
                scrollFrameHeight = self.scrollable_frame.winfo_height()
                #If there is a horizontal scrollbar, then assum that the scrollable_frame is slightly larger.
                if self.horizontal:
                    scrollFrameHeight += self.scrollbar_h.winfo_height()

                if scrollFrameHeight <= canvasHeight:
                    self.hideVertical = True
                    # print("Enough height to display the entire frame")
                else:
                    self.hideVertical = False
                    # print("Not enough height to display the entire frame")

        if self.horizontal:
            #If the canvas is wide enough to display the entire scrollable frame, then the scrollbar should be hidden
            scrollFrameWidth = self.scrollable_frame.winfo_width()
            #If there is a vertical scrollbar, then assum that the scrollable_frame is slightly larger.
            if self.verticle:
                scrollFrameWidth += self.scrollbar.winfo_width()

            if scrollFrameWidth <= canvasWidth:
                self.hideHorizontal = True
                # print("Enough width to display the entire frame")
            else:
                self.hideHorizontal = False
                # print("Not enough width to display the entire frame")

        #If autohide is off (meaning scrollbars should "always" be visible), then whenever the canvas can't display all the contents, the canvas should be a little smaller to make room for the scrollbar.
        if not self.autohide:
            if not self.hideVertical:
                canvasWidth -= self.scrollbar.winfo_width()
            if not self.hideHorizontal:
                canvasHeight -= self.scrollbar_h.winfo_height()

        #Make the canvas the same size as the parent
        self.canvas.configure(width=canvasWidth, height=canvasHeight)

        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        return

    def show_scrollbars(self, event):
        # print("Showing Scrollbars")
        self.update_idletasks()
        if self.verticle and not self.hideVertical:
            self.scrollbar.grid()
            self.canvas.configure(width=self.winfo_width()-self.scrollbar.winfo_width())
        if self.horizontal and not self.hideHorizontal:
            self.scrollbar_h.grid()
            self.canvas.configure(height=self.winfo_height()-self.scrollbar_h.winfo_height())
        return

    def hide_scrollbars(self, event):
        # print("Hiding Scrollbars")
        self.update_idletasks()
        if self.verticle:
            self.scrollbar.grid_remove()
            self.canvas.configure(width=self.winfo_width())
        if self.horizontal:
            self.scrollbar_h.grid_remove()
            self.canvas.configure(height=self.winfo_height())
        return
    
    def hoverEnter(self, event):
        # print("Hovering over the frame")
        #If you hover over the canvas, mousewheel scrolling should be enabled
        self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)
        return
    
    def hoverLeave(self, event):
        # print("Leaving the frame")
        #Once you leave the canvas, mousewheel scrolling should be disabled
        self.canvas.unbind_all("<MouseWheel>")
        return
    
    def onMouseWheel(self, event):
        # print("Mousewheel Scrolling")
        #If the mousewheel is scrolled, the canvas should scroll
        #Prioritize vertical scrolling over horizontal scrolling
        #There may be a better way to do this than just prioritizng one over the other, but I think this works fine. - James
        if self.verticle and not self.hideVertical:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.horizontal and not self.hideHorizontal:
            self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
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
        """Load a given image found at imagePath into the ImageViewer."""
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
        """Redraws the image on the canvas."""
        #This maybe should be called when the canvas is resized.
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
            self.imagepath = imagepath
            self.name = "File Not Found"
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
            #Check if you are within the bounds of the linked reel.
            if self.linkedReel:
                #Maybe have these as attributes of the reel instead of calculating them every time??
                x, y, w, h = self.linkedReel.winfo_rootx(), self.linkedReel.winfo_rooty(), self.linkedReel.winfo_width(), self.linkedReel.winfo_height()
                #If the mouse is within the bounds of the reel,
                if event.x_root > x and event.x_root < x+w and event.y_root > y and event.y_root < y+h:
                    #If the icon is at the left/right edge of the reel, slowly scroll in that direction.
                    

                    #Check and see if the user is hovering over a divider. If they are, highlight the divider
                    for divider in self.linkedReel.dividers:
                        x, y, w, h = divider.winfo_rootx(), divider.winfo_rooty(), divider.winfo_width(), divider.winfo_height()
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

        #Bind click - Not Needed
        self.label.bind("<ButtonRelease-1>", self.clickDivider)


    def clickDivider(self, event):
        #Not needed.
        print(f"Clicked on divider {self.index}")
        return

    def reset(self):
        self.label.configure(text="", bootstyle="default")
        self.configure(relief=tk.FLAT, borderwidth=0)
        return

class SlideIcon(FileIcon):
    """
    SlideIcon litteraly just a FileIcon but with the extra slide attribute. It's used in the SlideReel.\n
    It has virtually the same functionality as file icon, execpt the drag and drop is changed to function with the SlideReel.\n
    If you drag a slide icon around within the slide reel, it will cause dividers to show up. You can then drop the slide icon onto a divider to move the slide to that index.\n
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
        rowNumber = 0
        self.nameLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Name: ", font=("Arial", 12))
        self.nameLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.name = tb.Label(self.projectInfoFrame.scrollable_frame, text=self.slideshow.name, font=("Arial", 12))
        self.name.grid(row=rowNumber, column=3, columnspan=10, sticky="w")

        rowNumber += 1
        self.countLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Slide Count: ", font=("Arial", 12))
        self.countLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.count = tb.Label(self.projectInfoFrame.scrollable_frame, text=str(len(self.slideshow.getSlides())), font=("Arial", 12))
        self.count.grid(row=rowNumber, column=3, columnspan=10, sticky="w")

        rowNumber += 1
        self.pathLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Path: ", font=("Arial", 12))
        self.pathLabel.grid(row=rowNumber, column=0, columnspan=3,sticky="w")
        self.path = tb.Label(self.projectInfoFrame.scrollable_frame, text=self.slideshow.getSaveLocation(), font=("Arial", 12))
        self.path.grid(row=rowNumber, column=3, sticky="w", columnspan=4)

        rowNumber += 1
        self.defaultSlideDurationLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Default Slide Duration: ", font=("Arial", 12))
        self.defaultSlideDurationLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.defaultSlideDuration = tb.Entry(self.projectInfoFrame.scrollable_frame, font=("Arial", 12), state=tk.NORMAL, takefocus=0)
        self.defaultSlideDuration.config(width=7)
        self.defaultSlideDuration.insert(0, self.slideshow.defaultSlideDuration)
        self.defaultSlideDuration.grid(row=rowNumber, column=3, sticky="w")

        self.defaultSlideDuration.bind("<FocusIn>", self.onDefaultDurationFocusIn)
        self.defaultSlideDuration.bind("<FocusOut>", self.onDefaultDurationFocusOut)

        #Manual or automatic slide control
        rowNumber += 1
        self.manualSlideControlLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Manual Slide Control: ", font=("Arial", 12))
        self.manualSlideControlLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.manualSlideControl = tb.Checkbutton(self.projectInfoFrame.scrollable_frame, style="Roundtoggle.Toolbutton")
        self.manualSlideControl.grid(row=rowNumber, column=3, sticky="w")

        #Set self.slideshow.manualSlideControl as the control variable
        self.manualSlideControl.var = tk.BooleanVar()
        self.manualSlideControl.var.set(self.slideshow.manual)
        #If self.slideshow.manualSlideControl is true, then the button should be toggled
        if self.slideshow.manual:
            self.manualSlideControl.invoke()
        #bind the toggle button to the slideshow
        def toggleManualSlideControl(event):
            self.slideshow.manual = not self.slideshow.manual
            return
        #Bind toggling the button to the control variable
        self.manualSlideControl.bind("<ButtonRelease-1>", toggleManualSlideControl)

        #Slide shuffle toggle button
        rowNumber += 1
        self.slideShuffleLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Slide Shuffle: ", font=("Arial", 12))
        self.slideShuffleLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.slideShuffle = tb.Checkbutton(self.projectInfoFrame.scrollable_frame, style="Roundtoggle.Toolbutton")
        self.slideShuffle.grid(row=rowNumber, column=3, sticky="w")

        #Set self.slideshow.shuffle as the control variable
        self.slideShuffle.var = tk.BooleanVar()
        self.slideShuffle.var.set(self.slideshow.shuffle)
        #If self.slideshow.shuffle is true, then the button should be toggled
        if self.slideshow.shuffle:
            self.slideShuffle.invoke()
        #bind the toggle button to the slideshow
        def toggleShuffle(event):
            self.slideshow.shuffle = not self.slideshow.shuffle
            return
        #Bind toggling the button to the control variable
        self.slideShuffle.bind("<ButtonRelease-1>", toggleShuffle)

        rowNumber += 1
        self.loopLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Loop: ", font=("Arial", 12))
        self.loopLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.loop = tb.Checkbutton(self.projectInfoFrame.scrollable_frame, style="Roundtoggle.Toolbutton")
        self.loop.grid(row=rowNumber, column=3, sticky="w")

        #Set self.slideshow.loop as the control variable
        self.loop.var = tk.BooleanVar()
        self.loop.var.set(self.slideshow.loop)
        #If self.slideshow.loop is true, then the button should be toggled
        if self.slideshow.loop:
            self.loop.invoke()
        #bind the toggle button to the slideshow
        def toggleLoop(event):
            self.slideshow.loop = not self.slideshow.loop
            return
        #Bind toggling the button to the control variable
        self.loop.bind("<ButtonRelease-1>", toggleLoop)

        #Separator
        rowNumber += 1
        self.separator = tb.Separator(self.projectInfoFrame.scrollable_frame, orient="horizontal")
        self.separator.grid(row=rowNumber, column=0, columnspan=10, sticky="ew", pady=10)

        #Read the playlist from the slideshow
        self.playlist: FP.Playlist = self.slideshow.getPlaylist()
        self.slideshow.playlist = self.playlist
        self.slideshow.playlist.validate()

        #Playlist Label
        rowNumber += 1
        self.PlaylistLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Playlist: ", font=("Arial", 12))
        self.PlaylistLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.PlaylistName = tb.Label(self.projectInfoFrame.scrollable_frame, text="None", font=("Arial", 12))
        self.PlaylistName.grid(row=rowNumber, column=3, columnspan=1,sticky="w")

        #Playlist Duration
        rowNumber += 1
        self.playlistDurationLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Duration: ", font=("Arial", 12))
        self.playlistDurationLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.playlistDuration = tb.Label(self.projectInfoFrame.scrollable_frame, text="0:00", font=("Arial", 12))
        self.playlistDuration.grid(row=rowNumber, column=3, columnspan=1, sticky="w")

        #ShufflePlaylist toggle button
        rowNumber += 1
        self.shufflePlaylistLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Shuffle Playlist: ", font=("Arial", 12))
        self.shufflePlaylistLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.shufflePlaylist = tb.Checkbutton(self.projectInfoFrame.scrollable_frame, style="Roundtoggle.Toolbutton")
        self.shufflePlaylist.grid(row=rowNumber, column=3, columnspan=1, sticky="w")
        
        #Set self.playlist.shuffle as the control variable
        self.shufflePlaylist.var = tk.BooleanVar()
        self.shufflePlaylist.var.set(self.playlist.shuffle)
        #If self.playlist.shuffle is true, then the button should be toggled
        if self.playlist.shuffle:
            self.shufflePlaylist.invoke()
        #bind the toggle button to the playlist
        def togglePlaylistShuffle(event):
            self.playlist.shuffle = not self.playlist.shuffle
            return
        #Bind toggling the button to the control variable
        self.shufflePlaylist.bind("<ButtonRelease-1>", togglePlaylistShuffle)

        #Loop toggle button
        rowNumber += 1
        self.loopPlaylistLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Loop Playlist: ", font=("Arial", 12))
        self.loopPlaylistLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.loopPlaylist = tb.Checkbutton(self.projectInfoFrame.scrollable_frame, style="Roundtoggle.Toolbutton")
        self.loopPlaylist.grid(row=rowNumber, column=3, columnspan=1, sticky="w")


        #Set self.playlist.loop as the control variable
        self.loopPlaylist.var = tk.BooleanVar()
        self.loopPlaylist.var.set(self.playlist.loop)
        #If self.playlist.loop is true, then the button should be toggled
        if self.playlist.loop:
            self.loopPlaylist.invoke()
        #bind the toggle button to the playlist
        def togglePlaylistLoop(event):
            self.playlist.loop = not self.playlist.loop
            return
        #Bind toggling the button to the control variable
        self.loopPlaylist.bind("<ButtonRelease-1>", togglePlaylistLoop)

        rowNumber += 1
        self.tree_frame = tb.Frame(self.projectInfoFrame.scrollable_frame)
        self.tree_frame.grid(row=rowNumber, column=1, columnspan=9, rowspan=7, sticky="w")

        #Scrollbar for the treeview
        tree_scrollbar = tb.Scrollbar(self.tree_frame, orient="vertical")
        tree_scrollbar.pack(side="right", fill="y")

        self.playlistTree = tb.Treeview(self.tree_frame, columns=("Name", "Order"), show="headings", selectmode="browse")
        self.playlistTree.heading("Name", text="Name")
        self.playlistTree.heading("Order", text="Order")
        self.playlistTree.column("Name", anchor="w", minwidth=100, width=150)
        self.playlistTree.column("Order", anchor="w", minwidth=50, width=100)
        self.playlistTree.pack(expand=True, fill="both")

        tree_scrollbar.config(command=self.playlistTree.yview)

        #Buttons to move a song up, down, or remove it from the playlist
        self.moveUpButton = tb.Button(self.projectInfoFrame.scrollable_frame, text="/\\", command=self.playListMoveUp, takefocus=0)
        self.moveUpButton.grid(row=rowNumber+3, column=0, sticky="e", padx=5)
        self.addSongButton = tb.Button(self.projectInfoFrame.scrollable_frame, text="+", command=self.playListAdd, takefocus=0, style="success.TButton")
        self.addSongButton.grid(row=rowNumber+4, column=0, sticky="e", padx=5)
        self.removeSongButton = tb.Button(self.projectInfoFrame.scrollable_frame, text="X", command=self.playListRemove, takefocus=0, style="danger.TButton")
        self.removeSongButton.grid(row=rowNumber+5, column=0, sticky="e", padx=5)
        self.moveDownButton = tb.Button(self.projectInfoFrame.scrollable_frame, text="\\/", command=self.playListMoveDown, takefocus=0)
        self.moveDownButton.grid(row=rowNumber+6, column=0, sticky="e", padx=5)

        #Fill the treeview with the playlist
        for i in range(len(self.playlist.songs)):
            self.playlistTree.insert("", "end", values=(FP.getBaseName([self.playlist.songs[i]])[0], i+1))

        #Empty space to pad the bottom of grid
        rowNumber += 7
        self.emptySpace = tb.Label(self.projectInfoFrame.scrollable_frame, text="", font=("Arial", 12))
        self.emptySpace.grid(row=rowNumber, column=0, columnspan=10, sticky="w")
        return

    def playListMoveUp(self):
        #Get the selected item
        selected = self.playlistTree.selection()

        #If nothing is selected, return early
        if len(selected) == 0:
            return
        
        #Get the song that was selected
        song = self.playlistTree.item(selected)['values'][0]
        print(f"Song: {song} moving up in the playlist")
        for songPath in self.playlist.songs:
            if FP.getBaseName([songPath])[0] == song:
                # print(f"Moving {songPath} up in the playlist")
                #Get the index of the song
                index = self.playlist.songs.index(songPath)
                self.playlist.moveSongUp(index)
                break
        
        #Move the song up in the treeview
        self.playlistTree.move(selected, "", self.playlistTree.index(selected)-1)
        #Redo the order numbers
        for i in range(len(self.playlist.songs)):
            self.playlistTree.item(self.playlistTree.get_children()[i], values=(self.playlistTree.item(self.playlistTree.get_children()[i])['values'][0], i+1))
        return

    def playListMoveDown(self):
        #Get the selected item
        selected = self.playlistTree.selection()

        #If nothing is selected, return early
        if len(selected) == 0:
            return
        
        #Get the song that was selected
        song = self.playlistTree.item(selected)['values'][0]
        print(f"Song: {song} moving down in the playlist")
        for songPath in self.playlist.songs:
            if FP.getBaseName([songPath])[0] == song:
                # print(f"Moving {songPath} down in the playlist")
                #Get the index of the song
                index = self.playlist.songs.index(songPath)
                self.playlist.moveSongDown(index)
                break

        #Move the song down in the treeview
        self.playlistTree.move(selected, "", self.playlistTree.index(selected)+1)
        #Redo the order numbers
        for i in range(len(self.playlist.songs)):
            self.playlistTree.item(self.playlistTree.get_children()[i], values=(self.playlistTree.item(self.playlistTree.get_children()[i])['values'][0], i+1))
        return

    def playListRemove(self):
        #Get the selected item
        selected = self.playlistTree.selection()
        print(self.playlist.songs)

        #If nothing is selected, return early
        if len(selected) == 0:
            return
        
        #Get the song that was selected
        song = self.playlistTree.item(selected)['values'][0]
        print(f"Song: {song}")

        #Search for the song in the playlist
        for songPath in self.playlist.songs:
            if FP.getBaseName([songPath])[0] == song:
                print(f"Removing {songPath} from the playlist")
                self.playlist.removeSong(songPath)
                break

        #Remove the song from the treeview
        self.playlistTree.delete(selected)
        return

    def playListAdd(self):
        #Open a file dialog to select a .mp3, .mp4, .wav, or .aiff file
        filetypes = [("Audio Files", "*.mp3 *.mp4 *.wav *.aiff")]
        file = filedialog.askopenfile(filetypes=filetypes, title="Select a song to add to the playlist")
        if file == None:
            return

        #Check if file is already in the playlist
        for song in self.playlist.songs:
            if song == file.name:
                print(f"{file.name} is already in the playlist")
                return

        #Add the file to the playlist
        #How many songs are in the playlist
        songCount = len(self.playlist.songs)
        self.playlistTree.insert("", "end", values=(FP.getBaseName([file.name])[0], songCount+1))
        self.playlist.addSong(file.name)
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
        #Set the style to normal
        self.defaultSlideDuration.config(style="TEntry")
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
        elif self.__icon == None:
            print("FillSlideInfo: No icon selected.")
            label = tb.Label(self.slideInfoFrame.scrollable_frame, text="Select an image or slide to view info.", font=("Arial", 12))
            label.grid(row=0, column=0, columnspan=2, sticky="w")
            return
        else:
            print(f"FillSlideInfo: Invalid icon type. {type(self.__icon)}")
            return

        #Grid layout for the slide info
        self.nameLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Name: ", font=("Arial", 12))
        self.nameLabel.grid(row=0, column=0, columnspan=3, sticky="w")
        self.name = tb.Label(self.slideInfoFrame.scrollable_frame, text=icon.name, font=("Arial", 12))
        self.name.grid(row=0, column=3, columnspan=10, sticky="ew")

        #imagePath
        self.imagePathLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Image Path: ", font=("Arial", 12))
        self.imagePathLabel.grid(row=1, column=0, columnspan=3,sticky="w")
        self.imagePath = tb.Label(self.slideInfoFrame.scrollable_frame, text=icon.imagepath, font=("Arial", 12))
        self.imagePath.grid(row=1, column=3, columnspan=10, sticky="ew",)

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

        #Slide ID
        rowNum = 2
        self.slideIDLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Slide ID: \t\t", font=("Arial", 12))
        self.slideIDLabel.grid(row=rowNum, column=0, columnspan=3, sticky="w")
        self.slideID = tb.Label(self.slideInfoFrame.scrollable_frame, text=str(icon.slide['slideID']), font=("Arial", 12))
        self.slideID.grid(row=rowNum, column=3, sticky="w")

        #Duration - Entry
        rowNum += 1
        self.durationLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Duration: ", font=("Arial", 12))
        self.durationLabel.grid(row=rowNum, column=0, columnspan=3, sticky="w")
        self.slideDuration = tb.Entry(self.slideInfoFrame.scrollable_frame, font=("Arial", 12), state=tk.NORMAL, takefocus=0)
        self.slideDuration.config(width=7)
        self.slideDuration.insert(0, icon.slide['duration'])
        self.slideDuration.grid(row=rowNum, column=3, sticky="w")
        self._slideDurationTemp = icon.slide['duration']

        self.slideDuration.bind("<FocusIn>", self.onSlideDurationFocusIn)
        self.slideDuration.bind("<FocusOut>", self.onSlideDurationFocusOut)

        #Transition Speed - Entry
        rowNum += 1
        self.transitionSpeedLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Transition Speed: ", font=("Arial", 12))
        self.transitionSpeedLabel.grid(row=rowNum, column=0, columnspan=3, sticky="w")
        self.transitionSpeed = tb.Entry(self.slideInfoFrame.scrollable_frame, font=("Arial", 12), state=tk.NORMAL, takefocus=0)
        self.transitionSpeed.config(width=7)
        self.transitionSpeed.insert(0, icon.slide['transitionSpeed'])
        self.transitionSpeed.grid(row=rowNum, column=3, sticky="w")
        self._transitionSpeedTemp = icon.slide['transitionSpeed']

        self.transitionSpeed.bind("<FocusIn>", self.onTransitionSpeedFocusIn)
        self.transitionSpeed.bind("<FocusOut>", self.onTransitionSpeedFocusOut)

        #Transition Type - Dropdown
        rowNum += 1
        self.transitionTypeLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Transition Type: ", font=("Arial", 12))
        self.transitionTypeLabel.grid(row=rowNum, column=0, columnspan=3, sticky="w")
        self.transitionType = tb.Combobox(self.slideInfoFrame.scrollable_frame, font=("Arial", 12), state="readonly", takefocus=0)
        self.transitionType.config(width=7)
        self.transitionType['values'] = ("Default", "Fade", "Wipe_Up", "Wipe_Down", "Wipe_Left", "Wipe_Right")
        self.transitionType.current(0)
        self.transitionType.grid(row=rowNum, column=3, columnspan=1, sticky="ew")

        self.transitionType.bind("<<ComboboxSelected>>", self.setTransitionType)

        #Set the transition type to the slide's transition type
        self.transitionType.set(icon.slide['transition'])

        #Preview Transition - Button
        rowNum += 1
        self.previewTransitionButton = tb.Button(self.slideInfoFrame.scrollable_frame, text="Preview Transition", command=self.previewTransition, takefocus=0)
        self.previewTransitionButton.grid(row=rowNum, column=1, columnspan=2, pady=15)

        #Remove slide button
        self.removeSlideButton = tb.Button(self.slideInfoFrame.scrollable_frame, text="Remove Slide", command=self.removeSlide, takefocus=0, style="danger.TButton")
        self.removeSlideButton.grid(row=rowNum, column=3, columnspan=2, pady=15)
        return
    
    def setSlideDuration(self, event):
        #Check if it is a valid number.
        try:
            float(self.slideDuration.get())
        except:
            print("Invalid input for slide duration.")
            self.slideDuration.delete(0, tk.END)
            self.slideDuration.insert(0, 3)

            #Set the outline to red
            self.slideDuration.config(style="danger.TEntry")
            return
        
        #No errors
        self.slideDuration.config(style="TEntry")
        # print(f"Slide Duration: {self.slideDuration.get()}")
        self.__icon.slide['duration'] = self.slideDuration.get()
        self.winfo_toplevel().focus_set()
        self._slideDurationTemp = self.slideDuration.get()
        return
    
    def onSlideDurationFocusIn(self, event):
        # self.defaultSlideDuration.config(state=tk.NORMAL)
        print("Slide Duration Focused In")
        self.slideDuration.bind("<Return>", self.setSlideDuration)
        #Bind escape to unfocus the entry
        self.slideDuration.bind("<Escape>", lambda event: self.focus_set())
        self._slideDurationTemp = self.slideDuration.get()
        #Set the style to normal
        self.slideDuration.config(style="TEntry")
        return
    
    def onSlideDurationFocusOut(self, event):
        # self.defaultSlideDuration.config(state=tk.DISABLED)
        print("Slide Duration Focused Out")
        self.slideDuration.unbind("<Return>")
        self.slideDuration.unbind("<Escape>")
        #Reset the entry
        self.slideDuration.delete(0, tk.END)
        self.slideDuration.insert(0, self._slideDurationTemp)

        #Change style to normal
        # self.defaultSlideDuration.config(style="TEntry", bootstyle="normal")
        return
    
    def setTransitionSpeed(self, event):
        #Check if it is a valid number.
        try:
            float(self.transitionSpeed.get())
        except:
            print("Invalid input for transition speed.")
            self.transitionSpeed.delete(0, tk.END)
            self.transitionSpeed.insert(0, 3)

            #Set the outline to red
            self.transitionSpeed.config(style="danger.TEntry")
            return
        
        #No errors
        self.transitionSpeed.config(style="TEntry")
        # print(f"Slide Duration: {self.transitionSpeed.get()}")
        self.__icon.slide['transitionSpeed'] = self.transitionSpeed.get()
        self.winfo_toplevel().focus_set()
        self._transitionSpeedTemp = self.transitionSpeed.get()
        return

    def onTransitionSpeedFocusIn(self, event):
        # self.defaultSlideDuration.config(state=tk.NORMAL)
        print("Transition Speed Focused In")
        self.transitionSpeed.bind("<Return>", self.setTransitionSpeed)
        #Bind escape to unfocus the entry
        self.transitionSpeed.bind("<Escape>", lambda event: self.focus_set())
        self._transitionSpeedTemp = self.transitionSpeed.get()
        #Set the style to normal
        self.transitionSpeed.config(style="TEntry")
        return
    
    def onTransitionSpeedFocusOut(self, event):
        # self.defaultSlideDuration.config(state=tk.DISABLED)
        print("Transition Speed Focused Out")
        self.transitionSpeed.unbind("<Return>")
        self.transitionSpeed.unbind("<Escape>")
        #Reset the entry
        self.transitionSpeed.delete(0, tk.END)
        self.transitionSpeed.insert(0, self._transitionSpeedTemp)

        #Change style to normal
        # self.defaultSlideDuration.config(style="TEntry", bootstyle="normal")
        return

    def setTransitionType(self, event):
        self.transitionType.selection_range(0,0)
        self.focus_set()
        print(f"Transition Type: {self.transitionType.get()}")
        self.__icon.slide['transition'] = self.transitionType.get()
        self.update_idletasks()
        print(self.__icon.slide)
        return
    
    def previewTransition(self):
        print("Previewing Transition")
        #Have the image previewer do a transition
        #not yet implemented.
        return

    def addSlide(self):
        print(self.__icon.imagepath)
        self.__icon.linkedReel.addSlide(self.__icon.imagepath)
        return

    def removeImage(self):
        print(self.__icon.imagepath)
        self.__icon.linkedBucket.removeFile(self.__icon.imagepath)
        return
    
    def removeSlide(self):
        self.__icon.linkedReel.slideshow.removeSlide(self.__icon.slide)
        self.__icon.linkedReel.fillReel()
        return

    def loadIcon(self, icon):
        if type(icon) == SlideIcon:
            self.image = False
            self.__icon = icon
            print(f"Loading Slide {icon.slide['slideID']} into InfoFrame")
            print(self.__icon.slide)
        elif type(icon) == FileIcon:
            self.image = True
            self.__icon = icon
        else:
            print("Error loading Icon into InfoFrame: Invalid icon type.")

        self.fillSlideInfo()
        self.notebook.select(0)
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
        self.infoFrame.count.config(text=str(len(self.slides)))

        self.update_idletasks()
        self.scrollFrame.resizeCanvas(None)
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
        return

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
    
