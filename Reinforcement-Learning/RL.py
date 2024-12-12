

import gym
from gym import spaces
import numpy as np
import matplotlib.pyplot as plt

class MultiAgentEnv(gym.Env):
    def __init__(self, grid_size=10, num_agents=2, num_obstacles=10):
        super(MultiAgentEnv, self).__init__()
        
        # Paramètres de la grille
        self.grid_size = grid_size
        self.num_agents = num_agents
        self.num_obstacles = num_obstacles
        
        # Espaces d'observation et d'action
        # Observation: grille (grid_size x grid_size)
        self.observation_space = spaces.Box(low=0, high=3, shape=(grid_size, grid_size), dtype=np.int32)
        # Actions: haut, bas, gauche, droite, ou rester immobile pour chaque agent
        self.action_space = spaces.MultiDiscrete([5] * num_agents)
        
        # Initialisation de la grille
        self.reset()

    def reset(self):
        # Grille vide
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        
        # Ajouter des obstacles (valeur 1)
        for _ in range(self.num_obstacles):
            x, y = np.random.randint(0, self.grid_size, size=2)
            self.grid[x, y] = 1  # Mur
        
        # Position des agents (valeur 2)
        self.agent_positions = []
        for _ in range(self.num_agents):
            while True:
                x, y = np.random.randint(0, self.grid_size, size=2)
                if self.grid[x, y] == 0:
                    self.grid[x, y] = 2
                    self.agent_positions.append((x, y))
                    break
        
        # Position de la cible (valeur 3)
        while True:
            x, y = np.random.randint(0, self.grid_size, size=2)
            if self.grid[x, y] == 0:
                self.grid[x, y] = 3
                self.target_position = (x, y)
                break
        
        return self.grid

    def step(self, actions):
        rewards = 0
        done = False
        
        # Mise à jour des positions des agents
        for i, action in enumerate(actions):
            x, y = self.agent_positions[i]
            new_x, new_y = x, y
            
            # Déterminer la nouvelle position selon l'action
            if action == 0:  # Haut
                new_x = max(0, x - 1)
            elif action == 1:  # Bas
                new_x = min(self.grid_size - 1, x + 1)
            elif action == 2:  # Gauche
                new_y = max(0, y - 1)
            elif action == 3:  # Droite
                new_y = min(self.grid_size - 1, y + 1)
            # Action 4 correspond à rester immobile
            
            # Vérifier les collisions
            if self.grid[new_x, new_y] == 0:  # Case vide
                self.grid[x, y] = 0  # Libérer l'ancienne position
                self.grid[new_x, new_y] = 2  # Occuper la nouvelle position
                self.agent_positions[i] = (new_x, new_y)
            elif (new_x, new_y) == self.target_position:
                rewards += 1
                done = True
            else:
                rewards -= 1
        # Calculer une récompense agrégée
        
        return self.grid, rewards, done, {}

    import matplotlib.pyplot as plt

    def render(self):
        cmap = {0: 'white', 1: 'black', 2: 'red'}
        grid_image = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                color = cmap[self.grid[x, y]]
                grid_image[x, y] = plt.cm.get_cmap('cool')(color)[:3]

        plt.imshow(grid_image)
        plt.axis('off')
        plt.show()


from stable_baselines3 import PPO

# Créer l'environnement
env = MultiAgentEnv(grid_size=10, num_agents=2, num_obstacles=15)

# Entraîner un agent PPO
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)

# Tester l'agent
obs = env.reset()
for _ in range(20):
    actions, _ = model.predict(obs)
    obs, rewards, done, _ = env.step(actions)
    env.render()
    if done:
        break
