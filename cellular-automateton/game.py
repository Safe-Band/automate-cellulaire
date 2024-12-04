""" UI filr for the game of life simulation

This file contains the Game class that manages the game loop and the display of the game.
It uses the simulation.py file that contain more of the behaviorial code for the simulation
to run the simulation and display it on the screen.

Creation date : 14 november 2024
Last update : 14 november 2024  

"""

import pygame as pg
import sys
import random
from simulation import Simulation, ACTIONS



class TextInput:
    def __init__(self, x, y, width, height, font, color, active_color, text=""):
        self.rect = pg.Rect(x, y, width, height)
        self.font = font
        self.color = color
        self.active_color = active_color
        self.text = text
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = pg.time.get_ticks()
        
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # Toggle l'activation si on clique sur le champ
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False  # Désactive si on clique en dehors

        if event.type == pg.KEYDOWN and self.active:  # Agit seulement si actif
            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]  # Supprime le dernier caractère
            elif event.key == pg.K_RETURN:
                self.active = False  # Désactive le champ sur Entrée (optionnel)
            else:
                self.text += event.unicode  # Ajoute le caractère saisi

        return self.text
    
    def draw(self, screen):
        # Couleur dynamique selon l'état actif
        color = self.active_color if self.active else self.color

        # Dessiner le contour du champ
        pg.draw.rect(screen, color, self.rect, 2)

        # Effacer l'intérieur du champ (remplissage blanc sans toucher au contour)
        inner_rect = self.rect.inflate(-4, -4)  # Réduire légèrement pour éviter d'écraser le contour
        screen.fill((255, 255, 255), inner_rect)

        # Rendu du texte aligné à droite
        text_surface = self.font.render(self.text, True, color)
        text_x = self.rect.x + self.rect.width - text_surface.get_width() - 5 # Déplacer vers la droite
        screen.blit(text_surface, (text_x, self.rect.y + 5))

        # Affichage du curseur uniquement si actif
        if self.active:
            if self.cursor_visible:
                cursor_x = text_x + text_surface.get_width()
                cursor_y = self.rect.y + 5
                pg.draw.line(screen, color, (cursor_x, cursor_y), (cursor_x, cursor_y + self.rect.height - 10))

            # Gestion du clignotement du curseur
            if pg.time.get_ticks() - self.cursor_timer > 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = pg.time.get_ticks()

