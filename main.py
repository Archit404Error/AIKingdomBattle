import sys
from math import *
from os import *
from random import *
from tkinter import Tk, messagebox

import pygame

screen_width = 800
screen_height = 600
tile_width = 60
tile_height = 60
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
        self.edge_tiles = set()
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
        self.add_edge_tiles(startTile)

    def add_edge_tiles(self, tile: Tile):
        x, y = tile.loc
        offsets = [1, 0, -1, 0, 1, 1, -1, -1, 1]
        for i in range(len(offsets) - 1):
            if (
                0 <= (xn := x + offsets[i]) < len(board)
                and 0 <= (yn := y + offsets[i + 1]) < len(board[0])
                and (ntile := board[xn][yn]).owner != self
            ):
                self.edge_tiles.add(ntile)

    def capitulate(self):
        self.alive = False
        self.land = []
        self.tile_posns = set()
        self.strength = 0
        self.piety = 0
        self.edge_tiles = set()

    def lose_tile(self, tile: Tile):
        self.strength -= uniform(1.0, 10.0)
        self.tile_posns.remove(tile.pos)
        self.land.pop(self.land.index(tile))

    def gain_tile(self, tile: Tile):
        if tile in self.edge_tiles:
            self.edge_tiles.remove(tile)
        tile.changeColor(self.color)
        tile.occupied = True
        self.strength += uniform(1.0, 10.0)
        tile.owner = self
        self.land.append(tile)
        self.tile_posns.add(tile.pos)
        self.add_edge_tiles(tile)

    def tile_battle(self, tile: Tile):
        if tile.occupied and tile.owner != self:
            self.battles += 1
            if (
                self.strength * self.piety
                > tile.owner.strength * tile.owner.piety * uniform(0.5, 1.5)
            ):
                self.wins += 1
                if not tile.capital:
                    tile.owner.lose_tile(tile)
                    self.gain_tile(tile)
                else:
                    tile.capital = False
                    tile.changeColor(self.color)
                    old_owner = tile.owner
                    for t in tile.owner.land:
                        self.gain_tile(t)
                    old_owner.capitulate()
            else:
                self.strength = floor(0.9 * self.strength)
                self.piety = floor(0.95 * self.piety)
        else:
            self.gain_tile(tile)

    def expand(self):
        to_expand = None
        min_str = float("inf")
        rearranged = list(self.edge_tiles)
        shuffle(rearranged)
        for edge in rearranged:
            if not edge.occupied:
                self.tile_battle(edge)
                return
            if edge.capital:
                self.tile_battle(edge)
                return
            if edge.owner.strength <= min_str:
                min_str = edge.owner.strength
                to_expand = edge
        if to_expand:
            self.tile_battle(to_expand)

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


def run_game(num_kings):
    Tk().wm_withdraw()
    pygame.init()
    pygame.display.set_caption("AI Kingdom Battle")
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    for i in range(tile_width):
        board.append([])
        for j in range(tile_height):
            board[i].append(Tile([i, j], (0, 0, 0)))

    kingdoms = []
    for i in range(num_kings):
        kingdoms.append(
            Kingdom(board[randint(0, len(board) - 1)][randint(0, len(board[0]) - 1)])
        )

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
                            Tiles on Map: {tile_width * tile_height}
                            Strength: {king.strength}
                            Piety: {king.piety}
                            Pacificity: {king.pacificity}
                            Belligerence: {king.belligerence}
                            """,
                        )
                        break
        clock.tick(60)

        for row in board:
            for tile in row:
                tile.draw(screen)

        for king in kingdoms:
            if king.alive:
                if len(king.land) == 1 and king.wins > 10:
                    king.alive = False
                    continue
                king.move()

        pygame.draw.rect(screen, (0, 0, 0), (600, 0, screen_width, screen_height))
        to_rank = top_kings(kingdoms)
        for i, king in enumerate(to_rank):
            if i < len(crowns):
                screen.blit(
                    crowns[i], (king.capital_pos[0] - 20, king.capital_pos[1] - 20)
                )
            render_high_scores(king, i, font, screen)
        pygame.display.update()


if __name__ == "__main__":
    run_game(20)
