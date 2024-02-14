import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *
import FileSupport as FP
from tkinter import filedialog
from tkinter import dnd
from PIL import Image, ImageTk
import os

#From https://blog.teclado.com/tkinter-scrollable-frames/
class ScrollableFrame(tb.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tb.Canvas(self)
        scrollbar = tb.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar_h = tb.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = tb.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.configure(xscrollcommand=scrollbar_h.set)

        scrollbar_h.pack(side="bottom", fill="x")
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

class ImageViewer(tb.Canvas):
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
        self.bind("<Configure>", lambda event: self.redrawImage())

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

    def redrawImage(self):
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

    def setBlankImage(self):
        print("Setting Blank Image")
        self.imagePath = None
        self.redrawImage()

class FileIcon(tk.Frame):
    def __init__(self, master, imagepath: str=None, **kwargs):
        super().__init__(master, **kwargs)
        self.width = 100
        self.height = 130
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
        nameCutoff: int = 14
        fn = self.name[:nameCutoff] + "..." if len(self.name) > nameCutoff else self.name
        self.label = tb.Label(self, text=fn, font=("Arial", 12), background="white")
        self.label.pack(expand=True, fill="both")

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

        #Event binding
        self.canvas.bind("<Double-Button-1>", self.openImage)
        self.canvas.bind("<Enter>", self.hoverEnter)
        self.canvas.bind("<Leave>", self.hoverLeave)
        self.__hover: bool = False
        self.canvas.bind("<ButtonRelease-1>", self.clickIcon)
        self.canvas.bind("<Button-1>", self.pickup)
        self.__startX: int = 0
        self.__startY: int = 0
        self.__popup: tk.Toplevel = None

    def openImage(self, event):
        os.startfile(self.imagepath)

    def hoverEnter(self, event):
        self.__hover = True
        self.configure(relief=tk.SUNKEN, borderwidth=2)

    def hoverLeave(self, event):
        self.__hover = False
        self.configure(relief=tk.FLAT, borderwidth=0)

    def clickIcon(self, event):
        print(f"Clicked on {self.name}")
        if self.linkedViewer != None:
            #Load image into the viewer
            self.linkedViewer.loadImage(self.imagepath)

        #Probably put info in the InfoFrame here
            
    def pickup(self, event):
        print(f"Click at {event.x}, {event.y} on {self.name}")
        self.__startX = event.x
        self.__startY = event.y
        #If missing image, don't allow dragging
        if self.missing == True:
            return
        self.canvas.bind("<B1-Motion>", self.dragIconStart)

    def dragIconStart(self, event):
        #Begin dragging after the mouse has moved a certain distance. Once it does, change the binding to dragIcon
        distance = 15
        if abs(event.x - self.__startX) > distance or abs(event.y - self.__startY) > distance:
            self.canvas.unbind("<B1-Motion>")
            self.canvas.bind("<B1-Motion>", self.dragIcon)

    def dragIcon(self, event):
        #Check if the popup exists. If it does move it to the mouse position
        if self.__popup:
            self.__popup.geometry(f"+{event.x_root}+{event.y_root}")
        else:
            #Create the popup which is a borderless transparent TopLevel window containing the image
            self.__popup = tk.Toplevel()
            self.__popup.overrideredirect(True)
            self.__popup.geometry(f"{self.canvasWidth}x{self.canvasHeight}+{event.x_root}+{event.y_root}")
            self.__popup.attributes("-transparentcolor", "white")
            self.__popup.attributes("-topmost", True)
            self.__popup.wm_attributes("-alpha", 0.8)

            #Create the canvas in the popup
            self.__popupCanvas = tk.Canvas(self.__popup, width=self.canvasWidth, height=self.canvasHeight)
            self.__popupCanvas.pack()
            self.__popupImage = ImageTk.PhotoImage(self.__imagePIL)
            self.__popupCanvas.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.__popupImage)

            #Bind the popup to the mouse
            self.__popup.bind("<B1-Motion>", self.dragIcon)
            self.canvas.bind("<ButtonRelease-1>", self.dropIcon)

    def dropIcon(self, event):
        print(f"Dropped at {event.x}, {event.y}")
        self.__popup.destroy()
        self.__popup = None
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
            x = self.linkedReel.winfo_rootx()
            y = self.linkedReel.winfo_rooty()
            w = self.linkedReel.winfo_width()
            h = self.linkedReel.winfo_height()
            if event.x_root > x and event.x_root < x+w and event.y_root > y and event.y_root < y+h:
                # print(f"Adding {self.imagepath} to the slideshow")
                self.linkedReel.addSlide(self.imagepath)
            return
        
#Extend FileIcon to make SlideIcon
class SlideIcon(FileIcon):
    def __init__(self, master, imgPath: str, **kwargs):
        super().__init__(master, imgPath, **kwargs)
        self.slide: FP.Slide = FP.Slide(imgPath)

    def setSlide(self, slide: FP.Slide):
        self.slide = slide
        return


