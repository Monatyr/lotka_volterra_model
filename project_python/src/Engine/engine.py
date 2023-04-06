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
from SimulationObject.Grass.grass import Grass


PREDATOR_SIZE = (78, 48)
PREY_SIZE = (54, 43)

class Engine():
  def __init__(self, width, height, screen_width, screen_height, predators_num, prey_num, grass_num):
    self.width = width
    self.height = height
    self.screen_width = screen_width
    self.screen_height = screen_height
    self.predators_num = predators_num
    self.prey_num = prey_num
    self.objects_count = {'predator': predators_num, 'prey': prey_num, 'grass': grass_num}
    self.all_objects = pygame.sprite.Group()


    with open('simulation_config.json') as file:
      self.config = json.load(file)

    self.show_images = self.config['simulation']['show_images']
    
    self.plane = Plane(height, width)

    self.window = pygame.display.set_mode((self.width, self.height))
    self.screen = pygame.Surface((self.screen_width, self.screen_height))
    self.clock = pygame.time.Clock()
    self.running = False
    self.paused = False
    self.counter = 0


  def run(self):
    pygame.init()
    self.running = True

    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])  # Plot some data on the axes.
    # plt.show()

    self.generate_population()
    self.generate_grass(self.objects_count['grass'])

    while self.running:
      if not self.all_objects:
        self.paused = True

      self.handle_keys()      
      if self.paused:
        continue

      self.counter += float(self.config["simulation"]["grass_per_round"])
      self.draw_background()

      if int(self.counter) == 1:
        self.generate_grass(1)
        self.counter = 0
      self.run_animal_turn()

      #if all animals are gone
      if not (self.objects_count['predator'] > 0 or self.objects_count['prey'] > 0) :
        self.paused = True
        continue

      print(self.objects_count['predator'] + self.objects_count['prey'])

      sprites = list(self.all_objects)
      self.kd_tree = KDTree([a.pos for a in sprites])
      
      pairs = self.kd_tree.query_pairs(r=10)
      pairs = list(pairs)

      self.object_interactions(pairs, sprites)

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

    for _ in range(self.prey_num):
      x, y = random.randint(0, self.screen_width-PREY_SIZE[0]),  random.randint(0, self.screen_height-PREY_SIZE[1])
      self.all_objects.add(Prey((x, y), prey_config["initial_energy"], prey_config, {'eat': 0.5, 'run': 0.5}, self.show_images))
    for _ in range(self.predators_num):
      x, y = random.randint(0, self.screen_width-PREDATOR_SIZE[0]),  random.randint(0, self.screen_height-PREDATOR_SIZE[1])
      self.all_objects.add(Predator((x, y), predator_config["initial_energy"], predator_config, {'hunt': 0.34, 'preserve': 0.33, 'rest': 0.33}, self.show_images))
  

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
    old_sprites = []
    
    for object in self.all_objects:
      if isinstance(object, Grass):
        self.screen.blit(object.image, object.pos)
        continue
      animal = object
      if animal.energy < 0:
        key = 'prey' if isinstance(animal, Prey) else 'predator'
        old_sprites.append((animal, key))
        continue
      self.move_animal(animal)
      self.screen.blit(animal.image, animal.pos)

    for old_sprite, key in old_sprites:
      old_sprite.alive = False
      self.all_objects.remove(old_sprite)
      self.objects_count[key] -= 1
  

  def object_interactions(self, pairs, sprites):
    '''Reproduction and hunting'''
    prey_config = self.config['animal']['prey']
    predator_config = self.config['animal']['predator']

    for pair in pairs:
      a1, a2 = sprites[pair[0]], sprites[pair[1]]

      if type(a1) is type(a2):
        if isinstance(a1, Grass):
          continue
        
        new_animal = a1.procreate(a2)
        if not new_animal:
          continue

        self.all_objects.add(new_animal)
        
        if isinstance(a1, Prey):
            self.objects_count['prey'] += 1
          # self.all_objects.add(Prey(a1.pos, min_energy - 10, prey_config, {'eat': 0.5, 'run': 0.5}, self.show_images))
        elif isinstance(a1, Predator):
          self.objects_count['predator'] += 1
          # self.all_objects.add(Predator(a1.pos, min_energy - 10, predator_config, {'hunt': 0.34, 'preserve': 0.33, 'rest': 0.33}, self.show_images))
      elif type(a1) is not type(a2):
        if any(isinstance(e, Grass) for e in [a1, a2]) and any(isinstance(e, Prey) for e in [a1, a2]):
          grass = a1 if isinstance(a1, Grass) else a2
          prey = a1 if isinstance(a1, Prey) else a2
          prey.eat(grass.energy)
          self.all_objects.remove(grass)
          self.objects_count['grass'] -= 1
        elif not isinstance(a1, Grass) and not isinstance(a2, Grass):
          predator = a1 if isinstance(a1, Predator) else a2
          prey = a1 if isinstance(a1, Prey) else a2
          if prey.alive:
            predator.eat(self.config["simulation"]["energy_gain"])
            self.all_objects.remove(prey)
            self.objects_count['prey'] -= 1

  
  def generate_grass(self, grass_num):
    grass_config = self.config["grass"]
    for _ in range(grass_num):
      grass_x, grass_y = random.randint(0, self.screen_width-1), random.randint(0, self.screen_height-1)
      self.all_objects.add(Grass((grass_x, grass_y), self.config["simulation"]["energy_gain"], grass_config, self.show_images))


  def draw_background(self):
    self.window.fill("black")
    self.window.blit(self.screen, (0, 0))
    self.screen.fill('#57B669')

  

  