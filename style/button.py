import pygame as pg

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

    def draw(self, fenetre: pg.Surface):
        mouse_x, mouse_y = pg.mouse.get_pos()
        color = (
            self.hover_color if self.rect.collidepoint(mouse_x, mouse_y) else self.color
        )
        pg.draw.rect(fenetre, color, self.rect, border_radius=15)
        pg.draw.rect(fenetre, (0, 0, 0), self.rect, 3, border_radius=15)

        # Center the text on the button
        button_font = pg.font.Font(None, 50)
        button_text = button_font.render(self.text, True, (255, 255, 255))
        fenetre.blit(
            button_text,
            (
                self.rect.centerx - button_text.get_width() // 2,
                self.rect.centery - button_text.get_height() // 2,
            ),
        )
