# Space Invaders 

from tkinter import Tk, Canvas, PhotoImage, Label
import random
from PIL import ImageTk, Image

class constants:
    width = 750
    height = 900
    life = 3
    alinePerLine = 8

class game_objects:
    def __init__(self, canvas, obj):
        self.canvas = canvas
        self.obj = obj

    ##Return Position
    def get_position(self):
        return self.canvas.coords(self.obj)

    def move_to(self, x, y):
        self.canvas.move(self.obj, x, y)

    def delete(self):
        self.canvas.delete(self.obj)

    def reset(self, x0, y0, x1, y1):
        self.canvas.coords(self.obj, x0, y0, x1, y1)

    def configure(self, color):
        self.canvas.itemconfig(self.obj, fill=color)
    
    def state(self, state):
        self.canvas.itemconfig(self.obj, state=state)

    def getState(self):
        return self.canvas.itemcget(self.obj, 'state')

class cannon(game_objects):
    def __init__(self, canvas, x0, y0, x1, y1):
        self.width = 50
        self.height = 50
        self.speed = 10
        """ Need to add image
        ix = Image.open("squirrelR.png")
        ix = ix.resize((100, 100))
        ix = ImageTk.PhotoImage(ix)
        item = canvas.create_image(x, y, image=ix)
        """
        item = canvas.create_rectangle(x0, y0, x1, y1, fill="yellow")
        super(cannon, self).__init__(canvas, item)
    
    def move(self, direction):
        self.move_to(direction, 0)

class razor(game_objects):
    def __init__(self, canvas, cannon):
        pos = cannon.get_position()
        item = canvas.create_rectangle(
            pos[0] + 20, 
            pos[1] + 5,  
            pos[2] - 20, 
            pos[3] - 5,  
            fill="red",
            state="hidden")
        super(razor, self).__init__(canvas, item)

class bunker(game_objects):
    def __init__(self, canvas, x0, y0, x1, y1):
        self.width = 125
        self.height = 50
        item = canvas.create_rectangle(
            x0, y0, x1, y1,
            fill="#AADDCC",
            outline="#000000",
            state="normal"
        )
        super(bunker, self).__init__(canvas, item)

class alien(game_objects):
    def __init__(self, canvas, x0, y0, x1, y1):
        self.width = 50
        self.height = 50
        item = canvas.create_rectangle(
            x0, y0, x1, y1,
            fill="#FFFFFF",
            outline="#000000",
            state="normal"
        )
        super(alien, self).__init__(canvas, item)
        
class projectile(game_objects):
    def __init__(self, canvas, alien):
        pos = alien.get_position()
        item = canvas.create_rectangle(
            pos[0] + 20, 
            pos[1] + 5,  
            pos[2] - 20, 
            pos[3] - 5,  
            fill="green",)
        super(projectile, self).__init__(canvas, item)
            
