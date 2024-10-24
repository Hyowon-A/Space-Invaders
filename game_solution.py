# Space Invaders 

from tkinter import Tk, Canvas, PhotoImage, Label
import random
from PIL import ImageTk, Image

def createWindow():
  window = Tk()
  window.title("Space Invaders")
  window.geometry("750x750")
  
  return window

def leftPressed(event):
  squirrel = bg_canvas.itemconfig(img=squirrelImgs[1])
  bg_canvas.move(squirrel, -50, 0)

def rightPressed(event):
  squirrel = bg_canvas.itemconfig(img=squirrelImgs[0])
  bg_canvas.move(squirrel, 50, 0) 

# Create a game window
window = createWindow()

# Add background image
bg = Image.open("bg.jpg")
bg = bg.resize((750, 750))
bg = ImageTk.PhotoImage(bg)
bg_canvas = Canvas(window, width=500, height=500)
bg_canvas.pack(fill="both", expand=True)
bg_canvas.create_image(0, 0, image=bg, anchor="nw")

# Add squirrel images
squirrelR = Image.open("squirrelR.png")
squirrelR= squirrelR.resize((120, 75))
squirrelL = Image.open("squirrelL.png")
squirrelL= squirrelR.resize((120, 75))
squirrelImgs = []
squirrelImgs.append(ImageTk.PhotoImage(squirrelR))
squirrelImgs.append(ImageTk.PhotoImage(squirrelL))
squirrel = bg_canvas.create_image(350, 500, image=squirrelImgs[0], anchor="nw")

# Make squirrel move / WORKING ON THIS!!!
bg_canvas.bind('<Left>', leftPressed)
bg_canvas.bind('<Right>', rightPressed)
bg_canvas.focus_set()
direction = ""

window.mainloop()
