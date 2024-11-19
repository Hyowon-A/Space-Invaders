# Space Invaders 

from tkinter import Tk, Canvas, PhotoImage, Label, Toplevel, ttk, Radiobutton, StringVar, Button, Frame, Listbox
import random
from PIL import ImageTk, Image

import os
import pathlib

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
        self.canvas.coords(self.obj, ((x0+x1)/2), ((y0+y1)/2))

    def configureColor(self, color):
        self.canvas.itemconfig(self.obj, fill=color)
        
    def configureText(self, txt):
        self.canvas.itemconfig(self.obj, text=txt)
    
    def state(self, state):
        self.canvas.itemconfig(self.obj, state=state)

    def getState(self):
        return self.canvas.itemcget(self.obj, 'state')

class Cannon(game_objects):
    def __init__(self, canvas, lives):
        self.width = 50
        self.height = 50
        self.speed = 5
        # Load and resize the image
        cannonImg = Image.open("cannon.png").resize((self.width, self.height), Image.Resampling.LANCZOS)
        self.cannonImg = ImageTk.PhotoImage(master=canvas, image=cannonImg)  # Keep a reference to the image
        item = canvas.create_image(constants.WIDTH/2, 680, image=self.cannonImg)
        
        self.lifeArray = []
        lifeImg = Image.open("life.png").resize((25, 25), Image.Resampling.LANCZOS)
        self.lifeImg = ImageTk.PhotoImage(master=canvas, image=lifeImg)  # Keep a reference to the image
        for i in range(lives):
            self.lifeArray.append(canvas.create_image(612.5+40*i, 37.5, image=self.lifeImg))
        super(Cannon, self).__init__(canvas, item)
    
    def moveLeft(self):
        self.move_to(-self.speed, 0)
        
    def moveRight(self):
        self.move_to(self.speed, 0)
        
    def getBbox(self):
        x, y = self.get_position()
        x0 = x - self.width / 2
        y0 = y - self.height / 2
        x1 = x + self.width / 2
        y1 = y + self.height / 2
        bbox = [x0, y0, x1, y1]
        return bbox

class Razor(game_objects):
    def __init__(self, canvas, cannon):
        self.speed = -10
        pos = cannon.getBbox()
        item = canvas.create_rectangle(
            pos[0] + 23, 
            pos[1] + 7,  
            pos[2] - 23, 
            pos[3] - 7,  
            fill="#66c2ff",
            state="hidden",
            width=0)
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
            
    def getCount(self):
        return self.bunkerCnt
    
    def updateCount(self, n):
        self.bunkerCnt = n
        self.canvas.itemconfig(self.cntText, text=str(self.bunkerCnt))

class Alien(game_objects):
    def __init__(self, canvas, x0, y0, x1, y1):
        self.width = 50
        self.height = 50
        # Load and resize the image
        alienImg = Image.open("alien1.png").resize((self.width, self.height), Image.Resampling.LANCZOS)
        self.alienImg = ImageTk.PhotoImage(master=canvas, image=alienImg)  # Keep a reference to the image
        
        # Create the image in the canvas
        center_x = (x0 + x1) / 2
        center_y = (y0 + y1) / 2
        item = canvas.create_image(center_x, center_y, image=self.alienImg)
        
        super(Alien, self).__init__(canvas, item)
    
    def getBbox(self):
        x, y = self.get_position()
        x0 = x - self.width / 2
        y0 = y - self.height / 2
        x1 = x + self.width / 2
        y1 = y + self.height / 2
        bbox = [x0, y0, x1, y1]
        return bbox
    
class projectile(game_objects):
    def __init__(self, canvas, alien):
        pos = alien.getBbox()
        item = canvas.create_rectangle(
            pos[0] + 23, 
            pos[1] + 7,  
            pos[2] - 23, 
            pos[3] - 7,  
            fill="#33ff33",
            width=0)
        super(projectile, self).__init__(canvas, item)
            
