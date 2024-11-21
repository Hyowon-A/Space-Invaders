# Space Invaders

from tkinter import (Tk, Canvas, Label, Toplevel, ttk,
                     Radiobutton, StringVar, Button, Frame, Listbox)
import random
import os
from PIL import ImageTk, Image


class Constants:
    WIDTH = 750
    HEIGHT = 750


class GameObjects:
    """
    A class to manage objects on a Tkinter canvas, with utility methods to
    retrieve positions, move, delete, reset coordinates, and configure
    properties such as color, text, and state.
    """

    def __init__(self, canvas, obj):
        self.canvas = canvas
        self.obj = obj

    def getPosition(self):
        """Get the position of the object as (x0, y0, x1, y1)."""
        return self.canvas.coords(self.obj)

    def moveTo(self, x, y):
        """Move the object by specified amounts along x and y axes."""
        self.canvas.move(self.obj, x, y)

    def delete(self):
        """Delete the object from the canvas."""
        self.canvas.delete(self.obj)

    def resetBbox(self, x0, y0, x1, y1):
        """Center the object in the given bounding box."""
        self.canvas.coords(self.obj, ((x0 + x1) / 2), ((y0 + y1) / 2))

    def resetCoords(self, x, y):
        """Reset the position to the specified coordinates."""
        self.canvas.coords(self.obj, x, y)

    def configureColor(self, color):
        """Change the fill color of the object."""
        self.canvas.itemconfig(self.obj, fill=color)

    def configureText(self, txt):
        """Update the text content of the object."""
        self.canvas.itemconfig(self.obj, text=txt)

    def state(self, state):
        """Set the state ('hidden' or 'normal') of the object."""
        self.canvas.itemconfig(self.obj, state=state)

    def getState(self):
        """Get the current state ('hidden' or 'normal') of the object."""
        return self.canvas.itemcget(self.obj, 'state')


class Cannon(GameObjects):
    """
    A class to represent and manage a cannon object on the canvas. It
    extends GameObjects and includes movement and bounding box utilities.
    """

    def __init__(self, canvas):
        """
        Initialize the cannon, its properties, and display it on the canvas.
        """
        self.width = 50
        self.height = 50
        self.speed = 5
        cannonImg = Image.open("cannon.png").resize(
            (self.width, self.height), Image.Resampling.LANCZOS
        )
        self.cannonImg = ImageTk.PhotoImage(master=canvas,
                                            image=cannonImg)
        item = canvas.create_image(Constants.WIDTH / 2, 650,
                                   image=self.cannonImg)
        super().__init__(canvas, item)

    def moveLeft(self):
        """Move the cannon left by its speed."""
        self.moveTo(-self.speed, 0)

    def moveRight(self):
        """Move the cannon right by its speed."""
        self.moveTo(self.speed, 0)

    def getBbox(self):
        """Get the bounding box of the cannon as [x0, y0, x1, y1]."""
        x, y = self.getPosition()
        x0 = x - self.width / 2
        y0 = y - self.height / 2
        x1 = x + self.width / 2
        y1 = y + self.height / 2
        return [x0, y0, x1, y1]


class Laser(GameObjects):
    """
    A class to represent and manage a laser fired from the cannon. The
    laser moves upward and can interact with objects.
    """

    def __init__(self, canvas, cannon):
        """
        Initialize the laser at the cannon's position, initially hidden.
        """
        self.speed = -10
        pos = cannon.getBbox()
        item = canvas.create_rectangle(
            pos[0] + 23, pos[1] + 7, pos[2] - 23, pos[3] - 7,
            fill="#66c2ff", state="hidden", width=0
        )
        super().__init__(canvas, item)


class Bunker(GameObjects):
    """
    A class to manage a bunker object on a Tkinter canvas. The bunker has
    a rectangular shape and a count representing its remaining strength.
    """

    def __init__(self, canvas, x0, y0, x1, y1, bunkerCnt):
        """
        Initialize a bunker with its position and initial strength.

        Args:
            canvas (Canvas): The canvas to draw the bunker on.
            x0, y0 (int): Top-left coordinates of the bunker.
            x1, y1 (int): Bottom-right coordinates of the bunker.
            bunkerCnt (int): The initial strength of the bunker.
        """
        self.width = 125
        self.height = 50
        item = canvas.create_rectangle(
            x0, y0, x1, y1, fill="#AADDCC", outline="#000000", state="normal"
        )
        self.bunkerCnt = bunkerCnt
        self.cntText = canvas.create_text(
            (x0 + x1) / 2, (y0 + y1) / 2, text=str(bunkerCnt),
            fill="white", font='Helvetica 15 bold'
        )
        super().__init__(canvas, item)

    def decreaseCount(self):
        """
        Decrease the bunker count by 1. Hide the bunker if the count is 0.
        """
        if self.bunkerCnt > 0:
            self.bunkerCnt -= 1
            self.canvas.itemconfig(self.cntText, text=str(self.bunkerCnt))
        if self.bunkerCnt == 0:
            self.delete()
            self.canvas.itemconfig(self.cntText, state="hidden")

    def getCount(self):
        """
        Get the current strength of the bunker.

        Returns:
            int: Current bunker strength.
        """
        return self.bunkerCnt

    def updateCount(self, n):
        """
        Update the bunker count to a new value.

        Args:
            n (int): New strength value for the bunker.
        """
        self.bunkerCnt = n
        self.canvas.itemconfig(self.cntText, text=str(n))


