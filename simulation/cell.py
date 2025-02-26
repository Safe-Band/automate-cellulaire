import math
import numpy as np
import pygame as pg
from enum import Enum


class TYPE_CELL(Enum):
    VIDE = 0
    MUR = 1
    PORTE = 2
    OCCUPED = 3
    PRODUCTOR = 4
    ATTRACTOR1 = 5
    ATTRACTOR2 = 6
    ATTRACTOR3 = 7
    ATTRACTOR4 = 8

class Cell:
    """
    class that represents a cell in the grid

    attributes:

    - x : int : x position of the cell
    - y : int : y position of the cell
    - taille : int : size of the cell
    - grille : Grille : the grid the cell belongs to
    - distance : list : list of distances to the different classes
    - current_state : TYPE_CELL : current state of the cell
    - player : Player : player on the cell
    - inertie : int : inertia of the player on the cell


    methods:

    - regles_de_comportement : apply the rules of the simulation
    - empty : set the cell to empty
    - set_wall : set the cell to wall
    - set_door : set the cell to door
    - is_occuped : check if the cell is occuped
    - is_empty : check if the cell is empty
    - is_wall : check if the cell is a wall
    - is_door : check if the cell is a door
    - draw : draw the cell on the screen
    - highlight : highlight the cell on the screen
    - pass_epoch : pass an epoch
    - set_productor : set the cell to productor
    - change_attractor : change the attractor of the cell

    """

    def __init__(self, x, y, taille, grille):
        self.x = x
        self.y = y
        self.taille = taille
        self.grille = grille
        self.distance = np.array(
            [
                math.sqrt((grille.x0[i] - x) ** 2 + (grille.y0[i] - y) ** 2)
                for i in range(len(grille.x0))
            ]
        )
        self.current_state = TYPE_CELL.VIDE
        self.player = None
        self.inertie = 0

    def empty(self):
        self.current_state = TYPE_CELL.VIDE
        self.joueur = None

    def set_wall(self):
        if self.current_state == TYPE_CELL.OCCUPED:
            self.empty()
        self.current_state = TYPE_CELL.MUR

    def set_door(self):
        if self.current_state == TYPE_CELL.OCCUPED:
            self.empty()
        self.current_state = TYPE_CELL.PORTE

    def set_productor(self):
        if self.current_state == TYPE_CELL.OCCUPED:
            self.empty()
        self.current_state = TYPE_CELL.PRODUCTOR

    def change_attractor(self, nb_attract):
        if self.current_state == TYPE_CELL.OCCUPED:
            self.empty()
        self.grille.cellule(
            self.grille.x0[nb_attract], self.grille.y0[nb_attract]
        ).empty()
        self.grille.x0[nb_attract] = self.x
        self.grille.y0[nb_attract] = self.y
        self.grille.change_distance(self.grille.x0, self.grille.y0)
        match nb_attract:
            case 0:
                self.current_state = TYPE_CELL.ATTRACTOR1
            case 1:
                self.current_state = TYPE_CELL.ATTRACTOR2

            case 2:
                self.current_state = TYPE_CELL.ATTRACTOR3
            case 3:
                self.current_state = TYPE_CELL.ATTRACTOR4

    def is_occuped(self):
        return self.current_state == TYPE_CELL.OCCUPED

    def is_empty(self):
        return self.current_state == TYPE_CELL.VIDE

    def is_wall(self):
        return self.current_state == TYPE_CELL.MUR

    def is_door(self):
        return self.current_state == TYPE_CELL.PORTE

    def is_productor(self):
        return self.current_state == TYPE_CELL.PRODUCTOR

    def draw(self, fenetre: pg.Surface):
        match self.current_state:
            case TYPE_CELL.OCCUPED:
                if self.grille.tomato_flag:
                    fenetre.fill(
                        (255, 255, 255),
                        (
                            self.x * self.taille,
                            self.y * self.taille,
                            self.taille,
                            self.taille,
                        ),
                    )
                    fenetre.blit(
                        self.player.image, (self.x * self.taille, self.y * self.taille)
                    )
                    pg.draw.rect(
                        fenetre,
                        (200, 200, 200),
                        (
                            self.x * self.taille,
                            self.y * self.taille,
                            self.taille,
                            self.taille,
                        ),
                        1,
                    )
                else:
                    if self.player.classe == 0:
                        pg.draw.circle(
                            fenetre,
                            (255, 0, 0),
                            (
                                self.x * self.taille + self.taille // 2,
                                self.y * self.taille + self.taille // 2,
                            ),
                            self.taille // 2,
                        )
                    elif self.player.classe == 1:
                        pg.draw.circle(
                            fenetre,
                            (0, 0, 255),
                            (
                                self.x * self.taille + self.taille // 2,
                                self.y * self.taille + self.taille // 2,
                            ),
                            self.taille // 2,
                        )
                    elif self.player.classe == 2:
                        pg.draw.circle(
                            fenetre,
                            (0, 255, 0),
                            (
                                self.x * self.taille + self.taille // 2,
                                self.y * self.taille + self.taille // 2,
                            ),
                            self.taille // 2,
                        )
                    elif self.player.classe == 3:
                        pg.draw.circle(
                            fenetre,
                            (255, 255, 0),
                            (
                                self.x * self.taille + self.taille // 2,
                                self.y * self.taille + self.taille // 2,
                            ),
                            self.taille // 2,
                        )
                    pg.draw.rect(
                        fenetre,
                        (200, 200, 200),
                        (
                            self.x * self.taille,
                            self.y * self.taille,
                            self.taille,
                            self.taille,
                        ),
                        1,
                    )
            case TYPE_CELL.VIDE:
                if self.grille.show_gradient:
                    
                    pg.draw.rect(
                        fenetre,
                        (
                            max(0, 255),
                            max(
                                0,
                                255 - self.grille.Dynamic_Field[0][self.x][self.y] * 25,
                            ),
                            (max(0, 255)),
                        ),
                        (
                            self.x * self.taille,
                            self.y * self.taille,
                            self.taille,
                            self.taille,
                        ),
                    )
                else:
                    pg.draw.rect(
                        fenetre,
                        (255, 255, 255),
                        (
                            self.x * self.taille,
                            self.y * self.taille,
                            self.taille,
                            self.taille,
                        ),
                    )
                pg.draw.rect(
                    fenetre,
                    (200, 200, 200),
                    (
                        self.x * self.taille,
                        self.y * self.taille,
                        self.taille,
                        self.taille,
                    ),
                    1,
                )
            case TYPE_CELL.MUR:
                pg.draw.rect(
                    fenetre,
                    (0, 0, 0),
                    (
                        self.x * self.taille,
                        self.y * self.taille,
                        self.taille,
                        self.taille,
                    ),
                )
            case TYPE_CELL.PORTE:
                pg.draw.rect(
                    fenetre,
                    (165, 42, 42),
                    (
                        self.x * self.taille,
                        self.y * self.taille,
                        self.taille,
                        self.taille,
                    ),
                )
            case TYPE_CELL.PRODUCTOR:
                pg.draw.rect(
                    fenetre,
                    (0, 255, 0),
                    (
                        self.x * self.taille,
                        self.y * self.taille,
                        self.taille,
                        self.taille,
                    ),
                )
            case TYPE_CELL.ATTRACTOR1:
                pg.draw.rect(
                    fenetre,
                    (0, 255, 255),
                    (
                        self.x * self.taille,
                        self.y * self.taille,
                        self.taille,
                        self.taille,
                    ),
                )
                font = pg.font.Font(None, 36)
                text = font.render("1", True, (0, 0, 0))
                fenetre.blit(
                    text,
                    (
                        self.x * self.taille + self.taille // 2 - text.get_width() // 2,
                        self.y * self.taille
                        + self.taille // 2
                        - text.get_height() // 2,
                    ),
                )
            case TYPE_CELL.ATTRACTOR2:
                pg.draw.rect(
                    fenetre,
                    (0, 255, 255),
                    (
                        self.x * self.taille,
                        self.y * self.taille,
                        self.taille,
                        self.taille,
                    ),
                )
                font = pg.font.Font(None, 36)
                text = font.render("2", True, (0, 0, 0))
                fenetre.blit(
                    text,
                    (
                        self.x * self.taille + self.taille // 2 - text.get_width() // 2,
                        self.y * self.taille
                        + self.taille // 2
                        - text.get_height() // 2,
                    ),
                )
            case TYPE_CELL.ATTRACTOR3:
                pg.draw.rect(
                    fenetre,
                    (0, 255, 255),
                    (
                        self.x * self.taille,
                        self.y * self.taille,
                        self.taille,
                        self.taille,
                    ),
                )
                font = pg.font.Font(None, 36)
                text = font.render("3", True, (0, 0, 0))
                fenetre.blit(
                    text,
                    (
                        self.x * self.taille + self.taille // 2 - text.get_width() // 2,
                        self.y * self.taille
                        + self.taille // 2
                        - text.get_height() // 2,
                    ),
                )
            case TYPE_CELL.ATTRACTOR4:
                pg.draw.rect(
                    fenetre,
                    (0, 255, 255),
                    (
                        self.x * self.taille,
                        self.y * self.taille,
                        self.taille,
                        self.taille,
                    ),
                )
                font = pg.font.Font(None, 36)
                text = font.render("4", True, (0, 0, 0))
                fenetre.blit(
                    text,
                    (
                        self.x * self.taille + self.taille // 2 - text.get_width() // 2,
                        self.y * self.taille
                        + self.taille // 2
                        - text.get_height() // 2,
                    ),
                )

    def highlight(self, fenetre: pg.Surface):
        pg.draw.rect(
            fenetre,
            (0, 100, 0),
            (self.x * self.taille, self.y * self.taille, self.taille, self.taille),
            1,
        )

    def pass_epoch(self):
        pass