class SlideReel(tk.Frame):
    def __init__(self, master, slideshow: FP.Slideshow, **kwargs):
        super().__init__(master, **kwargs)
        self.addStack = []
        self.slideshow: FP.Slideshow = slideshow
        self.previewer: ImageViewer = None  
        self.slides: list[FP.Slide] = self.slideshow.getSlides()

        #Horizontal Scrollable Frame
        self.scrollFrame = ScrollableFrame(self)
        self.scrollFrame.pack(expand=True, fill="both")

        #bind a configure event to the canvas
        self.__after_id = None
        self.bind("<Configure>", self.afterEvent)

    def afterEvent(self, event):
        if self.__after_id:
            self.after_cancel(self.__after_id)
        self.__after_id = self.after(33, self.fillReel)


    def loadProject(self, project: FP.Slideshow):
        self.slideshow = project
        self.slides = project.getSlides()
        self.fillReel()
        return
    
    def linkPreviewer(self, previewer: ImageViewer):
        self.previewer = previewer
        return
    
    #fillReel just takes the slides and puts them in the scrollable frame IN ORDER
    def fillReel(self):
        # print("Filling the reel with these")
        # print(self.slideshow.printSlides())

        #First of all pack forget everything in the scrollable frame
        for slide in self.scrollFrame.scrollable_frame.winfo_children():
            slide.pack_forget()

        for slide in self.slides:
            try:
                imgPath = slide["imagePath"]
            except:
                imgPath = slide.imagePath
            # print(imgPath)
            slideIcon = SlideIcon(self.scrollFrame.scrollable_frame, imgPath)
            slideIcon.linkedViewer = self.previewer
            slideIcon.linkedReel = self
            slideIcon.pack(side="left", padx=3, pady=3)

        
    #Need these:
    #Add slide
    #Remove slide

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


class MediaBucket(tk.Frame):
    def __init__(self, master, slideshow: FP.Slideshow="New Project", **kwargs):
        super().__init__(master, **kwargs)
        self.files: list[str] = []
        self.icons: list[FileIcon] = []
        #Keeps track of files added to the bucket. Used for undoing.
        self.addStack = []
        self.previewer: ImageViewer = None
        self.reel: SlideReel = None
        self.project: FP.Slideshow = slideshow
        self.loadProject(slideshow)

        #Label for the project
        self.projectLabel = tb.Label(self, text=self.project.name, font=("Arial", 16), background="white")
        self.projectLabel.pack()

        #Frame for the icons
        self.iconFrame = ScrolledFrame(self, autohide=True)
        self.iconFrame.pack(expand=True, fill="both")

        #FileIcons are 100x130
        self.columnCount: int = 0

        self.__resizeAfter = None
        self.bind("<Configure>", self.resizeBucket)
    
    def resizeBucket(self, event):
        if self.__resizeAfter:
            self.after_cancel(self.__resizeAfter)
        self.__resizeAfter = self.after(33, self.fillBucket)

    def linkPreviewer(self, previewer: ImageViewer):
        self.previewer = previewer
        return
    
    def linkReel(self, reel: SlideReel):
        self.reel = reel
        return

    def removeDuplicates(self):
        self.files = list(dict.fromkeys(self.files))
        return

    def fillBucket(self):
        # print("Filling Bucket")

        #Remove duplicates
        self.removeDuplicates()

        self.update()
        #find the number of columns
        width = self.winfo_width()
        #Only even attempt to fill the bucket if the width is greater than like 10. If it's less than 10 the window probably doesn't exist yet.
        if width < 10:
            print("Width too small")
            print("\n")
            return

        #Icons should be 100 wide with 3 pixels of padding on each side
        columnCount = width // 106
        filecount = len(self.files)

        #If the column count is the same as before, don't do anything
        if columnCount == self.columnCount and len(self.icons) == filecount:
            return
        self.columnCount = columnCount

        print(f"Column Count: {self.columnCount}")
        print(f"Width: {width}")
        
        for icon in self.iconFrame.winfo_children():
            icon.destroy()

        i=0
        j=0
        for file in self.files:
            icon = FileIcon(self.iconFrame, file)
            icon.linkedViewer = self.previewer
            icon.linkedReel = self.reel
            icon.grid(row=i, column=j, padx=3, pady=3)
            self.icons.append(icon)
            j += 1
            if j >= self.columnCount:
                j = 0
                i += 1
        print("\n")
        return
          
    def loadProject(self, project: FP.Slideshow):
        self.files = project.filesInProject
        self.fillBucket()
        return

    def addFile(self, file):
        files = []
        #Sometimes the input is a string or like a tuple. This is to catch that.
        if type(file) == str:
            print(f"Adding {file} to the bucket")
            self.files.append(file)
            files.append(file)
        elif type(file) == tuple:
            print(f"Adding tuple {file} to the bucket")
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
        self.files.remove(file)
        self.fillBucket()
        return
    



    

















        

















    








        





        


        