class gameBoard(Canvas):

    def __init__(self, window, playerName, selectedKeys, gameLevel, *args):
        Canvas.__init__(
            self,
            window,
            bg="#000000",
            width=constants.WIDTH,
            height=constants.HEIGHT
        )
        self.pack()
        self.playerName = playerName
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
        self.cannonMoveLeft = False
        self.cannonMoveRight = False
        self.attack = False
        self.bunkers = []
        for i in range(3):
            self.bunkers.append(Bunker(self, 75+242.5*i, 500, 200+242.5*i, 550, self.bunkerCnt))
        self.hitEdge = 0
        self.aliens = []
        self.projectiles = []
        
        if len(args) == 0:
            self.lives = 3
            self.cannon = Cannon(self, self.lives)
            self.razor = Razor(self, self.cannon)
            self.score = 0
            self.scoreText = self.create_text(constants.WIDTH / 2, 40, text=("Score: "+ str(self.score)), fill="white", font="Hevetica 25 bold")
            self.round = 0
            self.roundText = self.create_text(80, 40, text=("Round: "+ str(self.round)), fill="white", font="Hevetica 25 bold")
            self.alienCnt = self.alienRow * self.alienCol
            for row in range(self.alienRow): 
                line = []
                for col in range(self.alienCol):
                    line.append(Alien(self, 145+60*col, 75+60*row, 185+60*col, 115+60*row))
                self.aliens.append(line)
        else:
            self.round = args[0]
            self.roundText = self.create_text(80, 40, text=("Round: "+ str(self.round)), fill="white", font="Hevetica 25 bold")
            self.score = args[1]
            self.scoreText = self.create_text(constants.WIDTH / 2, 40, text=("Score: "+ str(self.score)), fill="white", font="Hevetica 25 bold")
            self.lives = args[2]
            self.alienCnt = args[3]
            line = []
            for i in range(self.alienRow * self.alienCol):
                alienPos = args[4][i]
                if alienPos == "0":
                    alien = Alien(self, 145 + 60 * i, 75 + 60 * i, 185 + 60 * i, 115 + 60 * i)
                    alien.state("hidden")
                else:
                    alienCoords = alienPos.strip("[]").split(",")
                    x1, y1, x2, y2 = map(float, alienCoords)  # Convert to floats
                    alien = Alien(self, x1, y1, x2, y2)
                line.append(alien)
                
                if len(line) == 8:
                    self.aliens.append(line)
                    line = []
                    
            i = 0
            bunkersCnt = args[5]
            for bunker in self.bunkers:
                bunker.updateCount(bunkersCnt[i])
                i += 1
            
            self.cannon = Cannon(self, self.lives) # relocate
            cannonPos = str(args[6]).replace("[", "").replace(']', '').split(',')
            x1, y1, x2, y2 = map(float, cannonPos)
            self.cannon.reset(x1, y1, x2, y2)
            print(self.cannon.get_position())

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
            ws = menu.winfo_screenwidth()
            hs = menu.winfo_screenheight()
            x = (ws / 2) - (400 / 2)
            y = (hs / 2) - (400 / 2)
            menu.geometry(f"{400}x{400}+{int(x)}+{int(y)}")
            menu.tk.call("tk", "scaling", 4.0)
            menu.resizable(False, False)
            
            def resume():
                self.menu = False
                menu.destroy()
                self.gameLoop()
            
            r = Button(menu, text="Resume", command=resume)
            r.pack()
            save = Button(menu, text="Save", command=self.save)
            save.pack()
            leaderboard = Button(menu, text="Leaderboard", command=openLeaderboard)
            leaderboard.pack()
                
        elif self.lives > 0:
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
            self.updateLeaderboard()
            openLeaderboard()
    
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
        pos = self.cannon.getBbox()
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
                    posAlien = self.aliens[row][col].getBbox()
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
        
        for row in range(self.alienRow):
            if self.aliens[row][rightCol].getState() != "hidden":
                pos = self.aliens[row][rightCol].getBbox()
                break
        else:
            return  # No visible aliens found
        
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
        
        for row in range(self.alienRow):
            if self.aliens[row][leftCol].getState() != "hidden":
                pos = self.aliens[row][leftCol].getBbox()
                break
            else:
                return  # No visible aliens found
            
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
        for col in range(self.alienCol - 1, -1, -1):  # iterate from the rightmost to leftmost columns
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
            posCannon = self.cannon.getBbox()
            if (posCannon[0] < posProjectile[2] < posCannon[2] and 
                posCannon[1] < posProjectile[3] < posCannon[3]):
                p.delete()
                self.projectiles.remove(p)
                self.decreaseLife()
                
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

    def decreaseLife(self):
        """Decrease one cannon's life if cannon is hit by projectile"""
        if self.lives > 0:
            self.lives -= 1
            self.itemconfig(self.cannon.lifeArray[self.lives], state='hidden')
            return True
        return False

    def updateLeaderboard(self):
        lb = {}
        with open("leaderboard.txt") as f:
            for line in f:
                (key, val) = line.split(':')
                lb[key] = int(val.removesuffix('\n'))
        lb[self.playerName] = self.score
        
        sortedScores = sorted(lb.items(), key=lambda x:x[1], reverse=True)
        sortedLb = dict(sortedScores)
        
        with open("leaderboard.txt", 'w') as f:  
            for key, value in sortedLb.items():  
                f.write('%s:%s\n' % (key, value))   
        
    def save(self):
        filename = f"{self.playerName}.txt"
        with open(filename, "w") as f:
            f.write(self.playerName +'\n')
            f.write(self.gameLevel + "\n")
            f.write(self.selectedKeys[0]+'_'+self.selectedKeys[1]+'_'+self.selectedKeys[2]+'\n')
            f.write(str(self.round)+'\n')
            f.write(str(self.score)+'\n')
            f.write(str(self.lives)+'\n')
            f.write(str(self.alienCnt)+'\n')
            for row in range(self.alienRow):
                for col in range(self.alienCol):
                    alienState = self.aliens[row][col].getState()
                    if alienState == 'hidden':
                        f.write("0\n")
                    else:
                        alienPos = self.aliens[row][col].getBbox()
                        f.write(str(alienPos)+"\n")
            for bunker in self.bunkers:
                f.write(str(bunker.getCount())+'\n')
            f.write(str(self.cannon.getBbox()))

       
