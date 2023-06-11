

import pygame
from SimulationObject.simulation_object import SimulationObject


class Grass(SimulationObject):
    def __init__(self, pos: tuple[int, int], grass_config, image: pygame.image=None):
        super().__init__(pos)
        self.nutrition_value = int(grass_config['nutrition_value'])
        self.sprite_width = grass_config['image_width']
        self.sprite_height = int(self.sprite_width * grass_config['image_ratio']) if image else grass_config['image_width']

        if image:
            # --- IMAGE ---
            self.image = image
            self.image = pygame.transform.scale(self.image, (self.sprite_width, self.sprite_height))
        else:
            # --- RECTANGLE ---
            self.image = pygame.Surface((self.sprite_width, self.sprite_height))
            self.image.fill(grass_config['color'])
            