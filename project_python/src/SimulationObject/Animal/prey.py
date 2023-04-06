# from __future__ import annotations
import pygame
from SimulationObject.Animal.animal import Animal

class Prey(Animal):
    def __init__(self, pos: tuple[int, int], energy: int, config, behavior=None, show_image: bool=False):
        super().__init__(pos, energy, config, behavior)

        self.sprite_width = config['image_width']
        self.sprite_height = int(self.sprite_width * config['image_ratio']) if show_image else config['image_width']
        self.rect = pygame.Rect(pos[0], pos[1], self.sprite_width, self.sprite_height)
        # self.behavior = {'eat': 0.5, 'run': 0.5}
        # self.behavior = behavior

        if show_image:
            # --- IMAGE ---
            self.image = pygame.image.load('assets/sheep.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.sprite_width, self.sprite_height))
        else:
            # --- RECTANGLE ---
            self.image = pygame.Surface((self.sprite_width, self.sprite_height))
            self.image.fill(config['color'])


    def procreate(self, other: Animal):
        new_behavior = super().procreate(other)
        if new_behavior:
            return Prey(self.pos, int(self.config['procreate_energy']) - 10, self.config, new_behavior, self.show_image)
        return None
        
