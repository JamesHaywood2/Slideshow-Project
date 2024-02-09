import tkinter as tk
from PIL import Image, ImageTk
import FileSupport as FP
import os
from tkinter import filedialog
from tkinter import dnd


class PreviewImage:
    #PreviewImage is essentially a canvas that holds an image.
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, bg="black")
        #Should fill the parent as much as it can.
        self.canvas.pack(fill=tk.BOTH, expand=True)
        #Get the size of the canvas
        parent.update()
        self.canvasWidth = self.canvas.winfo_width()
        self.canvasHeight = self.canvas.winfo_height()

        #Initially there is no image.
        self.imagePath = None
        self.imagePIL = None
        self.image = None
        self.canvasImage = None

        #Label on the canvas that says the name of the image
        self.imageLabel = self.canvas.create_text(10, 10, anchor="nw", text="", font=("Arial", 16), fill="#FF1D8E")


    def loadImage(self, imagePath:str):
        #Clear the canvas
        self.canvas.delete("all")
        #Test if the file is a valid image file
        try:
            img = Image.open(imagePath)
            self.imagePath = imagePath
            self.imagePIL = img
            #Delete & replace old label
            self.imageLabel = self.canvas.create_text(10, 10, anchor="nw", text=FP.removeExtension(FP.removePath([self.imagePath]))[0], font=("Arial", 16), fill="#FF1D8E")
        except:
            # print(f"{imagePath} is not a valid image file.")
            self.imagePath = r"Creator\MissingImage.png"
            img = Image.open(self.imagePath)
            self.imagePIL = img

        #Resize the image while using the aspect ratio
        self.imagePIL.thumbnail((self.canvasWidth, self.canvasHeight))
        self.image = ImageTk.PhotoImage(self.imagePIL)
        self.canvasImage = self.canvas.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)


    def redrawImage(self):
        #Return early if there is no image
        if self.imagePath == None:
            return

        #Get the size of the canvas
        self.canvasWidth = self.canvas.winfo_width()
        self.canvasHeight = self.canvas.winfo_height()
        # print(f"Current Window Size: {event.width}x{event.height}")
        # print(f"Canvas Size: {self.canvasWidth}x{self.canvasHeight}")
        #Clear the canvas
        self.canvas.delete("all")
        #Resize the image while using the aspect ratio
        img = Image.open(self.imagePath)
        self.imagePIL = img
        self.imagePIL.thumbnail((self.canvasWidth, self.canvasHeight))
        self.image = ImageTk.PhotoImage(self.imagePIL)
        self.canvasImage = self.canvas.create_image(self.canvasWidth//2, self.canvasHeight//2, image=self.image)
        self.imageLabel = self.canvas.create_text(10, 10, anchor="nw", text=FP.removeExtension(FP.removePath([self.imagePath]))[0], font=("Arial", 16), fill="#FF1D8E")
        return

    def printCanvasSize(self):
        self.canvasWidth = self.canvas.winfo_width()
        self.canvasHeight = self.canvas.winfo_height()
        print(f"Canvas Size: {self.canvasWidth}x{self.canvasHeight}")



class FileViewer(tk.Frame):
    def __init__(self, parent, files:list=[]):
        tk.Frame.__init__(self, parent)
        self.imageList = files
        self.iconList: list[PhotoIcon] = []
        #if there are no files, put MissingImage.png in the list as a placeholder.
        if len(self.imageList) == 0:
            self.imageList.append(r"Creator\MissingImage.png")

        self.parent = parent #The parent of the FileViewer. media in GUA.py
        self.previewer = None #The previewer that the FileViewer is linked to. previewImage in GUI.py

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)

        #Add canvas to the frame
        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        #Add a scrollbar to the frame
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set) 

        self.fileContainer = tk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.fileContainer, anchor="nw")

        #Print the size of the canvas
        self.parent.update()
        # print(f"parent Size: {self.parent.winfo_width()}x{self.parent.winfo_height()}")
        self.parentHeight = self.parent.winfo_height()
        self.parentWidth = self.parent.winfo_width()

        self.propogateList()

        #Keep track of the previous file list so we can revert to it if needed.
        self.addStack = []

        

    


    def removeDuplicates(self):
        self.imageList = list(dict.fromkeys(self.imageList))
        return

    def propogateList(self):
        #If the file list has at least one file, remove the placeholder.
        if len(self.imageList) > 1 and self.imageList[0] == r"Creator\MissingImage.png":
            self.imageList.remove(r"Creator\MissingImage.png")
        #If the file list is empty, add the placeholder.
        if len(self.imageList) == 0:
            self.imageList.append(r"Creator\MissingImage.png")

        #Remove any duplicate items in the file list
        self.removeDuplicates()
        #Print imageList
        print(self.imageList)
        #Clear the file container
        for widget in self.fileContainer.winfo_children():
            widget.destroy()
        #Get the size of parent container
        self.parent.update()
        parentWidth = self.parent.winfo_width()
        parentHeight = self.parent.winfo_height()
        # print(f"Parent Size: {parentWidth}x{parentHeight}")

        #Icons are like 110 pixels wide. 
        iconPerRow = parentWidth//110
        # print(f"Icons per row: {iconPerRow}")
        i=0
        j=0
        for file in self.imageList:
            #Create a PhotoIcon and place it in the fileContainer
            icon = PhotoIcon(self.fileContainer, file).grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
            self.iconList.append(icon)
            j+=1
            if j == iconPerRow:
                j=0
                i+=1

        self.fileContainer.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        for icon in self.fileContainer.winfo_children():
            icon.linkPreviewer(self.previewer)
        return
        

    def addFile(self, file):
        #Add file to the addStack
        self.addStack.append(file)
        #Sometimes the input is a list, sometimes it's a string. This will make sure it's a list.
        if type(file) == str:
            self.imageList.append(file)
        elif type(file) == tuple:
            for f in file:
                self.imageList.append(f)
        else:
            raise TypeError(f"Expected string or list of strings. Got {type(file)}")
        self.propogateList()
        return
    
    def addFolder(self, folder):
        # print(f"Adding folder: {folder}")
        files = []
        if type(folder) == str:
            files = FP.getJPEG(folder, True)
        elif type(folder) == tuple:
            for f in folder:
                files.extend(FP.getJPEG(f, True))
        else:
            raise TypeError(f"Expected string or list of strings. Got {type(folder)}")  
        #Add files to the addStack
        self.addStack.append(files)
        # print(f"Files: {files}")
        self.imageList.extend(files)
        self.propogateList()
        return
    
    def revertList(self):
        #Pop the last item off the addStack and remove it from the imageList
        if len(self.addStack) > 0:
            last = self.addStack.pop()
            if type(last) == str:
                self.imageList.remove(last)
            else:
                for f in last:
                    self.imageList.remove(f)
        self.propogateList()
        return
    
    def removeFile(self, file:str):
        self.imageList.remove(file)
        self.propogateList()
        return
    
    def linkPreviewer(self, previewer):
        self.previewer = previewer
        for icon in self.fileContainer.winfo_children():
            icon.linkPreviewer(previewer)
        return


