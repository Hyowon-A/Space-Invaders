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
  global direction
  direction = "left"
  bg_canvas.itemconfig(squirrel, image=squirrelL)
  move()

def rightPressed(event):
  global direction
  direction = "right"
  bg_canvas.itemconfig(squirrel, image=squirrelR)
  move()

def move():
  global direction
  if direction == "left":
    bg_canvas.move(squirrel, -10, 0)
  elif direction == "right":
    bg_canvas.move(squirrel, 10, 0) 

def createAcorn(event):
  squirrelPos = bg_canvas.coords(squirrel)
  global acorn
  if moving == False:
    acorn = bg_canvas.create_image(int(squirrelPos[0]), int(squirrelPos[1]), image=acornImg, anchor="nw")
    moveAcorn()
  if moving == True:
    bg_canvas.moveto(acorn, int(squirrelPos[0]), int(squirrelPos[1]))
    moveAcorn()

def moveAcorn():
  global moving
  moving = True
  bg_canvas.move(acorn, 0, -5)
  window.after(75, moveAcorn)  

# WORKING ON THIS: When acorn and emeny are overlapped, both should be deleted from canvas
def overlap():
  acornPos = bg_canvas.coords(acorn)
  for i in range(8):
    eaglePos = bg_canvas.coords(eagle[i])
    if overlap(acornPos, eaglePos):
      bg_canvas.delete(eagle[i])

def overlapping(a, b):
  if a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]:
    return True
  return False


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
squirrelR = ImageTk.PhotoImage(squirrelR)
squirrelL = Image.open("squirrelL.png")
squirrelL= squirrelL.resize((120, 75))
squirrelL = ImageTk.PhotoImage(squirrelL)
squirrel = bg_canvas.create_image(350, 600, image=squirrelL, anchor="nw")

# Make squirrel move
bg_canvas.bind('<Left>', leftPressed)
bg_canvas.bind('<Right>', rightPressed)
# Make squirrel throw an acorn
bg_canvas.bind('<space>', createAcorn)
bg_canvas.focus_set()
direction = ""

# Add acorn image
acornImg = Image.open("acorn.png")
acornImg = acornImg.resize((50, 30))
acornImg = ImageTk.PhotoImage(acornImg)

# Add enemies
eagle = Image.open("eagle.png")
eagle = eagle.resize((75, 75))
eagle = ImageTk.PhotoImage(eagle)
ems = []
for i in range(1, 9, 1):
  ems.append(bg_canvas.create_image(i * 75, 200, image=eagle, anchor="nw"))

moving = False

window.mainloop()
