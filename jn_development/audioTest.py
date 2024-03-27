import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
import customtkinter as ctk
from mutagen.mp3 import MP3
from mutagen.aiff import AIFF
from mutagen.wave import WAVE
import threading
import pygame
import time
import os

from PIL import Image, ImageDraw, ImageTk

# Initialize pygame mixer
pygame.mixer.init()

# Store the current position of the music
current_position = 0
paused = False
selected_folder_path = "" # Store the selected folder path



def draw_image(draw:ImageDraw, img, dest_rect, source_rect):
    draw.rectangle(dest_rect, fill=None, outline=None)
    cropped_img = img.crop(source_rect)
    startImg.paste(cropped_img, dest_rect[:2], mask=cropped_img.convert("RGBA").split()[3])
    return cropped_img

def update_image():
    draw = ImageDraw.Draw(startImg)
    dest_rect = (0, 0, 300, 300)
    source_rect = (0, 0, 300, 300)
    draw_image(draw, endImg, dest_rect, source_rect)

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image  # Keep a reference to prevent garbage collection

def defaultImg():
    startImg = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\ball300.jpg")
    endImg = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\ballOrange300.jpg")

    draw = ImageDraw.Draw(endImg)
    dest_rect = (0, 0, 1000, 1000)
    source_rect = (0, 0, 1000, 1000)
    draw_image(draw, startImg, dest_rect, source_rect)

dest_rect = (0, 0, 300, 300)
def update_image2(iteration):
    global dest_rect
    
    source_rect = (0, 0, 300, 300)
    draw = ImageDraw.Draw(startImg)
    draw_image(draw, endImg, dest_rect, source_rect)

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image  # Keep a reference to prevent garbage collection

    # Increase rectangle size for the next iteration
    dest_rect = (dest_rect[0] - 10, dest_rect[1] - 10, dest_rect[2] + 10, dest_rect[3] + 10)

    if iteration < 9:
        # Schedule the next update after 1000ms (1 second)
        window.after(1000, update_image2, iteration+1)
    else:
        print('done')
        #window.after(1000, window.quit)

def transition():
    global transitionDone
    imgWidth, imgHeight = endImg.size
    incY = 10
    #(int)(imgHeight/(speedDur*1000.0))
    if (incY<1.0):
        incY = 1
    print(imgHeight, incY)
    
    #window.after(dur*1000, wipeDown, 0, 100, incY, imgWidth)
    crossFade(0, 100, incY, imgWidth)

        
def wipeDown(i, max, incY, width):
    draw = ImageDraw.Draw(startImg)
    dest_rect = (0, 0, width, (i*incY)+incY)
    source_rect = (0, 0, width, (i*incY)+incY)
    draw_image(draw, endImg, dest_rect, source_rect)

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image
    if i < max:
        # Schedule the next update after 1000ms (1 second)
        window.after(1, wipeDown, i+1, max, incY, width)
    else:
        print('done')
        transitionDone = True
        #window.after(100, )

def wipeUp(i, max, incY, width):
    draw = ImageDraw.Draw(startImg)
    dest_rect = (0, 1000-(i*incY), width, 1000)
    source_rect = (0, 1000-(i*incY), width, 1000)
    draw_image(draw, endImg, dest_rect, source_rect)

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image
    if i < max:
        # Schedule the next update after 1000ms (1 second)
        window.after(1, wipeUp, i+1, max, incY, width)
    else:
        print('done')
        transitionDone = True
        #window.after(100, )

def wipeLeft(i, max, incY, width):
    draw = ImageDraw.Draw(startImg)
    dest_rect = (0, 0, (i*incY), 1000)
    source_rect = (0, 0, (i*incY), 1000)
    draw_image(draw, endImg, dest_rect, source_rect)

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image
    if i < max:
        # Schedule the next update after 1000ms (1 second)
        window.after(1, wipeLeft, i+1, max, incY, width)
    else:
        print('done')
        transitionDone = True
        #window.after(100, )

def wipeRight(i, max, incY, width):
    draw = ImageDraw.Draw(startImg)
    dest_rect = (width-(i*incY), 0, width, 1000)
    source_rect = (width-(i*incY), 0, width, 1000)
    draw_image(draw, endImg, dest_rect, source_rect)

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image
    if i < max:
        # Schedule the next update after 1000ms (1 second)
        window.after(1, wipeRight, i+1, max, incY, width)
    else:
        print('done')
        transitionDone = True
        #window.after(100, )

