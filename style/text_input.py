import pygame as pg

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
        inner_rect = self.rect.inflate(
            -4, -4
        )  # Réduire légèrement pour éviter d'écraser le contour
        screen.fill((255, 255, 255), inner_rect)

        # Rendu du texte aligné à droite
        text_surface = self.font.render(self.text, True, color)
        text_x = (
            self.rect.x + self.rect.width - text_surface.get_width() - 5
        )  # Déplacer vers la droite
        screen.blit(text_surface, (text_x, self.rect.y + 5))

        # Affichage du curseur uniquement si actif
        if self.active:
            if self.cursor_visible:
                cursor_x = text_x + text_surface.get_width()
                cursor_y = self.rect.y + 5
                pg.draw.line(
                    screen,
                    color,
                    (cursor_x, cursor_y),
                    (cursor_x, cursor_y + self.rect.height - 10),
                )

            # Gestion du clignotement du curseur
            if pg.time.get_ticks() - self.cursor_timer > 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = pg.time.get_ticks()