class gameBoard(Canvas):

    def __init__(self, window):
        Canvas.__init__(
            self,
            window,
            bg="#000000",
            width=constants.width,
            height=constants.height
        )
        self.pack()
        self.cannon = cannon(self, 355, 750, 395, 790)
        self.razor = razor(self, self.cannon)
        self.attack = False
        self.pressedKey = [None, None]
        self.bunkers = []
        for i in range(3):
            self.bunkers.append(bunker(self, 75+242.5*i, 600, 200+242.5*i, 650))
        
        self.hitEdge = 0
        self.aliens = []
        for i in range(5): 
            line = []
            for j in range(8):
                line.append(alien(self, 145+60*j, 20+60*i, 185+60*j, 60+60*i))
            self.aliens.append(line)
        self.moveAlienR()
        self.projectiles = []
        self.projectileCnt = 0
        #self.gameLoop()
    
    def fire(self):
        self.razor.state("normal")
        self.razor.move_to(0, -10)
        posRazor = self.razor.get_position()
        if posRazor[1] < 5:
            self.razor.delete()
            self.attack = False
        for i in range(3):
            posBunker = self.bunkers[i].get_position()
            if posBunker[0] < posRazor[2] < posBunker[2] and posBunker[1] < posRazor[1] < posBunker[3]:
                self.razor.delete()
                self.attack = False
        for i in range(5):
            for j in range(8):
                state = self.aliens[i][j].getState()
                if state != "hidden": 
                    posAlien = self.aliens[i][j].get_position()
                    if posAlien[0] < posRazor[2] < posAlien[2] and posAlien[1] < posRazor[1] < posAlien[3]:
                        self.razor.delete()
                        self.aliens[i][j].state("hidden")
                        self.attack = False
        window.after(40, self.fire)
        
    def moveAlienR(self):
        pos = self.aliens[0][7].get_position()
        for i in range(5):
            for j in range(8):
                state = self.aliens[i][j].getState()
                if state != "hidden": 
                    self.aliens[i][j].move_to(2, 0)
        if pos[2] > constants.width - 15:
            self.hitEdge += 1
            self.moveAlienL()
        else:
            window.after(60, self.moveAlienR)
            
    def moveAlienL(self):
        pos = self.aliens[0][0].get_position()
        for i in range(5):
            for j in range(8):
                state = self.aliens[i][j].getState()
                if state != "hidden": 
                    self.aliens[i][j].move_to(-2, 0)
        if pos[0] < 15:
            self.hitEdge += 1
            if self.hitEdge == 4:
                self.hitEdge = 0
                self.moveAlienDown()
            self.moveAlienR()
        else:
            window.after(60, self.moveAlienL)
    
    def moveAlienDown(self):
        for i in range(5):
            for j in range(8):
                state = self.aliens[i][j].getState()
                if state != "hidden": 
                    self.aliens[i][j].move_to(0, 60)
    
    # WORKING ON FIRING PROJECTILES                
    def placeProjectile(self):
        while self.projectileCnt < 3:
            r = random.randint(0, 4)
            c = random.randint(0, 7)
            if self.aliens[r][c].getState() != 'hidden':
                self.projectiles.append(projectile(self, self.aliens[r][c])) 
                print(self.projectiles[0])
                self.projectileCnt += 1
        
        self.fireProjectile(0)
        #window.after(2000, self.placeProjectile)
            
    def fireProjectile(self, i):
        self.projectiles[i].state("normal")
        self.projectiles[i].move_to(0, 10)
        posProjectile = self.projectiles[i].get_position()
        print(posProjectile)
        if posProjectile != []: 
            if 800 < posProjectile[1]:
                self.projectiles[i].delete()
            
            for _ in range(3):
                posBunker = self.bunkers[_].get_position()
                if posBunker[0] < posProjectile[2] < posBunker[2] and posBunker[1] < posProjectile[1] < posBunker[3]:
                    self.projectiles[i].delete()
                    
            window.after(40, self.fireProjectile(i))
            

    def gameLoop(self):
        i = 0
        while(i < 10000):
            if self.pressedKey[0]: # Left
                self.cannon.move(-self.cannon.speed)
                i += 1
            elif self.pressedKey[1]: # Right
                self.cannon.move(-self.cannon.speed)
                i += 1
            self.collisions(self.razor)
                
def keyPressed(event):
    global board 
    if event.keysym == "Left":
        board.pressedKey[0] = 1
        board.cannon.move_to(-10, 0)
    elif event.keysym == "Right":
        board.pressedKey[1] = 1
        board.cannon.move_to(10, 0)
    elif event.keysym == "space" and board.attack == False:
        board.attack = True
        board.razor = razor(board, board.cannon)
        board.fire()



window = Tk()
window.title("Space Invaders")

ws = window.winfo_screenwidth()  # computers screen size
hs = window.winfo_screenheight()
x = (ws / 2) - (constants.width / 2)  # calculate center
y = (hs / 2) - (constants.height / 2)
window.geometry(
    "%dx%d+%d+%d" % (constants.width, constants.height, x, y)
)  # show the window at the middle of the screen
window.resizable(False, False)
window.tk.call("tk", "scaling", 4.0)
window.bind("<KeyPress>", keyPressed)
#window.bind("<KeyRelease>", Released)

board = gameBoard(window)
board.mainloop()