class Alien(GameObjects):
    """
    A class to manage an alien object on a Tkinter canvas. The alien is
    represented by an image and positioned using a bounding box.
    """

    def __init__(self, canvas, x0, y0, x1, y1):
        """
        Initialize an alien at a given position.

        Args:
            canvas (Canvas): The canvas to draw the alien on.
            x0, y0 (int): Top-left coordinates of the bounding box.
            x1, y1 (int): Bottom-right coordinates of the bounding box.
        """
        self.width = 50
        self.height = 50
        alienImg = Image.open("alien1.png").resize(
            (self.width, self.height), Image.Resampling.LANCZOS
        )
        self.alienImg = ImageTk.PhotoImage(master=canvas, image=alienImg)
        centerX = (x0 + x1) / 2
        centerY = (y0 + y1) / 2
        item = canvas.create_image(centerX, centerY, image=self.alienImg)
        super().__init__(canvas, item)

    def getBbox(self):
        """
        Get the bounding box of the alien.

        Returns:
            list: Bounding box as [x0, y0, x1, y1].
        """
        x, y = self.getPosition()
        x0 = x - self.width / 2
        y0 = y - self.height / 2
        x1 = x + self.width / 2
        y1 = y + self.height / 2
        return [x0, y0, x1, y1]


class Projectile(GameObjects):
    """
    A class to initialize and manage projectiles fired by aliens
    on a Tkinter canvas. This class extends the GameObjects class
    and represents projectiles as rectangles.

    Methods:
        Inherits all methods from the GameObjects class.
    """

    def __init__(self, canvas, alien):
        """
        Initializes the Projectile object.

        Args:
            canvas (tkinter.Canvas): The canvas for the projectile.
            alien (Alien): The alien firing the projectile.
        """
        # Determine the projectile's initial position
        pos = alien.getBbox()

        # Create a rectangular projectile on the canvas
        item = canvas.create_rectangle(
            pos[0] + 23,  # Adjusted projectile width
            pos[1] + 7,   # Adjusted projectile height
            pos[2] - 23,
            pos[3] - 7,
            fill="#33ff33",  # Projectile color
            width=0          # No border width
        )

        # Initialize the base GameObjects class
        super(Projectile, self).__init__(canvas, item)


