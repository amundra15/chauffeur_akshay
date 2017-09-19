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
	else:
		from gta_recorder import Recorder
		if type_of_driver == "Human":
			from gta_human import GTAHuman
			driver = GTAHuman()
		else:
			from gta_machine import GTAMachine
			driver = GTAMachine("0",experiment_name)

		#gta_surface = get_gta_map_surface((800,600))
	# Instance the environemnt

	noiser = Noiser(noise_type)
	print host
	print port


	driver.start(host,port,config_path,resolution)
	first_time = True
	if show_screen:
		screen_manager.start_screen(resolution,3,2)


	folder_name = str(datetime.datetime.today().day) +'_'+drivers_name
	folder_name += '_'+ str(get_latest_file_number(path,folder_name))
	recorder = Recorder(path + folder_name +'/',100,200)
	#Note: resolution size is 400,300. but we give input to network 200,100 by cropping it.
	direction = 2
	old_speed = 0

	iteration = 0
	try:
		while direction != -1:		#which never happens
			capture_time  = time.time()
			direction_time = time.time()
			rewards,image = driver.get_sensor_data() # Later it would return more image like [rewards,images,segmentation]
			'''print '**********'
			print len(image[0])
			print len(image[1])
			print len(image[2])
			print len(image[1][0])
			print len(image[1][1])
			print len(image[1][2])
			print len(image[1][3])
			print len(image[0][0])
			print len(image[2][0])'''
			#sensor_data = frame2numpy(image,[800,600])


			
			# Compute now the direction
			
			for event in pygame.event.get(): # User did something
				if event.type == pygame.QUIT: # If user clicked close
					done=True # Flag that we are done so we exit this loop



			recording = driver.get_recording()



			action, new_speed = driver.compute_action(old_speed,rewards,image)	#passing rewards so that finally carla speed = computed speed
			#depending on driver being human or machine, new_speed can be the one given by driver or the network resp.

			action_noisy,drifting_time,will_drift = noiser.compute_noise(action)
			
			if recording:
				recorder.record(image,rewards,action,action_noisy)


			'''#only for 3 images, i.e. augmented version
			if recording:
				for i in range(len(image)):
					recorder.record(image[i],rewards,actions[i],action_noisy,i)'''

			#print "RECORDING ? ",recording and not exist_noise



			if show_screen:
				if game == "Carla":

					screen_manager.plot_driving_interface( capture_time,np.copy(image),\
						action,action_noisy,recording and (drifting_time == 0.0 or  will_drift),\
						drifting_time,will_drift,rewards.speed,new_speed,0,0,0) #

					'''#for 3 images
					screen_manager.plot_driving_interface( capture_time,np.copy(image[0]),\
						actions[0],action_noisy,recording and (drifting_time == 0.0 or  will_drift),\
						drifting_time,will_drift,rewards.speed,new_speed,0,0,0) #
					screen_manager.plot_driving_interface( capture_time,np.copy(image[1]),\
						actions[1],action_noisy,recording and (drifting_time == 0.0 or  will_drift),\
						drifting_time,will_drift,rewards.speed,new_speed,0,0,1) 
					screen_manager.plot_driving_interface( capture_time,np.copy(image[2]),\
						actions[2],action_noisy,recording and (drifting_time == 0.0 or  will_drift),\
						drifting_time,will_drift,rewards.speed,new_speed,0,0,2) '''


					'''screen_manager.plot_driving_interface( capture_time,np.copy(image[0]),\
						actions[0],action_noisy,recording and (drifting_time == 0.0 or  will_drift),\
						drifting_time,will_drift,rewards.speed,0,0,0) #
					screen_manager.plot_driving_interface( capture_time,np.copy(image[1]),\
						actions[1],action_noisy,recording and (drifting_time == 0.0 or  will_drift),\
						drifting_time,will_drift,rewards.speed,0,0,1) 
					screen_manager.plot_driving_interface( capture_time,np.copy(image[2]),\
						actions[2],action_noisy,recording and (drifting_time == 0.0 or  will_drift),\
						drifting_time,will_drift,rewards.speed,0,0,2) '''
				else:
					dist_to_goal = math.sqrt(( rewards.goal[0]- rewards.position[0]) *(rewards.goal[0] - rewards.position[0]) + (rewards.goal[1] - rewards.position[1]) *(rewards.goal[1] - rewards.position[1]))
					
					image = image[:, :, ::-1]
					screen_manager.plot_driving_interface( capture_time,np.copy(image),	action,action_noisy,\
						rewards.direction,recording and (drifting_time == 0.0 or  will_drift),drifting_time,will_drift\
						,rewards.speed,0,0,None,rewards.reseted,driver.get_number_completions(),dist_to_goal,0) #
			
			if type_of_driver == "Machine":
				pass
				#image_vbp =driver.compute_perception_activations(image[0],rewards.speed)

				#screen_manager.plot_image(image_vbp,1)


			iteration +=1
			old_speed = new_speed
			driver.act(action_noisy)

	except:
		traceback.print_exc()

	finally:

		#driver.write_performance_file(path,folder_name,iteration)
		pygame.quit()


