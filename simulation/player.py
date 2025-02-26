from simulation.cell import Cell, TYPE_CELL
import pygame as pg
import numpy as np
import random


image_tomate = pg.image.load("./images/auTOMATE.png")
image_tomate2 = pg.image.load("./images/auTOMATE2.png")
image_tomate = pg.transform.scale(image_tomate, (50, 50))
image_tomate2 = pg.transform.scale(image_tomate2, (50, 50))

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
