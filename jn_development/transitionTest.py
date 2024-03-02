import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import time

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
    incY = 10
    #(int)(imgHeight/(speedDur*1000.0))
    if (incY<1.0):
        incY = 1
    print(imgHeight, incY)
    
    #root.after(dur*1000, wipeDown, 0, 100, incY, imgWidth)
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
        root.after(10, pushRight, i+1, max, incY, width)
    else:
        print('done')
        tk_image = ImageTk.PhotoImage(endImg)
        label.config(image=tk_image)
        label.image = tk_image
        #root.after(100, )

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
        root.after(10, pushLeft, i+1, max, incY, width)
    else:
        print('done')
        tk_image = ImageTk.PhotoImage(endImg)
        label.config(image=tk_image)
        label.image = tk_image
        #root.after(100, )

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
        root.after(10, pushUp, i+1, max, incY, width)
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
        root.after(10, pushDown, i+1, max, incY, width)
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
        root.after(10, crossFade, i+1, max, incY, width)
    else:
        print('done')
        tk_image = ImageTk.PhotoImage(endImg)
        label.config(image=tk_image)
        label.image = tk_image

root = tk.Tk()
root.title("Tkinter Window with ImageDraw")

startImg = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ball.jpg")
endImg = Image.open(r"C:\Users\JKMJKM\Documents\uah\spring2024\CS499\test\proto\Creator\ballOrange.jpg")

label = tk.Label(root)
label.pack()

tk_image = ImageTk.PhotoImage(startImg)
label.config(image=tk_image)
label.image = tk_image

update_image_button = tk.Button(root, text="Update Image", command=transition)
update_image_button.pack()



root.mainloop()