class gameBoard(Canvas):
    """
    A class to initialize and manage the game board in a Tkinter window.

    The game board contains game elements such as aliens, bunkers,
    cannon, projectiles, and background, along with player settings
    and game states.

    Attributes:
        playerName (str): The player's name.
        selectedKeys (list): Player control keys.
        gameLevel (str): The game level ("beginner" or "advanced").
        alienRow (int): Number of alien rows.
        alienCol (int): Number of alien columns.
        projectilesNo (int): Max alien projectiles.
        bunkerCnt (int): Initial bunker strength.
        menuOn (bool): Whether the menu is displayed.
        cannonMoveLeft (bool): Whether the cannon moves left.
        cannonMoveRight (bool): Whether the cannon moves right.
        attack (bool): Whether the cannon is firing.
        bunkers (list): List of Bunker objects.
        hitEdge (int): Tracks edge collisions by aliens.
        aliens (list): 2D list of Alien objects.
        projectiles (list): List of Projectile objects.
        pressedKeys (set): Currently pressed keys.
        passingLaser (bool): Whether a laser is passing.
        lifeArray (list): List of life indicator objects.
        lives (int): Remaining player lives.
        cannon (Cannon): Player-controlled cannon.
        laser (Laser): Player's laser object.
        score (int): Player's score.
        scoreText (int): Canvas text for score.
        round (int): Current game round.
        roundText (int): Canvas text for the round.

    Methods:
        gameLoop(): Starts the main game loop.
    """

    def __init__(self, window, playerName, selectedKeys, gameLevel, *args):
        """
        Initializes the game board and its elements.

        Args:
            window (tkinter.Tk): The game window.
            playerName (str): The player's name.
            selectedKeys (str): Underscore-separated keys for controls.
            gameLevel (str): The game difficulty level.
            *args: Optional saved game state data.
        """
        # Initialize the Canvas
        Canvas.__init__(self, window, bg="#000000",
                        width=Constants.WIDTH, height=Constants.HEIGHT)
        self.pack()

        # Load and display the background image
        bg = Image.open("spaceBg.jpg").resize(
            (Constants.WIDTH, Constants.HEIGHT)
        )
        self.bgImage = ImageTk.PhotoImage(bg)  # Prevent GC
        self.create_image(0, 0, anchor="nw", image=self.bgImage)

        # Initialize player and game state variables
        self.playerName = playerName
        self.selectedKeys = selectedKeys.split('_')
        self.gameLevel = gameLevel
        self.menuOn = False
        self.cannonMoveLeft = False
        self.cannonMoveRight = False
        self.attack = False
        self.bunkers = []
        self.aliens = []
        self.projectiles = []
        self.pressedKeys = set()
        self.passingLaser = False
        self.hitEdge = 0

        # Configure game parameters based on the difficulty
        if self.gameLevel == "beginner":
            self.alienRow = 2
            self.alienCol = 8
            self.projectilesNo = 2
            self.bunkerCnt = 40
        else:
            self.alienRow = 4
            self.alienCol = 8
            self.projectilesNo = 3
            self.bunkerCnt = 30

        # Initialize bunkers
        for i in range(3):
            self.bunkers.append(
                Bunker(self, 75 + 242.5 * i, 500, 200 + 242.5 * i, 550,
                       self.bunkerCnt)
            )

        # Initialize life indicators
        self.lifeArray = []
        lifeImg = Image.open("life.png").resize(
            (25, 25), Image.Resampling.LANCZOS
        )
        self.lifeImg = ImageTk.PhotoImage(master=self, image=lifeImg)

        # Initialize game elements
        if len(args) == 0:  # New game
            self.lives = 3
            self.cannon = Cannon(self)
            self.laser = Laser(self, self.cannon)
            self.score = 0
            self.round = 0

            # Add score and round text
            self.scoreText = self.create_text(
                Constants.WIDTH / 2, 40, text=f"Score: {self.score}",
                fill="white", font="Helvetica 25 bold"
            )
            self.roundText = self.create_text(
                80, 40, text=f"Round: {self.round}", fill="white",
                font="Helvetica 25 bold"
            )

            # Initialize aliens
            self.alienCnt = self.alienRow * self.alienCol
            for row in range(self.alienRow):
                line = []
                for col in range(self.alienCol):
                    line.append(
                        Alien(self, 145 + 60 * col, 75 + 60 * row,
                              185 + 60 * col, 115 + 60 * row)
                    )
                self.aliens.append(line)
        else:  # Load saved game state
            self.round = args[0]
            self.score = args[1]
            self.lives = args[2]
            self.alienCnt = args[3]

            # Add round and score text
            self.roundText = self.create_text(
                80, 40, text=f"Round: {self.round}", fill="white",
                font="Helvetica 25 bold"
            )
            self.scoreText = self.create_text(
                Constants.WIDTH / 2, 40, text=f"Score: {self.score}",
                fill="white", font="Helvetica 25 bold"
            )

            # Restore aliens
            line = []
            for i in range(self.alienRow * self.alienCol):
                alienPos = args[4][i]
                if alienPos == "0":
                    alien = Alien(
                        self, 145 + 60 * i, 75 + 60 * i, 185 + 60 * i,
                        115 + 60 * i
                    )
                    alien.state("hidden")
                else:
                    alienCoords = alienPos.strip("[]").split(",")
                    x1, y1, x2, y2 = map(float, alienCoords)
                    alien = Alien(self, x1, y1, x2, y2)
                line.append(alien)
                if len(line) == 8:
                    self.aliens.append(line)
                    line = []

            # Restore bunkers
            bunkersCnt = args[5]
            for i, bunker in enumerate(self.bunkers):
                bunker.updateCount(bunkersCnt[i])

            # Restore cannon position
            cannonPos = str(args[6])
            cannonPos = cannonPos.replace("[", "").replace("]", "").split(",")
            x1, y1, x2, y2 = map(float, cannonPos)
            self.cannon = Cannon(self)
            self.cannon.resetBbox(x1, y1, x2, y2)

        # Add life indicators
        for i in range(self.lives):
            self.lifeArray.append(
                self.create_image(612.5 + 40 * i, 37.5, image=self.lifeImg)
            )

        # Start the game loop
        self.gameLoop()

    def gameLoop(self):
        """
        Main game loop to handle the continuous gameplay mechanics including:
        - Alien movements
        - Projectile firing (both by cannon and aliens)
        - Collision checks
        - Game state updates
        - Handling the in-game menu and checking for game over conditions

        This method recursively updates the game state at regular intervals.
        """
        if self.alienCnt == 0:
            # Reset the aliens if all have been destroyed
            self.resetAliens()

        # Move aliens in the current direction (right or left)
        if self.hitEdge % 2 == 0:
            self.moveAlienR()
        else:
            self.moveAlienL()

        # Move the cannon's laser if it is active (attacking)
        if self.attack:
            self.fire()

        # Handle cannon movement based on user input
        self.moveCannon()

        # Allow aliens to fire projectiles
        self.fireProjectile()

        # Check if the in-game menu is active
        if self.menuOn:
            # Pause the game and display a menu window
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
                """
                Resume the game by closing the menu and
                restarting the game loop.
                """
                self.menuOn = False
                menu.destroy()
                self.gameLoop()

            def save():
                """
                Save the current game state to a file named after the player.
                """
                filename = f"{self.playerName}.txt"
                with open(filename, "w") as f:
                    # Save player details, game level, and key configurations
                    f.write(self.playerName + '\n')
                    f.write(self.gameLevel + "\n")
                    f.write('_'.join(self.selectedKeys) + '\n')

                    # Save game round, score, lives, and alien count
                    f.write(str(self.round) + '\n')
                    f.write(str(self.score) + '\n')
                    f.write(str(self.lives) + '\n')
                    f.write(str(self.alienCnt) + '\n')

                    # Save aliens' states and positions
                    for row in range(self.alienRow):
                        for col in range(self.alienCol):
                            alienState = self.aliens[row][col].getState()
                            if alienState == 'hidden':
                                f.write("0\n")
                            else:
                                alienPos = self.aliens[row][col].getBbox()
                                f.write(str(alienPos) + "\n")

                    # Save bunker states
                    for bunker in self.bunkers:
                        f.write(str(bunker.getCount()) + '\n')

                    # Save cannon's position
                    f.write(str(self.cannon.getBbox()))
                menu.destroy()
                root.destroy()

            # Create buttons for menu options
            resumeBtn = Button(menu, text="Resume", command=resume)
            resumeBtn.pack()
            saveBtn = Button(menu, text="Save", command=save)
            saveBtn.pack()
            leaderboard = Button(menu, text="Leaderboard",
                                 command=openLeaderboard)
            leaderboard.pack()

        elif self.lives > 0:
            # Continue the game loop if the player has remaining lives
            self.after(30, self.gameLoop)
        else:
            # Game over: display the message and end the loop
            self.create_text(
                Constants.WIDTH // 2,
                Constants.HEIGHT // 2,
                text="Game Over",
                fill="red",
                font="Helvetica 30 bold"
            )
            # Update the leaderboard and display it
            self.updateLeaderboard()
            openLeaderboard()

    def resetAliens(self):
        """
        Reset the aliens for the next round by:
        - Clearing the current alien list
        - Reinitializing the alien grid
        - Updating round and game parameters
        """
        self.aliens = []  # Clear existing aliens
        self.alienCnt = self.alienRow * self.alienCol  # Reset alien count
        self.round += 1  # Increment the round count
        self.itemconfigure(
            self.roundText, text="Round: " + str(self.round)
        )  # Update round display
        self.hitEdge = 0  # Reset edge tracking

        # Increase the number of projectiles every 3 rounds
        if self.round != 0 and self.round % 3 == 0:
            self.projectilesNo += 1

        # Recreate aliens in their initial positions
        for row in range(self.alienRow):
            line = []
            for col in range(self.alienCol):
                # Position aliens in a grid formation
                alien = Alien(
                    self, 145 + 60 * col, 75 + 60 * row, 185 + 60 * col,
                    115 + 60 * row
                )
                line.append(alien)
            self.aliens.append(line)

    def moveCannon(self):
        """
        Move the cannon left or right smoothly within the screen boundaries.
        The direction is based on user input flags `cannonMoveLeft` or
        `cannonMoveRight`.
        """
        posCannon = self.cannon.getBbox()  # Get cannon's current position

        # Move left if the flag is set and cannon is not at the left boundary
        if self.cannonMoveLeft and posCannon[0] > 5:
            self.cannon.moveLeft()
        # Move right if the flag is set and cannon is not at the right boundary
        elif self.cannonMoveRight and posCannon[2] < Constants.WIDTH - 5:
            self.cannon.moveRight()

        # Check for collisions with aliens
        for row in range(self.alienRow):
            for col in range(self.alienCol):
                state = self.aliens[row][col].getState()  # Get alien's state
                if state != "hidden":  # Only check visible aliens
                    posAlien = self.aliens[row][col].getBbox()
                    # Check if laser intersects with alien
                    if (posAlien[0] < posCannon[2] and  # Alien's left is before cannon's right
                            posAlien[2] > posCannon[0] and  # Alien's right is after cannon's left
                            posAlien[1] < posCannon[3] and  # Alien's top is above cannon's bottom
                            posAlien[3] > posCannon[1]):  # Top of alien < Top of cannon < Bottom of alien
                        self.lives = 0

    def fire(self):
        """
        Fire the laser from the cannon and handle:
        - Collisions with bunkers or aliens
        - Laser movement and boundary checks
        """
        self.laser.state("normal")  # Activate laser
        self.laser.moveTo(0, -15)  # Move the laser upwards
        posLaser = self.laser.getPosition()  # Get laser's position

        # Remove laser if it reaches the top of the screen
        if posLaser[1] <= 0:
            self.laser.delete()  # Remove laser from the screen
            self.attack = False  # Reset attack flag

        # Check for collisions with bunkers
        for bunker in self.bunkers:
            posBunker = bunker.getPosition()  # Get bunker position
            if posBunker:  # Ensure the bunker is present
                if (posBunker[0] < posLaser[2] < posBunker[2] and
                        posBunker[1] < posLaser[1] < posBunker[3]):
                    self.laser.delete()  # Remove laser
                    bunker.decreaseCount()  # Decrease bunker health
                    self.attack = False  # Reset attack flag

        # Check for collisions with aliens
        for row in range(self.alienRow):
            for col in range(self.alienCol):
                state = self.aliens[row][col].getState()  # Get alien's state
                if state != "hidden":  # Only check visible aliens
                    posAlien = self.aliens[row][col].getBbox()
                    # Check if laser intersects with alien
                    if (posAlien[0] < posLaser[2] < posAlien[2] and
                            posAlien[1] < posLaser[1] < posAlien[3]):
                        self.aliens[row][col].state("hidden")  # Hide the alien
                        self.alienCnt -= 1  # Decrement alien count
                        self.score += 100  # Increase score by 100
                        self.itemconfigure(self.scoreText, text="Score: " + str(self.score))
                        # Flash the score text briefly
                        def flashScore(count=6):
                            """
                            Flash score text by toggling its visibility.
                            Count represents the number of state changes.
                            """
                            if count > 0:
                                if count % 2 == 0:
                                    currentColor = "red"
                                else:
                                    currentColor = "white"
                                self.itemconfig(self.scoreText, fill=currentColor)
                                self.after(     # Toggle every 50ms
                                    50, flashScore, count - 1
                                )
                        # Flash score text when the score is multiple of 1000
                        if self.score % 1000 == 0:
                            flashScore()
                        # If passingLaser is off, remove laser upon collision
                        if not self.passingLaser:
                            self.laser.delete()
                            self.attack = False

    def moveAlienR(self):
        """
        Move aliens one step to the right. If they hit the screen edge,
        update the `hitEdge` flag.
        """
        rightCol = self.getRightmostActiveColumn()  # Get rightmost column
        if rightCol == -1:
            return  # No aliens left, exit function

        # Get the rightmost alien's position
        for row in range(self.alienRow):
            if self.aliens[row][rightCol].getState() != "hidden":
                pos = self.aliens[row][rightCol].getBbox()
                break
        else:
            return  # No visible aliens found

        # Move visible aliens to the right
        for row in range(self.alienRow):
            for col in range(self.alienCol):
                if self.aliens[row][col].getState() != "hidden":
                    self.aliens[row][col].moveTo(5, 0)

        if pos[2] > Constants.WIDTH - 15:  # Check if aliens hit the edge
            self.hitEdge += 1

    def moveAlienL(self):
        """
        Move aliens one step to the left. If they hit the screen edge,
        move them down and reset the `hitEdge` flag.
        """
        leftCol = self.getLeftmostActiveColumn()  # Get leftmost column
        if leftCol == -1:
            return  # No aliens left, exit function

        # Get the leftmost alien's position
        for row in range(self.alienRow):
            if self.aliens[row][leftCol].getState() != "hidden":
                pos = self.aliens[row][leftCol].getBbox()
                break

        # Move visible aliens to the left
        for row in range(self.alienRow):
            for col in range(self.alienCol):
                if self.aliens[row][col].getState() != "hidden":
                    self.aliens[row][col].moveTo(-5, 0)

        if pos[0] < 15:  # Check if aliens hit the edge
            self.hitEdge += 1
            if self.hitEdge == 2:  # Move down after hitting both edges
                self.moveAlienDown()
                self.hitEdge = 0

    def getLeftmostActiveColumn(self):
        """
        Find the leftmost column with at least one visible alien.
        """
        for col in range(self.alienCol):
            for row in range(self.alienRow):
                if self.aliens[row][col].getState() != "hidden":
                    return col
        return -1  # No visible aliens found

    def getRightmostActiveColumn(self):
        """
        Find the rightmost column with at least one visible alien.
        """
        for col in range(self.alienCol - 1, -1, -1):
            for row in range(self.alienRow):
                if self.aliens[row][col].getState() != "hidden":
                    return col
        return -1  # No visible aliens found

    def moveAlienDown(self):
        """
        Move all visible aliens one step down.
        """
        for row in range(self.alienRow):
            for col in range(self.alienCol):
                if self.aliens[row][col].getState() != "hidden":
                    self.aliens[row][col].moveTo(0, 60)

    def fireProjectile(self):
        """
        Fire projectiles from up to 3 random visible aliens and check for
        collisions with bunkers, the cannon, or screen boundaries.
        """
        # Ensure we have a maximum of `projectilesNo` active projectiles
        if len(self.projectiles) < self.projectilesNo:
            # Randomly select an alien to fire a projectile
            x = random.randint(0, self.alienRow - 1)
            y = random.randint(0, self.alienCol - 1)

            # Only fire if the selected alien is visible
            if self.aliens[x][y].getState() != 'hidden':
                # Create a projectile and add it to the list
                newProjectile = Projectile(self, self.aliens[x][y])
                self.projectiles.append(newProjectile)

        # Move each projectile downward and check for collisions or boundaries
        for p in self.projectiles[:]:  # Work on a copy of the list
            p.moveTo(0, 3)  # Move projectile downward
            posProjectile = p.getPosition()

            # Check if the projectile goes out of bounds
            if posProjectile[3] >= Constants.HEIGHT:
                p.delete()
                self.projectiles.remove(p)
                continue  # Skip further checks for this projectile

            # Check collision with cannon
            posCannon = self.cannon.getBbox()
            if (posCannon[0] < posProjectile[2] < posCannon[2] and
                    posCannon[1] < posProjectile[3] < posCannon[3]):
                p.delete()
                self.projectiles.remove(p)

                # Flash the cannon briefly and reset its position
                def flashCannon(count=6):
                    """
                    Flash cannon by toggling its visibility.
                    Count represents the number of state changes.
                    """
                    if count > 0:
                        if count % 2 == 0:
                            current_state = "hidden"
                        else:
                            current_state = "normal"
                        self.cannon.state(current_state)
                        self.after(     # Toggle every 50ms
                            50, flashCannon, count - 1
                        )

                flashCannon()  # Start flashing effect
                self.cannon.resetCoords(    # Reset position
                    Constants.WIDTH / 2, 680
                )
                self.decreaseLife()  # Decrease life of cannon

            # Check collision with bunkers
            for bunker in self.bunkers:
                posBunker = bunker.getPosition()
                if posBunker:  # Ensure the bunker exists
                    if (posBunker[0] < posProjectile[2] < posBunker[2] and
                            posBunker[1] < posProjectile[3] < posBunker[3]):
                        p.delete()
                        self.projectiles.remove(p)
                        bunker.decreaseCount()  # Reduce bunker health
                        break  # Exit bunker collision checks

    def decreaseLife(self):
        """
        Decrease the player's lives when the cannon is hit by a projectile.
        Removes one life indicator from the screen.
        """
        if self.lives > 0:
            self.lives -= 1  # Decrement lives
            self.delete(self.lifeArray[self.lives])  # Remove life indicator
            self.lifeArray.pop()  # Remove from the list of life indicators

    def increaseLife(self):
        """
        Increase the player's lives, up to a maximum of 3.
        Adds a life indicator to the screen.
        """
        if self.lives < 3 and self.lives > 0:
            self.lives += 1  # Increment lives
            # Add new life indicator to the screen
            self.lifeArray.append(
                self.create_image(
                    612.5 + 40 * (self.lives - 1), 37.5, image=self.lifeImg
                )
            )

    def updateLeaderboard(self):
        """
        Update the leaderboard file with the current player's score.
        - Reads the existing leaderboard
        - Adds the current player's score
        - Sorts and writes the updated leaderboard back to the file
        """
        lb = {}  # Dictionary to store leaderboard data

        # Read existing leaderboard file
        with open("leaderboard.txt") as f:
            for line in f:
                key, val = line.split(':')
                lb[key] = int(val.strip())

        # Update the leaderboard with the current player's score
        lb[self.playerName] = self.score

        # Sort the leaderboard by score in descending order
        sortedScores = sorted(lb.items(), key=lambda x: x[1], reverse=True)
        sortedLb = dict(sortedScores)

        # Write the updated leaderboard back to the file
        with open("leaderboard.txt", 'w') as f:
            for key, value in sortedLb.items():
                f.write(f'{key}:{value}\n')


