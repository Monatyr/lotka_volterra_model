from __future__ import annotations
import pygame
import random
from enum import Enum

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    IDLE = (0, 0)


class Animal(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], hunger: int):
        pygame.sprite.Sprite.__init__(self)
        self.sprite_height = 32
        self.sprite_width = 32
        # self.rect = pygame.Rect(pos[0], pos[1], self.sprite_width, self.sprite_height)

        self.pos = pos
        self.hunger = hunger


    def generate_move_constrained(self, max_w, max_h):
        direction = self.generate_move()
        new_pos = tuple(map(sum, zip(self.pos, direction)))
        
        while new_pos[0] < 0 or new_pos[0] >= max_w - self.sprite_width or new_pos[1] < 0 or new_pos[1] >= max_h - self.sprite_height:
            direction = self.generate_move()
            new_pos = tuple(map(sum, zip(self.pos, direction)))
        
        return direction


    def generate_move(self):
        return random.choice(list(Direction)).value


    def move(self, new_pos: tuple[int, int]):
        self.pos = new_pos
        # self.rect = pygame.Rect(*self.pos, self.sprite_width, self.sprite_height)
        self.hunger -= 1


    def get_new_position(self):
        direction = self.generate_move()
        return tuple(map(sum, zip(self.pos, direction)))


    def eat(self, energy_consumed):
        self.hunger += energy_consumed


    def get_width(self):
        return self.sprite_width
    

    def get_height(self):
        return self.sprite_height


    # def procreate(self, other: Animal):
    #     offspring_hunger = (self.hunger + other.hunger)//2
    #     if isinstance(other, Predator):
    #         print('is predator')