def pushRight(i, max, incY, width):
    startImg2 = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ball.jpg")
    draw = ImageDraw.Draw(startImg)
    dest_rect = ((incY*i), 0, width, width)
    source_rect = (0, 0, width-(i*incY), width)
    draw_image(draw, startImg2, dest_rect, source_rect)
    dest_rect2 = (0, 0, (incY*i), width)
    source_rect2 = (width-(i*incY), 0, width, width)
    draw_image(draw, endImg, dest_rect2, source_rect2)

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image
    if i < max-1:
        # Schedule the next update after 1000ms (1 second)
        window.after(10, pushRight, i+1, max, incY, width)
    else:
        print('done')
        tk_image = ImageTk.PhotoImage(endImg)
        label.config(image=tk_image)
        label.image = tk_image
        #window.after(100, )

def pushLeft(i, max, incY, width):
    startImg2 = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ball.jpg")
    draw = ImageDraw.Draw(startImg)
    
    dest_rect = (0, 0, width-(i*incY), width)
    source_rect = ((incY*i), 0, width, width)
    draw_image(draw, startImg2, dest_rect, source_rect)
    dest_rect2 = (width-(i*incY), 0, width, width)
    source_rect2 = (0, 0, (incY*i), width)
    draw_image(draw, endImg, dest_rect2, source_rect2)

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image
    if i < max-1:
        # Schedule the next update after 1000ms (1 second)
        window.after(10, pushLeft, i+1, max, incY, width)
    else:
        print('done')
        tk_image = ImageTk.PhotoImage(endImg)
        label.config(image=tk_image)
        label.image = tk_image
        #window.after(100, )

def pushUp(i, max, incY, width):
    startImg2 = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ball.jpg")
    draw = ImageDraw.Draw(startImg)
    #sAY1 =  incY;         dAY2 = imgHeight - incY; // bottom Y of rectangle to move upward in A
    #sBY2 = incY;          dBY1
    #0, 0, imgWidth, dAY2, 0, sAY1, imgWidth, imgHeight
    dest_rect = (0, 0, width, width-(i*incY))
    source_rect = (0, (incY*i), width, width)
    draw_image(draw, startImg2, dest_rect, source_rect)
    #0, dAY2, imgWidth, imgHeight, 0, 0, imgWidth, sBY2
    dest_rect2 = (0, width-(i*incY), width, width)
    source_rect2 = (0, 0, width, (i*incY))
    draw_image(draw, endImg, dest_rect2, source_rect2)

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image
    if i < max-1:
        # Schedule the next update after 1000ms (1 second)
        window.after(10, pushUp, i+1, max, incY, width)
    else:
        print('done')
        tk_image = ImageTk.PhotoImage(endImg)
        label.config(image=tk_image)
        label.image = tk_image

def pushDown(i, max, incY, width):
    startImg2 = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ball.jpg")
    draw = ImageDraw.Draw(startImg)
    #sAY2 = imgHeight - incY;          dAY1 = incY;
    #dBY2 = incY;        sBY1 = imgHeight - incY;
    #0, dAY1, imgWidth, imgHeight, 0, 0, imgWidth, sAY2
    dest_rect = (0, (incY*i), width, width)
    source_rect = (0, 0, width, width-(i*incY))
    draw_image(draw, startImg2, dest_rect, source_rect)
    #0, 0, imgWidth, dBY2, 0, sBY1, imgWidth, imgHeight
    dest_rect2 = (0, 0, width, (i*incY))
    source_rect2 = (0, width-(i*incY), width, width)
    draw_image(draw, endImg, dest_rect2, source_rect2)

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image
    if i < max-1:
        # Schedule the next update after 1000ms (1 second)
        window.after(10, pushDown, i+1, max, incY, width)
    else:
        print('done')
        tk_image = ImageTk.PhotoImage(endImg)
        label.config(image=tk_image)
        label.image = tk_image

def crossFade(i, max, incY, width):
    # = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ball.jpg")
    startImg.putalpha(255-(int)(i*255/max))
    endImg.putalpha((int)(i*255/max))
    draw = ImageDraw.Draw(startImg)
    dest_rect = (0, 0, width, width)
    startImg.paste(endImg, dest_rect[:2], mask=endImg.convert("RGBA").split()[3])

    tk_image = ImageTk.PhotoImage(startImg)
    label.config(image=tk_image)
    label.image = tk_image
    if i < max-1:
        # Schedule the next update after 1000ms (1 second)
        window.after(10, crossFade, i+1, max, incY, width)
    else:
        print('done')
        tk_image = ImageTk.PhotoImage(endImg)
        label.config(image=tk_image)
        label.image = tk_image



