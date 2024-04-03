import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.constants import *
import FileSupport as FP
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageOps
import os
from copy import deepcopy
import time
import math

updateRate = 100 #Milliseconds
transition_START = time.time()
transition_END = time.time()
    
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
            else:
                self.hideHorizontal = False

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
        self.update_idletasks()
        if self.verticle and not self.hideVertical:
            self.scrollbar.grid()
            self.canvas.configure(width=self.winfo_width()-self.scrollbar.winfo_width())
        if self.horizontal and not self.hideHorizontal:
            self.scrollbar_h.grid()
            self.canvas.configure(height=self.winfo_height()-self.scrollbar_h.winfo_height())
        return

    def hide_scrollbars(self, event):
        self.update_idletasks()
        if self.verticle:
            self.scrollbar.grid_remove()
            self.canvas.configure(width=self.winfo_width())
        if self.horizontal:
            self.scrollbar_h.grid_remove()
            self.canvas.configure(height=self.winfo_height())
        return
    
    def hoverEnter(self, event):
        #If you hover over the canvas, mousewheel scrolling should be enabled
        self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)
        return
    
    def hoverLeave(self, event):
        #Once you leave the canvas, mousewheel scrolling should be disabled
        self.canvas.unbind_all("<MouseWheel>")
        return
    
    def onMouseWheel(self, event):
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

        self.transition_id = None #Used as after_id for transitions incase they need to be cancelled early
        self.transitioning: bool = False #If a transition is currently happening
        self.deltaTime = 80 #Target time between frames in ms
        self.frameCounter = 0
        self.totalTransitionTime = 0
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

    def cancelTransition(self):
        if self.transition_id:
            self.after_cancel(self.transition_id)
            self.transition_id = None
            self.transitioning = False
        return

    def loadImage(self, imagePath:str):
        self.cancelTransition()
        #Clear the canvas
        self.delete("all")
        pth = FP.file_check(imagePath, FP.relative_project_path)
        print(f"Loading {pth} into ImageViewer")
        #Test if the file is a valid image file
        try:
            img = Image.open(pth)
            img = ImageOps.exif_transpose(img)
            self.imagePath = imagePath
            self.imagePIL = img
            #Delete & replace old label
            self.imageLabel = self.create_text(10, 10, anchor="nw", text=FP.removeExtension(FP.removePath([self.imagePath]))[0], font=("Arial", 16), fill="#FF1D8E")
            # print(f"Loaded {imagePath} into ImageViewer")
        except:
            print(f"{imagePath} is not a valid image file.")
            self.imagePath = FP.MissingImage
            img = Image.open(self.imagePath)
            self.imagePIL = img
            print(f"Loaded {imagePath} into ImageViewer as Missing Image")

        #Resize the image while using the aspect ratio
        self.imagePIL.thumbnail((self.canvasWidth, self.canvasHeight), resample=Image.NEAREST, reducing_gap=None)
        self.image = ImageTk.PhotoImage(self.imagePIL)
        self.canvasImage = self.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
        self.redrawImage()
        return
    
    def loadImagePIL(self, imagePIL:Image):
        transition_START = time.time()
        self.cancelTransition()
        #Clear the canvas
        self.delete("all")
        self.imagePath = None
        self.imagePIL = imagePIL
        #Resize the image while using the aspect ratio
        self.image = ImageTk.PhotoImage(self.imagePIL)
        self.canvasImage = self.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
        transition_END = time.time()
        print(f"Load From PIL Time: {(transition_END - transition_START) * 1000:.2f}ms")
        return
    
    def getImage(self):
        return self.imagePIL

    def redrawImage(self):
        """Redraws the image on the canvas. Called when canvas is resized."""
        #Return early if there is no image
        if self.imagePIL == None:
            print("No image to redraw")
            self.delete("all")
            return
        print("Image to redraw")

        #Get the size of the canvas
        self.canvasWidth = self.winfo_width()
        self.canvasHeight = self.winfo_height()
        #Clear the canvas
        self.delete("all")
        #Resize the image while using the aspect ratio
        pth = FP.file_check(self.imagePath, FP.relative_project_path)
        img = Image.open(pth)
        img = ImageOps.exif_transpose(img)
        self.imagePIL = img
        self.imagePIL.thumbnail((self.canvasWidth, self.canvasHeight), resample=Image.NEAREST, reducing_gap=None)
        self.image = ImageTk.PhotoImage(self.imagePIL)
        self.canvasImage = self.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
        self.imageLabel = self.create_text(10, 10, anchor="nw", text=FP.removeExtension(FP.removePath([self.imagePath]))[0], font=("Arial", 16), fill="#FF1D8E")

        # if self.imagePath == FP.MissingImage:
        #     self.after(3000, self.setBlankImage)
        return
    
    def executeTransition(self, transitionType: str, transitionTime, endImg: Image, startImg: Image=None):
        """Execute a transition to the endImg. If startImg is None, then it will use a blank black image as the start image.\n
        transitionType: str - The type of transition to execute. Options are: "default", "wipedown", "wipeup", "wipeleft", "wiperight", "fade" """
        if startImg == None:
            #Use a blank black image as the start image
            startImg = Image.new("RGB", (self.canvasWidth, self.canvasHeight), (0, 0, 0))

        print(f"transitionTime: {transitionTime}ms")
        # transitionTime = transitionTime//1000 #Convert to seconds

        #Check if the images are the same size. If they are good. If not then resize the start image to the same size as the end image.
        if startImg.width != endImg.width or startImg.height != endImg.height:
            print("Resizing start image to match end image")
            startImg = startImg.resize((endImg.width, endImg.height), resample=Image.NEAREST)

        #Booster just makes the transition SLIGHTLY faster. Maybe not necessary if we made the transitions better, but whatever.
        booster = 1 + (transitionTime * (0.0005/100)) #For every ms, add X% to the transition speed
        print(f"Booster: {booster}%")
        self.frameCounter = 0
        self.totalTransitionTime = 0

        if transitionType == FP.transitionType.DEFAULT:
            #Just change the image after the transition time
            print(f"Default transition. Nothing to really preview")
            self.loadImagePIL(endImg)
        elif transitionType == FP.transitionType.WIPEDOWN:
            increment = endImg.height / (transitionTime) #Unit per ms
            increment = increment * self.deltaTime * booster
            self.transitioning = True
            print(f"Increment: {increment}")
            self.transition_WipeDown(startImg, endImg, 0, increment)
        elif transitionType == FP.transitionType.WIPEUP:
            increment = endImg.height / (transitionTime) #Unit per ms
            increment = increment * self.deltaTime * booster
            #Basically it's going to get the amount of pixels that needs to reveal every 40ms to complete the transition in the specified time.
            self.transitioning = True
            print(f"Increment: {increment}")
            self.transition_WipeUp(startImg, endImg, 0, increment)

        elif transitionType == FP.transitionType.WIPELEFT:
            increment = endImg.width / (transitionTime) #Unit per ms
            increment = increment * self.deltaTime * booster #40ms per iteration

            #Basically it's going to get the amount of pixels that needs to reveal every 40ms to complete the transition in the specified time.
            self.transitioning = True
            print(f"Increment: {increment}")
            self.transition_WipeLeft(startImg, endImg, 0, increment)

        elif transitionType == FP.transitionType.WIPERIGHT:
            increment = endImg.width / (transitionTime) #Unit per ms
            increment = increment * self.deltaTime * booster #40ms per iteration

            #Basically it's going to get the amount of pixels that needs to reveal every 40ms to complete the transition in the specified time.
            self.transitioning = True
            print(f"Increment: {increment}")
            self.transition_WipeRight(startImg, endImg, 0, increment)

        elif transitionType == FP.transitionType.FADE:
            inc = 255 / (transitionTime) #Unit per ms
            inc = inc * self.deltaTime * booster
            self.transitioning = True
            print(f"Increment: {inc:.2f}")
            self.transition_Fade(startImg, endImg, 0, inc)

    #########################
    # Could potentially just combined every wipe transition into one function. - James

    def transition_WipeRight(self, startImg: Image, endImg: Image, counter: float, increment: float):
        """endImg renders in top startImg in sections in specified direciton. Time is deteremined by the increment ammount.\n  
        Timing is (255/increment) * self.deltaTime."""
        transition_START = time.time()
        #If the counter is greater than the width of the image, then the transition is complete.
        if counter > endImg.width + 10:
            print("Transition Complete")
            self.cancelTransition()
            return 1
        else:
            self.frameCounter += 1
        #Basically next image, crop it to correct size, then paste it on top of the current image.
        #Then draw the new image on the canvas.

        cnum = round(counter)
        #Crop the end image to counter
        endCrop = endImg.crop((0, 0, cnum, endImg.height))
        #Paste the end image onto the start image
        startImg.paste(endCrop, (0,0))
        #Draw the start image onto the canvas
        self.image = ImageTk.PhotoImage(startImg)
        self.canvasImage = self.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
        
        transition_END = time.time()
        transitionTime = (transition_END - transition_START) * 1000 #ms
        remainingTime = int(math.ceil(self.deltaTime - (transitionTime)-1))
        self.totalTransitionTime += transitionTime + remainingTime
        # print(f"Remaining Time: {remainingTime}ms = delta: {self.deltaTime}ms - transitionTime: {(transitionTime):.2f}ms")
        self.transition_id = self.after(remainingTime, self.transition_WipeRight, startImg, endImg, counter+increment, increment)
        return
    
    def transition_WipeLeft(self, startImg: Image, endImg: Image, counter: float, increment: float):
        """endImg renders in top startImg in sections in specified direciton. Time is deteremined by the increment ammount.\n  
        Timing is (255/increment) * self.deltaTime."""
        transition_START = time.time()
        #If the counter is greater than the width of the image, then the transition is complete.
        if counter > endImg.width + 10:
            print("Transition Complete")
            self.cancelTransition()
            return 1
        else:
            self.frameCounter += 1
        #Basically next image, crop it to correct size, then paste it on top of the current image.
        #Then draw the new image on the canvas.
        cnum = round(counter)
        #Crop the end image to counter
        endCrop = endImg.crop((endImg.width - cnum, 0, endImg.width, endImg.height))
        #Paste the end image onto the start image
        startImg.paste(endCrop, (endImg.width - cnum, 0))
        #Draw the start image onto the canvas
        self.image = ImageTk.PhotoImage(startImg)
        self.canvasImage = self.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
        
        transition_END = time.time()
        transitionTime = (transition_END - transition_START) * 1000 #ms
        remainingTime = int(math.ceil(self.deltaTime - (transitionTime)-1))
        self.totalTransitionTime += transitionTime + remainingTime
        # print(f"Remaining Time: {remainingTime}ms = delta: {self.deltaTime}ms - transitionTime: {(transitionTime):.2f}ms")
        self.transition_id = self.after(remainingTime, self.transition_WipeLeft, startImg, endImg, counter+increment, increment)
        return
    
    def transition_WipeDown(self, startImg: Image, endImg: Image, counter: float, increment: float):
        """endImg renders in top startImg in sections in specified direciton. Time is deteremined by the increment ammount.\n  
        Timing is (255/increment) * self.deltaTime."""
        transition_START = time.time()
        #If the counter is greater than the width of the image, then the transition is complete.
        if counter >= endImg.height + 10:
            print("Transition Complete")
            self.cancelTransition()
            return 1
        else:
            self.frameCounter += 1
        #Basically next image, crop it to correct size, then paste it on top of the current image.
        #Then draw the new image on the canvas.

        cnum = round(counter)
        #Crop the end image to counter
        endCrop: Image = endImg.crop((0, 0, endImg.width, cnum))
        #Paste the end image onto the start image
        startImg.paste(endCrop, (0,0))
        #Draw the start image onto the canvas
        self.image = ImageTk.PhotoImage(startImg)
        self.canvasImage = self.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
       
        transition_END = time.time()
        transitionTime = (transition_END - transition_START) * 1000 #ms
        remainingTime = int(math.ceil(self.deltaTime - (transitionTime)-1))
        self.totalTransitionTime += transitionTime + remainingTime
        # print(f"Remaining Time: {remainingTime}ms = delta: {self.deltaTime}ms - transitionTime: {(transitionTime):.2f}ms")
        self.transition_id = self.after(remainingTime, self.transition_WipeDown, startImg, endImg, counter+increment, increment)
        return
    
    def transition_WipeUp(self, startImg: Image, endImg: Image, counter: float, increment: float):
        """endImg renders in top startImg in sections in specified direciton. Time is deteremined by the increment ammount.\n  
        Timing is (255/increment) * self.deltaTime."""
        transition_START = time.time()
        #If the counter is greater than the width of the image, then the transition is complete.
        if counter > endImg.height + 10:
            print("Transition Complete")
            self.cancelTransition()
            return 1
        else:
            self.frameCounter += 1
        #Basically next image, crop it to correct size, then paste it on top of the current image.
        #Then draw the new image on the canvas.

        #Crop the end image to counter
        cnum = round(counter)
        endCrop = endImg.crop((0, endImg.height - cnum, endImg.width, endImg.height))
        #Paste the end image onto the start image
        startImg.paste(endCrop, (0, endImg.height - cnum))
        #Draw the start image onto the canvas
        self.image = ImageTk.PhotoImage(startImg)
        self.canvasImage = self.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
        
        transition_END = time.time()
        transitionTime = (transition_END - transition_START) * 1000 #ms
        remainingTime = int(math.ceil(self.deltaTime - (transitionTime)-1))
        self.totalTransitionTime += transitionTime + remainingTime
        # print(f"Remaining Time: {remainingTime}ms = delta: {self.deltaTime}ms - transitionTime: {(transitionTime):.2f}ms")
        self.transition_id = self.after(remainingTime, self.transition_WipeUp, startImg, endImg, counter+increment, increment)
        return
    
    def transition_Fade(self, startImg: Image, endImg: Image, counter: float, increment: float):
        """Fades from startImg to endImg. Time is deteremined by the increment ammount.\n  
        Timing is (255/increment) * self.deltaTime."""
        transition_START = time.time()
        #If the counter is greater than the opacity of the image, then the transition is complete.
        if counter >= 255-increment:
            print("Transition Complete")
            self.cancelTransition()
            return 1
        else:
            self.frameCounter += 1           
        #Interpolate the two images
        newImg = Image.blend(startImg, endImg, counter/255)
        self.image = ImageTk.PhotoImage(newImg)
        # transition_START = time.time()
        self.canvasImage = self.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
        
        transition_END: float = time.time()
        transitionTime: float = (transition_END - transition_START) * 1000 #ms
        remainingTime: int = max(1, int(math.ceil(self.deltaTime - (transitionTime)-1)))
        self.totalTransitionTime += transitionTime + remainingTime
        # print(f"Remaining Time: {remainingTime}ms = delta: {self.deltaTime}ms - transitionTime: {(transitionTime):.2f}ms")
        self.transition_id = self.after(remainingTime, self.transition_Fade, startImg, endImg, counter+increment, increment)
        return
        
           
    def printCanvasSize(self):
        self.canvasWidth = self.canvas.winfo_width()
        self.canvasHeight = self.canvas.winfo_height()
        print(f"Canvas Size: {self.canvasWidth}x{self.canvasHeight}")
        return

    def setBlankImage(self):
        print("Setting Blank Image")
        self.imagePath = ""
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
        
        #If we are dealing with SliceIcons, check and see if the file is in the folder.
        pth = imagepath
        if isinstance(self, SlideIcon):
            pth = FP.file_check(imagepath, FP.relative_project_path)
            
        #Test if the file is a valid image file
        try:
            img = Image.open(pth)
        except:
            # print(f"{imagepath} is not a valid image file.")
            self.missing = True
            img = Image.open(FP.MissingImage)
            self.name = "File Not Found"

        img = ImageOps.exif_transpose(img)
        self.imagepath = imagepath
        self.__imagePIL = img
        self.__imagePIL.thumbnail((self.canvasWidth, self.canvasHeight), resample=Image.NEAREST, reducing_gap=None)
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

    def refreshImage(self):
        pth = self.imagepath
        if isinstance(self, SlideIcon):
            pth = FP.file_check(self.imagepath, FP.relative_project_path)

        #Test if the file is a valid image file
        try:
            img = Image.open(pth)
        except:
            # print(f"{imagepath} is not a valid image file.")
            self.missing = True
            img = Image.open(FP.MissingImage)
            self.name = "File Not Found"

        img = ImageOps.exif_transpose(img)
        self.__imagePIL = img
        self.__imagePIL.thumbnail((self.canvasWidth, self.canvasHeight), resample=Image.NEAREST, reducing_gap=None)
        self.image = ImageTk.PhotoImage(self.__imagePIL)
        self.canvasImage = self.canvas.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image, anchor=tk.CENTER)

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
        #If the name of the icon is "File Not Found" then return early.
        # if self.missing == True:
        #     return

        if self.linkedViewer != None:
            #Load image into the viewer
            self.linkedViewer.loadImage(self.imagepath)

        #Probably put info in the InfoFrame here
        if self.linkedInfo != None:
            self.linkedInfo.loadIcon(self)
        else:
            print(f"No InfoFrame linked to {self.name}")

        self.refreshImage()
        return
     
    def pickup(self, event):
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
                return

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

        self.defaultSlideDuration = 5
        self.defaultTransitionDuration = 1

        self.image: bool = False #If True, display the image info. If False, display the slide info.
        self.__icon = None #This will be the icon that was clicked on to open the info frame.

        self.fillProjectInfo()
        self.fillSlideInfo()
        self.notebook.select(1)

        self.transition_checker = None #Used to check if the imageViewer is showing a transition.
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

        #Manual or automatic slide control
        rowNumber += 1
        self.manualSlideControlLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Manual Slide Control: ", font=("Arial", 12))
        self.manualSlideControlLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.manualSlideControl = tb.Checkbutton(self.projectInfoFrame.scrollable_frame, style="Roundtoggle.Toolbutton")
        self.manualSlideControl.grid(row=rowNumber, column=3, sticky="w")

        ###########
        #Check after loop setting creation for manual slide control stuff.

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
        #Loop Settings combobox
        self.loopLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Loop Settings: ", font=("Arial", 12))
        self.loopLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.loopSettingsCombo = tb.Combobox(self.projectInfoFrame.scrollable_frame, font=("Arial", 12), state="readonly", takefocus=0)
        self.loopSettingsCombo.config(width=7)
        self.loopSettingsCombo['values'] = (FP.loopSetting.INDEFINITE, FP.loopSetting.UNTIL_PLAYLIST_ENDS, FP.loopSetting.UNTIL_SLIDES_END)
        self.loopSettingsCombo.current(0)
        self.loopSettingsCombo.grid(row=rowNumber, column=3, columnspan=1, sticky="ew")

        self.loopSettingsCombo.bind("<<ComboboxSelected>>", self.setLoopSettings)

        #Set the transition type to the slide's transition type
        self.loopSettingsCombo.set(self.slideshow.loopSettings)

        #Tooltip for the loop settings combobox
        loopToolTipText = """This is the loop setting for the slideshow. The options are as follows:
        \n- Indefinite: The slideshow will loop indefinitely until manually stopped.
        \n- Until Playlist Ends: The slideshow will loop until the playlist ends.
        \n- Until Slides End: The slideshow will loop until the slides end.
        \nWhen Manual controls are selected, only Indefinite is available."""
        loopToolTip = ToolTipIcon(self.projectInfoFrame.scrollable_frame, loopToolTipText)
        loopToolTip.grid(row=rowNumber, column=4, sticky="w", padx=2)


        
        #If manual slide control is enabled, then only option 1 should be available.

        #Set self.slideshow.manualSlideControl as the control variable
        self.manualSlideControl.var = tk.BooleanVar()
        self.manualSlideControl.var.set(self.slideshow.manual)
        #If self.slideshow.manualSlideControl is true, then the button should be toggled
        if self.slideshow.manual:
            self.manualSlideControl.invoke()

        def updateLoopOptionMenu():
            #If manual slide controls are enabled, then only option 1 should be available.
            if self.slideshow.manual:
                self.loopSettingsCombo['values'] = (FP.loopSetting.INDEFINITE,)
                self.loopSettingsCombo.current(0)
            else:
                self.loopSettingsCombo['values'] = (FP.loopSetting.INDEFINITE, FP.loopSetting.UNTIL_PLAYLIST_ENDS, FP.loopSetting.UNTIL_SLIDES_END)
                self.loopSettingsCombo.current(0)

        #bind the toggle button to the slideshow
        def toggleManualSlideControl(event):
            self.slideshow.manual = not self.slideshow.manual
            updateLoopOptionMenu()
            return
        #Bind toggling the button to the control variable
        self.manualSlideControl.bind("<ButtonRelease-1>", toggleManualSlideControl)

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

        #Playlist Duration
        rowNumber += 1
        self.playlistDurationLabel = tb.Label(self.projectInfoFrame.scrollable_frame, text="Duration: ", font=("Arial", 12))
        self.playlistDurationLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.playlistDuration = tb.Label(self.projectInfoFrame.scrollable_frame, text="0:00", font=("Arial", 12))
        self.playlistDuration.grid(row=rowNumber, column=3, columnspan=1, sticky="w")
        #Fill the playlist duration
        duration = self.playlist.getDuration()
        self.playlistDuration.config(text=FP.formatTime(duration))

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

        rowNumber += 1
        self.tree_frame = tb.Frame(self.projectInfoFrame.scrollable_frame)
        self.tree_frame.grid(row=rowNumber, column=1, columnspan=14, rowspan=7, sticky="w", pady=5)

        #Scrollbar for the treeview
        tree_scrollbar = tb.Scrollbar(self.tree_frame, orient="vertical")
        tree_scrollbar.pack(side="right", fill="y")

        self.playlistTree = tb.Treeview(self.tree_frame, columns=("Name", "Order", "Status"), show="headings", selectmode="browse")
        self.playlistTree.heading("Name", text="Name", anchor="w")
        self.playlistTree.heading("Order", text="Order", anchor="w")
        self.playlistTree.heading("Status", text="Status", anchor="w")
        self.playlistTree.column("Name", anchor="w", minwidth=100, width=150)
        self.playlistTree.column("Order", anchor="w", minwidth=50, width=30)
        self.playlistTree.column("Status", anchor="w", minwidth=75, width=150)
        
        self.playlistTree.pack(expand=True, fill="both")

        tree_scrollbar.config(command=self.playlistTree.yview)

        #Tooltip for the playlist tree
        treeToolTipText = """This is the playlist for the slideshow. You can add, remove, and reorder songs in the playlist.
        \nName is the name of the song. Order is the order in which the song will play. Status is where the file is located.
        \nGood status: File is at the same file location as when you added it.
        \nIn Project Folder: File is in the same location as the project file.
        \nWarning: Only in Cache: File is only in the cache folder. Recommend moving or replacing the file.
        \nError: Missing: File is missing. Recommend replacing the file."""
        self.playlistTreeTooltip = ToolTipIcon(self.projectInfoFrame.scrollable_frame, text=treeToolTipText)
        self.playlistTreeTooltip.grid(row=rowNumber+2, column=0, sticky="e", padx=5, pady=2)

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
            song = self.playlist.songs[i]
            #Convert the song to a Song object
            if isinstance(song, dict):
                song = FP.Song(song['filePath'])
            song_name = FP.getBaseName([song.filePath])[0]
            
            song_location = FP.file_loc(song.filePath)
            status = "Good"
            if song_location == 1:
                status = "In Project Folder"
            elif song_location == 2:
                status = "Warning: Only in Cache"
            elif song_location == 3:
                status = "Error: Missing"

            self.playlistTree.insert("", "end", values=(song_name, i+1, status))




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
        for songT in self.playlist.songs:
            songPath = songT.filePath
            if FP.getBaseName([songPath])[0] == song:
                #Get the index of the song
                index = self.playlist.songs.index(songT)
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
        for songT in self.playlist.songs:
            songPath = songT.filePath
            if FP.getBaseName([songPath])[0] == song:
                #Get the index of the song
                index = self.playlist.songs.index(songT)
                self.playlist.moveSongUp(index)
                break

        #Move the song down in the treeview
        self.playlistTree.move(selected, "", self.playlistTree.index(selected)+1)
        #Redo the order numbers
        for i in range(len(self.playlist.songs)):
            self.playlistTree.item(self.playlistTree.get_children()[i], values=(self.playlistTree.item(self.playlistTree.get_children()[i])['values'][0], i+1))
        return

    def playListRemove(self):
        print("\n")
        #Get the selected item
        selected = self.playlistTree.selection()
        # print(self.playlist.songs)

        #If nothing is selected, return early
        if len(selected) == 0:
            return
        
        #Get the song that was selected
        song = self.playlistTree.item(selected)['values'][0]

        #Search for the song in the playlist
        songToRemove: FP.Song = None
        for s in self.playlist.songs:
            songPath = FP.getBaseName([s.filePath])[0]
            if songPath == song:
                songToRemove = s
                break

        if songToRemove == None:
            print(f"Could not find {song} in the playlist.")
            print(songToRemove.__dict__)
            return
        
        #Remove the song from the playlist
        print(f"Removing {songToRemove} from the playlist")
        self.playlist.removeSong(songToRemove)

        #Remove the song from the treeview
        self.playlistTree.delete(selected)
        self.update_idletasks()
        #Redo the order numbers
        for i in range(len(self.playlist.songs)):
            self.playlistTree.item(self.playlistTree.get_children()[i], values=(self.playlistTree.item(self.playlistTree.get_children()[i])['values'][0], i+1))
        duration = self.playlist.getDuration()
        self.playlistDuration.config(text=FP.formatTime(duration))

        try:
            FP.openFiles[songToRemove.filePath].close()
            del FP.openFiles[songToRemove.filePath]
        except:
            print(f"Could not close {songToRemove.filePath} with close() in InfoFrame.playListRemove()")
        return

    def playListAdd(self):
        print("")
        #Open a file dialog to select a .mp3, .mp4, .wav, or .aiff file
        filetypes = [("Audio Files", "*.mp3 *.mp4 *.wav *.aiff")]
        file = filedialog.askopenfile(filetypes=filetypes, title="Select a song to add to the playlist")
        if file == None:
            return

        #Check if file is already in the playlist
        for song in self.playlist.songs:
            if song.filePath == file.name:
                print(f"{file.name} is already in the playlist as {song}")
                return

        #Add the file to the playlist
        #How many songs are in the playlist
        songCount = len(self.playlist.songs)
        self.playlistTree.insert("", "end", values=(FP.getBaseName([file.name])[0], songCount+1))
        self.playlist.addSong(file.name)
        duration = self.playlist.getDuration()
        self.playlistDuration.config(text=FP.formatTime(duration))

        try:
            f = open(file.name, "rb")
            FP.openFiles[file.name] = f
        except:
            print(f"Could not open {file.name} with open() in InfoFrame.playListAdd()")
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
        rowNumber = 0
        self.nameLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Name: ", font=("Arial", 12))
        self.nameLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.name = tb.Label(self.slideInfoFrame.scrollable_frame, text=icon.name, font=("Arial", 12))
        self.name.grid(row=rowNumber, column=3, columnspan=10, sticky="ew")

        #imagePath
        rowNumber += 1
        pathlabelrow = rowNumber
        self.imagePathLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Image Path: ", font=("Arial", 12))
        self.imagePathLabel.grid(row=rowNumber, column=0, columnspan=3,sticky="w")
        self.imagePath = tb.Label(self.slideInfoFrame.scrollable_frame, text=icon.imagepath, font=("Arial", 12))
        self.imagePath.grid(row=rowNumber, column=3, columnspan=10, sticky="ew",)

        pth = icon.imagepath
        pth_location = FP.file_loc(pth, FP.relative_project_path)
        # if not os.path.exists(pth):
        #     self.imagePath.config(style="danger.TLabel")
        #     rowNumber += 1
        #     tb.Label(self.slideInfoFrame.scrollable_frame, text="This path is not valid. Image may be stored in project folder or cache. Consider replacing.", font=("Arial", 12), style="danger.TLabel").grid(row=rowNumber, column=0, columnspan=7)

        if pth_location == 0: #Full path
            print("Full path")
            pass
        elif pth_location == 1: #Project folder
            print("Project folder")
            pass
        elif pth_location == 2: #Cache
            print("Cache")
            self.imagePath.config(style="warning.TLabel")
            rowNumber += 1
            tb.Label(self.slideInfoFrame.scrollable_frame, text="This image is stored in the cache. Consider moving it to the project folder.", font=("Arial", 12), style="warning.TLabel").grid(row=rowNumber, column=0, columnspan=7)
        elif pth_location == 3: #Not found
            print("Not found")
            self.imagePath.config(style="danger.TLabel")
            rowNumber += 1
            tb.Label(self.slideInfoFrame.scrollable_frame, text="This image is missing. It may exist elsewhere. Consider replacing.", font=("Arial", 12), style="danger.TLabel").grid(row=rowNumber, column=0, columnspan=7)


        if self.image:
            rowNumber += 1
            #Change the notebook tab text to "Image Info"
            self.notebook.tab(0, text="Image Info")
            #Button for adding image to the slideshow
            self.addSlideButton = tb.Button(self.slideInfoFrame.scrollable_frame, text="Add Slide", command=self.addSlide, takefocus=0, style="success.TButton")
            self.addSlideButton.grid(row=rowNumber, column=0, sticky="w")
            #Button to remove image from the project.
            self.removeImageButton = tb.Button(self.slideInfoFrame.scrollable_frame, text="Remove Image", command=self.removeImage, takefocus=0, style="danger.TButton")
            self.removeImageButton.grid(row=rowNumber, column=1, sticky="w")
            return
            
        icon: SlideIcon = self.__icon
        self.notebook.tab(0, text="Slide Info")

        #open photo image
        buttonImage = Image.open(FP.resource_path(FP.refreshIcon))
        buttonImage.thumbnail((10, 10))
        self.buttonImage = ImageTk.PhotoImage(buttonImage)
        self.replaceImageButton = tb.Button(self.slideInfoFrame.scrollable_frame, command=self.replaceImage, takefocus=0, style="info.TButton", image=self.buttonImage)
        self.replaceImageButton.grid(row=pathlabelrow, column=0, columnspan=3, sticky="e")

        #Slide ID
        rowNumber += 1
        self.slideIDLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Slide ID: \t\t", font=("Arial", 12))
        self.slideIDLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.slideID = tb.Label(self.slideInfoFrame.scrollable_frame, text=str(icon.slide['slideID']), font=("Arial", 12))
        self.slideID.grid(row=rowNumber, column=3, sticky="w")

        rowNumber += 1
        tb.Label(self.slideInfoFrame.scrollable_frame, text="Press Enter to set the value. Unfocus or press Escape to cancel.", font=("Arial", 10)).grid(row=rowNumber, column=0, columnspan=10, sticky="w")

        #Duration - Entry
        rowNumber += 1
        self.durationLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Duration: ", font=("Arial", 12))
        self.durationLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.slideDuration = tb.Entry(self.slideInfoFrame.scrollable_frame, font=("Arial", 12), state=tk.NORMAL, takefocus=0)
        self.slideDuration.config(width=7)
        self.slideDuration.insert(0, float(icon.slide['duration']))
        self.slideDuration.insert(tk.END, "s")
        self.slideDuration.grid(row=rowNumber, column=3, sticky="w")
        self._slideDurationTemp = float(icon.slide['duration'])

        self.slideDuration.bind("<FocusIn>", self.onSlideDurationFocusIn)
        self.slideDuration.bind("<FocusOut>", self.onSlideDurationFocusOut)

        self.slideDurationRangeLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Must be between 1 and 60 seconds.", font=("Arial", 10), style="danger.TLabel")
        self.slideDurationRangeLabel.grid(row=rowNumber, column=4, columnspan=1, sticky="w")
        self.slideDurationRangeLabel.grid_remove()

        #Transition Speed - Entry
        rowNumber += 1
        self.transitionSpeedLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Transition Speed: ", font=("Arial", 12))
        self.transitionSpeedLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.transitionSpeed = tb.Entry(self.slideInfoFrame.scrollable_frame, font=("Arial", 12), state=tk.NORMAL, takefocus=0)
        self.transitionSpeed.config(width=7)
        self.transitionSpeed.insert(0, float(icon.slide['transitionSpeed']))
        self.transitionSpeed.insert(tk.END, "s")
        self.transitionSpeed.grid(row=rowNumber, column=3, sticky="w")
        self._transitionSpeedTemp = float(icon.slide['transitionSpeed'])

        self.transitionSpeed.bind("<FocusIn>", self.onTransitionSpeedFocusIn)
        self.transitionSpeed.bind("<FocusOut>", self.onTransitionSpeedFocusOut)

        self.transitionSpeedRangeLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Must be between 0.5 and 10 seconds.", font=("Arial", 10), style="danger.TLabel")
        self.transitionSpeedRangeLabel.grid(row=rowNumber, column=4, columnspan=1, sticky="w")
        self.transitionSpeedRangeLabel.grid_remove()

        #Transition Type - Dropdown
        rowNumber+= 1
        self.transitionTypeLabel = tb.Label(self.slideInfoFrame.scrollable_frame, text="Transition Type: ", font=("Arial", 12))
        self.transitionTypeLabel.grid(row=rowNumber, column=0, columnspan=3, sticky="w")
        self.transitionType = tb.Combobox(self.slideInfoFrame.scrollable_frame, font=("Arial", 12), state="readonly", takefocus=0)
        self.transitionType.config(width=7)
        self.transitionType['values'] = ("Default", "Fade", "Wipe_Up", "Wipe_Down", "Wipe_Left", "Wipe_Right")
        self.transitionType.current(0)
        self.transitionType.grid(row=rowNumber, column=3, columnspan=1, sticky="ew")

        self.transitionType.bind("<<ComboboxSelected>>", self.setTransitionType)

        #Set the transition type to the slide's transition type
        self.transitionType.set(icon.slide['transition'])

        #Preview Transition - Button
        rowNumber+= 1
        self.previewTransitionButton = tb.Button(self.slideInfoFrame.scrollable_frame, text="Preview Transition", command=self.previewTransition, takefocus=0)
        self.previewTransitionButton.grid(row=rowNumber, column=1, columnspan=2, pady=15)

        #Remove slide button
        self.removeSlideButton = tb.Button(self.slideInfoFrame.scrollable_frame, text="Remove Slide", command=self.removeSlide, takefocus=0, style="danger.TButton")
        self.removeSlideButton.grid(row=rowNumber, column=3, columnspan=2, pady=15)
        return
    
    def replaceImage(self):
        #Open a file dialog to select a new image
        filetypes = [("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff")]
        file = filedialog.askopenfile(filetypes=filetypes, title="Select a new image")
        if file == None:
            return
        #Close the previous imagePath in FP.openFiles
        try:
            FP.openFiles[self.__icon.imagepath].close()
            del FP.openFiles[self.__icon.imagepath]
        except:
            pass

        #Replace the image in the icon
        self.__icon.slide['imagePath'] = file.name
        self.__icon.imagepath = file.name
        #Update the image path label
        self.imagePath.config(text=file.name)

        try:
            f = open(file.name, "rb")
            FP.openFiles[file.name] = f
        except:
            print(f"Could not open {file.name} with open() in replaceImage.")

        #Redraw the image in the viewer
        if self.__icon.linkedViewer:
            self.__icon.linkedViewer.loadImage(file.name)
            self.__icon.linkedViewer.redrawImage()

        self.update_idletasks()

        #Update the icon in the slide reel
        self.__icon.linkedReel.fillReel()

        #Refresh the slide info
        self.fillSlideInfo()

        #Update the name label
        self.name.config(text=FP.getBaseName([file.name])[0])
        return
    
    
    def setSlideDuration(self, event):
        text = self.slideDuration.get()
        #If the last character is an s, remove it.
        if text[-1] == "s":
            text = text[:-1]
        
        #If the number can be converted to a float it should be valid.
        try:
            time = float(text)
        except:
            print("Invalid input for slide duration.")
            self.slideDuration.delete(0, tk.END)
            self.slideDuration.insert(0, self._slideDurationTemp)
            #Set the outline to red
            self.slideDuration.config(style="danger.TEntry")
            return
        
        #The duration must be between 1 and 60 seconds
        if time < 1 or time > 60:
            self.slideDurationRangeLabel.grid()
            self.slideDuration.config(style="danger.TEntry")
            #clamp the value
            if time < 1:
                time = 1
            elif time > 60:
                time = 60
            self.slideDuration.delete(0, tk.END)
            self.slideDuration.insert(0, time)
            return
        
        #Input was a valid number
        self.slideDurationRangeLabel.grid_remove()
        #Insert an s character at the end of the number
        self.slideDuration.config(style="TEntry")
        self.__icon.slide['duration'] = time
        self.winfo_toplevel().focus_set()
        self._slideDurationTemp = time
        return
    
    def onSlideDurationFocusIn(self, event):
        print("Slide Duration Focused In")
        self.slideDuration.bind("<Return>", self.setSlideDuration)
        #Bind escape to unfocus the entry
        self.slideDuration.bind("<Escape>", lambda event: self.focus_set())
        text = self.slideDuration.get()
        if text[-1] == "s":
            text = text[:-1]
        self._slideDurationTemp = float(text)
        self.slideDuration.delete(0, tk.END)
        self.slideDuration.insert(0, self._slideDurationTemp)
        #Set the style to normal
        self.slideDuration.config(style="TEntry")
        return
    
    def onSlideDurationFocusOut(self, event):
        print("Slide Duration Focused Out")
        self.slideDuration.unbind("<Return>")
        self.slideDuration.unbind("<Escape>")
        #Reset the entry
        text = str(self._slideDurationTemp) + "s"
        self.slideDuration.delete(0, tk.END)
        self.slideDuration.insert(0, text)
        return
    
    def setTransitionSpeed(self, event):
        text = self.slideDuration.get()
        #If the last character is an s, remove it.
        if text[-1] == "s":
            text = text[:-1]

        #Check if it is a valid number.
        try:
            speed = float(self.transitionSpeed.get())
        except:
            print("Invalid input for transition speed.")
            self.transitionSpeed.delete(0, tk.END)
            self.transitionSpeed.insert(0, self._transitionSpeedTemp)
            #Set the outline to red
            self.transitionSpeed.config(style="danger.TEntry")
            return
        
        #Must be between 0.5 and 10 seconds
        if speed < 0.5 or speed > 10:
            self.transitionSpeedRangeLabel.grid()
            self.transitionSpeed.config(style="danger.TEntry")
            #clamp the value
            if speed < 0.5:
                speed = 0.5
            elif speed > 10:
                speed = 10
            self.transitionSpeed.delete(0, tk.END)
            self.transitionSpeed.insert(0, speed)
            return
        
        #No errors
        self.transitionSpeedRangeLabel.grid_remove()
        self.transitionSpeed.config(style="TEntry")
        # print(f"Slide Duration: {self.transitionSpeed.get()}")
        self.__icon.slide['transitionSpeed'] = speed
        self.winfo_toplevel().focus_set()
        self._transitionSpeedTemp = speed
        return

    def onTransitionSpeedFocusIn(self, event):
        print("Transition Speed Focused In")
        self.transitionSpeed.bind("<Return>", self.setTransitionSpeed)
        #Bind escape to unfocus the entry
        self.transitionSpeed.bind("<Escape>", lambda event: self.focus_set())
        text = self.transitionSpeed.get()
        if text[-1] == "s":
            text = text[:-1]
        self._transitionSpeedTemp = float(text)
        self.transitionSpeed.delete(0, tk.END)
        self.transitionSpeed.insert(0, self._transitionSpeedTemp)
        #Set the style to normal
        self.transitionSpeed.config(style="TEntry")
        return
    
    def onTransitionSpeedFocusOut(self, event):
        print("Transition Speed Focused Out")
        self.transitionSpeed.unbind("<Return>")
        self.transitionSpeed.unbind("<Escape>")
        #Reset the entry
        text = str(self._transitionSpeedTemp) + "s"
        self.transitionSpeed.delete(0, tk.END)
        self.transitionSpeed.insert(0, text)
        return

    def setTransitionType(self, event):
        self.transitionType.selection_range(0,0)
        self.focus_set()
        print(f"Transition Type: {self.transitionType.get()}")
        self.__icon.slide['transition'] = self.transitionType.get()
        self.update_idletasks()
        print(self.__icon.slide)
        return
    
    def setLoopSettings(self, event):
        self.loopSettingsCombo.selection_range(0,0)
        self.focus_set()
        print(f"Loop Settings: {self.loopSettingsCombo.get()}")
        self.slideshow.loopSettings = self.loopSettingsCombo.get()
        self.update_idletasks()
        return
    
    def checkTransition(self, imagePath):
        if self.__icon.linkedViewer.transitioning:
            self.transition_checker = self.after(16, self.checkTransition, imagePath)
        else:
            self.transition_checker = None
            self.__icon.linkedViewer.loadImage(imagePath)
    
    def previewTransition(self):
        print("Previewing Transition")
        if self.transition_checker:
            self.after_cancel(self.transition_checker)
            self.transition_checker = None
            self.after_cancel(self.__icon.linkedViewer.transition_id)
        #Have the image previewer do a transition 
        if type(self.__icon) == SlideIcon:
            transitionType = self.__icon.slide['transition']
            transitionSpeed = self.__icon.slide['transitionSpeed'] * 1000
            
            endImg = Image.open(FP.file_check(self.__icon.imagepath, FP.relative_project_path))
            endImg = ImageOps.exif_transpose(endImg)
            previousSlide = self.slideshow.getSlide(self.__icon.slide['slideID']-1)
            if previousSlide == None:
                startImg = Image.new("RGB", (1920, 1080), (0, 0, 0))
            else:
                startImg = Image.open(FP.file_check(previousSlide['imagePath'], FP.relative_project_path))
                startImg = ImageOps.exif_transpose(startImg)
            startImg.thumbnail((self.__icon.linkedViewer.canvasWidth, self.__icon.linkedViewer.canvasHeight), resample=Image.NEAREST, reducing_gap=None)
            endImg.thumbnail((self.__icon.linkedViewer.canvasWidth, self.__icon.linkedViewer.canvasHeight), resample=Image.NEAREST, reducing_gap=None)
            
            self.__icon.linkedViewer.executeTransition(transitionType, transitionSpeed, endImg, startImg)
            self.checkTransition(self.__icon.slide['imagePath'])
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
        #If the new icon and old icon are the same, return early
        if icon == self.__icon:
            return

        if type(icon) == SlideIcon:
            self.image = False
            self.__icon = icon
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

            try:
                f = open(imgPath, "rb")
                FP.openFiles[imgPath] = f
            except:
                print(f"Could not open {imgPath} with open() in fillReel.")


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
                child.refreshImage()
            child.grid()
        return

    def addSlide(self, imagePath:str, index:int=-1):
        #First check if there is a slideshow object. If there isn't there isn't a point in adding a slide.
        if self.slideshow == None:
            print("\n\nNo slideshow object to add slide to.")
            return

        #Add the slide to the slideshow object
        slide = FP.Slide(imagePath)
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
            #Refresh the icons instead
            for icon in self.icons:
                icon.refreshImage()

            return
        self.columnCount = columnCount
        
        for icon in self.iconFrame.winfo_children():
            icon.destroy()

        
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
            if j == columnCount:
                j = 0
                i += 1
        
        addFileButton = tb.Button(self.iconFrame, text="Add File", command=lambda: self.addFile(filedialog.askopenfilenames(multiple=True, filetypes=[("Image Files", "*.jpg *.jpeg *.png")])))
        addFolderButton = tb.Button(self.iconFrame, text="Add Folder", command=lambda: self.addFolder(filedialog.askdirectory()))
        addFileButton.grid(row=i, column=j, padx=3, pady=3)
        j += 1
        if j == columnCount:
            j = 0
            i += 1
        addFolderButton.grid(row=i, column=j, padx=3, pady=3)

        # # print(f"Files in bucket: {len(self.files)}")
        # if len(self.files) == 0:
        #     print("No files in the bucket")
        #     #Create buttons to add files
        #     addFileButton = tb.Button(self.iconFrame, text="Add File", command=lambda: self.addFile(filedialog.askopenfilenames(multiple=True, filetypes=[("Image Files", "*.jpg *.jpeg *.png")])))
        #     addFileButton.pack()
        #     addFolderButton = tb.Button(self.iconFrame, text="Add Folder", command=lambda: self.addFolder(filedialog.askdirectory()))
        #     addFolderButton.pack()
        #     return
        
        return
          
    def loadProject(self, project: FP.Slideshow):
        """Given a project object it will load all the files in the project into the bucket."""
        self.files = project.filesInProject
        self.projectLabel.config(text=project.name)
        self.fillBucket()
        for file in self.files:
            try:
                f = open(file, "rb")
                FP.openFiles[file] = f
            except:
                print(f"Error opening file: {file}")
        return

    def addFile(self, file):
        """
        Given an imagePath, it will add the image to the bucket.
        """
        files = []
        #Sometimes the input is a string or like a tuple. This is to catch that.
        if type(file) == str:
            # print(f"Adding {file} to the bucket")
            #Check if the file exists
            if os.path.exists(file):
                self.files.append(file)
                files.append(file)
            else:
                pass
        elif type(file) == tuple:
            # print(f"Adding tuple {file} to the bucket")
            for f in file:
                print(f)
                self.files.append(f)
                files.append(f)
        else:
            print(f"Invalid file type: {type(file)}")
            return
        self.addStack.append(files)
        self.fillBucket()
        for file in files:
            try:
                f = open(file, "rb")
                FP.openFiles[file] = f
                #Add the file to the cache
                FP.copyFileToCache(file)
            except:
                print(f"Error opening file: {file}")
        return
    
    def addFolder(self, folder):
        """
        Given a folderPath it will add all the images it finds within the folder and subfolders to the bucket.
        """
        files = []
        if type(folder) == str:
            #Check if the folder exists
            if os.path.exists(folder):
                files = FP.getJPEG(folder, True)
            else:
                print(f"Folder {folder} does not exist.")
                return
        elif type(folder) == tuple:
            for f in folder:
                files.extend(FP.getJPEG(f, True))
        else:
            print(f"Expected string or tuple of strings. Got {type(folder)}")
            return
        self.addStack.append(files)
        self.files.extend(files)
        self.fillBucket()
        for file in files:
            try:
                f = open(file, "rb")
                FP.openFiles[file] = f
                #Add the file to the cache
                FP.copyFileToCache(file)
            except:
                print(f"Error opening file: {file}")
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
        try:
            FP.openFiles[file].close()
            del FP.openFiles[file]
        except:
            print(f"Error closing file: {file}")
        return
    
    def verifyFile(self, file):
        """
        Checks if the file is in the bucket. If it is, returns True. If it isn't, returns False.
        """
        if file in self.files:
            return True
        else:
            return False
    
