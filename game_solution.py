# Space Invaders 

from tkinter import Tk, Canvas, PhotoImage, Label
import random
from PIL import ImageTk, Image

class constants:
    width = 750
    height = 950
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

    def configureColor(self, color):
        self.canvas.itemconfig(self.obj, fill=color)
        
    def configureText(self, txt):
        self.canvas.itemconfig(self.obj, text=txt)
    
    def state(self, state):
        self.canvas.itemconfig(self.obj, state=state)

    def getState(self):
        return self.canvas.itemcget(self.obj, 'state')

class Cannon(game_objects):
    def __init__(self, canvas):
        self.speed = 6
        """ Need to add image
        ix = Image.open("squirrelR.png")
        ix = ix.resize((100, 100))
        ix = ImageTk.PhotoImage(ix)
        item = canvas.create_image(x, y, image=ix)
        """
        item = canvas.create_rectangle(355, 850, 395, 890, fill="yellow")
        self.lives = constants.life
        self.lifeArray = []
        for i in range(constants.life):
            self.lifeArray.append(canvas.create_rectangle(600+40*i, 25, 625+40*i, 50, fill="red"))
        super(Cannon, self).__init__(canvas, item)
    
    def moveLeft(self):
        self.move_to(-self.speed, 0)
        
    def moveRight(self):
        self.move_to(self.speed, 0)
        
    def decreaseLife(self):
        """Decrease one cannon's life if cannon is hit by projectile"""
        if self.lives > 0:
            self.lives -= 1
            self.canvas.itemconfig(self.lifeArray[self.lives*-1+2], state='hidden')
            return True
        
        return False

class Razor(game_objects):
    def __init__(self, canvas, cannon):
        self.speed = -10
        pos = cannon.get_position()
        item = canvas.create_rectangle(
            pos[0] + 20, 
            pos[1] + 5,  
            pos[2] - 20, 
            pos[3] - 5,  
            fill="red",
            state="hidden")
        super(Razor, self).__init__(canvas, item)

class Bunker(game_objects):
    def __init__(self, canvas, x0, y0, x1, y1):
        self.width = 125
        self.height = 50
        item = canvas.create_rectangle(
            x0, y0, x1, y1,
            fill="#AADDCC",
            outline="#000000",
            state="normal"
        )
        self.bunkerCnt = 15
        self.cntText = canvas.create_text((x0+x1)/2, (y0+y1)/2, text=str(self.bunkerCnt), fill="white", font=('Helvetica 15 bold'))
        super(Bunker, self).__init__(canvas, item)
        
    def decreaseCount(self):
        """Decrease bunker count and update the text display."""
        if self.bunkerCnt > 0:
            """Decrease bunker count by 1 and update the text display"""
            self.bunkerCnt -= 1
            self.canvas.itemconfig(self.cntText, text=str(self.bunkerCnt))
        
        # Hide the bunker if count reaches zero
        if self.bunkerCnt == 0:
            """Delete bunker and text if the count is 0"""
            self.delete()
            self.canvas.itemconfig(self.cntText, state="hidden")