class PhotoIcon(tk.Frame):
    def __init__(self, parent, imagePath:str):
        tk.Frame.__init__(self, parent, relief=tk.FLAT, borderwidth=2)
        self.width = 100
        self.height = 100
        self.previewer = None
        self.parent = parent

        self.canvas = tk.Canvas(self, width=100, height=100)
        self.canvas.pack(fill=tk.NONE, expand=False, side=tk.TOP)
  
        self.fileName = FP.removeExtension(FP.removePath([imagePath]))[0]
        fn = self.fileName[:10] + "..." if len(self.fileName) > 10 else self.fileName
        self.nameLabel = tk.Label(self, text=fn, font=("Arial", 12))
        self.nameLabel.pack(fill=tk.NONE, expand=False)

        #Test if the file is a valid image file
        try:
            img = Image.open(imagePath)
            self.imagePath = imagePath
            self.imagePIL = img
        except:
            print(f"{imagePath} is not a valid image file.")
            self.imagePath = r"Creator\MissingImage.png"
            img = Image.open(self.imagePath)
            self.imagePIL = img
        # print(f"Image Path: {self.imagePath}")
        #Resize the image while using the aspect ratio
        self.imagePIL.thumbnail((self.width, self.height))
        self.image = ImageTk.PhotoImage(self.imagePIL)
        self.canvasImage = self.canvas.create_image(self.width//2, self.height//2, image=self.image, anchor=tk.CENTER)

        self.canvas.bind("<Double-Button-1>", self.openImage)

        self.canvas.bind("<Enter>", self.sinkIcon)
        self.canvas.bind("<Leave>", self.riseIcon)
        self.hover = False

        self.canvas.bind("<ButtonRelease-1>", self.selectIcon)

    
        self.canvas.bind("<Button-1>", self.pickup)
        self.startX = 0
        self.startY = 0
        self.popup = None #This is a borderless, transparent top level window that contains the image. It follows the mouse when the user drags the icon.


    def pickup(self, event):
        #Save the initial click location of the move
        print(f"Click: {event.x}, {event.y}")
        self.startX = event.x
        self.startY = event.y
        self.canvas.bind("<B1-Motion>", self.dragStart)

    def dragStart(self, event):
        #If the user has dragged the icon a certain distance, change the event to a drag event.
        if abs(event.x - self.startX) > 15 or abs(event.y - self.startY) > 15:
            print("Begin Dragging")
            self.canvas.unbind("<Button-1>")
            self.canvas.bind("<B1-Motion>", self.dragging)

    def dragging(self, event):
        #Check if the popup exists. If it does, move it to the new location.
        if self.popup:
            self.popup.geometry(f"+{event.x_root-50}+{event.y_root-50}")
        else:
            #Create the popup if it doesn't exist.
            self.popup = tk.Toplevel()
            self.popup.overrideredirect(True)
            self.popup.geometry(f"{self.width}x{self.height}+{event.x_root-50}+{event.y_root-50}")
            self.popup.wm_attributes("-transparentcolor", "white")
            self.popup.wm_attributes("-topmost", 1)
            self.popup.wm_attributes("-alpha", 0.8)
            self.popupCanvas = tk.Canvas(self.popup, width=self.width, height=self.height)
            self.popupCanvas.pack(fill=tk.BOTH, expand=True)
            self.popupImage = ImageTk.PhotoImage(self.imagePIL)
            self.popupCanvas.create_image(self.width//2, self.height//2, image=self.popupImage)
            self.popup.bind("<B1-Motion>", self.dragging)
            self.canvas.bind("<ButtonRelease-1>", self.drop)

    def drop(self, event):
        #Revert everything back to normal.
        print(f"Dropped at: {event.x}, {event.y}")
        self.popup.destroy()
        self.popup = None
        self.canvas.bind("<Button-1>", self.pickup)
        self.canvas.unbind("<B1-Motion>")
        self.canvas.bind("<ButtonRelease-1>", self.selectIcon)
        #Check if the user has dropped the icon on the previewer. If they have, load the image.
        if self.previewer:
            x = self.previewer.canvas.winfo_rootx()
            y = self.previewer.canvas.winfo_rooty()
            w = self.previewer.canvas.winfo_width()
            h = self.previewer.canvas.winfo_height()
            if event.x_root > x and event.x_root < x+w and event.y_root > y and event.y_root < y+h:
                self.previewer.loadImage(self.imagePath)
                self.previewer.redrawImage()
        return
        
        
    def sinkIcon(self, event):
        # print("Sinking")
        self.hover = True
        self.config(relief=tk.SUNKEN)

    def riseIcon(self, event):
        # print("Rising")
        self.hover = False
        self.config(relief=tk.FLAT)
        self.canvas.bind("<Leave>", self.riseIcon)

    def selectIcon(self, event):
        # print("Selecting")
        if self.hover:
            self.previewer.loadImage(self.imagePath)
            self.previewer.redrawImage()
            
    def openImage(self, event):
        os.startfile(self.imagePath)

    def linkPreviewer(self, previewer):
        self.previewer = previewer
        return
    

class SlideInfo(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)

        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas.create_text(10, 10, text="Slide Info", anchor="nw", font=("Arial", 16))
    

                


