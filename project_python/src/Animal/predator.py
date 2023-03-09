import pygame
from Animal.animal import Animal

class Predator(Animal):
    def __init__(self, pos: tuple[int, int], hunger: int, predator_config, show_image: bool=False):
        super().__init__(pos, hunger)

        self.sprite_width = int(predator_config['image_width']) if show_image else int(predator_config['width'])
        self.sprite_height = int(predator_config['image_height']) if show_image else int(predator_config['height'])
        self.rect = pygame.Rect(pos[0], pos[1], self.sprite_width, self.sprite_height)

        if show_image:
            # --- IMAGE ---
            self.image = pygame.image.load('assets/wolf.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.sprite_width, self.sprite_height))
        else:
            # --- RECTANGLE ---
            self.image = pygame.Surface((self.sprite_width, self.sprite_height))
            self.image.fill(predator_config['color'])

