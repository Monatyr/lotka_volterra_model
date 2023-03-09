import pygame
import random
import matplotlib
from sqlalchemy import all_
matplotlib.use('module://pygame_matplotlib.backend_pygame')
import matplotlib.pyplot as plt
import json


from Plane.plane import Plane
from Animal.predator import Predator
from Animal.animal import Direction, Animal
from Animal.prey import Prey

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
    
    self.plane = Plane(height, width)
    self.btn_image = 'bomb.png'
    # self.button = pygame.image.load(f'assets/{self.btn_image}').convert_alpha()
    # self.button = pygame.transform.scale(self.button, (50, 75))

    self.window = pygame.display.set_mode((self.width, self.height))
    # self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
    self.screen = pygame.Surface((self.screen_width, self.screen_height))
    # self.background = pygame.Surface((0, 0))
    self.clock = pygame.time.Clock()
    self.running = False
    self.paused = False


  def run(self):
    pygame.init()
    self.running = True

    with open('simulation_config.json') as file:
      config = json.load(file)

    show_images = config['simulation']['show_images']

    self.button = pygame.image.load(f'assets/{self.btn_image}').convert_alpha()
    self.button = pygame.transform.scale(self.button, (50, 75))

    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])  # Plot some data on the axes.
    # plt.show()

    # predator = Predator((10, 4), 0)
    prey_config = config['animal']['prey']
    prey_width = prey_config['image_width'] if show_images else prey_config['width']
    prey_height = prey_config['image_height'] if show_images else prey_config['height']
    prey = Prey((100, 100), 0, prey_config, show_images)
    # all_sprites = pygame.sprite.Group([predator, prey])
    all_sprites = self.generate_population(self.predators_num, self.prey_num, config)

    while self.running:

      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            self.running = False
          if event.key == pygame.K_SPACE:
            self.paused = not self.paused

      if self.paused:
        continue

      # self.predator_control(predator)
      self.prey_control(prey)
      
      self.window.fill("black")
      self.window.blit(self.screen, (0, 0))
      self.screen.fill('#EEC8CD')

      self.screen.blit(self.button, (280, 280))
      
      self.screen.blit(prey.image, prey.pos)
      if abs(prey.pos[0]-280) <= 30 and abs(prey.pos[1]-280) <= 30 and self.btn_image != 'explosion.png':
        self.btn_image = 'explosion.png'
        count = True
        self.button = pygame.image.load(f'assets/{self.btn_image}').convert_alpha()
        self.button = pygame.transform.scale(self.button, (61, 61))
        all_sprites = pygame.sprite.Group(filter(lambda x: type(x) != Predator, all_sprites))

      for entity in all_sprites:
        self.move_animal(entity)
        self.screen.blit(entity.image, entity.pos)
        if pygame.sprite.groupcollide(all_sprites, all_sprites, False, False):
          # print('colision')
          pass
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

  
  def generate_population(self, predators, prey, config):
    show_images = config['simulation']['show_images']

    prey_config = config['animal']['prey']
    prey_width = prey_config['image_width'] if show_images else prey_config['width']
    prey_height = prey_config['image_height'] if show_images else prey_config['height']

    predator_config = config['animal']['predator']
    predator_width = predator_config['image_width'] if show_images else predator_config['width']
    predator_height = predator_config['image_height'] if show_images else predator_config['height']

    population = pygame.sprite.Group()
    for _ in range(prey):
      x, y = random.randint(0, self.screen_width-PREY_SIZE[0]),  random.randint(0, self.screen_height-PREY_SIZE[1])
      population.add(Prey((x, y), 10, prey_config, show_images))
    for _ in range(predators):
      x, y = random.randint(0, self.screen_width-PREDATOR_SIZE[0]),  random.randint(0, self.screen_height-PREDATOR_SIZE[1])
      population.add(Predator((x, y), 10, predator_config, show_images))
    return population
  

  def check_position_validity(self, pos: tuple[int, int], obj_w, obj_h, max_w, max_h):
    return pos[0] <= max_w - obj_w and pos[0] >= 0 and pos[1] <= max_h - obj_h and pos[1] >= 0
  