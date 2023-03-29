import pygame
import random
import matplotlib
matplotlib.use('module://pygame_matplotlib.backend_pygame')
import matplotlib.pyplot as plt
import json
from scipy.spatial import KDTree

from Plane.plane import Plane
from SimulationObject.Animal.animal import Direction, Animal
from SimulationObject.Animal.predator import Predator
from SimulationObject.Animal.prey import Prey


PREDATOR_SIZE = (78, 48)
PREY_SIZE = (54, 43)

class Engine():
  def __init__(self, width, height, screen_width, screen_height, predators_num, prey_num):
    self.width = width
    self.height = height
    self.screen_width = screen_width
    self.screen_height = screen_height
    self.predators_num = predators_num
    self.prey_num = prey_num
    self.all_sprites = []

    with open('simulation_config.json') as file:
      self.config = json.load(file)
      # self.bg = pygame.image.load("assets/grass_bg.webp")


    self.show_images = self.config['simulation']['show_images']
    
    self.plane = Plane(height, width)

    self.window = pygame.display.set_mode((self.width, self.height))
    self.screen = pygame.Surface((self.screen_width, self.screen_height))
    self.clock = pygame.time.Clock()
    self.running = False
    self.paused = False


  def run(self):
    pygame.init()
    self.running = True

    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])  # Plot some data on the axes.
    # plt.show()

    # prey_config = self.config['animal']['prey']
    # my_prey = Prey((100, 100), 0, prey_config, self.show_images)

    self.all_sprites = self.generate_population()

    while self.running:
      if not self.all_sprites:
        self.paused = True

      self.handle_keys()      
      if self.paused:
        continue

      self.draw_background()

      # self.prey_control(my_prey)
      # self.screen.blit(my_prey.image, my_prey.pos)
      
      self.run_animal_turn()

      if not self.all_sprites:
        self.paused = True
        continue

      sprites = list(self.all_sprites)
      self.kd_tree = KDTree([a.pos for a in sprites])
      
      pairs = self.kd_tree.query_pairs(r=10)
      pairs = list(pairs)

      self.animal_interactions(pairs, sprites)

      pygame.display.update()
      self.clock.tick(240)


  def move_animal(self, animal: Animal):
    new_pos = animal.get_new_position()
    while not self.check_position_validity(new_pos, animal.get_width(), animal.get_height(), self.screen_width, self.screen_width):
      new_pos = animal.get_new_position()
    animal.move(new_pos)


  def predator_control(self, predator: Predator):
    dir = Direction.IDLE.value
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
      dir = tuple(map(sum, zip(dir, Direction["LEFT"].value)))
    if keys[pygame.K_RIGHT]:
      dir = tuple(map(sum, zip(dir, Direction["RIGHT"].value)))
    if keys[pygame.K_UP]:
      dir = tuple(map(sum, zip(dir, Direction["UP"].value)))
    if keys[pygame.K_DOWN]:
      dir = tuple(map(sum, zip(dir, Direction["DOWN"].value)))
    
    new_pos = tuple(map(sum, zip(dir, predator.pos)))
    if self.check_position_validity(new_pos, predator.get_width(), predator.get_height(), self.screen_width, self.screen_height):
      predator.move(new_pos)


  def prey_control(self, prey: Prey):
    dir = Direction.IDLE.value
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
      dir = tuple(map(sum, zip(dir, Direction["LEFT"].value)))
    if keys[pygame.K_d]:
      dir = tuple(map(sum, zip(dir, Direction["RIGHT"].value)))
    if keys[pygame.K_w]:
      dir = tuple(map(sum, zip(dir, Direction["UP"].value)))
    if keys[pygame.K_s]:
      dir = tuple(map(sum, zip(dir, Direction["DOWN"].value)))

    new_pos = tuple(map(sum, zip(dir, prey.pos)))
    if self.check_position_validity(new_pos, prey.get_width(), prey.get_height(), self.screen_width, self.screen_height):
      prey.move(new_pos)

  
  def generate_population(self):
    prey_config = self.config['animal']['prey']
    predator_config = self.config['animal']['predator']
    population = pygame.sprite.Group()

    for _ in range(self.prey_num):
      x, y = random.randint(0, self.screen_width-PREY_SIZE[0]),  random.randint(0, self.screen_height-PREY_SIZE[1])
      population.add(Prey((x, y), self.config["simulation"]["initial_energy"], prey_config, self.show_images))
    for _ in range(self.predators_num):
      x, y = random.randint(0, self.screen_width-PREDATOR_SIZE[0]),  random.randint(0, self.screen_height-PREDATOR_SIZE[1])
      population.add(Predator((x, y), self.config["simulation"]["initial_energy"], predator_config, self.show_images))

    return population
  

  def check_position_validity(self, pos: tuple[int, int], obj_w, obj_h, max_w, max_h):
    return pos[0] <= max_w - obj_w and pos[0] >= 0 and pos[1] <= max_h - obj_h and pos[1] >= 0
  

  def handle_keys(self):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            self.running = False
          if event.key == pygame.K_SPACE:
            self.paused = not self.paused

  
  def run_animal_turn(self):
    '''Make animal move. Cleanup deceased animals'''
    new_sprites = pygame.sprite.Group()
    
    for animal in self.all_sprites:
        if animal.energy < 0:
          continue

        new_sprites.add(animal)

        self.move_animal(animal)
        self.screen.blit(animal.image, animal.pos)
    
    self.all_sprites = new_sprites
  

  def animal_interactions(self, pairs, sprites):
    '''Reproduction and hunting'''
    prey_config = self.config['animal']['prey']
    predator_config = self.config['animal']['predator']

    for pair in pairs:
      a1, a2 = sprites[pair[0]], sprites[pair[1]]
      min_energy = self.config["simulation"]["procreate_energy"]

      if type(a1) is type(a2) and a1.energy > min_energy and a2.energy > min_energy:
        if isinstance(a1, Prey):
          self.all_sprites.add(Prey(a1.pos, min_energy - 10, prey_config, self.show_images))
        else:
          self.all_sprites.add(Predator(a1.pos, min_energy - 10, predator_config, self.show_images))
        a1.energy -= min_energy//3
        a2.energy -= min_energy//3

      elif type(a1) is not type(a2):
        predator = a1 if isinstance(a1, Predator) else a2
        prey = a1 if isinstance(a1, Prey) else a2

        if predator.energy < 100:
          predator.eat(self.config["simulation"]["energy_gain"])
          self.all_sprites.remove(prey)


  def draw_background(self):
    self.window.fill("black")
    self.window.blit(self.screen, (0, 0))
    self.screen.fill('#57B669')

  

  