def openLeaderboard():
    """
    Opens a leaderboard window displaying player ranks, names, and scores.
    Reads the leaderboard data from a text file and displays it in a GUI.
    """
    lb = {}  # Dictionary to store leaderboard data
    with open("leaderboard.txt") as f:
        for line in f:
            key, val = line.split(':')
            lb[key] = val.removesuffix('\n')  # Remove newline characters

    # Create and configure the leaderboard window
    lbWin = Tk()
    lbWin.title("Leaderboard")
    ws = lbWin.winfo_screenwidth()
    hs = lbWin.winfo_screenheight()
    x = (ws / 2) - (400 / 2)
    y = (hs / 2) - (400 / 2)
    lbWin.geometry(f"{400}x{400}+{int(x)}+{int(y)}")
    lbWin.tk.call("tk", "scaling", 4.0)
    lbWin.resizable(False, False)

    # Title label
    title = Label(lbWin, text="Leaderboard", font='Helvetica 18 bold')
    title.pack(anchor="center")

    # Separator line
    separator = ttk.Separator(lbWin, orient="horizontal")
    separator.pack(fill="x", padx=20, pady=5)

    # Header row for the leaderboard table
    header = Frame(lbWin)
    header.pack(pady=5)
    Label(header, text="Rank", font=("Arial", 14, "bold"),
          width=10, anchor="center").pack(side="left")
    Label(header, text="Player", font=("Arial", 14, "bold"),
          width=15, anchor="center").pack(side="left")
    Label(header, text="Score", font=("Arial", 14, "bold"),
          width=10, anchor="center").pack(side="left")

    # Top 3 ranks are displayed in specific colors
    colors = ["#FFD700", "#C0C0C0", "#CD7F32"]  # Gold, Silver, Bronze
    i = 0
    for player, score in lb.items():
        row = Frame(lbWin)
        row.pack(pady=2)

        # Assign a specific color for top 3 players
        color = colors[i] if i < 3 else "black"

        Label(row, text=f"{i + 1}", font=("Arial", 14), width=10,
              anchor="center", fg=color).pack(side="left")
        Label(row, text=player, font=("Arial", 14), width=15,
              anchor="center", fg=color).pack(side="left")
        Label(row, text=str(score), font=("Arial", 14), width=10,
              anchor="center", fg=color).pack(side="left")
        i += 1
        if i > 11:  # Display up to 12 entries
            break


