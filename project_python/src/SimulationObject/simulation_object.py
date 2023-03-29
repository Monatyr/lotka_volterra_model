from pygame.sprite import Sprite


class SimulationObject(Sprite):
    def __init__(self, pos: tuple[int, int]):
        Sprite.__init__(self)
        self.pos = pos
