from simulation.cell import Cell, TYPE_CELL
from simulation.player import Player
import pygame as pg
import numpy as np
import math
import random
from scipy.signal import convolve2d

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