class Button:
    """
    Class that represents a button in the game.
    attributes:
    - x : int : x position of the button
    - y : int : y position of the button
    - width : int : width of the button
    - height : int : height of the button
    - text : str : text displayed on the button
    - color : tuple : color of the button
    - hover_color : tuple : color of the button when hovered
    - rect : pg.Rect : rectangle object representing the button
    methods:
    - draw : draw the button on the screen
    """
    
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.rect = pg.Rect(x, y, width, height)

        
    def draw(self, fenetre : pg.Surface):
        mouse_x, mouse_y = pg.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_x, mouse_y) else self.color
        pg.draw.rect(fenetre, color, self.rect, border_radius=15)
        pg.draw.rect(fenetre, (0, 0, 0), self.rect, 3, border_radius=15)
        
        # Center the text on the button
        button_font = pg.font.Font(None, 50)
        button_text = button_font.render(self.text, True, (255, 255, 255))
        fenetre.blit(button_text, (self.rect.centerx - button_text.get_width() // 2, self.rect.centery - button_text.get_height() // 2))

        
class Game:

    """
    Class that manages the game loop and the display of the game.
    It uses the simulation.py file that contain more of the behaviorial code for the simulation
    to run the simulation and display it on the screen.
    attributes:
    - state : str : current state of the game (MENU or Random or Choose)
    - menu_choices : list : list of choices for the menu screen
    - SCREEN_HEIGHT : int : height of the screen
    - SCREEN_WIDTH : int : width of the screen
    - clock : pg.time.Clock : clock object to manage the game speed
    - eta : float : parameter for the parallel version of the simulation
    - parallel : bool : True if the parallel version of the simulation is used
    - colors : dict : dictionnary of colors used in the game
    methods:
    - update_screen_infos : update SCREEN_WIDTH and SCREEN_HEIGHT
    - handle_events : handle events for the menu screen
    - menu : display the menu screen and handle events
    - run_simulation : run the simulation with the chosen mode
    - jouer : main function that manages the passage between the menu and the simulation
    """
    
    def __init__(self):
        pg.init()
        self.state = "MENU"
        self.menu_choices = ["Random", "Choose"]
        self.SCREEN_HEIGHT = 0 
        self.SCREEN_WIDTH = 0
        self.clock = pg.time.Clock()
        self.param = {'colonnes': 60, 
                      'lignes': 30,
                      'eta': 10,
                      'Parallel': 1,
                      'mu': 0.5,
                      'nu': 0.5,
                      'grad_coeff': 0.3,
                      'proba_player': 0.2,
                      'proba_wall': 0.05,
                      'classes': 1,
                      'Productor': 0,
                      'coeff_prod': 0.05,
                      'exit': 1,
                      'change_place': 0
                      }
                      
        
        self.colors = {
            "background": (255, 255, 255),
            "text": (0, 0, 0),
            "button": (0, 128, 0),
            "hover": (34, 139, 34)
        }
        
        self.update_screen_infos()
        
        
    def update_screen_infos(self):
        """update SCREEN_WIDTH and SCREEN_HEIGHT"""
        screen_infos = pg.display.Info()
        self.SCREEN_WIDTH = screen_infos.current_w
        self.SCREEN_HEIGHT = screen_infos.current_h
    
    
    def handle_events(self, buttons, inputs, label):
        """Handle events for the menu screen with two functionnalities:
        - Quit the game if the user closes the window
        - return text of the button clicked if a button is clicked
        - else, return None
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.rect.collidepoint(event.pos):
                        return button.text
            if inputs:
                for name, input_field in inputs.items():
                        value = input_field.handle_event(event)
                        if value:
                            self.param[name] = value

        return None
        
        
    def menu(self, fenetre : pg.Surface):
        """Display the menu screen and handle events 
        with button choices given in self.menu_choices"""
        self.update_screen_infos()

        # Font and input fields
        title_font = pg.font.Font(None, 74)
        input_font = pg.font.Font(None, 36)

        # Render title
        title_text = title_font.render("Automate Cellulaire", True, self.colors["text"])
        
        # Position title at the top
        fenetre.fill(self.colors["background"])
        fenetre.blit(title_text, ( self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))


        # Text input fields
        inputs = {
            "colonnes": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100, y=500, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['colonnes'])
            ),
            "lignes": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100, y=550, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['lignes'])
            ),
            "eta": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100, y=600, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['eta'])
            ),
            "Parallel": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100, y=650, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['Parallel'])
            ),
            "mu": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100, y=700, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['nu'])
            ),
            "nu": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100, y=750, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['nu'])
            ),
            "grad_coeff": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100, y=800, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['grad_coeff'])
            ),
            "proba_player": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300, y=800, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['proba_player'])
            ),
            "proba_wall": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300, y=750, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['proba_wall'])
            ),
            "classes": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300, y=700, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['classes'])
            ),
            "Productor": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300, y=650, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['Productor'])
            ),
            "coeff_prod": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300, y=600, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['coeff_prod'])
            ),
            "exit": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300, y=550, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['exit'])
            ),
            "change_place": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300, y=500, width=200, height=40,
                font=input_font, color=self.colors["text"], active_color=self.colors["hover"], text = str(self.param['change_place'])
            )


    }
        # Button dimensions and positions
        button_width, button_height = 200, 60
        buttons = {}
        for i, choice in enumerate(self.menu_choices):
            buttons[choice] = Button( 
                x = self.SCREEN_WIDTH // 2 - button_width // 2,
                y = 300 + i * 100,
                width = button_width,
                height = button_height,
                text = choice,
                color = self.colors["button"],
                hover_color = self.colors["hover"]
                )
        


        # Draw the buttons and handle events
        while self.state == "MENU":
            
            self.update_screen_infos()
            
            # update buttons display (for hover effect)
            for button in buttons.values():
                button.draw(fenetre)
            
            # Gestion des événements
            action = self.handle_events(buttons.values(), inputs, "Menu")
        

            if action:
                self.state = action
                break

            for label, input_field in inputs.items():
                input_text = input_font.render(label, True, self.colors["text"])
                fenetre.blit(input_text, (input_field.rect.x - 150, input_field.rect.y + 5))
                input_field.draw(fenetre)

            


            self.clock.tick(500)  # Adjust tick speed to avoid excessive refresh
            pg.display.update()
    
    
    def run_simulation(self, fenetre : pg.Surface):
        """Run the simulation with the chosen mode,
        display the simulation and handle events like 'back to menu' button
        """
            
        self.update_screen_infos()
        
        # Draw title and background
        title_font = pg.font.Font(None, 74)
        title_text = title_font.render("Automate Cellulaire", True, self.colors["text"])
        fenetre.fill(self.colors["background"])
        fenetre.blit(title_text, ( self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # draw back to menu button
        button_width, button_height = 300, 60
        back_to_menu_button = Button(
            x = self.SCREEN_WIDTH // 2 - button_width // 2,
            y = self.SCREEN_HEIGHT - button_height - 50,
            width = button_width,
            height = button_height,
            text = "Back to Menu",
            color = (128, 128, 128),
            hover_color = (34, 139, 34)
            )
        back_to_menu_button.draw(fenetre)
    
        # Initialize simulation
        simulation = Simulation(fenetre, int(self.param['colonnes']), int(self.param['lignes']), float(self.param['proba_wall']) , float(self.param['proba_player']), int(self.param['classes']), bool(int(self.param['Productor'])), float(self.param['coeff_prod'] ), bool(int(self.param['exit'])), float(self.param['change_place']))
        
        if self.state == "Random":
            simulation.random_setup()
        elif self.state == "Choose":
            simulation.choice_setup()

        simulation.draw(fenetre)
        pg.display.update()
        
        simulation.map.gradient_obstacle( float(self.param['grad_coeff']) , 2 )
        
        def add(x,y,action):
            if x >= simulation.map.nb_colonnes or y >= simulation.map.nb_lignes:
                return
            cell = simulation.map.cellule(x, y)
            match action:
                case ACTIONS.ADDING_WALLS:
                    simulation.map.ajouter_mur(x, y)
                case ACTIONS.ADDING_DOORS:
                    simulation.map.ajouter_porte(x, y)
                case ACTIONS.ADDING_PLAYERS:
                    simulation.map.add_player(x, y)
                case ACTIONS.ADDING_PRODUCTORS:
                    simulation.map.add_productor(x, y)
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
                case ACTIONS.DO_NOTHING:
                    pass
            cell.draw(simulation.fenetre)
        

        running = True
        mouse_held = False
        action = ACTIONS.ADDING_PLAYERS

        pg.key.set_repeat(20, 5)
        while running :

            for event in pg.event.get():
                # fermeture de la fenêtre
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                # pression sur la touche entrée pour valider le placement des joueurs
                
                # clic de souris
                

                
                elif event.type == pg.KEYDOWN:
                    
                    def act(action, actions):
                        if action == actions:
                            action = ACTIONS.DO_NOTHING
                        else:
                            action = actions
                        return action
                    if event.key == pg.K_RETURN:
                        running = False
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
                    cell_x = x // simulation.map.taille_cellule
                    cell_y = y // simulation.map.taille_cellule
                    add(cell_x, cell_y, action)

            pg.display.update()
                

            
            


            if not self.param['Parallel'] == "1":
                simulation.apply_rules(float(self.param['eta']), float(self.param['nu']) )
            else:
                simulation.apply_rules_parallel( float(self.param['eta']), float(self.param['mu']),float(self.param['nu']) )
            
            # simulation.pass_epoch()
            
            simulation.draw(fenetre)
            back_to_menu_button.draw(fenetre)
            
            # Event handling
            if self.handle_events([back_to_menu_button], None, None) == "Back to Menu":
                running = False
                self.state = "MENU"
                break
            
        
            pg.time.delay(50)
            pg.display.update()
          
  
    def jouer(self):
        """ fonction principale qui gère le passage entre le menu et la simulation"""
        
        self.update_screen_infos()
        
        fenetre = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # Initialize pg screen and other setup code here
        clock = pg.time.Clock()

        # Main loop
        while True:

            if self.state == "MENU":
                self.menu(fenetre)
                
            else : 
                self.run_simulation(fenetre)
            
            if not self.state :
                self.state = "MENU"
                    
                    

if __name__ == "__main__":
    print("Running the game")
    game = Game()
    game.jouer()