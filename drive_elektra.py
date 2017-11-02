#can be later merged with drive.py(only diff is of drive_config file)
import traceback

import sys


sys.path.append('drive_interfaces')
sys.path.append('drive_interfaces/elektra_interface')
sys.path.append('drive_interfaces/carla_interface/carla_client')

sys.path.append('drive_interfaces/carla_interface/carla_client/protoc')
sys.path.append('test_interfaces')
sys.path.append('utils')
sys.path.append('dataset_manipulation')
sys.path.append('configuration')
sys.path.append('structures')
sys.path.append('evaluation')





import math
import argparse
from noiser_elektra import Noiser

import datetime

from screen_manager import ScreenManager

import numpy as np
import os
import time

import pygame

#from config import *
#from eConfig import *
from drawing_tools import *
from extra import *

pygame.init()
clock = pygame.time.Clock()
def frame2numpy(frame, frameSize):
	return np.resize(np.fromstring(frame, dtype='uint8'), (frameSize[1], frameSize[0], 3))

# TODO: TURN this into A FACTORY CLASS
def get_instance(drive_config,experiment_name,drivers_name,memory_use,input_method):

	from elektra_recorder import Recorder
	if drive_config.type_of_driver == "Human":
		from elektra_human import ElektraHuman
		driver = ElektraHuman(drive_config,input_method)
	else:
		from elektra_machine import ElektraMachine
		driver = ElektraMachine("0",experiment_name,drive_config,memory_use)


	if drivers_name is not None:
		folder_name = str(datetime.datetime.today().day) +'_'+drivers_name
		folder_name += '_'+ str(get_latest_file_number(drive_config.path,folder_name))
		recorder = Recorder(drive_config.path + folder_name +'/',88,200,image_cut= drive_config.image_cut)
	else:

		recorder = Recorder(drive_config.path,88,200,image_cut= drive_config.image_cut)


	return driver,recorder



def drive_elektra(experiment_name,drive_config,input_method,name = None,memory_use=1.0, ):
	
	driver,recorder = get_instance(drive_config,experiment_name,name,memory_use,input_method)

	noiser = Noiser(drive_config.noise)

	#print 'before starting'
	driver.start()
	first_time = True
	if drive_config.show_screen:
		screen_manager = ScreenManager()
		screen_manager.start_screen(drive_config.resolution,drive_config.number_screens,drive_config.scale_factor)

	driver.use_planner =False

	old_speed = 0		#the speed we start the car with
	direction = 2

	iteration = 0
	try:
		while direction != -1:
			capture_time  = time.time()
			images = driver.get_sensor_data()


			for event in pygame.event.get(): # User did something
				if event.type == pygame.QUIT: # If user clicked close
					done=True # Flag that we are done so we exit this loop



			recording = driver.get_recording()		#just booleans, received from joystick
			driver.get_reset()			#just booleans, received from joystick

			action,new_speed = driver.compute_action(images,old_speed) #rewards.speed


			#action_noisy,drifting_time,will_drift = noiser.compute_noise(action[drive_config.middle_camera])
			action_noisy,drifting_time,will_drift = noiser.compute_noise(action)
			

			if recording:
				print "RECORDING"
				recorder.record(images,action.speed,action.steer,action_noisy.steer)


			#####TODO: implement this for elektra
			if drive_config.show_screen:
				if drive_config.interface == "Carla":
					for i in range(drive_config.number_screens-1):
						screen_manager.plot_driving_interface( capture_time,np.copy(images[i]),\
							action[i],action_noisy,driver.compute_direction((rewards.player_x,rewards.player_y,22),(rewards.ori_x,rewards.ori_y,rewards.ori_z)),recording and (drifting_time == 0.0 or  will_drift),\
							drifting_time,will_drift,rewards.speed,0,0,i) #

				elif drive_config.interface == "GTA":

					dist_to_goal = math.sqrt(( rewards.goal[0]- rewards.position[0]) *(rewards.goal[0] - rewards.position[0]) + (rewards.goal[1] - rewards.position[1]) *(rewards.goal[1] - rewards.position[1]))
					
					image = image[:, :, ::-1]
					screen_manager.plot_driving_interface( capture_time,np.copy(images),	action,action_noisy,\
						rewards.direction,recording and (drifting_time == 0.0 or  will_drift),drifting_time,will_drift\
						,rewards.speed,0,0,None,rewards.reseted,driver.get_number_completions(),dist_to_goal,0) #

				elif drive_config.interface == "DeepRC":
					for key,value in drive_config.cameras_to_plot.iteritems():
						screen_manager.plot_driving_interface( capture_time,np.copy(images[key]),\
							action[key],action_noisy,rewards.direction,recording and (drifting_time == 0.0 or  will_drift),\
							drifting_time,will_drift,rewards.speed,0,0,value) #
				else:
					print "Not supported interface"
					pass

			
			'''if drive_config.type_of_driver == "Machine" and drive_config.show_screen and drive_config.plot_vbp:

				image_vbp =driver.compute_perception_activations(images[drive_config.middle_camera],rewards.speed)

				screen_manager.plot_image(image_vbp,1)'''


			iteration +=1
			old_speed = new_speed
			driver.act(action_noisy)

	except:
		traceback.print_exc()

	finally:
		driver.end()
		#driver.write_performance_file(path,folder_name,iteration)
		pygame.quit()

