import pygame
import random
import matplotlib
matplotlib.use('module://pygame_matplotlib.backend_pygame')
import matplotlib.pyplot as plt
import json
from scipy.spatial import KDTree
import pygame.freetype

from SimulationObject.Animal.animal import Animal
from SimulationObject.Animal.predator import Predator
from SimulationObject.Animal.prey import Prey
from SimulationObject.Grass.grass import Grass


PREDATOR_SIZE = (78, 48)
PREY_SIZE = (54, 43)


class Engine():
  def __init__(self, width, height, screen_width, screen_height, predators_num, prey_num, grass_num):
    pygame.init()
    self.width = width
    self.height = height
    self.screen_width = screen_width
    self.screen_height = screen_height
    self.predators_num = predators_num
    self.prey_num = prey_num
    self.objects_count = {'predator': predators_num, 'prey': prey_num, 'grass': grass_num}
    self.all_objects = pygame.sprite.Group()
    self.result_file = open('result.txt', 'w')

    self.fig, self.axes = plt.subplots(1, 1,)

    with open('simulation_config.json') as file:
      self.config = json.load(file)

    self.show_images = self.config['simulation']['show_images']
    self.vision_range = self.config['simulation']['vision_range']

    
    self.window = pygame.display.set_mode((self.width, self.height))
    self.screen = pygame.Surface((self.screen_width, self.screen_height))
    self.graph = pygame.Surface((self.width - self.screen_width, self.screen_height*3//5))
    self.info = pygame.Surface((self.width - self.screen_width, self.screen_height*2//5))
    # self.info_font = pygame.font.SysFont(pygame.font.get_default_font(), 40)
    self.info_font = pygame.font.SysFont('dubai', 30)
    self.predator_image = pygame.image.load('assets/fox.png').convert_alpha()
    self.prey_image = pygame.image.load('assets/hare.png').convert_alpha()
    self.grass_image = pygame.image.load('assets/grass.png').convert_alpha()
    self.clock = pygame.time.Clock()

    self.running = True
    self.paused = False
    self.counter = 0


  def run(self):
    self.init_simulation()
    self.main_loop()

  
  def init_simulation(self):
    self.generate_population()
    self.generate_grass(self.objects_count['grass'])


  def main_loop(self):
    while self.running:
      if not self.all_objects:
        self.paused = True

      self.handle_keys()      
      if self.paused:
        continue

      self.counter += float(self.config["simulation"]["grass_per_round"])
      self.update_frontend()

      if int(self.counter) == 1:
        self.result_file.write(f"{self.objects_count['predator']}, {self.objects_count['prey']}\n")
        self.generate_grass(1)
        self.counter = 0

      self.run_animals_turn()

      #if all animals are gone
      if not (self.objects_count['predator'] > 0 or self.objects_count['prey'] > 0) :
        self.paused = True
        continue

      self.object_interactions()
      self.clock.tick(240)


  def move_animal(self, animal: Animal, neighbors):
    new_pos = animal.get_new_position(neighbors)
    while not self.check_position_validity(new_pos, animal.get_width(), animal.get_height(), self.screen_width, self.screen_width):
      animal.change_favorite_direction(new_pos, self.screen_width)
      new_pos = animal.get_new_position(neighbors)
    animal.move(new_pos)
 
  
  def generate_population(self):
    prey_config = self.config['animal']['prey']
    predator_config = self.config['animal']['predator']

    prey_behavior = {'eat': 0.34, 'run': 0.33, 'reproduce': 0.33}
    predator_behavior = {'hunt': 0.34, 'rest': 0.33, 'reproduce': 0.33}

    for _ in range(self.prey_num):
      x, y = random.randint(0, self.screen_width-PREY_SIZE[0]),  random.randint(0, self.screen_height-PREY_SIZE[1])
      self.all_objects.add(Prey((x, y), prey_config["initial_energy"], prey_config, prey_behavior, self.prey_image))
    for _ in range(self.predators_num):
      x, y = random.randint(0, self.screen_width-PREDATOR_SIZE[0]),  random.randint(0, self.screen_height-PREDATOR_SIZE[1])
      self.all_objects.add(Predator((x, y), predator_config["initial_energy"], predator_config, predator_behavior, self.predator_image))
  

  def check_position_validity(self, pos: tuple[int, int], obj_w, obj_h, max_w, max_h):
    return pos[0] <= max_w - obj_w and pos[0] >= 0 and pos[1] <= max_h - obj_h and pos[1] >= 0
  

  def handle_keys(self):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            self.result_file.close()
            self.running = False
          if event.key == pygame.K_SPACE:
            self.paused = not self.paused
        if event.type == pygame.MOUSEBUTTONDOWN:
          mouse_pos = pygame.mouse.get_pos()
          local_animals = list(map(lambda x: (x.behavior, x.energy, x.favorite_move), filter(lambda x: isinstance(x, Animal) and abs(mouse_pos[0] - x.pos[0]) <= 10 and abs(mouse_pos[1] - x.pos[1]) <= 10, list(self.all_objects))))
          for el in local_animals:
            print(el)
          print(len(local_animals))

  
  def run_animals_turn(self):
    '''Make animals move. Cleanup deceased animals'''
    old_sprites = []

    neighbors = self.get_pairs_dict(self.vision_range)

    for object in self.all_objects:
      if isinstance(object, Grass):
        self.screen.blit(object.image, object.pos)
        continue
      animal = object
      if animal.energy < 0:
        key = 'prey' if isinstance(animal, Prey) else 'predator'
        old_sprites.append((animal, key))
        continue

      self.move_animal(animal, neighbors.get(animal, None))
      self.screen.blit(animal.image, animal.pos)

    for old_sprite, key in old_sprites:
      old_sprite.exists = False
      self.all_objects.remove(old_sprite)
      self.objects_count[key] -= 1
  

  def object_interactions(self):
    '''Reproduction and hunting'''
    
    pairs = self.get_object_pairs(10)

    for a1, a2 in pairs:
      if type(a1) is type(a2):
        if isinstance(a1, Grass):
          continue

        new_animal = a1.reproduce(a2)
        if not new_animal:
          continue

        self.all_objects.add(new_animal)
        
        if isinstance(a1, Prey):
            self.objects_count['prey'] += 1
        elif isinstance(a1, Predator):
          self.objects_count['predator'] += 1

      else:
        if any(isinstance(e, Grass) for e in [a1, a2]) and any(isinstance(e, Predator) for e in [a1, a2]):
          continue
        elif any(isinstance(e, Grass) for e in [a1, a2]) and any(isinstance(e, Prey) for e in [a1, a2]):
          consumer = a1 if isinstance(a1, Prey) else a2
          food = a1 if isinstance(a1, Grass) else a2
          key = 'grass'
        else:
          consumer = a1 if isinstance(a1, Predator) else a2
          food = a1 if isinstance(a1, Prey) else a2
          key = 'prey'

        if food.exists:
          consumer.eat(food)
          food.exists = False
          self.all_objects.remove(food)
          self.objects_count[key] -= 1

  
  def generate_grass(self, grass_num):
    grass_config = self.config["grass"]
    for _ in range(grass_num):
      grass_x, grass_y = random.randint(0, self.screen_width-1), random.randint(0, self.screen_height-1)
      self.all_objects.add(Grass((grass_x, grass_y), grass_config, self.grass_image))


  def get_object_pairs(self, radius):
    sprites = list(self.all_objects)
    self.kd_tree = KDTree([a.pos for a in sprites])
    pairs = self.kd_tree.query_pairs(r=radius) #the radius is should be the maximum interaction distance between two objects e.g. predator spotting prey
    pairs = list(map(lambda x: (sprites[x[0]], sprites[x[1]]), list(pairs)))
    return pairs
  

  def get_pairs_dict(self, radius):
    result = {}
    pairs = self.get_object_pairs(radius)

    for pair in pairs:
      for i, el in enumerate(pair):
        if isinstance(el, Animal):
          curr_dict = result.get(el, el.generate_neighbors_dict())
          curr_dict = el.add_neighbor(curr_dict, pair[(i+1)%2])
          result[el] = curr_dict
    
    return result
  

  def update_frontend(self):
    self.draw_background()
    self.show_info()
    pygame.display.update()

  
  def draw_background(self):
    self.graph.fill("#312E38")
    self.window.blit(self.screen, (0, 0))
    self.window.blit(self.graph, (self.screen_width, 0))
    self.window.blit(self.info, (self.screen_width, self.screen_height*3//5))
    self.screen.fill('#57B669')


  def show_info(self):
    self.info.fill("#26252D")
    
    prey_surface = self.info_font.render("Prey", True, (255, 255, 255))
    prey_num = self.info_font.render(str(self.objects_count['prey']), True, (255, 255, 255))
    predator_surface = self.info_font.render("Predator", True, (255, 255, 255))
    predator_num = self.info_font.render(str(self.objects_count['predator']), True, (255, 255, 255))
    
    self.info.blit(prey_surface, (80, 50))
    self.info.blit(prey_num, (250, 50))
    self.info.blit(predator_surface, (65, 150))
    self.info.blit(predator_num, (250, 150))

    # self.info.blit()
    