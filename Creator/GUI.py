import tkinter as tk
import ImageSupport as IS



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
        self.base = tk.PanedWindow(self.root, orient=tk.VERTICAL, bd=5, sashwidth=8)
        self.base.pack(expand=True, fill="both")

        #Top PanedWindow that houses media bucket and preview. 
        self.top = tk.PanedWindow(self.base, orient=tk.HORIZONTAL, bd=5, sashwidth=8)
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
        # self.root.update()
        self.win_width = self.root.winfo_width()
        self.win_height = self.root.winfo_height()

        self.__sizeConfig()

        #Bind the resize event to the on_resize function
        self.root.bind("<Configure>", self.on_resize)
        self.root.mainloop()

    #Right now it just prints the size of the window. Updates whenever anything is resized including the PanedWindows.
    def on_resize(self, event):
        self.win_width = self.root.winfo_width()
        self.win_height = self.root.winfo_height()


        #This is to prevetn an infinite loop of resizing. pane.configure() ends up triggering the on_resize event, which triggers the pane.configure() event, etc.
        #This snippet of code will only run if the window itself has changed size, not any of the PanedWindows.
        if (self.win_width == event.width) and (self.win_height == event.height):
            # print(f"Current Window Size: {event.width}x{event.height}")
            self.__sizeConfig()

            return


        return
    
    def __sizeConfig(self):
        #Top PanedWindow should take up 2/3 of the window
        self.base.paneconfigure(self.top, height=self.win_height//3*2, minsize=self.win_height//3)

        #Bottom frame should take up 1/3 of the window
        self.base.paneconfigure(self.reel, height=self.win_height//3, minsize=self.win_height//4)

        #Media bucket should take up 1/3 of the top PanedWindow
        self.top.paneconfigure(self.media, width=self.win_width//3, minsize=self.win_width//4)

        #Preview should take up 2/3 of the top PanedWindow
        self.top.paneconfigure(self.preview, width=self.win_width//3*2, minsize=self.win_width//3)
        return





#Create the window
root = tk.Tk()
app = Window(root)
