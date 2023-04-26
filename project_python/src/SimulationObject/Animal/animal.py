from __future__ import annotations
import random
import operator
from enum import Enum
from SimulationObject.simulation_object import SimulationObject
from numpy.random import choice 
from abc import ABC, abstractmethod

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    IDLE = (0, 0)


    @classmethod
    def get_random_weighted_direction(cls, last_direction):
        directions = Direction.get_directions_list(False)
        if last_direction == Direction.IDLE:
            return random.choice(directions)
        
        last_direction_index = directions.index(last_direction)
        res = choice(directions, None, p=[0.7 if i == last_direction_index else 0.1 for i in range(4)])
        # print(last_direction == res)
        return res


    @classmethod
    def get_base_directions(cls, direction):
        if direction in [e.value for e in Direction]:
            return [direction]
        
        result = []
        if direction[0] == 1:
            result.append(Direction.RIGHT.value)
        if direction[0] == -1:
            result.append(Direction.LEFT.value)
        if direction[1] == 1:
            result.append(Direction.DOWN.value)
        if direction[1] == -1:
            result.append(Direction.UP.value)

        if not result:
            return [Direction.IDLE.value]
        return result
    

    @classmethod
    def get_directions_list(cls, with_idle: bool=True):
        result = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        if with_idle:
            result.append(Direction.IDLE)
        return result



class Animal(SimulationObject, ABC):
    def __init__(self, pos: tuple[int, int], energy: int, config, behavior: dict=None, show_image: bool=False):
        super().__init__(pos)
        self.sprite_height = 32
        self.sprite_width = 32

        self.config = config
        self.energy = energy
        self.behavior = behavior
        self.show_image = show_image
        self.last_move = Direction.IDLE


    def generate_move_constrained(self, max_w, max_h):
        direction = self.generate_move()
        new_pos = tuple(map(sum, zip(self.pos, direction)))
        
        while new_pos[0] < 0 or new_pos[0] >= max_w - self.sprite_width or new_pos[1] < 0 or new_pos[1] >= max_h - self.sprite_height:
            direction = self.generate_move()
            new_pos = tuple(map(sum, zip(self.pos, direction)))
        
        return direction
    

    def random_move(self):
        res = Direction.get_random_weighted_direction(self.last_move)
        # print("RES", res, type(res))
        return res.value
        # return random.choice(list(Direction)).value


    @abstractmethod
    def generate_move(self, neighbors: dict):
        return


    def move(self, new_pos: tuple[int, int]):
        diff = tuple(map(operator.sub, new_pos, self.pos))
        # print("DIRECTION(DIFF): ", Direction(diff))
        self.last_move = Direction(diff)
        self.pos = new_pos
        self.energy -= 0.1


    def get_new_position(self, neighbors):
        direction = self.generate_move(neighbors)
        return tuple(map(sum, zip(self.pos, direction)))


    def eat(self, food: SimulationObject):
        self.energy += food.nutrition_value


    def get_width(self):
        return self.sprite_width
    

    def get_height(self):
        return self.sprite_height
    

    def generate_behavior(self):
        index = random.random()
        for key, value in self.behavior.items():
            if index < value:
                return key
            else:
                index -= value


    @abstractmethod
    def generate_neighbors_dict(self):
        return
    

    @abstractmethod
    def add_neighbor(self, neighbors_dict: dict, neighbor: SimulationObject):
        return


    def reproduce(self, other: Animal) -> dict:
        if self.energy < self.config['reproduce_energy'] or other.energy < other.config['reproduce_energy']:
            return None
        
        self.energy -= self.config['reproduce_energy']//2
        other.energy -= other.config['reproduce_energy']//2

        b1, b2 = self.behavior, other.behavior
        keys = list(b1.keys())
        n = len(b1)
        b_new = {}

        #behavior average from parents
        for (k1, v1), (k2, v2) in zip(b1.items(), b2.items()):
            b_new[k1] = (v1 + v2) / 2

        #mutations
        print(int(100 * self.config['mutation_rate']))
        for _ in range(int(100 * self.config['mutation_rate'])):
            mutation = random.uniform(0.01, 0.03)
            i1, i2 = random.sample(range(0, n), 2)
            if 0 < b_new[keys[i1]] + mutation < 1 and 0 < b_new[keys[i2]] - mutation < 1:
                b_new[keys[i1]] += mutation
                b_new[keys[i2]] -= mutation
                
        return b_new