class RecentSlideshowList(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        slideshows = FP.getRecentSlideshows()
        # for s in slideshows:
        #     print(s)


        #Create a label frame
        self.labelFrame = tb.LabelFrame(self, text="Recent Slideshows", bootstyle="primary")
        self.labelFrame.pack(expand=True, fill="both", padx=10, pady=10)

        #Create a tableView
        col_names = [
            "Name",
            "Date Modified",
            {"text": "Path", "stretch": True}
        ]

        row_data = []
        for s in slideshows:
            #Split using '$' as a delimiter
            s = s.split("$")
            name = FP.getBaseName([s[0]])[0]
            # print(name)
            row_data.append((name, s[1], s[0]))
        self.tableView = Tableview(master=self.labelFrame, 
                                    coldata=col_names, 
                                    rowdata=row_data, 
                                    bootstyle=tb.PRIMARY,
                                    searchable=True,
                                    autofit=True)
        self.tableView.pack(expand=True, fill="both")
        
        #Bind the double click event to open the slideshow
        # self.tableView.view.bind("<Double-1>", self.openSlideshow)
        return
    
class ToolTipIcon(tk.Canvas):
    def __init__(self, master, text:str=None, **kwargs):
        super().__init__(master, **kwargs)
        self.text = text
        if self.text == None:
            self.text = "Hello World."

        #Set canvas background
        # self.config(bg="red")

        #Set canvas size to 20x20
        self.config(width=25, height=25)

        #Get size of the canvas
        self.width = self.winfo_width()
        self.height = self.winfo_height()

        #Open the image
        self.image = Image.open(FP.resource_path(FP.toolTipIcon))
        self.image.thumbnail((self.width, self.height))
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.create_image(self.width//2, self.height//2, image=self.tkimage)

        #bind the configure event
        self.bind("<Configure>", self.resize)
        
        ToolTip(self, text=self.text)
        return
    
    def resize(self, event):
        #If the size has changed
        if self.width != self.winfo_width() or self.height != self.winfo_height():
            self.width = self.winfo_width()
            self.height = self.winfo_height()
            self.image = Image.open(FP.resource_path(FP.toolTipIcon))
            self.image.thumbnail((self.width, self.height))
            self.tkimage = ImageTk.PhotoImage(self.image)
            self.create_image(self.width//2, self.height//2, image=self.tkimage)
        return
    
    def setSize(self, width:int, height:int):
        self.width = width
        self.height = height
        self.image = Image.open(FP.resource_path(FP.toolTipIcon))
        self.image.thumbnail((self.width, self.height))
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.create_image(self.width//2, self.height//2, image=self.tkimage)
        return