import pygame
import sys
import random

image_tomate = pygame.image.load('./images/auTOMATE.png')
image_tomate2 = pygame.image.load('./images/auTOMATE2.png')
image_tomate = pygame.transform.scale(image_tomate, (50, 50))

image_tomate = pygame.image.load('./images/auTOMATE.png')
image_tomate2 = pygame.image.load('./images/auTOMATE2.png')
image_tomate = pygame.transform.scale(image_tomate, (50, 50))

class Cellule:
    def __init__(self, x, y, taille, etat=False):
    def __init__(self, x, y, taille, etat=False):
        self.x = x
        self.y = y
        self.etat = etat
        self.image = pygame.transform.scale(random.choice([image_tomate, image_tomate2]), (taille, taille))
        self.etat = etat
        self.image = pygame.transform.scale(random.choice([image_tomate, image_tomate2]), (taille, taille))

class Grille:
    def __init__(self, largeur, hauteur, taille):
    def __init__(self, largeur, hauteur, taille):
        self.largeur = largeur
        self.hauteur = hauteur
        self.grille = [[Cellule(x, y, taille) for x in range(largeur)] for y in range(hauteur)]
        self.grille = [[Cellule(x, y, taille) for x in range(largeur)] for y in range(hauteur)]

    def cellule(self, x, y):
        return self.grille[y][x]

    def recuperer_voisins(self, x, y):
        return [self.cellule(x + dx, y + dy) 
                for dx in [-1, 0, 1] 
                for dy in [-1, 0, 1] 
                if (dx != 0 or dy != 0) and 0 <= x + dx < self.largeur and 0 <= y + dy < self.hauteur]

    def appliquer_regles(self, taille):
        nouvelle_grille = [[Cellule(x, y, taille, cell.etat) for x, cell in enumerate(cells)] for y, cells in enumerate(self.grille)]
    def appliquer_regles(self, taille):
        nouvelle_grille = [[Cellule(x, y, taille, cell.etat) for x, cell in enumerate(cells)] for y, cells in enumerate(self.grille)]
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

    def afficher(self, fenetre, TAILLE_CELLULE, Screen_Width, Screen_Height):
        for cells in self.grille:
            for cell in cells:
                if cell.etat:
                    fenetre.fill((255, 255, 255), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
                    fenetre.blit(cell.image, (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE))
                    pygame.draw.rect(fenetre, (200, 200, 200), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE), 1)
                    pygame.draw.rect(fenetre, (200, 200, 200), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE), 1)
                else:
                    pygame.draw.rect(fenetre, (255, 255, 255), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE))
                    pygame.draw.rect(fenetre, (200, 200, 200), (cell.x * TAILLE_CELLULE, cell.y * TAILLE_CELLULE, TAILLE_CELLULE, TAILLE_CELLULE), 1)
        
        # Draw the "Back to Menu" button
        button_width, button_height = 200, 50
        button_x = Screen_Width // 2 - button_width // 2
        button_y = Screen_Height - button_height - 50
        pygame.draw.rect(fenetre, (128, 128, 128), (button_x, button_y, button_width, button_height))

                # Draw the button text
        font = pygame.font.Font(None, 36)
        button_text = font.render("Back to Menu", True, (255, 255, 255))
        fenetre.blit(button_text, (button_x + (button_width - button_text.get_width()) // 2, button_y + (button_height - button_text.get_height()) // 2))

        pygame.display.update()

class AutomateCellulaire:
    def __init__(self, largeur, hauteur):
        pygame.init()
        screen_info = pygame.display.Info()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
        self.TAILLE_CELLULE = min(self.SCREEN_WIDTH // largeur, self.SCREEN_HEIGHT // hauteur)
        self.grille = Grille(largeur, hauteur, self.TAILLE_CELLULE)
        self.state = "MENU"
        
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

        pygame.display.update()

        # Handle button clicks

    # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if random_button_rect.collidepoint(event.pos):
                    
                    self.state = "SETUP_RANDOM"  # État pour "Random"
                elif choose_button_rect.collidepoint(event.pos):
                    self.state = "SETUP"  # État pour "Choose"
            
        pygame.display.update()

    def avancer(self):
        self.grille.appliquer_regles(self.TAILLE_CELLULE)
    
    def jouer(self):
        fenetre = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # Initialize Pygame screen and other setup code here
        clock = pygame.time.Clock()

        # Main loop
        while True:
            if self.state == "MENU":
                # Show menu function here
                self.afficher_menu(fenetre)

            elif self.state == "SETUP":
                self.setup_grille(fenetre)

            elif self.state == "SETUP_RANDOM":
                # Set up grid with random states
                for cells in self.grille.grille:
                    for cell in cells:
                        cell.etat = random.choice([True, False])
                self.state = "RUNNING"

            elif self.state == "RUNNING":
                # Progress the automaton and fill the background
                self.avancer()
                fenetre.fill((255, 255, 255))
                self.grille.afficher(fenetre, self.TAILLE_CELLULE, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

                
                button_width, button_height = 200, 50
                button_x = self.SCREEN_WIDTH // 2 - button_width // 2
                # Event handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos
                        # Check if the click is within the button area
                        if button_x <= x <= button_x + button_width and button_y <= y <= button_y + button_height:
                            self.state = "MENU"  # Go back to menu

            # Control frame rate
                clock.tick(5)  # Adjust tick speed to avoid excessive refresh

    def setup_grille(self, fenetre):
        print("hello")
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
               
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_held = True
                    x, y = event.pos
                    cell_x = x // self.TAILLE_CELLULE
                    cell_y = y // self.TAILLE_CELLULE
                    cell = self.grille.cellule(cell_x, cell_y)
                    cell.etat = not cell.etat
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_held = False
                
                
                    
                

            # Check if mouse is held down and moved to draw
            if mouse_held:
                x, y = pygame.mouse.get_pos()
                cell_x = x // self.TAILLE_CELLULE
                cell_y = y // self.TAILLE_CELLULE
                cell = self.grille.cellule(cell_x, cell_y)
                cell.etat = True  # Set cell to alive when dragging

            # Redraw the grid
            fenetre.fill((255, 255, 255))
            self.grille.afficher(fenetre, self.TAILLE_CELLULE)
            pygame.display.update()


