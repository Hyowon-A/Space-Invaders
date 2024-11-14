# Space Invaders 

from tkinter import Tk, Canvas, PhotoImage, Label, Toplevel, ttk, Radiobutton, StringVar, Button, simpledialog
import random
from PIL import ImageTk, Image

class constants:
    WIDTH = 750
    HEIGHT = 750

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
        item = canvas.create_rectangle(355, 650, 395, 690, fill="yellow")
        self.lives = 3
        self.lifeArray = []
        for i in range(3):
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
    def __init__(self, canvas, x0, y0, x1, y1, bunkerCnt):
        self.width = 125
        self.height = 50
        item = canvas.create_rectangle(
            x0, y0, x1, y1,
            fill="#AADDCC",
            outline="#000000",
            state="normal"
        )
        self.bunkerCnt = bunkerCnt
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

    def __init__(self, window, selectedKeys, gameLevel):
        Canvas.__init__(
            self,
            window,
            bg="#000000",
            width=constants.WIDTH,
            height=constants.HEIGHT
        )
        self.pack()
        self.selectedKeys = selectedKeys.split('_')
        self.gameLevel = gameLevel
        if self.gameLevel == "biginner":
            self.alienRow = 2
            self.alienCol = 8
            self.projectilesNo = 2
            self.bunkerCnt = 40
        elif self.gameLevel == "advanced":
            self.alienRow = 4
            self.alienCol = 8
            self.projectilesNo = 3
            self.bunkerCnt = 30
            
        self.menu = False
        self.score = 0
        self.scoreText = self.create_text(constants.WIDTH / 2, 40, text=("Score: "+ str(self.score)), fill="white", font="Hevetica 25 bold")
        self.round = 0
        self.roundText = self.create_text(80, 40, text=("Round: "+ str(self.round)), fill="white", font="Hevetica 25 bold")
        self.cannon = Cannon(self)
        self.cannonMoveLeft = False
        self.cannonMoveRight = False
        self.razor = Razor(self, self.cannon)
        self.attack = False
        self.bunkers = []
        for i in range(3):
            self.bunkers.append(Bunker(self, 75+242.5*i, 500, 200+242.5*i, 550, self.bunkerCnt))
        self.hitEdge = 0
        self.aliens = []
        self.alienCnt = self.alienRow * self.alienCol
        for row in range(self.alienRow): 
            line = []
            for col in range(self.alienCol):
                line.append(Alien(self, 145+60*col, 75+60*row, 185+60*col, 115+60*row))
            self.aliens.append(line)
        self.projectiles = []
        self.gameLoop()

    def gameLoop(self):
        """Main game loop to handle movements, projectile firing, and collision checks."""
        if self.alienCnt == 0:
            self.resetAliens()
        
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
        if self.menu == True:
            # Continue the loop if the player still has lives left
            print("Pause")
            menu = Tk()
            menu.title("Menu")
            menu.geometry("600x600")
            
            def resume():
                self.menu = False
                menu.destroy()
                self.gameLoop()
            
            r = Button(menu, text="Resume", command=resume)
            r.pack()
            save = Button(menu, text="Save")
            save.pack()
            leaderboard = Button(menu, text="Leaderboard")
            leaderboard.pack()
                
        elif self.cannon.lives > 0:
            self.after(30, self.gameLoop)
        else:
            # Game over, end the loop, and display a message
            self.create_text(
                constants.WIDTH // 2,
                constants.HEIGHT // 2,
                text="Game Over",
                fill="red",
                font="Helvetica 30 bold"
            )
    
    def resetAliens(self):
        self.aliens = []  # Clear existing aliens
        self.alienCnt = self.alienRow * self.alienCol  # Reset alien count
        self.round += 1     # Increase the round count
        self.itemconfigure(self.roundText, text=("Round: " + str(self.round)))
        self.hitEdge = 0
        
        if self.round != 0 and self.round % 3 == 0:
            self.projectilesNo += 1

        for row in range(self.alienRow): 
            line = []
            for col in range(self.alienCol):
                # Recreate each alien in its original position
                line.append(Alien(self, 145 + 60 * col, 75 + 60 * row, 185 + 60 * col, 115 + 60 * row))
            self.aliens.append(line)
    
    def moveCannon(self):
        """Move the cannon smoothly based on current key flags."""
        pos = self.cannon.get_position()
        if self.cannonMoveLeft and pos[0] > 5:
            self.cannon.moveLeft()
        elif self.cannonMoveRight and pos[2] < constants.WIDTH - 5:
            self.cannon.moveRight()
    
    def fire(self):
        """Fire razor when user press space and check collisions"""
        self.razor.state("normal")
        self.razor.move_to(0, -15)
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
        for row in range(self.alienRow):
            for col in range(self.alienCol):
                state = self.aliens[row][col].getState()
                if state != "hidden": 
                    posAlien = self.aliens[row][col].get_position()
                    if posAlien[0] < posRazor[2] < posAlien[2] and posAlien[1] < posRazor[1] < posAlien[3]:
                        self.razor.delete()
                        self.aliens[row][col].state("hidden")
                        self.alienCnt -= 1
                        self.score += 100
                        self.itemconfigure(self.scoreText, text=("Score: " + str(self.score)))
                        self.attack = False
        
    def moveAlienR(self):
        rightCol = self.getRightmostActiveColumn()  # get the current rightmost active column
        if rightCol == -1:
            return  # no aliens left, exit the function
        
        pos = None
        for row in range(self.alienRow):
            pos = self.aliens[row][rightCol].get_position()
            if pos:  # get the position of the first visible alien in the column
                break
        for row in range(self.alienRow):
            for col in range(self.alienCol):
                state = self.aliens[row][col].getState()
                if state != "hidden": 
                    self.aliens[row][col].move_to(1, 0)
        if pos[2] > constants.WIDTH - 15:
            self.hitEdge += 1
            
    def moveAlienL(self):
        leftCol = self.getLeftmostActiveColumn()  # get the current leftmost active column
        if leftCol == -1:
            return  # no aliens left, exit the function
        
        pos = None
        for row in range(self.alienRow):
            pos = self.aliens[row][leftCol].get_position()
            if pos:  # get the position of the first visible alien in the column
                break
            
        for row in range(self.alienRow):
            for col in range(self.alienCol):
                state = self.aliens[row][col].getState()
                if state != "hidden": 
                    self.aliens[row][col].move_to(-1, 0)
        if pos[0] < 15:
            self.hitEdge += 1
            if self.hitEdge == 2:
                self.moveAlienDown()
                self.hitEdge = 0
    
    def getLeftmostActiveColumn(self):
        for col in range(self.alienCol):  # iterate from the leftmost to rightmost columns
            for row in range(self.alienRow):  # check each row in the column
                if self.aliens[row][col].getState() != "hidden":
                    return col  # return the first column with a visible alien
        return -1  # if all aliens are hidden
    
    def getRightmostActiveColumn(self):
        for col in range(7, -1, -1):  # iterate from the rightmost to leftmost columns
            for row in range(self.alienRow):  # check each row in the column
                if self.aliens[row][col].getState() != "hidden":
                    return col  # return the first column with a visible alien
        return -1  # if all aliens are hidden
    
    def moveAlienDown(self):
        for row in range(self.alienRow):
            for col in range(self.alienCol):
                state = self.aliens[row][col].getState()
                if state != "hidden": 
                    self.aliens[row][col].move_to(0, 60)
    
    def fireProjectile(self):
        """Fire projectiles from 3 random aliens and check collisions"""
        # Ensure we have a maximum of 3 active projectiles on the screen
        if len(self.projectiles) < self.projectilesNo:
            # Randomly select an alien to fire a projectile
            x = random.randint(0, self.alienRow - 1)
            y = random.randint(0, self.alienCol - 1)
            
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
            if posProjectile[1] >= constants.HEIGHT:
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
    if event.keysym == board.selectedKeys[0] and posCannon[0] > 5:
        board.cannonMoveLeft = True
    elif event.keysym == board.selectedKeys[1] and posCannon[2] < constants.WIDTH - 5:
        board.cannonMoveRight = True
    elif event.keysym == board.selectedKeys[2] and board.attack == False:
        board.attack = True
        board.razor = Razor(board, board.cannon)
        board.fire()
    elif event.keysym == 'm':
        board.menu = True

