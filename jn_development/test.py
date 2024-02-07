import tkinter as tk
from tkinter import filedialog
import json

def open_slideshow_window(json_file):
    # Disable the button
    button.config(state=tk.DISABLED)

    new_window = tk.Toplevel(root)
    new_window.title("Slide Show")
    
    # Get the screen width and height
    screen_width = new_window.winfo_screenwidth()
    screen_height = new_window.winfo_screenheight()

    # Set the size of the window to the screen size
    new_window.geometry(f"{screen_width}x{screen_height}")

    # Read and display the content of the selected JSON file
    with open(json_file, 'r') as file:
        json_content = json.load(file)

    label = tk.Label(new_window, text=f"Content of {json_file}:\n{json_content}")
    label.pack()

    # Bind the window closing event to re-enable the button
    new_window.protocol("WM_DELETE_WINDOW", lambda: on_close(new_window))


def on_close(window):
    # Re-enable the button when the fullscreen window is closed
    button.config(state=tk.NORMAL)
    window.destroy()

def choose_json_file():
    json_file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if json_file:
        open_slideshow_window(json_file)

# Create the main window
root = tk.Tk()
root.title("Slide Show Creator")
label_root = tk.Label(root, text="Create a slide show using images")
label_root.pack()

# Create a button to open a fullscreen window
button = tk.Button(root, text="Start Slide Show", command=open_slideshow_window)
button.pack()

# Create a button to open a fullscreen window with selected JSON file
button = tk.Button(root, text="Choose JSON File", command=choose_json_file)
button.pack()

# Run the Tkinter event loop
root.mainloop()