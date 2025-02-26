import pygame as pg
import random
import sys
import math
from style.text_input import TextInput
from style.button import Button

# Initialize pg
pg.init()

# Constants
SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 1000
GRID_SIZE = 10
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 12
NUM_PLAYERS = 10
MOVEMENT_SPEED = 5
FPS = 60
RANDOM_TURN_CHANCE = 0.03  # 5% chance to randomly change direction each update

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
COLORS = [RED, GREEN, BLUE, (255, 165, 0), (128, 0, 128)]  # Red, Green, Blue, Orange, Purple

class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.color = color
        
        # Directions: N, NE, E, SE, S, SW, W, NW
        self.directions = [
            (0, -1),    # North
            (1, -1),    # North-East
            (1, 0),     # East
            (1, 1),     # South-East
            (0, 1),     # South
            (-1, 1),    # South-West
            (-1, 0),    # West
            (-1, -1)    # North-West
        ]
        
        self.direction = random.choice(self.directions)
        self.speed = MOVEMENT_SPEED
        self.original_image = pg.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pg.SRCALPHA)
        pg.draw.rect(self.original_image, self.color, (0, 0, PLAYER_WIDTH, PLAYER_HEIGHT))
        pg.draw.polygon(self.original_image, BLACK, [(PLAYER_WIDTH//2, 0), 
                                                       (PLAYER_WIDTH//2 - 5, 10), 
                                                       (PLAYER_WIDTH//2 + 5, 10)]) # Direction pointer
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x + PLAYER_WIDTH//2, y + PLAYER_HEIGHT//2))
        
    def get_rect(self):
        return pg.Rect(self.x, self.y, self.width, self.height)
    
    def get_direction_points(self):
        """Return points in front of the player based on current direction"""
        points = []
        
        # Calculate the angle in degrees
        angle = self.get_angle_from_direction()
        
        # Calculate the front edge of the rotated rectangle
        # For simplicity, check points along the front edge based on direction
        cx, cy = self.rect.center
        
        if self.direction[0] == 0 and self.direction[1] == -1:  # North
            for i in range(-self.width//2, self.width//2 + 1, GRID_SIZE):
                points.append((cx + i, cy - self.height//2 - GRID_SIZE))
        elif self.direction[0] == 1 and self.direction[1] == -1:  # North-East
            for i in range(GRID_SIZE):
                points.append((cx + self.width//2 + i, cy - self.height//2 - i))
        elif self.direction[0] == 1 and self.direction[1] == 0:  # East
            for i in range(-self.height//2, self.height//2 + 1, GRID_SIZE):
                points.append((cx + self.width//2 + GRID_SIZE, cy + i))
        elif self.direction[0] == 1 and self.direction[1] == 1:  # South-East
            for i in range(GRID_SIZE):
                points.append((cx + self.width//2 + i, cy + self.height//2 + i))
        elif self.direction[0] == 0 and self.direction[1] == 1:  # South
            for i in range(-self.width//2, self.width//2 + 1, GRID_SIZE):
                points.append((cx + i, cy + self.height//2 + GRID_SIZE))
        elif self.direction[0] == -1 and self.direction[1] == 1:  # South-West
            for i in range(GRID_SIZE):
                points.append((cx - self.width//2 - i, cy + self.height//2 + i))
        elif self.direction[0] == -1 and self.direction[1] == 0:  # West
            for i in range(-self.height//2, self.height//2 + 1, GRID_SIZE):
                points.append((cx - self.width//2 - GRID_SIZE, cy + i))
        elif self.direction[0] == -1 and self.direction[1] == -1:  # North-West
            for i in range(GRID_SIZE):
                points.append((cx - self.width//2 - i, cy - self.height//2 - i))
                
        return points
    
    def get_angle_from_direction(self):
        """Convert direction to angle in degrees"""
        dx, dy = self.direction
        if dx == 0 and dy == -1:  # North
            return 0
        elif dx == 1 and dy == -1:  # North-East
            return 45
        elif dx == 1 and dy == 0:  # East
            return 90
        elif dx == 1 and dy == 1:  # South-East
            return 135
        elif dx == 0 and dy == 1:  # South
            return 180
        elif dx == -1 and dy == 1:  # South-West
            return 225
        elif dx == -1 and dy == 0:  # West
            return 270
        elif dx == -1 and dy == -1:  # North-West
            return 315
        return 0
    
    def turn_random(self):
        """Change to a random direction"""
        # Choose a random direction different from the current one
        new_direction = random.choice(self.directions)
        while new_direction == self.direction:
            new_direction = random.choice(self.directions)
        
        self.direction = new_direction
        self.update_rotation()
    
    def turn_clockwise(self):
        """Change direction (rotate 45 degrees clockwise)"""
        current_index = self.directions.index(self.direction)
        next_index = (current_index + 1) % len(self.directions)
        self.direction = self.directions[next_index]
        self.update_rotation()
    
    def update_rotation(self):
        """Update the rotated image based on direction"""
        angle = self.get_angle_from_direction()
        self.image = pg.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def move(self):
        """Move in the current direction"""
        # For diagonal movement, adjust speed to maintain consistent velocity
        diagonal = self.direction[0] != 0 and self.direction[1] != 0
        speed_factor = 0.7071 if diagonal else 1.0  # sqrt(2)/2 for diagonal movement
        
        dx = self.direction[0] * self.speed * speed_factor
        dy = self.direction[1] * self.speed * speed_factor
        
        self.x += dx
        self.y += dy
        self.rect.center = (self.x + self.width // 2, self.y + self.height // 2)
        
        # Handle screen boundaries
        boundary_hit = False
        
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.left
            boundary_hit = True
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.x = self.rect.left
            boundary_hit = True
            
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = self.rect.top
            boundary_hit = True
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.y = self.rect.top
            boundary_hit = True
            
        if boundary_hit:
            if random.random() < 0.5:
                if random.random() < 0.4:
                    self.turn_random()  # Choose a random new direction after hitting a boundary
            else:
                # Go backwards
                opposite_direction = (-self.direction[0], -self.direction[1])
                if opposite_direction in self.directions:
                    self.direction = opposite_direction
                    self.update_rotation()
    
    def draw(self, screen):
        """Draw the rotated rectangle"""
        screen.blit(self.image, self.rect.topleft)
        
        # Draw direction name (for debugging)
        dir_names = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        dir_index = self.directions.index(self.direction)
        font = pg.font.SysFont(None, 18)
        text = font.render(dir_names[dir_index], True, BLACK)
        screen.blit(text, (self.rect.centerx - 5, self.rect.centery - 5))

class Simulation:
    def __init__(self, player_number=None):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Player Grid Simulation with Random Turns")
        self.clock = pg.time.Clock()
        self.players = []
        self.running = True
        self.font = pg.font.SysFont(None, 24)
        self.player_number = player_number

    def random_setup(self):
        """Create a random setup of players"""
        self.player_number = random.randint(5, 15)
        self.create_players()

    def choice_setup(self):
        if self.player_number is None:
            self.player_number = 10
        self.create_players()

    def create_players(self, count = None):
        if count is None:
            count = self.player_number
        for i in range(count):
            x = random.randint(50, SCREEN_WIDTH - PLAYER_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - PLAYER_HEIGHT - 50)
            color = COLORS[i % len(COLORS)]
            new_player = Player(x, y, color)
            new_player.update_rotation()
            retries = 0
            while self.check_collision(new_player) and retries < 10:
                x = random.randint(50, SCREEN_WIDTH - PLAYER_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - PLAYER_HEIGHT - 50)
                new_player = Player(x, y, color)
                new_player.update_rotation()
                retries += 1
            if retries < 10:
                self.players.append(new_player)

    def check_collision(self, player):
        for other in self.players:
            if player != other and player.rect.colliderect(other.rect):
                return True
        return False

    def check_collision_with_others(self, player):
        for other in self.players:
            if player != other and player.rect.colliderect(other.rect):
                return True, other
        return False, None

    def check_point_collision(self, points):
        for point in points:
            px, py = int(point[0]), int(point[1])
            for player in self.players:
                if player.rect.collidepoint(px, py):
                    return True
        return False

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pg.draw.line(self.screen, (200, 200, 200), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pg.draw.line(self.screen, (200, 200, 200), (0, y), (SCREEN_WIDTH, y))

    def update(self):
        for i, player in enumerate(self.players):
            old_x, old_y = player.x, player.y
            old_rect = player.rect.copy()
            if random.random() < RANDOM_TURN_CHANCE:
                player.turn_random()
            player.move()
            has_collision, other_player = self.check_collision_with_others(player)
            if has_collision:
                player.x, player.y = old_x, old_y
                player.rect = old_rect
                player.turn_random()

    def render(self):
        self.screen.fill(WHITE)
        self.draw_grid()
        for player in self.players:
            player.draw(self.screen)
        instructions = [
            "Controls: A = Add Player, R = Reset, T = Force Turns, ESC = Quit",
            f"Random Turn Chance: {RANDOM_TURN_CHANCE * 100}%"
        ]
        for i, text in enumerate(instructions):
            rendered_text = self.font.render(text, True, BLACK)
            self.screen.blit(rendered_text, (10, 10 + 25 * i))
        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                elif event.key == pg.K_a:
                    self.create_players(1)
                elif event.key == pg.K_r:
                    self.players = []
                    self.create_players(self.player_number)
                elif event.key == pg.K_t:
                    for player in self.players:
                        player.turn_random()

    def run(self):
        if self.player_number is None:
            self.random_setup()
        else:
            self.choice_setup()
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        pg.quit()
        sys.exit()

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Player Grid Simulation with Menu")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(None, 48)
        self.text_input = TextInput(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, pg.font.SysFont(None, 36), (0, 100, 0), (0, 0, 255))
        self.start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50, "Start", BLACK, (128, 128, 128))
        self.running = True
        self.simulation = None

    def draw_menu(self):
        self.screen.fill(WHITE)
        
        # Load and draw the background image
        background_image = pg.image.load('images/SafeBand.png')
        background_image = pg.transform.scale(background_image, (background_image.get_width() // 2, background_image.get_height() // 2))
        background_rect = background_image.get_rect(center=(SCREEN_WIDTH // 2, background_image.get_height() // 2))
        self.screen.blit(background_image, background_rect)
        
        title = self.font.render("Player Grid Simulation", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        for event in pg.event.get():
            self.text_input.handle_event(event)
        self.text_input.draw(self.screen)
        
        self.start_button.draw(self.screen)
        
        pg.display.flip()

    def handle_menu_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
            self.text_input.handle_event(event)
            if self.start_button.handle_event(event):
                try:
                    player_number = int(self.text_input.text)
                except ValueError:
                    player_number = None
                self.simulation = Simulation(player_number)
                self.simulation.run()

    def run(self):
        while self.running:
            self.handle_menu_events()
            self.draw_menu()
            self.clock.tick(FPS)
        pg.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()

# if __name__ == "__main__":
#     simulation = Simulation()
#     simulation.run()
