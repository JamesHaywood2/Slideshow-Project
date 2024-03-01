import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import time

transitionDone = False
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
    startImg = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ball.jpg")
    endImg = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ballOrange.jpg")

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
        root.after(1000, update_image2, iteration+1)
    else:
        print('done')
        #root.after(1000, root.quit)

def transition():
    global transitionDone
    imgWidth, imgHeight = endImg.size
    
    dur = (int)(inputtxt.get(1.0, "end-1c"))
    speedDur = (int)(input2txt.get(1.0, "end-1c"))
    choice = (int)(input3txt.get(1.0, "end-1c"))
    incY = 10
    #(int)(imgHeight/(speedDur*1000.0))
    if (incY<1.0):
        incY = 1
    print(imgHeight, incY)
    if choice == 1:
        root.after(dur*1000, wipeRight, 0, 100, incY, imgWidth)
    if choice == 2:
        root.after(dur*1000, wipeLeft, 0, 100, incY, imgWidth)
    if choice == 3:
        root.after(dur*1000, wipeUp, 0, 100, incY, imgWidth)
    if choice == 4:
        root.after(dur*1000, wipeDown, 0, 100, incY, imgWidth)

        
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
        root.after(1, wipeDown, i+1, max, incY, width)
    else:
        print('done')
        transitionDone = True
        #root.after(100, )

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
        root.after(1, wipeUp, i+1, max, incY, width)
    else:
        print('done')
        transitionDone = True
        #root.after(100, )

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
        root.after(1, wipeLeft, i+1, max, incY, width)
    else:
        print('done')
        transitionDone = True
        #root.after(100, )

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
        root.after(1, wipeRight, i+1, max, incY, width)
    else:
        print('done')
        transitionDone = True
        #root.after(100, )

root = tk.Tk()
root.title("Tkinter Window with ImageDraw")

startImg = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ball.jpg")
endImg = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ballOrange.jpg")

l = tk.Label(root, text = "Duration")
l.config(font =("Courier", 12))
l.pack()
inputtxt = tk.Text(root, name = "slideDur", height = 1, width = 10)
inputtxt.pack()

l2 = tk.Label(root, text = "Speed")
l2.config(font =("Courier", 12))
l2.pack()
input2txt = tk.Text(root, name = "transitionSpeed", height = 1, width = 10)
input2txt.pack()

l3 = tk.Label(root, text = "Choice (1-R, 2-L, 3-U, 4-D)")
l3.config(font =("Courier", 12))
l3.pack()
input3txt = tk.Text(root, name = "choice", height = 1, width = 10)
input3txt.pack()

label = tk.Label(root)
label.pack()

tk_image = ImageTk.PhotoImage(startImg)
label.config(image=tk_image)
label.image = tk_image

update_image_button = tk.Button(root, text="Update Image", command=transition)
update_image_button.pack()



root.mainloop()



