"""
Behavorial part for the crowd simulation

This module contains the classes and functions that are used to simulate the crowd behavior.

A simulation includes a map and a list of players that are on the map.
Players have there own behavior rules and are meant to interact with each other.

Creation date : 14 november 2024
Last update : 5 december 2024
"""

import pygame as pg
import numpy as np
import random
import sys
import math
from enum import Enum
from scipy.signal import convolve2d


image_tomate = pg.image.load("./images/auTOMATE.png")
image_tomate2 = pg.image.load("./images/auTOMATE2.png")
image_tomate = pg.transform.scale(image_tomate, (50, 50))
image_tomate2 = pg.transform.scale(image_tomate2, (50, 50))


class ACTIONS(Enum):
    ADDING_PLAYERS = 1
    ADDING_WALLS = 2
    ADDING_DOORS = 3
    ADDING_PRODUCTORS = 4
    ADDING_EMPTY = 5
    CHANGE_ATTRACTOR1 = 6
    CHANGE_ATTRACTOR2 = 7
    CHANGE_ATTRACTOR3 = 8
    CHANGE_ATTRACTOR4 = 9
    DO_NOTHING = 10


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


class Grille:
    """
    class that represents a grid in the simulation

    attributes:

    - x0 : list : x position of the classes
    - y0 : list : y position of the classes
    - fenetre : pg.Surface : surface of the window
    - porte : list : list of positions of the doors
    - mur : list : list of positions of the walls
    - nb_colonnes : int : number of columns
    - nb_lignes : int : number of rows
    - x0 : list : x position of the classes
    - y0 : list : y position of the classes
    - taille_cellule : int : size of the cell
    - grille : list : list of cells
    - players : list : list of players
    - productor : list : list of productors
    - attractor : list : list of attractors
    - tomato_flag : bool : flag to know if the simulation is in tomato mode
    - change_place : float : probability to change place with another player
    - grad_matrix : np.array : gradient matrix
    - exit : bool : if the simulation has an exit

    methods:

    - cellule : get a cell at a position
    - ajouter_mur : add a wall at a position
    - ajouter_porte : add a door at a position
    - add_player : add a player at a position
    - get_cellules : get all the cells
    - recuperer_voisins : get the neighbors of a cell
    - draw : draw the grid on the screen
    - gradient_obstacle : get the gradient of the obstacles
    - show_gradient : show the gradient on the screen
    - change_distance : change the distance of the players
    - delete_class : delete a class of players
    - open_class : open a class of players
    - add_productor : add a productor at a position

    """

    def __init__(
        self,
        x0,
        y0,
        fenetre,
        porte=None,
        mur=None,
        nb_colonnes=30,
        nb_lignes=60,
        classes=[0],
        productor=True,
        p0=None,
        p1=None,
        exit=True,
        change_place=0,
        Diff=0,
        Decay=0,
        show_gradient = False,
        change_class = 0.001
    ):
        screen_info = pg.display.Info()
        self.SCREEN_WIDTH = screen_info.current_w
        self.SCREEN_HEIGHT = screen_info.current_h
        self.fenetre = fenetre

        self.nb_colonnes = nb_colonnes
        self.nb_lignes = nb_lignes
        self.grad_matrix = np.zeros((nb_colonnes, nb_lignes))
        self.x0 = x0
        self.y0 = y0
        self.taille_cellule = min(
            self.SCREEN_WIDTH // nb_colonnes, (self.SCREEN_HEIGHT * 0.9) // nb_lignes
        )
        self.change_place = change_place
        self.grille = [
            [Cell(x, y, self.taille_cellule, self) for x in range(nb_colonnes)]
            for y in range(nb_lignes)
        ]
        self.players = []
        self.productor = []
        self.attractor = []
        if Decay == 0:
            self.decay = 1.1 * Diff
        else:
            self.decay = Decay
        self.Diff = Diff
        self.exit = exit
        self.change_class = change_class
        self.tomato_flag = False
        self.Dynamic_Field = np.array(
            [
                [[0 for _ in range(nb_lignes)] for _ in range(nb_colonnes)]
                for _ in range(len(x0))
            ],
            dtype=np.float64,
        )
        self.show_gradient = show_gradient

        if not porte:
            if productor:
                self.porte = [
                    (x0[z] + i, y0[z] + j)
                    for i in range(-1, 2)
                    for j in range(-1, 2)
                    for z in range(len(x0))
                    if (i, j) != (0, 0)
                ]
                self.productor = [
                    (p0 + i, p1 + j) for i in range(-1, 2) for j in range(-1, 2)
                ]
            else:
                self.porte = [
                    (x0[z] + i, y0[z] + j)
                    for i in range(-1, 2)
                    for j in range(-1, 2)
                    for z in range(len(x0))
                    if (i, j) != (0, 0)
                ]
                self.attractor = [(x0[z], y0[z]) for z in range(len(x0))]
            for z in range(len(x0)):
                match z:
                    case 0:
                        self.grille[y0[z]][x0[z]].current_state = TYPE_CELL.ATTRACTOR1
                    case 1:
                        self.grille[y0[z]][x0[z]].current_state = TYPE_CELL.ATTRACTOR2
                    case 2:
                        self.grille[y0[z]][x0[z]].current_state = TYPE_CELL.ATTRACTOR3
                    case 3:
                        self.grille[y0[z]][x0[z]].current_state = TYPE_CELL.ATTRACTOR4

        else:
            self.porte = porte
        if not mur:
            self.mur = (
                [(x, 0) for x in range(nb_colonnes)]
                + [(x, nb_lignes - 1) for x in range(nb_colonnes)]
                + [(0, y) for y in range(nb_lignes)]
                + [(nb_colonnes - 1, y) for y in range(nb_lignes)]
            )
        else:
            self.mur = mur

        for x, y in self.mur:
            self.grille[y][x].current_state = TYPE_CELL.MUR
        for x, y in self.porte:
            self.grille[y][x].current_state = TYPE_CELL.PORTE
        for x, y in self.productor:
            self.grille[y][x].current_state = TYPE_CELL.PRODUCTOR

    def cellule(self, x, y) -> Cell:
        return self.grille[int(y)][int(x)]

    def gradient_obstacle(self, grad_coeff, elarg) -> np.array:
        gradient = np.zeros((self.nb_colonnes, self.nb_lignes))
        x_coords, y_coords = zip(*self.mur)
        for dx in range(-elarg, elarg + 1):
            for dy in range(-elarg, elarg + 1):
                weight = grad_coeff / (abs(dx) + abs(dy) + 1)
                gradient[
                    np.clip(np.array(x_coords) + dx, 0, self.nb_colonnes - 1),
                    np.clip(np.array(y_coords) + dy, 0, self.nb_lignes - 1),
                ] += weight
        self.grad_matrix = gradient
        return gradient

    def ajouter_mur(self, x, y):
        cell = self.cellule(x, y)
        if cell.is_occuped():
            self.players.remove(cell.player)
            del cell.player
            cell.empty()
        self.mur.append((x, y))
        cell.set_wall()

    def ajouter_porte(self, x, y):
        cell = self.cellule(x, y)
        if cell.is_occuped():
            self.players.remove(cell.player)
            del cell.player
            cell.empty()
        self.porte.append((x, y))
        cell.set_door()

    def add_player(self, x, y):
        cell = self.cellule(x, y)
        if cell.current_state == TYPE_CELL.VIDE:
            cell.current_state = TYPE_CELL.OCCUPED
            player = Player(cell)
            cell.player = player
            self.players.append(player)
        if cell.current_state == TYPE_CELL.PRODUCTOR:
            player = Player(cell)
            cell.player = player
            self.players.append(player)
            cell.current_state = TYPE_CELL.PRODUCTOR

    def add_productor(self, x, y):
        cell = self.cellule(x, y)
        if cell.current_state == TYPE_CELL.VIDE:
            cell.current_state = TYPE_CELL.PRODUCTOR
            self.productor.append((x, y))

    def get_cellules(self):
        return [cell for cells in self.grille for cell in cells]

    def change_distance(self, x0, y0):
        for cell in self.get_cellules():
            cell.distance = [
                math.sqrt((x0[i] - cell.x) ** 2 + (y0[i] - cell.y) ** 2)
                for i in range(len(x0))
            ]

    def recuperer_voisins(self, x, y):
        voisin_positions = [
            (x, y - 1),
            (x, y + 1),
            (x - 1, y),
            (x + 1, y),
        ]
        voisins = [
            self.cellule(x, y)
            for x, y in voisin_positions
            if 0 <= x < self.nb_colonnes and 0 <= y < self.nb_lignes
        ]
        return voisins
    
    def recuperer_densite(self, x, y, size=5):
        width = size // 2
        voisins = [
            (i, j)
            for i in range(x - width, x + width + 1)
            for j in range(y - width, y + width + 1)
            if (0 <= i < self.nb_colonnes and 0 <= j < self.nb_lignes)
            if self.cellule(i, j).is_occuped() or self.cellule(i, j).is_empty()
        ]
        if len(voisins) <= 5:
            return 0
        densite = sum(1 for i, j in voisins if (self.cellule(i, j).is_occuped()))
        densite *= 10/len(voisins)
        return densite

    def recuperer_max_densite_grille(self):
        max_densite = 0
        densite = 0
        x_max,y_max=0,0
        for x in range(self.nb_colonnes):
            for y in range(self.nb_lignes):
                if self.cellule(x, y).is_occuped() or self.cellule(x, y).is_empty():
                    densite = self.recuperer_densite(x, y, size=7)
                if densite > max_densite:
                    max_densite = densite
                    x_max, y_max=x,y
                    if max_densite == 10:
                        return max_densite, (x_max, y_max)
        print(max_densite)
        return max_densite, (x_max,y_max)

    def delete_class(self, classe):
        for player in self.players:
            while player.classe == classe:
                player.classe = random.choice(range(len(self.x0)))
                player.change_color()

    def open_class(self, classe):
        for player in self.players:
            if random.random() < 1 / (len(self.x0) + 1):
                player.classe = classe
                player.change_color()

    def decay_Field(self):
        pass

    def diffusion_Field(self):
        # Initialisation d'une copie pour éviter d'écraser les valeurs pendant le calcul
        new_field = np.copy(self.Dynamic_Field)

        # Définition du noyau de convolution pour les voisins (haut, bas, gauche, droite)
        kernel = self.Diff * np.array(
            [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        )  # Ne prend en compte que les voisins directs
        import time

        # Parcourir les classes discrétisées
        for k in range(len(self.x0)):
            # Calcul de la somme des voisins via convolution
            field = self.Dynamic_Field[k]
            sum_voisins = convolve2d(field, kernel, mode="same")

            # Mise à jour du champ dynamique avec l'équation de diffusion
            new_field[k] = sum_voisins / 4 + (1 - self.decay) * self.Dynamic_Field[k]
        new_field = new_field.clip(0, 5)
        # Remplacement du champ par le nouveau champ mis à jour
        self.Dynamic_Field = new_field


class Player:
    """
    class that represents a player in the simulation

    attributes:

    - current_cell : Cell : current cell of the player
    - inertie : int : inertia of the player
    - last_encoutered : list : last encountered positions
    - grille : Grille : the grid the player belongs to
    - image : pg.Surface : image of the player
    - classe : int : class of the player
    - is_arrived : bool : if the player has arrived
    - wanna_go : Cell : cell the player wants to go to


    methods:

    - move : move the player to a cell
    - apply_rules : apply the rules of the simulation
    - apply_rules_parallel : apply the rules of the simulation in parallel
    - inertia_and_grad : compute the inertia and the gradient
    - choose_index : choose the index of the cell to go to
    - change_color : change the color of the player
    - exchange : exchange the position of the player with another player


    """

    def __init__(self, cell: Cell):
        self.current_cell = cell
        self.inertie = 0
        self.last_encoutered = []
        self.grille: Grille = cell.grille
        self.image = pg.transform.scale(
            random.choice([image_tomate, image_tomate2]),
            (self.current_cell.taille, self.current_cell.taille),
        )
        self.classe = random.choice(range(len(self.grille.x0)))
        self.is_arrived = False
        self.wanna_go = None
        self.current_cell.player = self

        match self.classe:
            case 1:
                self.image.fill((0, 0, 180), special_flags=pg.BLEND_MULT)
            case 2:
                self.image.fill((0, 250, 0), special_flags=pg.BLEND_MULT)
            case 3:
                self.image.fill((0, 255, 255), special_flags=pg.BLEND_MULT)

    def change_color(self):
        match self.classe:
            case 1:
                self.image.fill((0, 0, 180), special_flags=pg.BLEND_MULT)
            case 2:
                self.image.fill((0, 250, 0), special_flags=pg.BLEND_MULT)
            case 3:
                self.image.fill((0, 255, 255), special_flags=pg.BLEND_MULT)

    def add_Field(self):
        self.grille.Dynamic_Field[self.classe][self.current_cell.x][
            self.current_cell.y
        ] += self.grille.Diff * 10

    def move(self, cell: Cell):
        self.last_encoutered.append((self.current_cell.x, self.current_cell.y))
        self.current_cell.empty()
        self.current_cell = cell
        cell.player = self
        if not cell.current_state == TYPE_CELL.PRODUCTOR:
            cell.current_state = TYPE_CELL.OCCUPED
        if self.grille.Diff != 0 and self.inertie == 0:
            self.add_Field()
        self.inertie = 0
        

    def exchange(self, cell: Cell):
        temp_player = cell.player
        cell.player = self
        self.current_cell.player = temp_player
        temp_player.current_cell = self.current_cell
        self.current_cell = cell
    
    def random_change(self):
        self.classe = random.choice(range(len(self.grille.x0)))
        self.change_color()

    def inertia_and_grad(self, H, nu, voisins_valides):
        list_i = []
        for j, voisin in enumerate(voisins_valides):
            if len(self.last_encoutered) != 0:
                for k in range(1, min(20, len(self.last_encoutered))):
                    if (
                        voisin.x == self.last_encoutered[-k][0]
                        and voisin.y == self.last_encoutered[-k][1]
                    ):
                        list_i.append(j)

        if self.grille.grad_matrix is not None:
            for j, voisin in enumerate(voisins_valides):
                H[j] += self.grille.grad_matrix[voisin.x][voisin.y]
        if nu * self.inertie < 10:
            inertia = nu * self.inertie
        else:
            inertia = 10
        if len(list_i) > 0:
            for i in list_i:
                H[i] += 3 - inertia
        H[-1] += inertia
        return H

    def choose_index(self, voisins_valides, eta, nu, voisins_occuped):
        if voisins_occuped:
            for voisin_occ in voisins_occuped:
                H = -np.array(
                    [
                        voisin.distance[voisin_occ.player.classe]
                        for voisin in voisins_valides
                    ]
                ) + np.array(
                    [voisin.distance[self.classe] for voisin in voisins_valides]
                )
        elif self.grille.Diff != 0:
            H = np.array(
                [
                    voisin.distance[self.classe]
                    - 0.75 * self.grille.Dynamic_Field[self.classe][voisin.x][voisin.y]
                    for voisin in voisins_valides
                ]
            )
            H = self.inertia_and_grad(H, nu, voisins_valides)
        else:
            H = np.array([voisin.distance[self.classe] for voisin in voisins_valides])
            H = self.inertia_and_grad(H, nu, voisins_valides)
        W = np.exp(
            (-eta * H) / (self.grille.nb_colonnes + self.grille.nb_lignes) ** 0.3
        )
        W /= W.sum()  # Normalisation pour avoir une somme de probabilités de 1

        # Choix de la position en fonction de la distribution de probabilités
        chosen_index = np.random.choice(len(W), p=W)
        chosen_cell = voisins_valides[chosen_index]
        return chosen_cell

    def should_exchange(self, chosen_cell):
        return (
            chosen_cell.player.wanna_go == self.current_cell
            and random.random() < self.grille.change_place
        )

    def apply_rules(self, eta, nu):
        # Obtenir une liste des cellules actives et la mélanger aléatoirement
        # active_cells = [cell for row in self.grille for cell in row if cell.etat]
        # random.shuffle(active_cells)
        # Mettre à jour les états des cellules actives
        # for cell in active_cells:
        # Positions voisines : haut, bas, gauche, droite, et la position actuelle
        voisins = self.grille.recuperer_voisins(
            self.current_cell.x, self.current_cell.y
        )

        # Conserver uniquement les positions valides
        voisins_valides = [
            voisin for voisin in voisins if voisin.is_empty() or voisin.is_door()
        ]

        # for voisin in voisins:
        #     voisin.highlight(self.grille.fenetre)
        # pg.display.update()
        voisins_valides += [self.current_cell]

        chosen_cell = self.choose_index(voisins_valides, eta, nu)
        # Activer la cellule choisie
        if chosen_cell == self.current_cell:
            pass
        elif chosen_cell.current_state == TYPE_CELL.PORTE:
            self.is_arrived = True
            self.current_cell.empty()
            self.current_cell = None
        elif (
            chosen_cell.current_state == TYPE_CELL.VIDE
            or chosen_cell.current_state == TYPE_CELL.PRODUCTOR
        ):
            self.move(chosen_cell)

    # Pour faire le parallèle, créer la matrice de conflit puis la gérer dans la boucle de grille/simu à voir

    def apply_rules_parallel(self, eta, matrice_conflit, nu):
        voisins = self.grille.recuperer_voisins(
            self.current_cell.x, self.current_cell.y
        )
        voisins_valides = [
            voisin
            for voisin in voisins
            if voisin.is_empty()
            or voisin.is_door()
            or (voisin.is_occuped() and self.grille.change_place != 0)
        ]
        voisins_occuped = [
            voisin
            for voisin in voisins
            if voisin.is_occuped()
            and not voisin == self.current_cell
            and voisin.player.classe != self.classe
        ]

        voisins_valides.append(self.current_cell)

        chosen_cell = self.choose_index(voisins_valides, eta, nu, voisins_occuped)

        # Activer la cellule choisie

        while (
            chosen_cell.current_state == TYPE_CELL.OCCUPED
            and not chosen_cell == self.current_cell
        ):
            self.wanna_go = chosen_cell
            if self.should_exchange(chosen_cell):
                self.exchange(chosen_cell)
            else:
                voisins_valides.remove(chosen_cell)
                chosen_cell = self.choose_index(
                    voisins_valides, eta, nu, voisins_occuped
                )
        if chosen_cell == self.current_cell:
            self.inertie += 1
            pass
        elif chosen_cell.current_state == TYPE_CELL.PORTE and self.grille.exit:
            self.is_arrived = True
            self.current_cell.empty()
            self.current_cell = None

        elif (
            chosen_cell.current_state == TYPE_CELL.VIDE
            or chosen_cell.current_state == TYPE_CELL.PRODUCTOR
        ):
            matrice_conflit[chosen_cell.x][chosen_cell.y].append(self)
            self.inertie = 0


class Simulation:
    """
    class that represents the simulation

    attributes:

    - fenetre : pg.Surface : surface of the window
    - SCREEN_WIDTH : int : width of the screen
    - SCREEN_HEIGHT : int : height of the screen
    - map : Grille : the grid of the simulation
    - cells : list : list of cells
    - proba_wall : float : probability of a wall
    - proba_player : float : probability of a player
    - classes : list : list of classes
    - coeff_prod : float : coefficient of production


    methods:

    - random_setup : setup the simulation randomly
    - choice_setup : setup the simulation by choosing the positions
    - apply_rules : apply the rules of the simulation
    - apply_rules_parallel : apply the rules of the simulation in parallel
    - pass_epoch : pass an epoch
    - draw : draw the simulation on the screen

    """

    def __init__(
        self,
        fenetre: pg.Surface = None,
        nb_colonnes=30,
        nb_lignes=60,
        proba_wall=0.05,
        proba_player=0.3,
        classes=1,
        Productor=True,
        coeff_prod=0.05,
        exit=False,
        change_place=0,
        Diff=0,
        Decay=0,
        show_gradient = False,
        change_class = 0.001
    ):
        self.fenetre = fenetre
        screen_info = pg.display.Info()
        self.SCREEN_WIDTH = screen_info.current_w
        self.SCREEN_HEIGHT = screen_info.current_h
        self.proba_wall = proba_wall
        self.proba_player = proba_player
        self.classes = range(classes)
        self.coeff_prod = coeff_prod

        self.map = Grille(
            nb_colonnes=nb_colonnes,
            nb_lignes=nb_lignes,
            x0=[nb_colonnes // 2, nb_colonnes - 2, 2, nb_colonnes // 2][
                : classes - int(Productor)
            ],
            y0=[nb_lignes - 2, nb_lignes // 2, nb_lignes // 2, 1][
                : classes - int(Productor)
            ],
            # porte=porte,
            fenetre=fenetre,
            classes=self.classes,
            productor=Productor,
            p0=[nb_colonnes // 2, nb_colonnes - 2, 2, nb_colonnes // 2][classes - 1],
            p1=[nb_lignes - 2, nb_lignes // 2, nb_lignes // 2, 1][classes - 1],
            exit=exit,
            change_place=change_place,
            Diff=Diff,
            Decay=Decay,
            show_gradient = show_gradient,
            change_class = change_class
        )
        self.cells = self.map.get_cellules()

    def random_setup(self):
        for cell in self.cells:
            if random.random() < self.proba_player:
                self.map.add_player(cell.x, cell.y)
            if random.random() < self.proba_wall:
                self.map.ajouter_mur(cell.x, cell.y)

    def choice_setup(self):
        running = True

        def add(x, y, action):
            if x >= self.map.nb_colonnes or y >= self.map.nb_lignes:
                return
            cell = self.map.cellule(x, y)
            match action:
                case ACTIONS.ADDING_WALLS:
                    self.map.ajouter_mur(x, y)
                case ACTIONS.ADDING_DOORS:
                    self.map.ajouter_porte(x, y)
                case ACTIONS.ADDING_PLAYERS:
                    self.map.add_player(x, y)
                case ACTIONS.ADDING_PRODUCTORS:
                    self.map.add_productor(x, y)
                case ACTIONS.ADDING_EMPTY:
                    cell.empty()
                case ACTIONS.CHANGE_ATTRACTOR1:
                    cell.change_attractor(0)
                case ACTIONS.CHANGE_ATTRACTOR2:
                    cell.change_attractor(1)
                case ACTIONS.CHANGE_ATTRACTOR3:
                    cell.change_attractor(2)
                case ACTIONS.CHANGE_ATTRACTOR4:
                    cell.change_attractor(3)

            cell.draw(self.fenetre)

        # initialisation de la vue
        self.draw(self.fenetre)
        pg.display.update()

        action = ACTIONS.ADDING_PLAYERS
        pg.key.set_repeat(20, 5)

        while running:
            # intercept events
            for event in pg.event.get():
                # fermeture de la fenêtre
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                # pression sur la touche entrée pour valider le placement des joueurs
                elif event.type == pg.KEYDOWN:
                    # clic de souris

                    def act(action, actions):
                        if action == actions:
                            action = ACTIONS.DO_NOTHING
                        else:
                            action = actions
                        return action

                    if event.key == pg.K_RETURN:
                        running = False
                        return

                    elif event.key == pg.K_w:
                        action = act(action, ACTIONS.ADDING_WALLS)
                    elif event.key == pg.K_d:
                        action = act(action, ACTIONS.ADDING_DOORS)
                    elif event.key == pg.K_p:
                        action = act(action, ACTIONS.ADDING_PLAYERS)
                    elif event.key == pg.K_r:
                        action = act(action, ACTIONS.ADDING_PRODUCTORS)
                    elif event.key == pg.K_e:
                        action = act(action, ACTIONS.ADDING_EMPTY)
                    elif event.key == pg.K_1:
                        action = act(action, ACTIONS.CHANGE_ATTRACTOR1)
                    elif event.key == pg.K_2:
                        action = act(action, ACTIONS.CHANGE_ATTRACTOR2)
                    elif event.key == pg.K_3:
                        action = act(action, ACTIONS.CHANGE_ATTRACTOR3)
                    elif event.key == pg.K_4:
                        action = act(action, ACTIONS.CHANGE_ATTRACTOR4)

                    x, y = pg.mouse.get_pos()
                    cell_x = x // self.map.taille_cellule
                    cell_y = y // self.map.taille_cellule
                    add(cell_x, cell_y, action)

            pg.display.update()

    def apply_rules(self, eta, nu):
        for player in self.map.players:
            if random.random() < self.map.change_class:
                player.random_change()
            if not player.is_arrived:
                player.apply_rules(eta=eta, nu=nu)
            else:
                del player
        for produc in self.map.productor:
            if random.random() < self.coeff_prod:
                self.map.add_player(produc[0], produc[1])

    def apply_rules_parallel(self, eta, mu, nu):
        
        if self.map.Diff != 0:
            self.map.decay_Field()
            self.map.diffusion_Field()

        matrice_conflit = [
            [[] for _ in range(self.map.nb_lignes)] for _ in range(self.map.nb_colonnes)
        ]
        for player in self.map.players:
            if random.random() < self.map.change_class:
                player.random_change()
            if not player.is_arrived:
                player.apply_rules_parallel(
                    eta=eta, matrice_conflit=matrice_conflit, nu=nu
                )
            else:
                self.map.players.remove(player)
                del player
        for x in range(self.map.nb_colonnes):
            for y in range(self.map.nb_lignes):
                if len(matrice_conflit[x][y]) > 1 and random.random() < mu:
                    random.shuffle(matrice_conflit[x][y])
                    matrice_conflit[x][y][0].move(self.map.cellule(x, y))
                elif len(matrice_conflit[x][y]) == 1:
                    matrice_conflit[x][y][0].move(self.map.cellule(x, y))
        for produc in self.map.productor:
            if random.random() < self.coeff_prod:
                self.map.add_player(produc[0], produc[1])

    def pass_epoch(self):
        for cell in self.cells:
            cell.pass_epoch()
    
    def draw_max_densite(self, fenetre):
        if not hasattr(self, 'max_density'):
            self.max_density = 0
            return
        self.max_density, (x_densite, y_densite) = self.map.recuperer_max_densite_grille()
        
        # draw max density
        overlay = pg.Surface((self.map.taille_cellule, self.map.taille_cellule), pg.SRCALPHA)
        overlay.fill((255, 255, 0, 100))  # RGBA color with 100 alpha for 40% opacity
        fenetre.blit(overlay, (x_densite * self.map.taille_cellule, y_densite * self.map.taille_cellule))

        # draw surrounding rectangle
        rect_size = 7
        half_rect = rect_size // 2
        x_start = max(0, x_densite - half_rect)
        y_start = max(0, y_densite - half_rect)
        x_end = min(self.map.nb_colonnes, x_densite + half_rect + 1)
        y_end = min(self.map.nb_lignes, y_densite + half_rect + 1)

        overlay = pg.Surface((self.map.taille_cellule * (x_end - x_start), self.map.taille_cellule * (y_end - y_start)), pg.SRCALPHA)
        overlay.fill((255, 255, 0, 50))  # RGBA color with 50 alpha for 20% opacity
        fenetre.blit(overlay, (x_start * self.map.taille_cellule, y_start * self.map.taille_cellule))

    def draw(self, fenetre):
        # clear the screen
        fenetre.fill((255, 255, 255))

        # draw players
        for cell in self.cells:
            cell.draw(fenetre)

        self.draw_max_densite(fenetre)
