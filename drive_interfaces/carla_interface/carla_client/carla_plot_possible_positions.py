from __future__ import print_function
from carlau3d import CarlaU3D

#from scene_parameters import SceneParams
from configcarla import *
import numpy as np

import matplotlib.pyplot as plt

import time


config =configCarla()
config.host = 'localhost'
config.port = 2000

# instance a carla universe with the configurations provided inside the config class
carla =CarlaU3D(config)
print ("STARTED U3D")

carla.connect()

print ("CONECTED WORLD")

modes,scenes= carla.receive_scene_conf()

print (" RECEIVED SCENE CONF")

carla.select_scene_conf(modes[0],scenes[0])

print ("SELECTED SCENE")


possible_positions = carla.receive_episode_conf()

print ("RECEIVED POSIBLE POSITIONS")

print(possible_positions)

plt.scatter(*zip(*possible_positions))    

labels = ['{0}'.format(i) for i in range(len(possible_positions))]
for label, pos in zip(labels, possible_positions):
    plt.annotate(
        label,
        xy=(pos[0], pos[1]), xytext=(0, 0),
        textcoords='offset points', ha='right', va='bottom',)

plt.show()





	
	