def openLeaderboard():
    lb = {}
    with open("leaderboard.txt") as f:
        for line in f:
            (key, val) = line.split(':')
            lb[key] = val.removesuffix('\n')

    lbWin = Tk()
    lbWin.title("Leaderboard")
    ws = lbWin.winfo_screenwidth()
    hs = lbWin.winfo_screenheight()
    x = (ws / 2) - (400 / 2)
    y = (hs / 2) - (400 / 2)
    lbWin.geometry(f"{400}x{400}+{int(x)}+{int(y)}")
    lbWin.tk.call("tk", "scaling", 4.0)
    lbWin.resizable(False, False)
    title = Label(lbWin, text="Leaderboard", font='Helvetica 18 bold')
    title.pack(anchor="center")
        
    separator = ttk.Separator(lbWin, orient="horizontal")
    separator.pack(fill="x", padx=20, pady=5)
        
    header = Frame(lbWin)
    header.pack(pady=5)
    Label(header, text="Rank", font=("Arial", 14, "bold"), width=10, anchor="center").pack(side="left")
    Label(header, text="Player", font=("Arial", 14, "bold"), width=15, anchor="center").pack(side="left")
    Label(header, text="Score", font=("Arial", 14, "bold"), width=10, anchor="center").pack(side="left")
        
    colors = ["#FFD700", "#C0C0C0", "#CD7F32"]  # Top 3 colors
    i = 0
    for player, score in lb.items():
        row = Frame(lbWin)
        row.pack(pady=2)
        
        # Set color for top 3
        color = colors[i] if i < 3 else "black"
        
        Label(row, text=f"{i + 1}", font=("Arial", 14), width=10, anchor="center", fg=color).pack(side="left")
        Label(row, text=player, font=("Arial", 14), width=15, anchor="center", fg=color).pack(side="left")
        Label(row, text=str(score), font=("Arial", 14), width=10, anchor="center", fg=color).pack(side="left")
        i += 1
      

def keyPressed(event):
    global board 
    posCannon = board.cannon.getBbox()
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
    initWin.title("Sign In")

    ws = initWin.winfo_screenwidth()
    hs = initWin.winfo_screenheight()
    x = (ws / 2) - (400 / 2)
    y = (hs / 2) - (750 / 2)
    initWin.geometry(f"{400}x{750}+{int(x)}+{int(y)}")
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

    submit_button = Button(initWin, text="Start Game", command=submit, font='Helvetica 16 bold', bg="blue")
    submit_button.pack(pady=10)
    lbButton = Button(initWin, text="Leaderboard", command=openLeaderboard, font='Helvetica 16 bold', bg="blue")
    lbButton.pack(pady=10)
    

    savedFiles = []
    for x in os.listdir():
        if x.endswith(".txt") and x != "leaderboard.txt":
            savedFiles.append(x)
    fileList = Listbox(initWin)
    for i in range(len(savedFiles)):
        fileList.insert(i, savedFiles[i])
    fileList.pack(anchor="w")
    
    def load():
        with open(fileList.get(fileList.curselection())) as f:
            txt = f.readlines()
            playerName = txt[0].removesuffix('\n')
            gameLevel = txt[1].removesuffix('\n')
            selectedKeys = txt[2].removesuffix('\n')
            round = int(txt[3].removesuffix('\n'))
            score = int(txt[4].removesuffix('\n'))
            lives = int(txt[5].removesuffix('\n'))
            alienCnt = int(txt[6].removesuffix('\n'))
            aliensPos = []
            if gameLevel == "biginner":
                totalAlienCnt = 16
            else: 
                totalAlienCnt = 32
            for i in range(totalAlienCnt):
                aliensPos.append(txt[i+7].removesuffix('\n'))
            bunkersCnt = []
            for i in range(3):
                bunkersCnt.append(int(txt[7+totalAlienCnt+i].removesuffix('\n')))
            cannonPos = txt[7+totalAlienCnt+3].removesuffix('\n')
            initWin.destroy()
            start_game(playerName, selectedKeys, gameLevel, 
                       round, score, lives, alienCnt, aliensPos, bunkersCnt, cannonPos)
    
    loadButton = Button(initWin, text="Load saved file", command=load)
    loadButton.pack(anchor="w")

def start_game(player_name, selected_keys, gameLevel, *args):
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
    if len(args) == 0:
        board = gameBoard(window, player_name, selected_keys, gameLevel)
    else:
        board = gameBoard(window, player_name, selected_keys, gameLevel, *args)
    window.bind("<KeyPress>", keyPressed)
    window.bind("<KeyRelease>", keyReleased)
    window.mainloop()

root = Tk()
root.withdraw()  # Hide main window initially
open_popup()  # Show popup to get player details and controls
root.mainloop()