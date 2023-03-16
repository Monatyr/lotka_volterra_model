import pygame
from Animal.animal import Animal

class Prey(Animal):
    def __init__(self, pos: tuple[int, int], hunger: int, prey_config, show_image: bool=False):
        super().__init__(pos, hunger)

        self.sprite_width = prey_config['image_width']
        self.sprite_height = int(self.sprite_width * prey_config['image_ratio']) if show_image else prey_config['image_width']
        self.rect = pygame.Rect(pos[0], pos[1], self.sprite_width, self.sprite_height)

        if show_image:
            # --- IMAGE ---
            self.image = pygame.image.load('assets/sheep.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.sprite_width, self.sprite_height))
        else:
            # --- RECTANGLE ---
            self.image = pygame.Surface((self.sprite_width, self.sprite_height))
            self.image.fill(prey_config['color'])