def keyPressed(event):
    """
    Handles key press events, controlling cannon movement, firing,
    and handling game shortcuts.
    """
    global board
    posCannon = board.cannon.getBbox()
    board.pressedKeys.add(event.keysym)

    # If 'i' and 'b' are pressed, reset and add bunkers
    if 'i' in board.pressedKeys and 'b' in board.pressedKeys:
        for bunker in board.bunkers:
            bunker.delete()
        board.bunkers.clear()
        for i in range(3):
            board.bunkers.append(Bunker(board, 75 + 242.5 * i,
                                        500, 200 + 242.5 * i, 550, 300))

    # If 'p' and 'l' are pressed, enable passing laser
    elif 'p' in board.pressedKeys and 'l' in board.pressedKeys:
        board.passingLaser = True

    # If 'i' and 'l' are pressed, increase life
    elif 'i' in board.pressedKeys and 'l' in board.pressedKeys:
        board.increaseLife()

    # Move cannon left if the left key is pressed and within bounds
    elif event.keysym == board.selectedKeys[0] and posCannon[0] > 5:
        board.cannonMoveLeft = True

    # Move cannon right if the right key is pressed and within bounds
    elif (event.keysym == board.selectedKeys[1]
          and posCannon[2] < Constants.WIDTH - 5):
        board.cannonMoveRight = True

    # Fire laser if the fire key is pressed and attack is not active
    elif event.keysym == board.selectedKeys[2] and not board.attack:
        board.attack = True
        board.laser = Laser(board, board.cannon)
        board.fire()

    # Open menu if 'm' is pressed
    elif event.keysym == 'm':
        board.menuOn = True
        board.cannonMoveLeft = False
        board.cannonMoveRight = False

    # Open fake working image for debug purposes
    elif event.keysym in ('Escape', "B"):
        board.menuOn = True
        showFakeWorkingImage()