def keyReleased(event):
    global board
    if event.keysym == board.selectedKeys[0]:
        board.cannonMoveLeft = False
    elif event.keysym == board.selectedKeys[1]:
        board.cannonMoveRight = False

def open_popup():
    initWin = Toplevel()
    initWin.geometry("400x550")
    initWin.title("Sign In")

    ws = initWin.winfo_screenwidth()
    hs = initWin.winfo_screenheight()
    x = (ws / 2) - (400 / 2)
    y = (hs / 2) - (550 / 2)
    initWin.geometry(f"{400}x{550}+{int(x)}+{int(y)}")
    initWin.tk.call("tk", "scaling", 4.0)
    initWin.resizable(False, False)

    # Add a label and entry for the user's name
    padding = Label(initWin)
    padding.pack(pady=10)
    name_label = Label(initWin, text="Enter your name:", font='Helvetica 18 bold')
    name_label.pack()
    name_entry = ttk.Entry(initWin)
    name_entry.pack(pady=10)

    # Add radio buttons for key options
    padding = Label(initWin)
    padding.pack(pady=10)
    key_option = Label(initWin, text="Choose control keys:", font='Helvetica 18 bold')
    key_option.pack(pady=10)

    movement_keys = StringVar(value="Left_Right_space")

    r1 = Radiobutton(initWin, text="Use arrow keys to move, space to fire", variable=movement_keys, value="Left_Right_space")
    r2 = Radiobutton(initWin, text="Use A/D to move, space to fire", variable=movement_keys, value="a_d_space")
    r3 = Radiobutton(initWin, text="Use A/D to move, W to fire", variable=movement_keys, value="a_d_w")

    r1.pack(anchor="w", padx=10)
    r2.pack(anchor="w", padx=10)
    r3.pack(anchor="w", padx=10)
    
    padding = Label(initWin)
    padding.pack(pady=10)

    level = StringVar(value="biginner")
    
    levelOption = Label(initWin, text="Choose the level: ", font='Helvetica 18 bold')
    levelOption.pack(pady=10)

    level1 = Radiobutton(initWin, text="Biginner", variable=level, value="biginner")
    level2 = Radiobutton(initWin, text="Advanced User", variable=level, value="advanced")
    
    level1.pack(anchor="w", padx=10)
    level2.pack(anchor="w", padx=10)
    
    # Add a button to submit and close the popup
    def submit():
        player_name = name_entry.get()
        if not player_name.strip():
            name = Toplevel(initWin)
            ws = name.winfo_screenwidth()
            hs = name.winfo_screenheight()
            x = (ws / 2) - (400 / 2)
            y = (hs / 2) - (100 / 2)
            name.geometry(f"{400}x{100}+{int(x)}+{int(y)}")
            name.tk.call("tk", "scaling", 4.0)
            name.resizable(False, False)
            name.title("Name")
            t = ttk.Label(name, text= "You need to enter your NAME", font=('Mistral 18 bold'))
            t.pack(pady=35, anchor="center")
        else:
            selectedKeys = movement_keys.get()
            gameLevel = level.get()

            # You can store these values or use them to modify the game controls
            print(f"Player Name: {player_name}")
            print(f"Selected Keys: {selectedKeys}")

            # Close the popup
            initWin.destroy()
            start_game(player_name, selectedKeys, gameLevel)

    padding = Label(initWin)
    padding.pack(pady=10)
    submit_button = Button(initWin, text="Start Game", command=submit, font='Helvetica 18 bold', bg="blue")
    submit_button.pack(pady=20)

def start_game(player_name, selected_keys, gameLevel):
    global board
    
    # Initialize main game window and center it on the screen
    window = Tk()
    window.title("Space Invaders")

    # Center the game window on the screen
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws / 2) - (constants.WIDTH / 2)
    y = (hs / 2) - (constants.HEIGHT / 2)
    window.geometry(f"{constants.WIDTH}x{constants.HEIGHT}+{int(x)}+{int(y)}")
    window.tk.call("tk", "scaling", 4.0)
    window.resizable(False, False)

    # Start the game board with player name and key selection
    board = gameBoard(window, selected_keys, gameLevel)
    window.bind("<KeyPress>", keyPressed)
    window.bind("<KeyRelease>", keyReleased)
    window.mainloop()

root = Tk()
root.withdraw()  # Hide main window initially
open_popup()  # Show popup to get player details and controls
root.mainloop()