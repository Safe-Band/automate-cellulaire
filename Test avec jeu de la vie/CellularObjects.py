import pygame
import sys
import random

LARGEUR_FENETRE = 100
HAUTEUR_FENETRE = 100
TAILLE_CELLULE = 75

image_tomate = pygame.image.load('./images/auTOMATE.png')  # Charger l'image de la tomate
image_tomate = pygame.transform.scale(image_tomate, (TAILLE_CELLULE, TAILLE_CELLULE))  # Redimensionner
image_tomate2 = pygame.image.load('./images/auTOMATE2.png')  # Charger l'image de la tomate
image_tomate2 = pygame.transform.scale(image_tomate2, (TAILLE_CELLULE, TAILLE_CELLULE))  # Redimensionner


#On crée une classe Cellule qui représente une cellule de l'automate cellulaire
class Cellule:
    """
        Classe représentant une cellule pour le jeu de la vie.
    attributs:
    x : int représentant la position x de la cellule
    y : int représentant la position y de la cellule
    etat : bool représentant l'état de la cellule (vivante ou morte)
    image : pygame.Surface représentant l'image de la cellule

        
    """
    def __init__(self, x, y, etat=False):
        self.x = x
        self.y = y
        self.etat = etat  # False = morte, True = vivante
        self.image = random.choice([image_tomate, image_tomate2])


class Grille:
    """
    Classe représentant une grille de cellules pour le jeu de la vie.

    Attributs:
    ----------
    largeur : int
        La largeur de la grille.
    hauteur : int
        La hauteur de la grille.
    grille : list
        Une liste 2D de cellules représentant la grille.

    Méthodes:
    ---------
    __init__(largeur, hauteur):
        Initialise la grille avec les dimensions spécifiées.
    cellule(x, y):
        Retourne la cellule à la position (x, y).
    recuperer_voisins(x, y):
        Retourne une liste des cellules voisines autour de la cellule à la position (x, y).
    appliquer_regles():
        Applique les règles du jeu de la vie à chaque cellule de la grille.
    afficher(fenetre):
        Affiche la grille sur la fenêtre spécifiée.
    """
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = [[Cellule(x, y) for x in range(largeur)] for y in range(hauteur)]

    def cellule(self, x, y):
        return self.grille[y][x]

    def recuperer_voisins(self, x, y):
        # On récupère les voisins autour de la cellule
        return [self.cellule(x + dx, y + dy) 
                for dx in [-1, 0, 1] 
                for dy in [-1, 0, 1] 
                if (dx != 0 or dy != 0) and 0 <= x + dx < self.largeur and 0 <= y + dy < self.hauteur]

    # On applique les règles du jeu de la vie pour chaque cellule, qu'on pourra mettre dans une boucle
    def appliquer_regles(self):
        nouvelle_grille = [[Cellule(x, y, cell.etat) for x, cell in enumerate(cells)] for y, cells in enumerate(self.grille)]
        for cells in self.grille:
            for cell in cells:
                voisins = self.recuperer_voisins(cell.x, cell.y)
                nb_voisins_vivants = sum([voisin.etat for voisin in voisins])
                if cell.etat:
                    if nb_voisins_vivants < 2 or nb_voisins_vivants > 3:
                        nouvelle_grille[cell.y][cell.x].etat = False
                else:
                    if nb_voisins_vivants == 3:
                        nouvelle_grille[cell.y][cell.x].etat = True
        self.grille = nouvelle_grille

    def afficher(self, fenetre):

        for cells in self.grille:

            for cell in cells:

                if cell.etat:
                    # Si la cellule est vivante, on affiche l'image de la tomate
                    fenetre.fill((255, 255, 255), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
                    fenetre.blit(cell.image, (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE))
                    pygame.draw.rect(fenetre, (0, 0, 0), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE), 1)  # 1 est l'épaisseur du contour

                else:
                    # Sinon, on colore la cellule en blanc (cellule morte)
                    pygame.draw.rect(fenetre, (255, 255, 255), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
                    pygame.draw.rect(fenetre, (0, 0, 0), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE), 1)  # 1 est l'épaisseur du contour

        pygame.display.update()

class AutomateCellulaire:
    """
    Classe représentant un automate cellulaire.
    Attributes:
        grille (Grille): La grille de l'automate cellulaire.
    Methods:
        __init__(largeur, hauteur):
            Initialise une nouvelle instance de l'automate cellulaire avec une grille de dimensions spécifiées.
        avancer():
            Avance l'automate cellulaire d'une étape en appliquant les règles de transition aux cellules de la grille.
        jouer(nb_iter, grille_initiale="random"):
            Lance le jeu de l'automate cellulaire pour un nombre spécifié d'itérations. Permet de choisir une grille initiale aléatoire
            on peut mettre random pour créer une grille random ou choose pour créer une grille choisie par l'utilisateur
    """
    def __init__(self, largeur, hauteur):
        self.grille = Grille(largeur, hauteur)

    def avancer(self):
        self.grille.appliquer_regles()

    def jouer(self, nb_iter, grille_initiale="random"):
        pygame.init()
        fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
        pygame.display.set_caption("Automate Cellulaire")

        # Initialisation de la grille
        if grille_initiale == "random":
            for cells in self.grille.grille:
                for cell in cells:
                    cell.etat = random.choice([True, False])
        elif grille_initiale == "choose":
            fenetre.fill((255, 255, 255))  # Fond blanc
            self.grille.afficher(fenetre)
            pygame.display.update()
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos
                        cell_x = x // TAILLE_CELLULE
                        cell_y = y // TAILLE_CELLULE
                        cell = self.grille.cellule(cell_x, cell_y)
                        cell.etat = not cell.etat
                        self.grille.afficher(fenetre)
                        pygame.display.update()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        running = False

        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Avancer le jeu et afficher la nouvelle grille
            self.avancer()
            fenetre.fill((255, 255, 255))  # Fond blanc pour effacer l'écran
            self.grille.afficher(fenetre)
            pygame.display.update()

            clock.tick(10)  # Limiter la vitesse du jeu (10 itérations par seconde)


