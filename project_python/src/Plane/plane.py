from Animal.predator import Predator
from Animal.prey import Prey

class Plane():
    def __init__(self, height: int, width: int, predators: list[Predator]=[], prey: list[Prey]=[]):
        self.height = height
        self.width = width
        self.predators = predators
        self.prey = prey
        self.animals = predators + prey

    
    def run_iteration(self):
        for animal in self.animals:
            direction = animal.generate_move()
            animal.move(direction)


if __name__ == "__main__":
    p = Plane(100, 100)
    