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
from simulation import Simulation


class Button:
    
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
    
    def __init__(self):
        pg.init()
        self.state = "MENU"
        self.menu_choices = ["Random", "Choose"]
        self.SCREEN_HEIGHT = 0 
        self.SCREEN_WIDTH = 0
        self.clock = pg.time.Clock()
        
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
    
    
    def handle_events(self, buttons):
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
        return None
        
        
    def menu(self, fenetre : pg.Surface):
        """Display the menu screen and handle events 
        with button choices given in self.menu_choices"""
        self.update_screen_infos()

        # Set font
        title_font = pg.font.Font(None, 74)

        # Render title
        title_text = title_font.render("Automate Cellulaire", True, self.colors["text"])
        
        # Position title at the top
        fenetre.fill(self.colors["background"])
        fenetre.blit(title_text, ( self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

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
            action = self.handle_events(buttons.values())
            if action:
                self.state = action
                break

            self.clock.tick(200)  # Adjust tick speed to avoid excessive refresh
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
        simulation = Simulation(fenetre)
        
        if self.state == "Random":
            simulation.random_setup()
        elif self.state == "Choose":
            simulation.choice_setup()

        simulation.draw(fenetre)
        pg.display.update()
        
        
        running = True
        while running :
            
            simulation.apply_rules()
            
            simulation.pass_epoch()
            
            simulation.draw(fenetre)
            back_to_menu_button.draw(fenetre)
            
            # Event handling
            if self.handle_events([back_to_menu_button]) == "Back to Menu":
                running = False
                self.state = "MENU"
                break
            
            pg.display.update()
        
        pg.time.Clock().tick(200)
          
  
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
    game = Game()
    game.jouer()