def update_progress():
    global current_position
    while True:
        if pygame.mixer.music.get_busy() and not paused:
            current_position = pygame.mixer.music.get_pos() / 1000
            pbar["value"] = current_position

            # Check if the current song has reached its maximum duration
            if current_position >= pbar["maximum"]:
                stop_music() # Stop the music playback
                pbar["value"] = 0 # Reset the pbar
            
            window.update()
        time.sleep(0.1)

# Create a thread to update the progress bar
pt = threading.Thread(target=update_progress)
pt.daemon = True
pt.start()

def select_music_folder():
    global selected_folder_path
    selected_folder_path = filedialog.askdirectory()
    if selected_folder_path:
        lbox.delete(0, tk.END)
        for filename in os.listdir(selected_folder_path):
            if filename.endswith(".aiff") or filename.endswith(".wav"):
                lbox.insert(tk.END, filename) # Insert only the filename, not the full path

def previous_song():
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        if current_index > 0:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(current_index - 1)
            play_selected_song()

def next_song():
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        if current_index < lbox.size() - 1:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(current_index + 1)
            play_selected_song()


def play_music():
    global paused
    if paused:
        # If the music is paused, unpause it
        pygame.mixer.music.unpause()
        paused = False
    else:
        # If the music is not paused, play the selected song
        play_selected_song()

def play_selected_song():
    global current_position, paused
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        selected_song = lbox.get(current_index)
        full_path = os.path.join(selected_folder_path, selected_song) # Add the full path again
        pygame.mixer.music.load(full_path) # Load the selected song
        pygame.mixer.music.play(start=current_position) # Play the song from the current position
        paused = False
        audio = None
        if selected_song.endswith(".aiff"):
            audio = AIFF(full_path)
        elif selected_song.endswith(".wav"):
            audio = WAVE(full_path)
        song_duration = audio.info.length
        pbar["maximum"] = song_duration # Set the maximum value of the pbar  to the song duration

def pause_music():
    global paused
    # Pause the currently playing music
    pygame.mixer.music.pause()
    paused = True

def stop_music():
    global paused
    # Stop the currently playing music and reset the progress bar
    pygame.mixer.music.stop()
    paused = False

# Create the main window
window = tk.Tk()
window.title("Music Player App")
window.geometry("600x900")

startImg = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\ball300.jpg")
endImg = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\ballOrange300.jpg")

label = tk.Label(window)
label.pack()

tk_image = ImageTk.PhotoImage(startImg)
label.config(image=tk_image)
label.image = tk_image

update_image_button = tk.Button(window, text="Update Image", command=transition)
update_image_button.pack()

# Create a label for the music player title
l_music_player = tk.Label(window, text="Music Player", font=("TkDefaultFont", 30, "bold"))
l_music_player.pack(pady=10)

# Create a button to select the music folder
btn_select_folder = ctk.CTkButton(window, text="Select Music Folder",
                                  command=select_music_folder,
                                  font=("TkDefaultFont", 18))
btn_select_folder.pack(pady=20)

# Create a listbox to display the available songs
lbox = tk.Listbox(window, width=50, font=("TkDefaultFont", 16))
lbox.pack(pady=10)

# Create a frame to hold the control buttons
btn_frame = tk.Frame(window)
btn_frame.pack(pady=20)

# Create a button to go to the previous song
btn_previous = ctk.CTkButton(btn_frame, text="<", command=previous_song,
                            width=50, font=("TkDefaultFont", 18))
btn_previous.pack(side=tk.LEFT, padx=5)

# Create a button to play the music
btn_play = ctk.CTkButton(btn_frame, text="Play", command=play_music, width=50,
                         font=("TkDefaultFont", 18))
btn_play.pack(side=tk.LEFT, padx=5)

# Create a button to pause the music
btn_pause = ctk.CTkButton(btn_frame, text="Pause", command=pause_music, width=50,
                          font=("TkDefaultFont", 18))
btn_pause.pack(side=tk.LEFT, padx=5)

# Create a button to go to the next song
btn_next = ctk.CTkButton(btn_frame, text=">", command=next_song, width=50,
                         font=("TkDefaultFont", 18))
btn_next.pack(side=tk.LEFT, padx=5)

# Create a progress bar to indicate the current song's progress
pbar = Progressbar(window, length=300, mode="determinate")
pbar.pack(pady=10)







window.mainloop()