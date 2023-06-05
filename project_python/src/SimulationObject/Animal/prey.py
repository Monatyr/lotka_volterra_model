from __future__ import annotations
from math import sqrt
import pygame
import random
from SimulationObject.Animal.animal import Animal
from SimulationObject.Grass.grass import Grass
from SimulationObject.Animal.animal import Direction


class Prey(Animal):
    def __init__(self, pos: tuple[int, int], energy: int, config, behavior: dict, image: pygame.image=None):
        super().__init__(pos, energy, config, behavior)

        self.nutrition_value = config['nutrition_value']
        self.sprite_width = config['image_width']
        self.sprite_height = int(self.sprite_width * config['image_ratio']) if image else config['image_width']
        self.rect = pygame.Rect(pos[0], pos[1], self.sprite_width, self.sprite_height)

        if image:
            # --- IMAGE ---
            self.image = image
            self.image = pygame.transform.scale(self.image, (self.sprite_width, self.sprite_height))
        else:
            # --- RECTANGLE ---
            self.image = pygame.Surface((self.sprite_width, self.sprite_height))
            self.image.fill(config['color'])


    def generate_move(self, neighbors: dict):
        behavior = self.generate_behavior()

        if not neighbors:
            return self.random_move()

        eat = (behavior == 'eat' and neighbors['food'][0] is not None)
        run = (behavior == 'run' and neighbors['predator'][0] is not None)
        reproduce = (behavior == 'reproduce' and neighbors['partner'][0] is not None and self.can_reproduce())

        if eat:
            target = neighbors['food'][0]
        elif run:
            target = neighbors['predator'][0]
        elif reproduce:
            target = neighbors['partner'][0]
        else:
            return self.random_move()
            
        vector = (target.pos[0] - self.pos[0], target.pos[1] - self.pos[1])
        vector = (vector[0]/abs(vector[0]) if vector[0] else 0, vector[1]/abs(vector[1]) if vector[1] else 0)

        if behavior == 'run':
            vector = (vector[0] * (-1), vector[1] * (-1))

        moves = Direction.get_base_directions(vector)
        return random.choice(moves)
    

    def move(self, new_pos: tuple[int, int]):
        super().move(new_pos)
        self.energy -= 0.1


    def reproduce(self, other: Animal) -> Prey:
        new_behavior = super().reproduce(other)
        if new_behavior:
            return Prey(self.pos, int(self.config['reproduce_energy']) - 10, self.config, new_behavior, self.image)
        return None  


    def generate_neighbors_dict(self):
        return {'predator': (None, float('+inf')), 'partner': (None, float('+inf')), 'food': (None, float('+inf'))}
    

    def add_neighbor(self, neighbors_dict, neighbor):
        distance = sqrt((self.pos[0] - neighbor.pos[0])**2 + (self.pos[1] - neighbor.pos[1])**2)
        if isinstance(neighbor, Prey) and distance < neighbors_dict['partner'][1]:
            neighbors_dict['partner'] = (neighbor, distance)
        elif isinstance(neighbor, Grass) and distance < neighbors_dict['food'][1]:
            neighbors_dict['food'] = (neighbor, distance)
        elif distance < neighbors_dict['predator'][1]:
            neighbors_dict['predator'] = (neighbor, distance)
        return neighbors_dict
