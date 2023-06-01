import pygame


class SidePanel:
    def __init__(self, width, height, prey_num, predator_num):
      self.width = width
      self.height = height
      self.surface = pygame.Surface((width, height))
      self.graph_area = pygame.Surface((self.width, self.height*3//5))
      self.chart = pygame.Surface((370, 330))
      self.info = pygame.Surface((self.width, self.height*2//5))
      self.info_font = pygame.font.SysFont('dubai', 30)
      self.chart_font = pygame.font.SysFont('dubai', 10)
      self.ylabels = [self.chart_font.render(str(i), True, "white") for i in range(25, 301, 25)]
      self.previous_values = (self.chart.get_height() - prey_num, self.chart.get_height() - predator_num)

      self.prey_color = "#006200"
      self.predator_color = "#A53860"
      self.time_index = 0
      self.chart_index = 0
  

    def render(self, prey_amount, predator_amount) -> pygame.Surface:
      self.render_graph(prey_amount, predator_amount)
      self.render_info(prey_amount, predator_amount)
      self.surface.blit(self.graph_area, (0, 0))
      self.surface.blit(self.info, (0, self.height*3//5))
      return self.surface
    

    def render_graph(self, prey_amount, predator_amount) -> None:
      if self.chart_index == 0:
        self.graph_area.fill("#312E38")
        self.chart.fill('#1E1C22')
        for i, el in enumerate(self.ylabels):
          pygame.draw.line(self.chart, "#4A4A4A", (0, self.chart.get_height() - (i+1)*25), (self.chart.get_width(), self.chart.get_height() - (i+1)*25))
          self.chart.blit(el, (self.chart.get_width() - 20, self.chart.get_height() - ((i+1)*25 + 8)))
      
      self.graph_area.blit(self.chart, (15, 15))
      self.time_index += 1

      if self.time_index%5 == 0:
        pygame.draw.line(self.chart, self.prey_color, (self.chart_index, self.previous_values[0]), (self.chart_index + 1, self.chart.get_height() - prey_amount), width=3)
        pygame.draw.line(self.chart, self.predator_color, (self.chart_index, self.previous_values[1]), (self.chart_index + 1, self.chart.get_height() - predator_amount), width=3)
        self.previous_values = (self.chart.get_height() - prey_amount, self.chart.get_height() - predator_amount)
        self.chart_index += 1
        self.chart_index %= self.chart.get_width()
        self.time_index %= 5
    

    def render_info(self, prey_amount, predator_amount) -> None:
      prey_surface = self.info_font.render("Prey", True, (255, 255, 255))
      prey_num = self.info_font.render(str(prey_amount), True, self.prey_color)
      predator_surface = self.info_font.render("Predator", True, (255, 255, 255))
      predator_num = self.info_font.render(str(predator_amount), True, self.predator_color)

      self.info.fill("#26252D")
      self.info.blit(prey_surface, (75, 40))
      self.info.blit(prey_num, (280, 40))
      self.info.blit(predator_surface, (55, 160))
      self.info.blit(predator_num, (280, 160))
      pygame.draw.line(self.info, (110, 109, 109), (200, 0), (200, 240))
      pygame.draw.line(self.info, (110, 109, 109), (0, 120), (400, 120))
    