class Alien(game_objects):
    def __init__(self, canvas, x0, y0, x1, y1):
        self.width = 50
        self.height = 50
        item = canvas.create_rectangle(
            x0, y0, x1, y1,
            fill="#FFFFFF",
            outline="#000000",
            state="normal"
        )
        super(Alien, self).__init__(canvas, item)
        
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
        self.score = 0
        self.scoreText = self.create_text(75, 40, text=("score: "+ str(self.score)), fill="white", font="Hevetica 25 bold")
        self.cannon = Cannon(self)
        self.cannonMoveLeft = False
        self.cannonMoveRight = False
        self.razor = Razor(self, self.cannon)
        self.attack = False
        self.bunkers = []
        for i in range(3):
            self.bunkers.append(Bunker(self, 75+242.5*i, 700, 200+242.5*i, 750))
        
        self.hitEdge = 0
        self.aliens = []
        for i in range(5): 
            line = []
            for j in range(8):
                line.append(Alien(self, 145+60*j, 75+60*i, 185+60*j, 115+60*i))
            self.aliens.append(line)
        self.projectiles = []
        self.gameLoop()

    def gameLoop(self):
        """Main game loop to handle movements, projectile firing, and collision checks."""
        # Move aliens
        if self.hitEdge % 2 == 0:
            self.moveAlienR()
        else:
            self.moveAlienL()

        # Move existing razor if it's in play
        if self.attack:
            self.fire()

        # Move cannon 
        self.moveCannon()

        # Aliens fire projectiles
        self.fireProjectile()

        # Check if the game is over
        if self.cannon.lives > 0:
            # Continue the loop if the player still has lives left
            self.after(30, self.gameLoop)
        else:
            # Game over, end the loop, and display a message
            self.create_text(
                constants.width // 2,
                constants.height // 2,
                text="Game Over",
                fill="red",
                font="Helvetica 30 bold"
            )
    
    def moveCannon(self):
        """Move the cannon smoothly based on current key flags."""
        pos = self.cannon.get_position()
        if self.cannonMoveLeft and pos[0] > 5:
            self.cannon.moveLeft()
        elif self.cannonMoveRight and pos[2] < constants.width - 5:
            self.cannon.moveRight()
    
    def fire(self):
        """Fire razor when user press space and check collisions"""
        self.razor.state("normal")
        self.razor.move_to(0, -5)
        posRazor = self.razor.get_position()
        """Check if razor is out of bound(top of screen)"""
        if posRazor[1] <= 0:
            self.razor.delete()
            self.attack = False
        
        """Check for collision with bunkers"""
        for bunker in self.bunkers:
            posBunker = bunker.get_position()
            if posBunker != []:
                if posBunker[0] < posRazor[2] < posBunker[2] and posBunker[1] < posRazor[1] < posBunker[3]:
                    self.razor.delete()
                    bunker.decreaseCount()
                    self.attack = False
                    
        """Check for collision with aliens"""
        for i in range(5):
            for j in range(8):
                state = self.aliens[i][j].getState()
                if state != "hidden": 
                    posAlien = self.aliens[i][j].get_position()
                    if posAlien[0] < posRazor[2] < posAlien[2] and posAlien[1] < posRazor[1] < posAlien[3]:
                        self.razor.delete()
                        self.aliens[i][j].state("hidden")
                        self.score += 100
                        self.itemconfigure(self.scoreText, text=("Score: " + str(self.score)))
                        self.attack = False
        
    def moveAlienR(self):
        pos = self.aliens[0][7].get_position()
        for i in range(5):
            for j in range(8):
                state = self.aliens[i][j].getState()
                if state != "hidden": 
                    self.aliens[i][j].move_to(1, 0)
        if pos[2] > constants.width - 15:
            self.hitEdge += 1
            
    def moveAlienL(self):
        pos = self.aliens[0][0].get_position()
        for i in range(5):
            for j in range(8):
                state = self.aliens[i][j].getState()
                if state != "hidden": 
                    self.aliens[i][j].move_to(-1, 0)
        if pos[0] < 15:
            self.hitEdge += 1
            if self.hitEdge == 4:
                self.moveAlienDown()
                self.hitEdge = 0
    
    def moveAlienDown(self):
        for i in range(5):
            for j in range(8):
                state = self.aliens[i][j].getState()
                if state != "hidden": 
                    self.aliens[i][j].move_to(0, 60)
    
    def fireProjectile(self):
        """Fire projectiles from 3 random aliens and check collisions"""
        # Ensure we have a maximum of 3 active projectiles on the screen
        if len(self.projectiles) < 3:
            # Randomly select an alien to fire a projectile
            x = random.randint(0, 4)
            y = random.randint(0, 7)
            
            # Check if the selected alien is visible (not hidden)
            if self.aliens[x][y].getState() != 'hidden':
                # Create a projectile from the alien and add it to the list
                new_projectile = projectile(self, self.aliens[x][y])
                self.projectiles.append(new_projectile)
        
        # Move each projectile downwards and check for collisions or boundaries
        for p in self.projectiles[:]:  # Use a copy of the list to modify safely
            p.move_to(0, 3)
            posProjectile = p.get_position()
            
            # Check if projectile is out of bounds (bottom of screen)
            if posProjectile[1] >= constants.height:
                p.delete()
                self.projectiles.remove(p)
                continue  # Skip further checks for this projectile
            
            # Check for collision with cannon
            posCannon = self.cannon.get_position()
            if (posCannon[0] < posProjectile[2] < posCannon[2] and 
                posCannon[1] < posProjectile[3] < posCannon[3]):
                p.delete()
                self.projectiles.remove(p)
                self.cannon.decreaseLife()
                
            # Check for collision with bunkers
            for bunker in self.bunkers:
                posBunker = bunker.get_position()
                if posBunker != []:
                    if (posBunker[0] < posProjectile[2] < posBunker[2] and 
                        posBunker[1] < posProjectile[3] < posBunker[3]):
                        p.delete()
                        self.projectiles.remove(p)
                        bunker.decreaseCount()
                        break  # Exit bunker collision check to avoid further checks
        # Schedule the next projectile firing update
                
def keyPressed(event):
    global board 
    posCannon = board.cannon.get_position()
    if event.keysym == "Left" and posCannon[0] > 5:
        board.cannonMoveLeft = True
    elif event.keysym == "Right" and posCannon[2] < constants.width - 5:
        board.cannonMoveRight = True
    elif event.keysym == "space" and board.attack == False:
        board.attack = True
        board.razor = Razor(board, board.cannon)
        board.fire()

def keyReleased(event):
    global board
    if event.keysym == "Left":
        board.cannonMoveLeft = False
    elif event.keysym == "Right":
        board.cannonMoveRight = False


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
window.bind("<KeyRelease>", keyReleased)

board = gameBoard(window)
board.mainloop()