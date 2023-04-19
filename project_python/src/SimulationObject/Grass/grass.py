

from pygame import Surface
from SimulationObject.simulation_object import SimulationObject


class Grass(SimulationObject):
    def __init__(self, pos: tuple[int, int], grass_config, show_image: bool=False):
        super().__init__(pos)
        self.nutrition_value = int(grass_config['nutrition_value'])
        self.sprite_width = grass_config['image_width']
        self.sprite_height = int(self.sprite_width * grass_config['image_ratio']) if show_image else grass_config['image_width']

        self.image = Surface((self.sprite_width, self.sprite_height))
        self.image.fill(grass_config['color'])