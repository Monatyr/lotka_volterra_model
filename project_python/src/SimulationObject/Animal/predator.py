import pygame
from SimulationObject.Animal.animal import Animal

class Predator(Animal):
    def __init__(self, pos: tuple[int, int], energy: int, config, behavior: dict=None, show_image: bool=False):
        super().__init__(pos, energy, config, behavior)

        self.sprite_width = config['image_width']
        self.sprite_height = int(self.sprite_width * config['image_ratio']) if show_image else config['image_width']
        self.rect = pygame.Rect(pos[0], pos[1], self.sprite_width, self.sprite_height)
        # self.behavior = {'hunt': 0.34, 'preserve': 0.33, 'rest': 0.33}

        if show_image:
            # --- IMAGE ---
            self.image = pygame.image.load('assets/wolf.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.sprite_width, self.sprite_height))
        else:
            # --- RECTANGLE ---
            self.image = pygame.Surface((self.sprite_width, self.sprite_height))
            self.image.fill(config['color'])


    def procreate(self, other: Animal):
        new_behavior = super().procreate(other)
        if new_behavior:
            return Predator(self.pos, int(self.config['procreate_energy']) - 10, self.config, new_behavior, self.show_image)
        return None
    