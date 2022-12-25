import sys
from math import *
from os import *
from random import *
from tkinter import Tk, messagebox

import pygame

screenWidth = 800
screenHeight = 600
board = []


class Tile:
    def __init__(self, loc, col):
        self.width = 10
        self.height = 10
        self.color = col
        self.value = randint(1, 10)
        self.pos = (loc[0] * 10, loc[1] * 10)
        self.loc = loc
        self.occupied = False
        self.owner = None
        self.capital = False

    def changeColor(self, col):
        self.color = col

    def draw(self, screen):
        pygame.draw.rect(
            screen, self.color, (self.pos[0], self.pos[1], self.width, self.height)
        )


class Kingdom:
    def __init__(self, startTile: Tile):
        self.land = [startTile]
        self.tile_posns = set([startTile.pos])
        self.capital_pos = startTile.pos
        self.strength = randint(1, 5)
        self.piety = randint(1, 5)
        self.belligerence = randint(1, 10)
        self.pacificity = randint(1, 4)
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.wins = 0
        self.battles = 0
        self.alive = True
        startTile.changeColor((255, 255, 255))
        startTile.occupied = True
        startTile.capital = True
        startTile.owner = self

    def loseTile(self, tile: Tile):
        self.strength -= uniform(1.0, 10.0)
        self.tile_posns.remove(tile.pos)
        self.land.pop(self.land.index(tile))

    def gainTile(self, tile: Tile):
        if not tile.capital:
            tile.changeColor(self.color)
            tile.occupied = True
            if tile.owner != self:
                self.strength += uniform(1.0, 10.0)
            tile.owner = self
            self.land.append(tile)
            self.tile_posns.add(tile.pos)

    def tileBattle(self, tile: Tile):
        if tile.occupied and tile.owner != self:
            self.battles += 1
            if (
                self.strength * self.piety
                > tile.owner.strength * tile.owner.piety * uniform(0.5, 1.5)
            ):
                self.wins += 1
                if not tile.capital:
                    self.gainTile(tile)
                    tile.owner.loseTile(tile)
                else:
                    tile.capital = False
                    tile.changeColor(self.color)
                    tile.owner.alive = False
                    old_owner = tile.owner
                    for t in tile.owner.land:
                        self.gainTile(t)
                    old_owner.land = []
                    old_owner.tile_posns = set()
                    old_owner.strength = 0
                    old_owner.piety = 0
            else:
                self.strength = floor(0.9 * self.strength)
                self.piety = floor(0.95 * self.piety)
                shuffle(self.land)
        else:
            self.gainTile(tile)

    def expand(self):
        finalList = self.land[len(self.land) - 1].loc
        available = []
        available.append(
            next((x for x in board if x.loc == [finalList[0] + 1, finalList[1]]), None)
        )
        available.append(
            next((x for x in board if x.loc == [finalList[0] - 1, finalList[1]]), None)
        )
        available.append(
            next((x for x in board if x.loc == [finalList[0], finalList[1] - 1]), None)
        )
        available.append(
            next((x for x in board if x.loc == [finalList[0], finalList[1] + 1]), None)
        )
        available.append(
            next(
                (x for x in board if x.loc == [finalList[0] + 1, finalList[1] + 1]),
                None,
            )
        )
        available.append(
            next(
                (x for x in board if x.loc == [finalList[0] - 1, finalList[1] + 1]),
                None,
            )
        )
        available.append(
            next(
                (x for x in board if x.loc == [finalList[0] + 1, finalList[1] - 1]),
                None,
            )
        )
        available.append(
            next(
                (x for x in board if x.loc == [finalList[0] - 1, finalList[1] - 1]),
                None,
            )
        )

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

    def pray(self):
        self.piety += uniform(0.1, 1)

    def move(self):
        if randint(1, 5) <= self.pacificity:
            self.pray()
        else:
            self.strength += self.belligerence
            self.expand()


def top_kings(king_lst):
    return sorted(king_lst, key=lambda k: -1 * k.strength * k.piety)[0:5]


def render_high_scores(king: Kingdom, i, font, screen):
    screen.blit(font.render("Top Scores", True, (255, 255, 255)), (620, 25))
    screen.blit(
        font.render(
            "{}".format(king.strength * king.piety),
            True,
            king.color,
        ),
        (620, 50 + 20 * i),
    )

    screen.blit(font.render("Top Strengths", True, (255, 255, 255)), (620, 175))
    screen.blit(
        font.render(
            "{}".format(king.strength),
            True,
            king.color,
        ),
        (620, 200 + 20 * i),
    )

    screen.blit(font.render("Top Piety", True, (255, 255, 255)), (620, 325))
    screen.blit(
        font.render(
            "{}".format(king.piety),
            True,
            king.color,
        ),
        (620, 350 + 20 * i),
    )

    screen.blit(font.render("Top Records", True, (255, 255, 255)), (620, 475))
    screen.blit(
        font.render(
            "{}/{}".format(king.wins, king.battles),
            True,
            king.color,
        ),
        (620, 500 + 20 * i),
    )


def run_game():
    Tk().wm_withdraw()
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

    font = pygame.font.SysFont(None, 24)

    crowns = []
    for i in range(1, 4):
        temp_crown = pygame.image.load(f"king{i}.png")
        temp_crown = pygame.transform.scale(temp_crown, (50, 20))
        crowns.append(temp_crown)

    pygame.display.set_icon(crowns[0])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                pos = (round(m_x / 10) * 10, round(m_y / 10) * 10)
                for king in kingdoms:
                    if king.alive and pos in king.tile_posns:
                        messagebox.showinfo(
                            "OK",
                            f"""
                            Land Tiles: {len(king.tile_posns)}
                            Strength: {king.strength}
                            Piety: {king.piety}
                            Pacificity: {king.pacificity}
                            Belligerence: {king.belligerence}
                            """,
                        )
                        break
        clock.tick(60)

        for tile in board:
            tile.draw(screen)

        for king in kingdoms:
            if king.alive:
                king.move()

        pygame.draw.rect(screen, (0, 0, 0), (600, 0, screenWidth, screenHeight))
        to_rank = top_kings(kingdoms)
        for i, king in enumerate(to_rank):
            if i < len(crowns):
                screen.blit(
                    crowns[i], (king.capital_pos[0] - 20, king.capital_pos[1] - 20)
                )
            render_high_scores(king, i, font, screen)
        pygame.display.update()


if __name__ == "__main__":
    run_game()
