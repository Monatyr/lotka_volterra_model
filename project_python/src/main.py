from Engine.engine import Engine
import json

if __name__ == "__main__":
  with open("./simulation_config.json") as file:
    config = json.load(file)

  sim_config = config["simulation"]
  width, height = int(sim_config["display_width"]), int(sim_config["display_height"]) 
  plane_width, plane_height = int(sim_config["plane_width"]), int(sim_config["display_height"]) 
  predators_num, prey_num, grass_num = int(sim_config["num_of_predators"]), int(sim_config["num_of_prey"]), int(sim_config["num_of_grass"])

  engine = Engine(width, height, plane_width, plane_height, predators_num, prey_num, grass_num)
  engine.run()