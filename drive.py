import traceback
import sys


sys.path.append('drive_interfaces')
sys.path.append('drive_interfaces/carla_interface')
sys.path.append('drive_interfaces/gta_interface')
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
from noiser import Noiser

import datetime

from screen_manager import ScreenManager

import numpy as np
import os
import time


#from config import *
#from eConfig import *
from drawing_tools import *
from extra import *

clock = pygame.time.Clock()
def frame2numpy(frame, frameSize):
	return np.resize(np.fromstring(frame, dtype='uint8'), (frameSize[1], frameSize[0], 3))


def drive(host,port,gpu_number,path,show_screen,resolution,noise_type,config_path,type_of_driver,experiment_name,city_name,game,drivers_name):

	print "port:",port

	use_planner = False

	screen_manager = ScreenManager()
	
	if game == "Carla":
		from carla_recorder import Recorder
		if type_of_driver == "Human":
			from carla_human import CarlaHuman
			driver = CarlaHuman(use_planner,'drive_interfaces/carla_interface/' + city_name + '.txt','drive_interfaces/carla_interface/' + city_name + '.png',augment_left_right=False)
		else:
			from carla_machine import CarlaMachine
			driver = CarlaMachine("0",experiment_name,use_planner,'drive_interfaces/carla_interface/' + city_name  + '.txt',\
				'drive_interfaces/carla_interface/' + city_name + '.png',augment_left_right=False)

	'''if drive_config.interface == "VirtualElektra":

		from carla_recorder import Recorder

		if drive_config.type_of_driver == "Human":
			from virtual_elektra_human import VirtualElektraHuman
			driver = VirtualElektraHuman(drive_config)
		else:
			from virtual_elektra_carla_machine import VirtualElektraMachine
			driver = VirtualElektraMachine("0",experiment_name,drive_config,memory_use)'''

	noiser = Noiser(noise_type)

	print host
	print port

	driver.start(host,port,config_path,resolution)
	first_time = True
	if show_screen:
		screen_manager.start_screen(resolution,3,2)


	folder_name = str(datetime.datetime.today().day) + '_' + 'Carla_' + type_of_driver + '_' + experiment_name
	folder_name += '_' + str(get_latest_file_number(path,folder_name))
	recorder = Recorder(path + folder_name +'/',88,200)
	#Note: resolution size is 400,300. but we give input to network 200,100 by cropping it.
	direction = 2
	old_speed = 0		#the speed we start the car with

	iteration = 0
	try:
		while direction != -1:		#which never happens
			capture_time  = time.time()
			direction_time = time.time()
			rewards,image = driver.get_sensor_data()

			
			for event in pygame.event.get(): # User did something
				if event.type == pygame.QUIT: # If user clicked close
					done=True # Flag that we are done so we exit this loop



			recording = driver.get_recording()



			action, new_speed, human_intervention = driver.compute_action(old_speed,rewards,image)	#passing rewards so that finally carla speed = computed speed
			#depending on driver being human or machine, new_speed can be the one given by driver or the network resp.

			action_noisy,drifting_time,will_drift = noiser.compute_noise(action)
			
			if recording:
				recorder.record(image,rewards,action,action_noisy,human_intervention)



			if show_screen:
				if game == "Carla":
					#print len(image)
					screen_manager.plot_driving_interface(capture_time,np.copy(image),\
						action,action_noisy,recording and (drifting_time == 0.0 or  will_drift),\
						drifting_time,will_drift,rewards.speed,new_speed,0,0,0,type_of_driver, driver.continous_steer, human_intervention) #

				else:
					dist_to_goal = math.sqrt(( rewards.goal[0]- rewards.position[0]) *(rewards.goal[0] - rewards.position[0]) + (rewards.goal[1] - rewards.position[1]) *(rewards.goal[1] - rewards.position[1]))
					
					image = image[:, :, ::-1]
					screen_manager.plot_driving_interface( capture_time,np.copy(image),	action,action_noisy,\
						rewards.direction,recording and (drifting_time == 0.0 or  will_drift),drifting_time,will_drift\
						,rewards.speed,0,0,None,rewards.reseted,driver.get_number_completions(),dist_to_goal,0) #


			iteration +=1
			old_speed = new_speed
			driver.act(action_noisy)

	except:
		traceback.print_exc()

	finally:

		#driver.write_performance_file(path,folder_name,iteration)
		pygame.quit()

		if type_of_driver == "Machine":			
			print "Machine:", driver.machine_driving_count 
			print "Human:", driver.human_driving_count 
			autonomy =  (float(driver.machine_driving_count) / float(driver.machine_driving_count + driver.human_driving_count)) *100
			print ("Autonomy: {0:.2f}%".format(autonomy))          


			print "Machine checkpoint score:", driver.checkpoint_score
			driver.tester.plot_map()



