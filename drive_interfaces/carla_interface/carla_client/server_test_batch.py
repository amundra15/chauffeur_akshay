from __future__ import print_function
from carlau3d import CarlaU3D
from reward_pack import RewardPack
import random
#from scene_parameters import SceneParams
from configcarla import *
from PIL import Image
import numpy as np

import time
from carla_save_images import run_n_steps
from carla_save_images_timestamp_example import run_n_steps_timestamp


def print_reward_pack(pack):

	image_result = Image.fromarray(pack.image)
	image_result.save('image.jpg')

	print (pack.speed)
	print (pack.impact)
	print (pack.sidewalk_intersect)
	print (pack.objective)
	print (pack.player_position)
	print (pack.inertia_x)
	print (pack.inertia_y)
	print (pack.inertia_z)
	print (pack.timestamp)
	print (pack.image_number)




def start_scene_protocol():

	config =configCarla()

	# instance a carla universe with the configurations provided inside the config class
	carla =CarlaU3D(config)
	print ("STARTED U3D")

	carla.connect()

	print ("CONECTED WORLD")

	modes,scenes= carla.receive_scene_conf()

	print (" RECEIVED SCENE CONF")

	carla.select_scene_conf(modes[0],scenes[0])

	print ("SELECTED SCENE")


	posible_positions = carla.receive_episode_conf()

	print ("RECEIVED POSIBLE POSITIONS")

	carla.connect_agent()

	

	return carla,posible_positions,modes,scenes




def disconect_client(carla):

	carla.close_conections()



def test_position_restart():

	carla,posible_positions,modes,scenes = start_scene_protocol()

	for pos_1 in range(len(posible_positions)):
		for pos_2 in range(len(posible_positions)):

			print ("Starting ON ",posible_positions[pos_1], "finishing on ", posible_positions[pos_2])
			carla.start_new_episode(pos_2,pos_1)

			run_n_steps(carla, 25000, restart_freq=0, restart_close_to_goal=0, \
									write_images_to='images'+str(pos_1)+str(pos_2), verbose=2, gas=1.0, steer=random.gauss(0,0.2), \
									log_detailed='log'+str(pos_1)+str(pos_2))




def test_position_restart_timestamp():

	carla,posible_positions,modes,scenes = start_scene_protocol()

	for pos_1 in range(len(posible_positions)):
		for pos_2 in range(len(posible_positions)):

			print ("Starting ON ",posible_positions[pos_1], "finishing on ", posible_positions[pos_2])
			carla.start_new_episode(pos_2,pos_1)

			run_n_steps_timestamp(carla, 100, restart_freq=0, restart_close_to_goal=0, \
									write_images_to='images'+str(pos_1)+str(pos_2), verbose=2, gas=1.0, steer=0.0, \
									log_detailed='log'+str(pos_1)+str(pos_2))



def test_disconect_reconection():


	carla,posible_positions,modes,scenes = start_scene_protocol()
	print ("FINISHED STARTING")
	carla.close_conections()
	print ("DISCONECTED")
	carla,posible_positions,modes,scenes = start_scene_protocol()
	print ("FINISHED STARTING")

	pack = carla.get_data()
	time.sleep(0.5)

def test_kill_server_reconection():


	carla,posible_positions,modes,scenes = start_scene_protocol()
	print ("FINISHED STARTING")
	carla.close_agent_conection()
	print ("DISCONECTED")
	carla.kill_server()
	time.sleep(1.5)
	print ("KILLED THE SERVER")

	carla,posible_positions,modes,scenes = start_scene_protocol()
	print ("FINISHED STARTING")

	carla.start_new_episode(0,1)
	print ("RUN AN EPISODE FOR TESTING")
	run_n_steps_timestamp(carla, 100, restart_freq=0, restart_close_to_goal=0, \
									write_images_to='images'+str(pos_1)+str(pos_2), verbose=2, gas=1.0, steer=0.0, \
									log_detailed='log'+str(pos_1)+str(pos_2))

	time.sleep(0.5)



def test_running():
	pass


if __name__ == '__main__':

	test_position_restart_timestamp()
	#test_disconect_reconection()











