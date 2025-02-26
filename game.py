"""UI filr for the game of life simulation

This file contains the Game class that manages the game loop and the display of the game.
It uses the simulation.py file that contain more of the behaviorial code for the simulation
to run the simulation and display it on the screen.

Creation date : 14 november 2024
Last update : 5 december 2024

"""

import pygame as pg
import sys
import random
from simulation.simulation import Simulation, ACTIONS
import time
from style.button import Button
from style.text_input import TextInput



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
    - param : dict : dictionnary of parameters for the simulation
    - update_screen_infos : update SCREEN_WIDTH and SCREEN_HEIGHT

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
        self.param = {
            "colonnes": 60,
            "lignes": 30,
            "eta": 10,
            "Parallel": 1,
            "mu": 0.5,
            "nu": 0.5,
            "grad_coeff": 0.3,
            "proba_player": 0.2,
            "proba_wall": 0.05,
            "classes": 1,
            "Productor": 0,
            "coeff_prod": 0.05,
            "exit": 1,
            "change_place": 0,
            "Diff": 0,
            "Decay": 0,
            "show_gradient": 0,
            "change_class": 0.001,

        }

        self.colors = {
            "background": (255, 255, 255),
            "text": (0, 0, 0),
            "button": (0, 128, 0),
            "hover": (34, 139, 34),
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

    def menu(self, fenetre: pg.Surface):
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
        fenetre.blit(
            title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100)
        )

        # Text input fields
        inputs = {
            "colonnes": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100,
                y=500,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["colonnes"]),
            ),
            "lignes": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100,
                y=550,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["lignes"]),
            ),
            "eta": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100,
                y=600,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["eta"]),
            ),
            "Parallel": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100,
                y=650,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["Parallel"]),
            ),
            "mu": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100,
                y=700,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["nu"]),
            ),
            "nu": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100,
                y=750,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["nu"]),
            ),
            "grad_coeff": TextInput(
                x=self.SCREEN_WIDTH // 2 - 100,
                y=800,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["grad_coeff"]),
            ),
            "proba_player": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300,
                y=800,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["proba_player"]),
            ),
            "proba_wall": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300,
                y=750,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["proba_wall"]),
            ),
            "classes": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300,
                y=700,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["classes"]),
            ),
            "Productor": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300,
                y=650,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["Productor"]),
            ),
            "coeff_prod": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300,
                y=600,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["coeff_prod"]),
            ),
            "exit": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300,
                y=550,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["exit"]),
            ),
            "change_place": TextInput(
                x=self.SCREEN_WIDTH // 2 + 300,
                y=500,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["change_place"]),
            ),
            "Diff": TextInput(
                x=self.SCREEN_WIDTH // 2 - 500,
                y=500,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["Diff"]),
            ),
            "Decay": TextInput(
                x=self.SCREEN_WIDTH // 2 - 500,
                y=550,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["Decay"]),
            ),
            "show_gradient": TextInput(
                x=self.SCREEN_WIDTH // 2 - 500,
                y=600,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["show_gradient"]),
            ),
            "change_class": TextInput(
                x=self.SCREEN_WIDTH // 2 - 500,
                y=650,
                width=200,
                height=40,
                font=input_font,
                color=self.colors["text"],
                active_color=self.colors["hover"],
                text=str(self.param["change_class"]),
            ),
        }
        # Button dimensions and positions
        button_width, button_height = 200, 60
        buttons = {}
        for i, choice in enumerate(self.menu_choices):
            buttons[choice] = Button(
                x=self.SCREEN_WIDTH // 2 - button_width // 2,
                y=300 + i * 100,
                width=button_width,
                height=button_height,
                text=choice,
                color=self.colors["button"],
                hover_color=self.colors["hover"],
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
                fenetre.blit(
                    input_text, (input_field.rect.x - 150, input_field.rect.y + 5)
                )
                input_field.draw(fenetre)

            self.clock.tick(500)  # Adjust tick speed to avoid excessive refresh
            pg.display.update()

    def run_simulation(self, fenetre: pg.Surface):
        """Run the simulation with the chosen mode,
        display the simulation and handle events like 'back to menu' button
        """

        self.update_screen_infos()

        # Draw title and background
        title_font = pg.font.Font(None, 74)
        title_text = title_font.render("Automate Cellulaire", True, self.colors["text"])
        fenetre.fill(self.colors["background"])
        fenetre.blit(
            title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100)
        )

        # draw back to menu button
        button_width, button_height = 300, 60
        back_to_menu_button = Button(
            x=self.SCREEN_WIDTH // 2 - button_width // 2,
            y=self.SCREEN_HEIGHT - button_height - 50,
            width=button_width,
            height=button_height,
            text="Back to Menu",
            color=(128, 128, 128),
            hover_color=(34, 139, 34),
        )
        back_to_menu_button.draw(fenetre)

        flag = True

        # Initialize simulation
        if flag:
            flag = False
            simulation = Simulation(
                fenetre,
                int(self.param["colonnes"]),
                int(self.param["lignes"]),
                float(self.param["proba_wall"]),
                float(self.param["proba_player"]),
                int(self.param["classes"]),
                bool(int(self.param["Productor"])),
                float(self.param["coeff_prod"]),
                bool(int(self.param["exit"])),
                float(self.param["change_place"]),
                float(self.param["Diff"]),
                float(self.param["Decay"]),
                bool(int(self.param["show_gradient"])),
                float(self.param['change_class'])
            )

        if self.state == "Random":
            simulation.random_setup()
        elif self.state == "Choose":
            simulation.choice_setup()

        simulation.draw(fenetre)
        pg.display.update()

        simulation.map.gradient_obstacle(float(self.param["grad_coeff"]), 2)

        def add(x, y, action):
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
        action = ACTIONS.DO_NOTHING

        pg.key.set_repeat(200, 50)
        while running:
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

                    if event.key == pg.K_t:
                        simulation.map.tomato_flag = True
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
                    elif event.key == pg.K_9:
                        if pg.key.get_mods() & pg.KMOD_SHIFT:
                            simulation.map.open_class(0)
                        else:
                            simulation.map.delete_class(0)
                    elif event.key == pg.K_8:
                        if pg.key.get_mods() & pg.KMOD_SHIFT:
                            simulation.map.open_class(1)
                        else:
                            simulation.map.delete_class(1)
                    elif event.key == pg.K_7:
                        if pg.key.get_mods() & pg.KMOD_SHIFT:
                            simulation.map.open_class(2)
                        else:
                            simulation.map.delete_class(2)
                    elif event.key == pg.K_6:
                        if pg.key.get_mods() & pg.KMOD_SHIFT:
                            simulation.map.open_class(3)
                        else:
                            simulation.map.delete_class(3)

                    x, y = pg.mouse.get_pos()
                    cell_x = x // simulation.map.taille_cellule
                    cell_y = y // simulation.map.taille_cellule
                    add(cell_x, cell_y, action)
            pg.display.update()

            if not self.param["Parallel"] == "1":
                simulation.apply_rules(
                    float(self.param["eta"]), float(self.param["nu"])
                )
            else:
                simulation.apply_rules_parallel(
                    float(self.param["eta"]),
                    float(self.param["mu"]),
                    float(self.param["nu"]),
                )
            # simulation.pass_epoch()

            simulation.draw(fenetre)
            back_to_menu_button.draw(fenetre)

            # Display max density
            density_font = pg.font.Font(None, 36)
            density_text = density_font.render(
                f"Densité maximale à cet instant: {simulation.max_density:.2f}", True, self.colors["text"]
            )
            fenetre.blit(density_text, (self.SCREEN_WIDTH - density_text.get_width() - 20, self.SCREEN_HEIGHT - 100))

            # Event handling
            if self.handle_events([back_to_menu_button], None, None) == "Back to Menu":
                running = False
                self.state = "MENU"
                break

            pg.time.delay(50)
            pg.display.update()

    def jouer(self):
        """fonction principale qui gère le passage entre le menu et la simulation"""

        self.update_screen_infos()

        fenetre = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # Initialize pg screen and other setup code here
        clock = pg.time.Clock()
        flag = True
        # Main loop
        while flag:
            if self.state == "MENU":
                self.menu(fenetre)

            else:
                self.run_simulation(fenetre)

            if not self.state:
                self.state = "MENU"


if __name__ == "__main__":
    print("Running the game")
    game = Game()
    game.jouer()