def keyReleased(event):
    """
    Handles key release events to stop cannon movement.
    """
    global board
    board.pressedKeys.discard(event.keysym)

    # Stop moving left when left key is released
    if event.keysym == board.selectedKeys[0]:
        board.cannonMoveLeft = False

    # Stop moving right when right key is released
    elif event.keysym == board.selectedKeys[1]:
        board.cannonMoveRight = False


def showFakeWorkingImage():
    """
    Opens a full-screen window displaying a placeholder "working" image.
    """
    # Create a new top-level window
    fakeWorkingWindow = Toplevel()
    fakeWorkingWindow.title("Working...")

    # Get screen dimensions and set window size
    ws = fakeWorkingWindow.winfo_screenwidth()
    hs = fakeWorkingWindow.winfo_screenheight()
    fakeWorkingWindow.geometry(f"{ws}x{hs-150}")
    fakeWorkingWindow.tk.call("tk", "scaling", 4.0)
    fakeWorkingWindow.resizable(False, False)

    # Load and resize the image to fit the screen
    fakeImage = Image.open("fakeWorkingImage.png")
    fakeImage.thumbnail((ws, hs), Image.Resampling.LANCZOS)

    # Convert the image to PhotoImage for Tkinter
    fakePhoto = ImageTk.PhotoImage(fakeImage)

    # Keep reference to avoid garbage collection
    fakeWorkingWindow.fakePhoto = fakePhoto

    # Add the image to the window
    fakeLabel = Label(fakeWorkingWindow, image=fakePhoto)
    fakeLabel.pack(expand=True, fill="both")


