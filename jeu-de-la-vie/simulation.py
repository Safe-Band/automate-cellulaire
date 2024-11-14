import pygame as pg
import random
import sys

image_tomate = pg.image.load('./images/auTOMATE.png')
image_tomate2 = pg.image.load('./images/auTOMATE2.png')
image_tomate = pg.transform.scale(image_tomate, (50, 50))


# class Player:
    
#     def __init__(self):
#         pass


# class Map:
    
#     def __init__(self):
#         self.WIDTH = 0
#         self.HEIGHT = 0
        
#     def initiate(self, screen_info):
#         """ give the map the size it could take"""
#         self.WIDTH = screen_info.current_w
#         self.HEIGHT = screen_info.current_h
        
class Cellule:
    def __init__(self, x, y, taille, is_alive=False):
        self.x = x
        self.y = y
        self.current_state = is_alive
        self.next_state = is_alive
        self.taille = taille
        self.image = pg.transform.scale(random.choice([image_tomate, image_tomate2]), (taille, taille))
        
    def regles_de_comportement(self, voisins):
        nb_voisins_vivants = sum([voisin.current_state for voisin in voisins])
        if self.current_state:
            if nb_voisins_vivants < 2 or nb_voisins_vivants > 3:
                self.next_state = False
        else:
            if nb_voisins_vivants == 3:
                self.next_state = True
        
    def draw(self, fenetre: pg.Surface):
        if self.current_state:
            fenetre.fill((255, 255, 255), (self.x * self.taille, self.y * self.taille, self.taille, self.taille))
            fenetre.blit(self.image, (self.x * self.taille, self.y * self.taille))
            pg.draw.rect(fenetre, (200, 200, 200), (self.x * self.taille, self.y * self.taille, self.taille, self.taille), 1)
        else:
            pg.draw.rect(fenetre, (255, 255, 255), (self.x * self.taille, self.y * self.taille, self.taille, self.taille))
            pg.draw.rect(fenetre, (200, 200, 200), (self.x * self.taille, self.y * self.taille, self.taille, self.taille), 1)
            
    def pass_epoch(self):
        self.current_state = self.next_state
        
        
  
class Grille:
    
    def __init__(self, nb_colonnes = 30, nb_lignes = 60):
        
        screen_info = pg.display.Info()
        self.SCREEN_WIDTH = screen_info.current_w
        self.SCREEN_HEIGHT = screen_info.current_h
        
        self.nb_colonnes = nb_colonnes
        self.nb_lignes = nb_lignes
        self.taille_cellule = min(self.SCREEN_WIDTH // nb_colonnes, self.SCREEN_HEIGHT // nb_lignes)
        self.grille = [[Cellule(x, y, self.taille_cellule) for x in range(nb_colonnes)] for y in range(nb_lignes)]

    def cellule(self, x, y) -> Cellule:
        return self.grille[y][x]
    
    def get_cellules(self):
        return [cell for cells in self.grille for cell in cells]

    def recuperer_voisins(self, x, y):
        return [self.cellule(x + dx, y + dy) 
                for dx in [-1, 0, 1] 
                for dy in [-1, 0, 1] 
                if (dx != 0 or dy != 0) and 0 <= x + dx < self.nb_colonnes and 0 <= y + dy < self.nb_lignes]

    def draw(self, fenetre):
        pass   
        
        

class Simulation():
        
    def __init__(self, fenetre: pg.Surface = None):
        self.fenetre = fenetre
        screen_info = pg.display.Info()
        self.SCREEN_WIDTH = screen_info.current_w
        self.SCREEN_HEIGHT =  screen_info.current_h
        
        self.map = Grille(60, 30)
        self.players = self.map.get_cellules()
        
    def random_setup(self):
        for cell in self.players:
            cell.current_state = random.choice([True, False])
        
    def choice_setup(self):
        running = True
        mouse_held = False  # Track if the mouse button is held down
        
        for cell in self.players:
                cell.draw(self.fenetre)

        while running:
            
            # intercept events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    running = False
               
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse_held = True
                    x, y = event.pos
                    cell_x = x // self.map.taille_cellule
                    cell_y = y // self.map.taille_cellule
                    cell = self.map.cellule(cell_x, cell_y)
                    cell.current_state = not cell.current_state
                    cell.draw(self.fenetre)
                elif event.type == pg.MOUSEBUTTONUP:
                    mouse_held = False
                

            # Set cell to alive when dragging
            if mouse_held:
                x, y = pg.mouse.get_pos()
                cell_x = x // self.map.taille_cellule
                cell_y = y // self.map.taille_cellule
                cell = self.map.cellule(cell_x, cell_y)
                cell.current_state = True  
                cell.draw(self.fenetre)

            pg.display.update()


    def apply_rules(self):
        for cell in self.players:
            voisins = self.map.recuperer_voisins(cell.x, cell.y)
            cell.regles_de_comportement(voisins)
    
    
    def pass_epoch(self):
        for cell in self.players:
            cell.pass_epoch()
            
    def draw(self,fenetre):
        # draw map
        self.map.draw(fenetre)
        # draw players
        for cell in self.players:
            cell.draw(fenetre)
                
            

            
            
            
        