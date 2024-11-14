import pygame
import sys
import random
import math
import numpy as np

try:
    image_tomate = pygame.image.load('./images/auTOMATE.png')
    image_tomate2 = pygame.image.load('./images/auTOMATE2.png')
except pygame.error as e:
    print(f"Error loading image: {e}")
    sys.exit()

class Cellule:
    def __init__(self, x, y, taille, nombre_classes,etat=False):
        self.x = x
        self.y = y
        self.etat = etat
        self.classe = random.choice(range(nombre_classes))
        self.image = pygame.transform.scale(random.choice([image_tomate, image_tomate2]), (taille, taille))
        
        if self.classe == 1:
            self.image.fill((0, 0, 255), special_flags=pygame.BLEND_MULT)  # Blue
        elif self.classe == 2:
            self.image.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)  # Red
        elif self.classe == 3:
            self.image.fill((255, 255, 0), special_flags=pygame.BLEND_MULT)  # Yellow
        elif self.classe == 4:
            self.image.fill((255, 165, 0), special_flags=pygame.BLEND_MULT)  # Orange
class Grille:
    def __init__(self, largeur, hauteur, taille, x0, y0, porte = None, mur = None):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = [[Cellule(x, y, taille, len(x0)) for x in range(largeur)] for y in range(hauteur)]
        self.distance = [[[math.sqrt((x0[i] - x)**2 + (y0[i] - y)**2) for x in range(self.largeur)] for y in range(self.hauteur)] for i in range(len(x0))]
        if porte:
            self.porte = porte
        else:
            self.porte = []
            for i in range(len(x0)):
                self.porte.append([x0[i], y0[i]])

        if mur:
            self.mur = mur
        else:
            self.mur = [(x, 0) for x in range(largeur)] + [(x, hauteur - 1) for x in range(largeur)] + [(0, y) for y in range(hauteur)] + [(largeur - 1, y) for y in range(hauteur)]
            self.mur = [pos for pos in self.mur if pos not in self.porte]
        

    def cellule(self, x, y):
        return self.grille[y][x]
    
    def ajouter_mur(self, x, y):
        if (x, y) not in self.mur and (x, y) not in self.porte:
            self.mur.append((x, y))

    def ajouter_porte(self, x, y):
        if (x, y) not in self.porte and (x, y) not in self.mur:
            self.porte.append((x, y))
    def deplacement(self, cell1, x, y):
        if cell1.etat:
            cell2 = self.cellule(x, y)
            cell2.x = cell1.x
            cell2.y = cell1.y
            cell1.x = x
            cell1.y = y
            
            
    def appliquer_regles(self, eta = 0.1, Parallel= False, mu = 1):
        if Parallel:

            # Step 1: Initialize the conflict grid
            conflict_grille = [[None for _ in range(self.largeur)] for _ in range(self.hauteur)]
            active_cells = [cell for row in self.grille for cell in row if cell.etat]
            random.shuffle(active_cells)

            # Step 2: Populate conflict_grille with intended moves
            for cell in active_cells:
                if (cell.x, cell.y) in self.porte:
                    cell.etat = False
                    continue
                # Define neighbor positions
                voisin_positions = [
                    (cell.x, cell.y - 1),
                    (cell.x, cell.y + 1),
                    (cell.x - 1, cell.y),
                    (cell.x + 1, cell.y),
                    (cell.x, cell.y)
                ]

                # Filter valid neighbors
                voisins_valides = [
                    pos for pos in voisin_positions
                    if 0 <= pos[0] < self.largeur and 0 <= pos[1] < self.hauteur
                    and (not self.grille[pos[1]][pos[0]].etat or pos == (cell.x, cell.y))
                    and pos not in self.mur
                ]

                # Calculate distances and probabilities
                H = np.array([self.distance[cell.classe][pos[1]][pos[0]] for pos in voisins_valides])
                W = np.exp(-eta * H)
                W /= W.sum()  # Normalize probabilities

                # Choose a position based on the probability distribution
                chosen_index = np.random.choice(len(W), p=W)
                chosen_pos = voisins_valides[chosen_index]

                # Record intended move in conflict_grille
                conflict_grille[chosen_pos[1]][chosen_pos[0]] = conflict_grille[chosen_pos[1]][chosen_pos[0]] or []
                conflict_grille[chosen_pos[1]][chosen_pos[0]].append(cell)

            # Step 3: Resolve conflicts in conflict_grille
            for y in range(self.hauteur):
                for x in range(self.largeur):
                    if conflict_grille[y][x]:
                        conflit = random.random() < mu
                        if conflit or len(conflict_grille[y][x]) == 1:
                            # Resolve conflict by choosing a random winner
                            winner = random.choice(conflict_grille[y][x])
                            # Update the winner's state
                            self.deplacement(winner, x, y)
                    
            
        else:
            # Obtenir une liste des cellules actives et la mélanger aléatoirement
            active_cells = [cell for row in self.grille for cell in row if cell.etat]
            random.shuffle(active_cells)
            # Mettre à jour les états des cellules actives
            for cell in active_cells:
                if (cell.x, cell.y) in self.porte:
                    cell.etat = False
                else:
                    # Positions voisines : haut, bas, gauche, droite, et la position actuelle
                    voisin_positions = [
                        (cell.x, cell.y - 1),
                        (cell.x, cell.y + 1),
                        (cell.x - 1, cell.y),
                        (cell.x + 1, cell.y),
                        (cell.x, cell.y)
                    ]

                    # Conserver uniquement les positions valides
                    voisins_valides = [pos for pos in voisin_positions if 0 <= pos[0] < self.largeur and 0 <= pos[1] < self.hauteur and (not self.grille[pos[1]][pos[0]].etat or pos == (cell.x, cell.y)) and pos not in self.mur]

                    # Calcul des distances pour les positions valides
                    H = np.array([self.distance[cell.classe][pos[1]][pos[0]] for pos in voisins_valides])

                    # Calcul des poids avec une distribution de Boltzmann
                    W = np.exp(-eta * H)
                    W /= W.sum()  # Normalisation pour avoir une somme de probabilités de 1

                    # Choix de la position en fonction de la distribution de probabilités
                    chosen_index = np.random.choice(len(W), p=W)
                    chosen_pos = voisins_valides[chosen_index]

                    # Activer la cellule choisie
                    if chosen_pos != (cell.x, cell.y):
                        self.deplacement(cell, chosen_pos[0], chosen_pos[1])

    def afficher(self, fenetre, TAILLE_CELLULE, button_x, button_y, button_width, button_height):
        for cells in self.grille:
            for cell in cells:
                if cell.etat:
                    fenetre.fill((255, 255, 255), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
                    fenetre.blit(cell.image, (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE))
                    pygame.draw.rect(fenetre, (200, 200, 200), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE), 1)
                else:
                    pygame.draw.rect(fenetre, (255, 255, 255), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
                    pygame.draw.rect(fenetre, (200, 200, 200), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE), 1)
        pygame.draw.rect(fenetre, (128, 128, 128), (button_x, button_y, button_width, button_height))
        font = pygame.font.Font(None, 36)
        button_text = font.render("Back to Menu", True, (255, 255, 255))
        fenetre.blit(button_text, (button_x + (button_width - button_text.get_width()) // 2, button_y + (button_height - button_text.get_height()) // 2))
        for (px, py) in self.porte:
            pygame.draw.rect(fenetre, (165, 42, 42), (px * TAILLE_CELLULE, py * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
        for (px, py) in self.mur:
            pygame.draw.rect(fenetre, (0, 0, 0), (px * TAILLE_CELLULE, py * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
        pygame.display.update()

class AutomateCellulaire:
    def __init__(self, largeur, hauteur):
        pygame.init()
        screen_info = pygame.display.Info()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
        self.TAILLE_CELLULE = min(self.SCREEN_WIDTH // largeur, self.SCREEN_HEIGHT // hauteur)
        self.grille = Grille(largeur, hauteur, self.TAILLE_CELLULE, [largeur // 2, largeur - 2], [hauteur - 2, hauteur // 2])
        self.state = "MENU"
        # Variables pour suivre l'état de la configuration
        self.is_adding_wall = False
        self.is_adding_door = False
        self.is_adding_cell = False 

    def afficher_menu(self, fenetre):
        # Define colors
        background_color = (255, 255, 255)
        text_color = (0, 0, 0)
        button_color = (0, 128, 0)
        hover_color = (34, 139, 34)

        # Set font
        title_font = pygame.font.Font(None, 74)
        button_font = pygame.font.Font(None, 50)

        # Render title
        title_text = title_font.render("Automate Cellulaire", True, text_color)
        
        # Position title at the top
        fenetre.fill(background_color)
        fenetre.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Button dimensions and positions
        button_width, button_height = 200, 60
        random_button_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - button_width // 2, 300, button_width, button_height)
        choose_button_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - button_width // 2, 400, button_width, button_height)

        # Get mouse position for hover effect
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Define hover effect
        def draw_button(rect, text):
            # Change color on hover
            color = hover_color if rect.collidepoint(mouse_x, mouse_y) else button_color
            pygame.draw.rect(fenetre, color, rect, border_radius=15)
            pygame.draw.rect(fenetre, (0, 0, 0), rect, 3, border_radius=15)  # Border for the button

            # Center the text on the button
            button_text = button_font.render(text, True, (255, 255, 255))
            fenetre.blit(button_text, (rect.centerx - button_text.get_width() // 2, rect.centery - button_text.get_height() // 2))

        # Draw the buttons
        draw_button(random_button_rect, "Random")
        draw_button(choose_button_rect, "Choose")

        # Update the screen after drawing the buttons
        pygame.display.update()

        # Handle button clicks and state transitions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if random_button_rect.collidepoint(event.pos):
                    self.state = "SETUP_RANDOM"  # Transition to random setup
                elif choose_button_rect.collidepoint(event.pos):
                    self.state = "SETUP"  # Transition to manual setup

    def avancer(self):
        self.grille.appliquer_regles(1)
    
    def jouer(self):
        fenetre = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        clock = pygame.time.Clock()

        while True:
            # Gestion des événements
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                if self.state == "MENU":
                    self.afficher_menu(fenetre)

                elif self.state == "SETUP":
                    self.setup_grille(fenetre)
                    if self.state == "RUNNING":
                        continue

                elif self.state == "SETUP_RANDOM":
                    # Set up grid with random states
                    for cells in self.grille.grille:
                        for cell in cells:
                            if (cell.x, cell.y) not in self.grille.mur:
                                cell.etat = random.random() < 0.1  # 10% chance of being True
                            
                    self.state = "RUNNING"
                elif self.state == "RUNNING":
                    self.avancer()

                    # Dessiner le bouton "Retour au Menu"
                    button_width, button_height = 200, 50
                    button_x = self.SCREEN_WIDTH // 2 - button_width // 2
                    button_y = self.SCREEN_HEIGHT - button_height - 50
                    self.grille.afficher(fenetre, self.TAILLE_CELLULE, button_x, button_y, button_width, button_height)
                clock.tick(30)  # Limit the frame rate to 10 FPS
                    
    def setup_grille(self, fenetre):
        running = True
        mouse_held = False  # Track if the mouse button is held down

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = "RUNNING"
                    running = False

                # Handle mouse clicks to add walls, doors or cells
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_held = True
                    x, y = event.pos
                    cell_x = x // self.TAILLE_CELLULE
                    cell_y = y // self.TAILLE_CELLULE
                    cell = self.grille.cellule(cell_x, cell_y)

                    if self.is_adding_wall:
                        # Add wall
                        if (cell_x, cell_y) not in self.grille.mur:
                            self.grille.ajouter_mur(cell_x, cell_y)
                    elif self.is_adding_door:
                        # Add door
                        if (cell_x, cell_y) not in self.grille.porte:
                            self.grille.ajouter_porte(cell_x, cell_y)
                    elif self.is_adding_cell:
                        # Add a new cell
                        self.grille.cellule(cell_x, cell_y).etat = True

                # Toggle the mode (wall, door, or cell) based on key presses
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.is_adding_wall = True
                        self.is_adding_door = False
                        self.is_adding_cell = False
                    elif event.key == pygame.K_d:
                        self.is_adding_door = True
                        self.is_adding_wall = False
                        self.is_adding_cell = False
                    elif event.key == pygame.K_c:
                        self.is_adding_cell = True
                        self.is_adding_wall = False
                        self.is_adding_door = False

                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_held = False
            
            # Check if mouse is held down and moved to draw
            if mouse_held:
                x, y = pygame.mouse.get_pos()
                cell_x = x // self.TAILLE_CELLULE
                cell_y = y // self.TAILLE_CELLULE
                cell = self.grille.cellule(cell_x, cell_y)
                if self.is_adding_wall:
                    self.grille.ajouter_mur(cell_x, cell_y)
                elif self.is_adding_door:
                    self.grille.ajouter_porte(cell_x, cell_y)
                elif self.is_adding_cell:
                    cell.etat = True

            # Clear the screen and redraw the grid with updated information
            fenetre.fill((255, 255, 255))  # Clear screen with white background

            # Redraw the grid with the updated state (walls, doors, cells)
            self.grille.afficher(fenetre, self.TAILLE_CELLULE, self.SCREEN_WIDTH // 2 - 200 // 2, self.SCREEN_HEIGHT - 50 - 50, 200, 50)

            pygame.display.update()  # Update the display