def openPopup():
    """
    Opens a sign-in popup window for players to input their name, select
    control keys, and choose game level. It also provides options to load
    a saved game or view the leaderboard.
    """
    # Create the sign-in window
    initWin = Toplevel()
    initWin.title("Sign In")

    # Center the window on the screen
    ws = initWin.winfo_screenwidth()
    hs = initWin.winfo_screenheight()
    x = (ws / 2) - (500 / 2)
    y = (hs / 2) - (600 / 2)
    initWin.geometry(f"{500}x{600}+{int(x)}+{int(y)}")
    initWin.tk.call("tk", "scaling", 4.0)
    initWin.resizable(False, False)

    # Add label and entry for the user's name
    nameLabel = Label(initWin, text="Enter your name:",
                       font='Helvetica 18 bold')
    nameEntry = ttk.Entry(initWin)
    nameLabel.grid(row=0, column=0, padx=(20, 10), pady=(20, 20))
    nameEntry.grid(row=0, column=1, padx=10, pady=(20, 20), sticky="W")

    # Add radio buttons for control key options
    keyOption = Label(initWin, text="Choose control keys:",
                       font='Helvetica 18 bold')
    keyOption.grid(row=1, column=0, padx=(20, 3), pady=(0, 3))

    # Default key setting
    movementKeys = StringVar(value="Left_Right_space")

    r1 = Radiobutton(initWin, text="Use arrow keys to move, space to fire",
                     variable=movementKeys, value="Left_Right_space")
    r2 = Radiobutton(initWin, text="Use A/D to move, space to fire",
                     variable=movementKeys, value="a_d_space")
    r3 = Radiobutton(initWin, text="Use A/D to move, W to fire",
                     variable=movementKeys, value="a_d_w")
    r1.grid(row=1, column=1, padx=3, pady=3, sticky="W")
    r2.grid(row=2, column=1, padx=3, pady=3, sticky="W")
    r3.grid(row=3, column=1, padx=3, pady=(3, 20), sticky="W")

    # Add radio buttons for game level selection
    level = StringVar(value="beginner")  # Default value

    levelOption = Label(initWin, text="Choose the level:",
                        font='Helvetica 18 bold')
    level1 = Radiobutton(initWin, text="Beginner",
                         variable=level, value="beginner")
    level2 = Radiobutton(initWin, text="Advanced User",
                         variable=level, value="advanced")
    levelOption.grid(row=4, column=0, padx=(20, 3), pady=(0, 3))
    level1.grid(row=4, column=1, padx=3, pady=3, sticky="W")
    level2.grid(row=5, column=1, padx=3, pady=(3, 20), sticky="W")

    # Submit button logic
    def submit():
        """
        Handles the submission of the player's name, selected controls, and
        game level. Starts the game or shows an error message if the name is
        missing.
        """
        playerName = nameEntry.get()
        if not playerName.strip():  # Check if name is empty
            name = Toplevel(initWin)
            ws = name.winfo_screenwidth()
            hs = name.winfo_screenheight()
            x = (ws / 2) - (400 / 2)
            y = (hs / 2) - (100 / 2)
            name.geometry(f"{400}x{100}+{int(x)}+{int(y)}")
            name.tk.call("tk", "scaling", 4.0)
            name.resizable(False, False)
            name.title("Name")
            t = ttk.Label(name, text="You need to enter your NAME",
                          font='Mistral 18 bold')
            t.pack(pady=35, anchor="center")
        else:
            # Retrieve the selected values
            selectedKeys = movementKeys.get()
            gameLevel = level.get()

            # Debugging outputs
            print(f"Player Name: {playerName}")
            print(f"Selected Keys: {selectedKeys}")
            print(f"Game Level: {gameLevel}")

            # Close the sign-in window and start the game
            initWin.destroy()
            startGame(playerName, selectedKeys, gameLevel)

    # Create and place the submit button
    submitButton = Button(initWin, text="Start a new game", 
                          command=submit, font='Helvetica 16 bold')
    submitButton.grid(row=6, column=1, padx=3, pady=3)

    # Create and place the leaderboard button
    lbButton = Button(initWin, text="Leaderboard",
                      command=openLeaderboard, font='Helvetica 16 bold')
    lbButton.grid(row=6, column=0, padx=3, pady=3)

    # Load saved game files
    savedFiles = []
    for x in os.listdir():
        if (x.endswith(".txt") and x != "leaderboard.txt"
                and x != "imgReference.txt"):
            savedFiles.append(x)

    # Display saved game files in a listbox
    fileList = Listbox(initWin)
    for i in range(len(savedFiles)):
        fileList.insert(i, savedFiles[i])
    fileList.grid(row=7, column=0, padx=(20, 0), pady=(50, 0))

    def load():
        """
        Loads a saved game file and starts the game from the saved state.
        """
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
            totalAlienCnt = 16 if gameLevel == "beginner" else 32
            for i in range(totalAlienCnt):
                aliensPos.append(txt[i + 7].removesuffix('\n'))
            bunkersCnt = []
            for i in range(3):
                bunkersCnt.append(
                    int(txt[7 + totalAlienCnt + i].removesuffix('\n'))
                )
            cannonPos = txt[7 + totalAlienCnt + 3].removesuffix('\n')

            # Close the window and start the game
            initWin.destroy()
            startGame(playerName, selectedKeys, gameLevel,
                       round, score, lives, alienCnt, aliensPos,
                       bunkersCnt, cannonPos)

    # Create and place the load button
    loadButton = Button(initWin, text="Load saved file", command=load)
    loadButton.grid(row=8, column=0, padx=(20, 0), pady=(10, 0))


def startGame(player_name, selected_keys, gameLevel, *args):
    """
    Initializes and starts the game based on the provided player details
    and game state. If arguments for the game state are provided, it loads
    the saved game state.
    """
    global board

    # Create the main game window
    window = Toplevel()
    window.title("Space Invaders")

    # Center the window on the screen
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws / 2) - (Constants.WIDTH / 2)
    y = (hs / 2) - (Constants.HEIGHT / 2)
    window.geometry(f"{Constants.WIDTH}x{Constants.HEIGHT}+{int(x)}+{int(y)}")
    window.tk.call("tk", "scaling", 4.0)
    window.resizable(False, False)

    # Start the game with player details
    if len(args) == 0:
        board = gameBoard(window, player_name, selected_keys, gameLevel)
    else:
        board = gameBoard(window, player_name, selected_keys, gameLevel, *args)

    # Bind keys for controlling the game
    window.bind("<KeyPress>", keyPressed)
    window.bind("<KeyRelease>", keyReleased)

    # Start the Tkinter event loop
    window.mainloop()


# Initialize main Tkinter window
root = Tk()
root.withdraw()  # Hide the main window initially
openPopup()  # Show the popup for player sign-in and settings
root.mainloop()
