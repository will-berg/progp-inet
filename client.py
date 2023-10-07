import sys
import math
import socket
import json
import pygame
from pygame.locals import *

# Connection details
HOST = '127.0.0.1'
PORT = 65432

# Game initialization
pygame.init()
pygame.font.init()
VELOCITY = 2
FONT = 16   # Represents the size of a hash (#) and a player (@)

# Display initialization
white = (255, 255, 255)
size = width, height = 800, 300
screen = pygame.display.set_mode(size)
pygame.display.set_caption("INET GAME")
font = pygame.font.SysFont("timesnewroman", FONT)
player_icon = font.render('@', True, white)
obstacle = font.render('#', True, white)


"""
Draw the map with obstacles (#) in the specified positions; creating a floor and a ceiling
as well as two walls with openings two hashes wide
"""
def draw_map():
    for x in range(width):
        for y in range (height):
            if (y == 20 and x % FONT == 0) or (y == 280 and x % FONT == 0):
                screen.blit(obstacle, (x, y))
            if (x == 350 and y % FONT == 0 and y > (20 + FONT*2) and y < 280) or (x == (450 + 18) and y % FONT == 0 and y > 20 and y < 280 - FONT*2):
                screen.blit(obstacle, (x, y))


class Item():
    def __init__(self, xPos, yPos, icon, range):
        self.xPos = xPos
        self.yPos = yPos
        self.icon = pygame.image.load(icon)
        self.range = range


class Player():
    def __init__(self, xPos, yPos, hasItem=False):
        self.xPos = xPos
        self.yPos = yPos
        self.hasItem = hasItem

    def update_pos(self, newXPos, newYPos):
        self.xPos = newXPos
        self.yPos = newYPos


# Use distance formula to calculate distance between two objects with coordinate attributes
def distance(obj1, obj2):
    return math.floor(math.sqrt(pow((obj2.xPos - obj1.xPos), 2) + pow((obj2.yPos - obj1.yPos), 2)))


"""
Move the player according to the registered keypresses, check for collisions with
the other player as well as collisions with the floor, the ceiling and the walls
"""
def move(p1, p2):
    key = pygame.key.get_pressed()

    if key[pygame.K_LEFT]:
        # Update the x coordinate for the player when the left key is pressed
        p1.xPos -= VELOCITY
        # Reset the x coordinate if the player comes in contact with the other player
        if distance(p1, p2) <= FONT or p1.xPos == 0:
            p1.xPos += VELOCITY
        # Reset the x coordinate if the player comes in contact with the left or right wall
        if ((p1.xPos == 350 + FONT/2 and p1.yPos > 20 + FONT*2) or (p1.xPos == (450 + 18) + FONT/2 and p1.yPos < 280 - FONT*2)):
            p1.xPos += VELOCITY

    if key[pygame.K_RIGHT]:
        p1.xPos += VELOCITY
        if distance(p1, p2) <= FONT or p1.xPos == 800 - FONT:
            p1.xPos -= VELOCITY
        if ((p1.xPos == 350 - FONT and p1.yPos > 20 + FONT*2) or (p1.xPos == (450 + 18) - FONT and p1.yPos < 280 - FONT*2)):
            p1.xPos -= VELOCITY

    if key[pygame.K_UP]:
        p1.yPos -= VELOCITY
        if distance(p1, p2) <= FONT or p1.yPos == 20 + FONT/2:
            p1.yPos += VELOCITY
        if (p1.xPos > (450 + 18) - FONT and p1.xPos < 450 + 18 + FONT/2 and p1.yPos < 280 - FONT*2):
            p1.yPos += VELOCITY

    if key[pygame.K_DOWN]:
        p1.yPos += VELOCITY
        if distance(p1, p2) <= FONT or p1.yPos == 280 - FONT:
            p1.yPos -= VELOCITY
        if (p1.xPos > 350 - FONT and p1.xPos < 350 + FONT/2 and p1.yPos > 20 + FONT*2):
            p1.yPos -= VELOCITY


