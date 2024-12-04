""" Behavorial part for the crowd simulation

This module contains the classes and functions that are used to simulate the crowd behavior.

A simulation includes a map and a list of players that are on the map.
Players have there own behavior rules and are meant to interact with each other.

Creation date : 14 november 2024
Last update : 14 november 2024  

"""

import pygame as pg
import numpy as np
import random
import sys
import math
from enum import Enum

image_tomate = pg.image.load('./images/auTOMATE.png')
image_tomate2 = pg.image.load('./images/auTOMATE2.png')
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
    
class TYPE_CELL(Enum):
        VIDE = 0
        MUR = 1
        PORTE = 2
        OCCUPED = 3
        PRODUCTOR =4
        ATTRACTOR = 5
        
        
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
    """
    
    def __init__(self, x, y, taille, grille):
        self.x = x
        self.y = y
        self.taille = taille
        self.grille = grille
        self.distance = [math.sqrt((grille.x0[i] - x)**2 + (grille.y0[i] - y)**2) for i in range(len(grille.x0))]
        self.current_state = TYPE_CELL.VIDE
        self.player = None
        self.inertie = 0
        
    def regles_de_comportement(self, voisins):
        nb_voisins_vivants = sum([voisin.current_state for voisin in voisins])
        if self.current_state:
            if nb_voisins_vivants < 2 or nb_voisins_vivants > 3:
                self.next_state = False
        else:
            if nb_voisins_vivants == 3:
                self.next_state = True
    
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
        self.grille.cellule(self.grille.x0[nb_attract], self.grille.y0[nb_attract]).empty()
        self.grille.x0[nb_attract] = self.x
        self.grille.y0[nb_attract] = self.y
        self.grille.change_distance(self.grille.x0, self.grille.y0)
        self.current_state = TYPE_CELL.ATTRACTOR
        
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
                fenetre.fill((255, 255, 255), (self.x * self.taille, self.y * self.taille, self.taille, self.taille))
                fenetre.blit(self.player.image, (self.x * self.taille, self.y * self.taille))
                pg.draw.rect(fenetre, (200, 200, 200), (self.x * self.taille, self.y * self.taille, self.taille, self.taille), 1)

            case TYPE_CELL.VIDE:
                pg.draw.rect(fenetre, (255, 255, 255), (self.x * self.taille, self.y * self.taille, self.taille, self.taille))
                pg.draw.rect(fenetre, (200, 200, 200), (self.x * self.taille, self.y * self.taille, self.taille, self.taille), 1)
            case TYPE_CELL.MUR:
                pg.draw.rect(fenetre, (0, 0, 0), (self.x * self.taille, self.y * self.taille, self.taille, self.taille))
            case TYPE_CELL.PORTE:
                pg.draw.rect(fenetre, (165, 42, 42), (self.x * self.taille, self.y * self.taille, self.taille, self.taille))
            case TYPE_CELL.PRODUCTOR:
                pg.draw.rect(fenetre, (0, 255, 0), (self.x * self.taille, self.y * self.taille, self.taille, self.taille))
            case TYPE_CELL.ATTRACTOR:
                pg.draw.rect(fenetre, (0, 255, 255), (self.x * self.taille, self.y * self.taille, self.taille, self.taille))
    def highlight(self, fenetre: pg.Surface):
        pg.draw.rect(fenetre, (0, 100, 0), (self.x * self.taille, self.y * self.taille, self.taille, self.taille), 1)
                
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
    methods:
    - cellule : get a cell at a position
    - ajouter_mur : add a wall at a position
    - ajouter_porte : add a door at a position
    - add_player : add a player at a position
    - get_cellules : get all the cells
    - recuperer_voisins : get the neighbors of a cell
    - draw : draw the grid on the screen
    """
    
    def __init__(self, x0, y0,fenetre, porte = None, mur=None, nb_colonnes = 30, nb_lignes = 60, classes = [0], productor = True,  p0 = None, p1 = None, exit = True, change_place = 0):
        
        screen_info = pg.display.Info()
        self.SCREEN_WIDTH = screen_info.current_w
        self.SCREEN_HEIGHT = screen_info.current_h
        self.fenetre = fenetre
        
        self.nb_colonnes = nb_colonnes
        self.nb_lignes = nb_lignes
        self.grad_matrix = None
        self.x0 = x0
        self.exit = exit
        self.y0 = y0
        self.taille_cellule = min(self.SCREEN_WIDTH // nb_colonnes, self.SCREEN_HEIGHT // nb_lignes)
        self.change_place = change_place
        self.grille = [[Cell(x, y, self.taille_cellule,self) for x in range(nb_colonnes)] for y in range(nb_lignes)]
        self.players = []
        self.productor = []
        self.attractor = []
        if not porte:
            if productor:
                self.porte = [(x0[z] + i, y0[z] + j) for i in range(-1, 2) for j in range(-1, 2) for z in range(len(x0)) if (i, j) != (0, 0)]
                self.productor = [(p0 + i, p1 + j) for i in range(-1, 2) for j in range(-1, 2)]
                self.attractor = [(x0[z], y0[z]) for z in range(len(x0))]
            else:
                self.porte = [(x0[z] + i, y0[z] + j) for i in range(-1, 2) for j in range(-1, 2) for z in range(len(x0)) if (i, j) != (0, 0)]
                self.attractor = [(x0[z], y0[z]) for z in range(len(x0))]
        else:
            self.porte = porte
        if not mur:
            self.mur = [(x, 0) for x in range(nb_colonnes)] \
            + [(x, nb_lignes - 1) for x in range(nb_colonnes)] \
            + [(0, y) for y in range(nb_lignes)] \
            + [(nb_colonnes - 1, y) for y in range(nb_lignes)]
        else:
            self.mur = mur


        for (x, y) in self.mur:
            self.grille[y][x].current_state = TYPE_CELL.MUR
        for (x, y) in self.porte:
            self.grille[y][x].current_state = TYPE_CELL.PORTE
        for (x, y) in self.productor:
            self.grille[y][x].current_state = TYPE_CELL.PRODUCTOR
        for (x, y) in self.attractor:
            self.grille[y][x].current_state = TYPE_CELL.ATTRACTOR


    def cellule(self, x, y) -> Cell:
        return self.grille[y][x]
    
    def gradient_obstacle(self, grad_coeff, elarg) -> np.array:
        gradient = np.zeros((self.nb_colonnes, self.nb_lignes))
        for x, y in self.mur:
            for i in range(-elarg, elarg + 1):
                for j in range(-elarg, elarg + 1):
                    if 0 <= x + i < self.nb_colonnes and 0 <= y + j < self.nb_lignes:
                        gradient[x + i][y + j] += grad_coeff / (abs(i) + abs(j) + 1)
        self.grad_matrix = gradient
        return gradient

    def show_gradient(self, fenetre, grad_coeff, elarg):
        gradient = self.gradient_obstacle(grad_coeff, elarg)
        for x in range(self.nb_colonnes):
            for y in range(self.nb_lignes):
                if self.cellule(x, y).current_state == TYPE_CELL.VIDE or self.cellule(x, y).current_state == TYPE_CELL.OCCUPED:
                    pg.draw.rect(fenetre, (255 - min(255, int(gradient[x][y] * 255)), 255 - min(255, int(gradient[x][y] * 255)), 255 - min(255, int(gradient[x][y] * 255))), (x * self.taille_cellule, y * self.taille_cellule, self.taille_cellule, self.taille_cellule))
                elif self.cellule(x ,y).current_state == TYPE_CELL.MUR:
                    pg.draw.rect(fenetre, (0, 0, 0), (x * self.taille_cellule, y * self.taille_cellule, self.taille_cellule, self.taille_cellule))
        pg.display.update()        
    
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

    
    
    
    def get_cellules(self):
        return [cell for cells in self.grille for cell in cells]


    def change_distance(self, x0, y0):
        for cell in self.get_cellules():
            cell.distance = [math.sqrt((x0[i] - cell.x)**2 + (y0[i] - cell.y)**2) for i in range(len(x0))]
            
    def recuperer_voisins(self, x, y):
        voisin_positions = [
                    (x, y - 1),
                    (x, y + 1),
                    (x - 1, y),
                    (x + 1, y),
                ]
        voisins = [
            self.cellule(x, y) for x, y in voisin_positions if 0 <= x < self.nb_colonnes and 0 <= y < self.nb_lignes
        ]
        return voisins

    def draw(self, fenetre):
        pass
   
        
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

    methods:

    - move : move the player to a cell
    - apply_rules : apply the rules of the simulation
    - apply_rules_parallel : apply the rules of the simulation in parallel
    """
    
    def __init__(self, cell: Cell):
        self.current_cell = cell
        self.inertie = 0
        self.last_encoutered = []
        self.grille: Grille = cell.grille
        self.image = pg.transform.scale(random.choice([image_tomate, image_tomate2]), (self.current_cell.taille, self.current_cell.taille))
        self.classe = random.choice( range(len(self.grille.x0)))
        self.is_arrived = False
        self.wanna_go = None

        match self.classe:
            case 1:
                self.image.fill((0, 0, 180), special_flags=pg.BLEND_MULT)
            case 2:
                self.image.fill((0, 250, 0), special_flags=pg.BLEND_MULT)
            case 3:
                self.image.fill((0, 255, 255), special_flags=pg.BLEND_MULT)
        
        self.current_cell.player = self
        
    def move(self, cell: Cell):
        self.last_encoutered.append((self.current_cell.x, self.current_cell.y))
        self.current_cell.empty()
        self.current_cell = cell
        cell.player = self 
        cell.current_state = TYPE_CELL.OCCUPED
        self.inertie = 0
    
    def exchange(self, cell: Cell):
        temp_player = cell.player
        cell.player = self
        self.current_cell.player = temp_player
        temp_player.current_cell = self.current_cell
        self.current_cell = cell
        


    def inertia_and_grad(self, H, nu, voisins_valides):
            list_i = []
            for j, voisin in enumerate(voisins_valides):
                if len(self.last_encoutered) != 0:
                    for k in range(1, min(50, len(self.last_encoutered))):
                        if voisin.x == self.last_encoutered[-k][0] and voisin.y == self.last_encoutered[-k][1]:
                            list_i.append(j)
            if self.grille.grad_matrix is not None:
                for j, voisin in enumerate(voisins_valides):
                    H[j] += self.grille.grad_matrix[voisin.x][voisin.y]
            if nu*self.inertie < 10:
                inertia = nu*self.inertie
            else:
                inertia = 10
            if len(list_i) > 0:
                for i in list_i:
                    H[i] += 3 - inertia
            H[-1] += inertia
            return H

    def choose_index(self, voisins_valides, eta, nu):
            H = np.array([ voisin.distance[self.classe] for voisin in voisins_valides ])
            
            H = self.inertia_and_grad(H, nu, voisins_valides)

            W = np.exp((-eta * H) / (self.grille.nb_colonnes + self.grille.nb_lignes)**0.2 )

            W /= W.sum()  # Normalisation pour avoir une somme de probabilités de 1

            # Choix de la position en fonction de la distribution de probabilités
            chosen_index = np.random.choice(len(W), p=W)
            chosen_cell = voisins_valides[chosen_index]
            return chosen_cell
    
    def apply_rules(self, eta, nu):
        # Obtenir une liste des cellules actives et la mélanger aléatoirement
        # active_cells = [cell for row in self.grille for cell in row if cell.etat]
        # random.shuffle(active_cells)
        # Mettre à jour les états des cellules actives
        # for cell in active_cells:
        # Positions voisines : haut, bas, gauche, droite, et la position actuelle
        voisins = self.grille.recuperer_voisins(self.current_cell.x, self.current_cell.y)

        # Conserver uniquement les positions valides
        voisins_valides = [voisin for voisin in voisins if voisin.is_empty() or voisin.is_door()]
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
        elif chosen_cell.current_state == TYPE_CELL.VIDE or chosen_cell.current_state == TYPE_CELL.PRODUCTOR:
            self.move(chosen_cell)
#Pour faire le parallèle, créer la matrice de conflit puis la gérer dans la boucle de grille/simu à voir
    def apply_rules_parallel(self, eta, matrice_conflit, nu):
        voisins = self.grille.recuperer_voisins(self.current_cell.x, self.current_cell.y)
        voisins_valides = [voisin for voisin in voisins if voisin.is_empty() or voisin.is_door() or (voisin.is_occuped() and self.grille.change_place != 0)]
        voisins_valides.append(self.current_cell)
        
        chosen_cell = self.choose_index(voisins_valides, eta, nu)

        # Activer la cellule choisie
        
        while chosen_cell.current_state == TYPE_CELL.OCCUPED and not chosen_cell == self.current_cell:
            self.wanna_go = chosen_cell
            if chosen_cell.player.wanna_go == self.current_cell and random.random() < self.grille.change_place:
                self.exchange(chosen_cell)
            else:
                voisins_valides.remove(chosen_cell)
                chosen_cell = self.choose_index(voisins_valides, eta, nu)
        if chosen_cell == self.current_cell:
            self.inertie += 1
            pass
        elif chosen_cell.current_state == TYPE_CELL.PORTE and self.grille.exit:
            self.is_arrived = True
            self.current_cell.empty()
            self.current_cell = None

        elif chosen_cell.current_state == TYPE_CELL.VIDE or chosen_cell.current_state == TYPE_CELL.PRODUCTOR:
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

    methods:

    - random_setup : setup the simulation randomly
    - choice_setup : setup the simulation by choosing the positions
    - apply_rules : apply the rules of the simulation
    - apply_rules_parallel : apply the rules of the simulation in parallel
    - pass_epoch : pass an epoch
    - draw : draw the simulation on the screen
    """
        
    def __init__(self, fenetre: pg.Surface = None, nb_colonnes = 30, nb_lignes = 60, proba_wall = 0.05, proba_player = 0.3, classes = 1, Productor = True, coeff_prod = 0.05, exit = False, change_place = 0):
        self.fenetre = fenetre
        screen_info = pg.display.Info()
        self.SCREEN_WIDTH = screen_info.current_w
        self.SCREEN_HEIGHT =  screen_info.current_h
        self.proba_wall = proba_wall
        self.proba_player = proba_player
        self.classes = range(classes)
        self.coeff_prod = coeff_prod        
        
        self.map = Grille(
            nb_colonnes=nb_colonnes, 
            nb_lignes=nb_lignes,
            x0=[nb_colonnes // 2, nb_colonnes - 2, 2, nb_colonnes // 2][:classes - int(Productor)],
            y0=[nb_lignes - 2, nb_lignes//2 , nb_lignes//2, 1][:classes - int(Productor)],
            #porte=porte,
            fenetre=fenetre,
            classes = self.classes,
            productor = Productor,
            p0=[nb_colonnes // 2, nb_colonnes - 2, 2, nb_colonnes // 2][classes - 1],
            p1=[nb_lignes - 2, nb_lignes//2 , nb_lignes//2, 1][classes - 1],
            exit = exit,
            change_place = change_place
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
        mouse_held = False  # Track if the mouse button is held down
        
        def add(x,y,action):
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
        while running:
            
            # intercept events
            for event in pg.event.get():
                # fermeture de la fenêtre
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                # pression sur la touche entrée pour valider le placement des joueurs
                elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    running = False
                # clic de souris
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse_held = True
                    x, y = event.pos
                    cell_x = x // self.map.taille_cellule
                    cell_y = y // self.map.taille_cellule
                    add(cell_x, cell_y, action)
                    
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_w:
                        action = ACTIONS.ADDING_WALLS
                    elif event.key == pg.K_d:
                        action = ACTIONS.ADDING_DOORS
                    elif event.key == pg.K_p:
                        action = ACTIONS.ADDING_PLAYERS
                    elif event.key == pg.K_r:
                        action = ACTIONS.ADDING_PRODUCTORS
                    elif event.key == pg.K_e:
                        action = ACTIONS.ADDING_EMPTY
                    elif event.key == pg.K_1:
                        action = ACTIONS.CHANGE_ATTRACTOR1
                    elif event.key == pg.K_2:
                        action = ACTIONS.CHANGE_ATTRACTOR2
                    elif event.key == pg.K_3:
                        action = ACTIONS.CHANGE_ATTRACTOR3
                    elif event.key == pg.K_4:
                        action = ACTIONS.CHANGE_ATTRACTOR4

                elif event.type == pg.MOUSEBUTTONUP:
                    mouse_held = False
                

            # Set cell to alive when dragging
            if mouse_held:
                x, y = pg.mouse.get_pos()
                cell_x = x // self.map.taille_cellule
                cell_y = y // self.map.taille_cellule
                add(cell_x, cell_y, action)

            pg.display.update()


    def apply_rules(self, eta, nu):
        for player in self.map.players:
            if not player.is_arrived:
                player.apply_rules(eta=eta, nu = nu)
            else:
                del player
        for produc in self.map.productor:
            if random.random() < self.coeff_prod:
                self.map.add_player(produc[0], produc[1])

    
    def apply_rules_parallel(self, eta, mu, nu):
        matrice_conflit = [[[] for _ in range(self.map.nb_lignes)] for _ in range(self.map.nb_colonnes)]
        for player in self.map.players:
            if not player.is_arrived:
                player.apply_rules_parallel(eta=eta, matrice_conflit = matrice_conflit, nu = nu)
        
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
            
    def draw(self,fenetre):
        # draw map
        self.map.draw(fenetre)
        # draw players
        for cell in self.cells:
            cell.draw(fenetre)
                
           
