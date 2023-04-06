from __future__ import annotations
import random
from enum import Enum

from scipy import rand
from SimulationObject.simulation_object import SimulationObject
from abc import ABC, abstractmethod

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    IDLE = (0, 0)


class Animal(SimulationObject, ABC):
    def __init__(self, pos: tuple[int, int], energy: int, config, behavior: dict=None, show_image: bool=False):
        super().__init__(pos)
        self.alive = True
        self.sprite_height = 32
        self.sprite_width = 32

        self.config = config
        self.energy = energy
        self.behavior = behavior
        self.show_image = show_image


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
        self.energy -= 0.1


    def get_new_position(self):
        direction = self.generate_move()
        return tuple(map(sum, zip(self.pos, direction)))


    def eat(self, energy_consumed):
        self.energy += energy_consumed


    def get_width(self):
        return self.sprite_width
    

    def get_height(self):
        return self.sprite_height


    # @abstractmethod
    # def procreate(self, other: Animal):
    #     pass

    def procreate(self, other: Animal):
        if self.energy < self.config['procreate_energy'] or other.energy < other.config['procreate_energy']:
            return None
        
        self.energy -= self.config['procreate_energy']//2
        other.energy -= other.config['procreate_energy']//2

        b1, b2 = self.behavior, other.behavior
        keys = b1.keys()
        n = len(b1)
        b_new = {}

        #behavior average from parents
        for (k1, v1), (k2, v2) in zip(b1.items(), b2.items()):
            b_new[k1] = (v1 + v2) / 2

        #mutations
        for _ in range(int(100 * int(self.config['mutation_rate']))):
            mutation = random.randrange(0.01, 0.03)
            i1, i2 = random.sample(range(0, n), 2)
            if 0 < b_new[keys[i1]] + mutation < 1 and 0 < b_new[keys[i2]] - mutation < 1:
                b_new[keys[i1]] += mutation
                b_new[keys[i2]] -= mutation

        return b_new


