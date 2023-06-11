from __future__ import annotations
import pygame
import random
import operator
from math import sqrt
from SimulationObject.Animal.animal import Animal
from SimulationObject.Animal.animal import Direction
from SimulationObject.Grass.grass import Grass

class Predator(Animal):
    def __init__(self, pos: tuple[int, int], energy: int, config, behavior: dict, image: pygame.image=None):
        super().__init__(pos, energy, config, behavior)

        self.sprite_width = config['image_width']
        self.sprite_height = int(self.sprite_width * config['image_ratio']) if image else config['image_width']
        self.rect = pygame.Rect(pos[0], pos[1], self.sprite_width, self.sprite_height)
        self.is_resting = False

        if image:
            # --- IMAGE ---
            self.image = image
            self.image = pygame.transform.scale(self.image, (self.sprite_width, self.sprite_height))
        else:
            # --- RECTANGLE ---
            self.image = pygame.Surface((self.sprite_width, self.sprite_height))
            self.image.fill(config['color'])

    
    def move(self, new_pos: tuple[int, int]):
        super().move(new_pos)
        self.energy = self.energy - self.config["resting_energy_drop"] if self.is_resting else self.energy - self.config["energy_drop"]
        self.is_resting = False


    def generate_move(self, neighbors: dict):
        behavior = self.generate_behavior()
        if behavior == 'rest':
            self.is_resting = True
            return Direction.IDLE.value
        
        if not neighbors:
            return self.random_move()
        
        hunt = (behavior == 'hunt' and neighbors['prey'][0] is not None)
        reproduce = (behavior == 'reproduce' and neighbors['partner'][0] is not None and self.can_reproduce())
        
        if hunt:
            target = neighbors['prey'][0]
        elif reproduce:
            target = neighbors['partner'][0]
        else:
            return self.random_move()
        
        vector = (target.pos[0] - self.pos[0], target.pos[1] - self.pos[1])
        vector = (vector[0]/abs(vector[0]) if vector[0] else 0, vector[1]/abs(vector[1]) if vector[1] else 0)

        moves = Direction.get_base_directions(vector)
        return random.choice(moves)


    def reproduce(self, other: Animal) -> Predator:
        new_behavior = super().reproduce(other)
        if new_behavior:
            return Predator(self.pos, int(self.config['reproduce_energy']) - 10, self.config, new_behavior, self.image)
        return None
    

    def generate_neighbors_dict(self):
        return {'partner': (None, float('+inf')), 'prey': (None, float('+inf'))}
    

    def add_neighbor(self, neighbors_dict, neighbor):
        if isinstance(neighbor, Grass):
            return neighbors_dict
        
        distance = sqrt((self.pos[0] - neighbor.pos[0])**2 + (self.pos[1] - neighbor.pos[1])**2)
        
        if isinstance(neighbor, Predator) and distance < neighbors_dict['partner'][1]:
            neighbors_dict['partner'] = (neighbor, distance)
        elif not isinstance(neighbor, Predator) and distance < neighbors_dict['prey'][1]:
            neighbors_dict['prey'] = (neighbor, distance)
        return neighbors_dict