"""
If the player has the sword, is within striking distance (determined by range attribute of item instance), and presses
space, the other player is killed and the game is over. Send a message to the server with gameOver set to 1 to signify this.
"""
def kill(p1, p2, item):
    if distance(p1, p2) <= item.range and (p1.hasItem == True):
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            p1_pos = { "xPos": p1.xPos, "yPos": p1.yPos, "gameOver": 1}
            s.sendall(bytes(json.dumps(p1_pos, indent = 4), encoding="utf-8"))
            game_over()


# Display the game over screen until the return key (ENTER) is pressed
def game_over():
    str = "Game Over! You win! Press enter to quit game"
    goFont = pygame.font.SysFont("timesnewroman", FONT * 2)
    goStr = goFont.render(str, True, white)
    screen.fill((0, 0, 0))
    pygame.event.clear()
    while True:
        screen.blit(goStr, (70, 150))
        pygame.display.update()
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_RETURN:
                pygame.quit()
                sys.exit()
                
# Display the game over screen when your opponent wins
def game_over_lose():
    str = "Game Over! You lose! Press enter to quit game"
    goFont = pygame.font.SysFont("timesnewroman", FONT * 2)
    goStr = goFont.render(str, True, white)
    screen.fill((0, 0, 0))
    pygame.event.clear()
    while True:
        screen.blit(goStr, (70, 150))
        pygame.display.update()
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_RETURN:
                pygame.quit()
                sys.exit()


# Draw the positions of the players on the screen and then update the display
def redraw(p1, p2, sword, text):
    playerpos1 = (p1.xPos, p1.yPos) # Put the players coordinates into tuples
    playerpos2 = (p2.xPos, p2.yPos) # -- || --
    item_pos = (sword.xPos, sword.yPos)
    screen.fill((0, 0, 0))
    draw_map()
    screen.blit(player_icon, playerpos1)
    screen.blit(player_icon, playerpos2)
    screen.blit(text, (550, 50))
    # Only draw the item if no player has picked it up
    if p1.hasItem == False and p2.hasItem == False:
        screen.blit(sword.icon, item_pos)
    pygame.display.update()


# Open client side socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    s.connect((HOST, PORT))

    # Get starting position for your player from the server
    p1StartPos = json.loads(s.recv(1024))

    # Create a player with the received starting positions
    p1 = Player(p1StartPos["xPos"], p1StartPos["yPos"])
    p2 = Player(750, 150)
    sword = Item(400, 150, "sword.png", 20)

    # Initiate a clock to control tickrate
    clock = pygame.time.Clock()
    text = font.render("", False, white)
   # boolean value keeping track of if the game is running
    is_running = True
    while is_running:
        # Tickrate is 60, send position to server 60 times/second
        clock.tick(60)
        p1_pos = { "xPos": p1.xPos, "yPos": p1.yPos, "gameOver": 0}
        # Send your player's position to the server
        s.sendall(bytes(json.dumps(p1_pos, indent = 4), encoding="utf-8"))
        # Read the other players position from the server
        received = s.recv(1024)
        data_obj = json.loads(received)
        # Update the other players position from the server
        p2.update_pos(data_obj["xPos"], data_obj["yPos"])
        # Check if a player has won
        if data_obj["gameOver"] == 1:
            game_over_lose()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                pygame.quit()

        move(p1, p2)
        # Check for item pick-up after the player has moved
        if p1.hasItem == False and p2.hasItem == False:
            if distance(p1, sword) <= FONT:
                p1.hasItem = True
                str = "You hold the sword"
                text = font.render(str, False, white)
            if distance(p2, sword) <= FONT:
                p2.hasItem = True
                str = "Your opponent holds the sword"
                text = font.render(str, False, white)

        redraw(p1, p2, sword, text)
        kill(p1, p2, sword)
    s.close()


if __name__ == "__main__":
    main()
