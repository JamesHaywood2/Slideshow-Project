import tkinter as tk
import ImageSupport as IS
from Widgets import PreviewImage



#Create the root window
class Window:
    def __init__(self, root):
        self.root = root
        self.root.title("Resizable Window")
        #Get the size of the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        #Should make the window half the size of the screen and centered
        self.root.geometry(f"{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//4}")
        
        #Base PanedWindow that holds everything. Takes up the whole window and should always be the same size as the window
        self.base = tk.PanedWindow(self.root, orient=tk.VERTICAL, bd=1, sashwidth=10)
        self.base.pack(expand=True, fill="both")

        #Top PanedWindow that houses media bucket and preview. 
        self.top = tk.PanedWindow(self.base, orient=tk.HORIZONTAL, bd=1, sashwidth=10)
        self.base.add(self.top)

        #Bottom frame that takes up 1/3 of the window
        self.reel = tk.Frame(self.base, bg="green")
        self.base.add(self.reel)

        #Create left and right labels for the top paned window
        self.media = tk.Frame(self.top, bg="yellow")
        self.top.add(self.media)
        self.preview = tk.Frame(self.top, bg="pink")
        self.top.add(self.preview)
        
        #Get the size of the window
        self.root.update()
        self.win_width = self.root.winfo_width()
        self.win_height = self.root.winfo_height()

        #Sets the initial size of the PanedWindows
        self.__sizeConfig()

        #Add an ImagePreview to the preview frame
        self.previewImage = PreviewImage(self.preview)
        self.previewImage.loadImage(r"Slideshow-Project\ball.jpg")
        

        #DEBUG STUFF REMOVE LATER
        printCanvasSize = tk.Button(self.reel, text="Print Canvas Size", command=self.previewImage.printCanvasSize)
        printCanvasSize.pack()
        redrawImage = tk.Button(self.reel, text="Redraw Image", command=self.previewImage.redrawImage)
        redrawImage.pack()
        #DEBUG STUFF REMOVE LATER

        #Get the position of the window
        self.win_xPos = self.root.winfo_x()
        self.win_yPos = self.root.winfo_y()

        #resize after call variable.
        self.resize_after = None


        #Bind the resize event to the on_resize function
        self.root.bind("<Configure>", self.on_resize)
        self.root.mainloop()

    #Debounce function. On_resize() gets called every <configure> event and creates a new after event.
    #If it gets called again, the after event gets cancelled and a new one is created.
    #If it doesn't it then calls the resize function.
    #This prevents the resize function from being spam and causing lag.
    def on_resize(self, event):
        if self.resize_after:
            self.root.after_cancel(self.resize_after)
        self.resize_after = self.root.after(50, self.resize, event)
        
    def resize(self, event):
        print("Resizing")
        self.win_width = self.root.winfo_width()
        self.win_height = self.root.winfo_height()

        
        #This is to prevetn an infinite loop of resizing. pane.configure() ends up triggering the on_resize event, which triggers the pane.configure() event, etc.
        #This snippet of code will only run if the window itself has changed size, not any of the PanedWindows.
        if (self.win_width == event.width) and (self.win_height == event.height):
            # print(f"Current Window Size: {event.width}x{event.height}")
            self.__sizeConfig()
            # print(f"Window Size: {self.win_width}x{self.win_height}")

        #If canvas size has changed, redraw the image
        if self.previewImage.canvas.winfo_width() != self.previewImage.canvasWidth or self.previewImage.canvas.winfo_height() != self.previewImage.canvasHeight:
            self.previewImage.redrawImage()
                
        return

    
    def __sizeConfig(self):
        #Top PanedWindow should take up 2/3 of the window
        self.base.paneconfigure(self.top, height=self.win_height//3*2, minsize=self.win_height//3)

        #Bottom frame should take up 1/3 of the window
        self.base.paneconfigure(self.reel, height=self.win_height//3, minsize=self.win_height//4)

        #Preview should take up 2/3 of the top PanedWindow
        self.top.paneconfigure(self.preview, width=self.win_width//3*2, minsize=self.win_width//3)

        #Media bucket should take up 1/3 of the top PanedWindow
        self.top.paneconfigure(self.media, width=self.win_width//3, minsize=self.win_width//4)
        return





#Create the window
root = tk.Tk()
app = Window(root)
