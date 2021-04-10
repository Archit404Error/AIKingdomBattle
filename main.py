import pygame
from random import *
from os import *

screenWidth = 600
screenHeight = 600
board = []

class Tile:
    def __init__(self, loc, col):
        self.width = 10
        self.height = 10
        self.color = col
        self.value = randint(1, 10)
        self.pos = [loc[0] * 10, loc[1] * 10]
        self.loc = loc
        self.occupied = False
        self.owner = None
        self.capital = False

    def changeColor(self, col):
        self.color = col

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.width, self.height))

class Kingdom:
    def __init__(self, startTile):
        self.land = [startTile]
        self.strength = randint(1, 5)
        self.wisdom = randint(1, 5)
        self.piety = randint(1, 5)
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.alive = True
        startTile.changeColor((255, 255, 255))
        startTile.occupied = True
        startTile.capital = True
        startTile.owner = self

    def loseTile(self, tile):
        self.strength -= 1
        self.land.pop(self.land.index(tile))

    def gainTile(self, tile):
        if not tile.capital:
            tile.changeColor(self.color)
            tile.occupied = True
            tile.owner = self
            self.strength += 1
            self.land.append(tile)

    def tileBattle(self, tile):
        if tile.occupied and tile.owner != self:
            if self.strength > tile.owner.strength:
                if not tile.capital:
                    self.gainTile(tile)
                    tile.owner.loseTile(tile)
                else:
                    tile.capital = False
                    tile.changeColor(self.color)
                    for i in board:
                        if i.color == tile.owner.color:
                            self.gainTile(i)
                        tile.owner.land = []
                        tile.owner.strength = 0
                        tile.owner.alive = False
            else:
                shuffle(self.land)
        else:
            self.gainTile(tile)

    def expand(self):
        finalList = self.land[len(self.land) - 1].loc
        available = []
        available.append(next((x for x in board if x.loc == [finalList[0] + 1, finalList[1]]), None))
        available.append(next((x for x in board if x.loc == [finalList[0] - 1, finalList[1]]), None))
        available.append(next((x for x in board if x.loc == [finalList[0], finalList[1] - 1]), None))
        available.append(next((x for x in board if x.loc == [finalList[0], finalList[1] + 1]), None))
        available.append(next((x for x in board if x.loc == [finalList[0] + 1, finalList[1] + 1]), None))
        available.append(next((x for x in board if x.loc == [finalList[0] - 1, finalList[1] + 1]), None))
        available.append(next((x for x in board if x.loc == [finalList[0] + 1, finalList[1] - 1]), None))
        available.append(next((x for x in board if x.loc == [finalList[0] - 1, finalList[1] - 1]), None))

        available = list(filter((None), available))
        notselfowned = []
        for t in available:
            if t.owner != self:
                notselfowned.append(t)
        for i in range(len(available) - 1):
            if len(notselfowned) == 0:
                tile = available[randint(0, len(available) - 1)]
            else:
                tile = notselfowned[randint(0, len(notselfowned) - 1)]
                notselfowned.pop(notselfowned.index(tile))
            self.tileBattle(tile)
            available.pop(available.index(tile))

    def move(self, val):
        if val == 0:
            self.expand()
        if val == 1:
            self.research()

def runGame():
    pygame.init()
    pygame.display.set_caption("AI Kingdom Battle")
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    clock = pygame.time.Clock()

    for i in range(60):
        for j in range(60):
            loc = [i, j]
            board.append(Tile(loc, (0, 0, 0)))

    kingdoms = []
    for i in range(100):
        kingdoms.append(Kingdom(board[randint(0, len(board) - 1)]))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
        clock.tick(60)
        for tile in board:
            tile.draw(screen)
        for king in kingdoms:
            if king.alive:
                king.expand()
        pygame.display.update()
    pygame.display.flip()
if __name__ == "__main__":
    runGame()
