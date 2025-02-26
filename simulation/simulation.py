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
from simulation.grille import Grille



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
