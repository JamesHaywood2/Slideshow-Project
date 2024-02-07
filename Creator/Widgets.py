import tkinter as tk
from PIL import Image, ImageTk
import ImageSupport as IS



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



    def loadImage(self, imagePath:str):
        #Clear the canvas
        self.canvas.delete("all")
        #Test if the file is a valid image file
        try:
            img = Image.open(imagePath)
            self.imagePath = imagePath
            self.imagePIL = img
        except:
            print(f"{imagePath} is not a valid image file.")
            self.imagePath = r"Slideshow-Project\MissingImage.png"
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
        return

    def printCanvasSize(self):
        self.canvasWidth = self.canvas.winfo_width()
        self.canvasHeight = self.canvas.winfo_height()
        print(f"Canvas Size: {self.canvasWidth}x{self.canvasHeight}")




# Create the root window for testing
# root = tk.Tk()
# root.title("Test window")
# screen_width = root.winfo_screenwidth()
# screen_height = root.winfo_screenheight()
# root.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
# print(f"{screen_width//2}x{screen_height//2}")


# #Create the preview image
# pi = PreviewImage(root)
# pi.loadImage(r"Slideshow-Project\ball.jpg")



# root.mainloop()