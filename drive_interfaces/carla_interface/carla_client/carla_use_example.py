from __future__ import print_function
from carla_unreal import CarlaUnreal


#from scene_parameters import SceneParams
from configcarla import *
from PIL import Image
import numpy as np

import random
import time
import sys
import argparse
import logging
from socket import error as socket_error
sys.path.append('protoc')

from carla_pack_pb2 import  Scene,EpisodeStart,EpisodeReady,Control,Reward




def print_reward(pack,image,i):

	image_result = Image.fromarray(image)
	image_result.save('image' + str(i) + '.png')

	print (pack.speed)
	print (pack.collision_gen)

	print (pack.platform_timestamp)



def use_example(path_config,port = 2000, host ='127.0.0.1'):

	

	run_experiments = True
	while run_experiments:
		#try:
		carla =CarlaUnreal(host,port,path_config,800,600)
		carla.startAgent()
		carla.requestNewEpisode()
		scene,positions = carla.receiveSceneConfiguration()
		carla.newEpisode(0,0)
		print ("Positions: 0");

		capture = time.time()
		i = 1
		positions_it = 1
		while run_experiments:
			# Use input to get action, save inputs for later backprops ... etc.

			data = carla.getReward()
			



			#print (data)
			print (len(data))
			reward = data[0]
			# Image 1 is without pos-processing

			# Image 2 is image with pos processing

			# image 3 is the Semantic Segmentation

			# image 4 is the depths
			image = data[2][0]

			print_reward(reward,image,i)

			rand = random.random()

			control = Control()
			control.gas = 0.9
			control.steer = (rand * 2) - 1

			 
			carla.sendCommand(control)

	
			print ('fps: ',1.0/(time.time() -capture))
			capture = time.time()
			i+=1
			#print ('i= ',i)
			if i % 1000 ==0:
				carla.requestNewEpisode()
				scene,positions = carla.receiveSceneConfiguration()
				if positions_it < len(positions):
					carla.newEpisode(positions_it, positions_it)
					positions_it+=1
				else :
					carla.newEpisode(0,0)
					positions_it = 1
			print("Position: ",positions_it-1)
		#except socket_error:
		#	print ("Cannot connect to the server, retry in 20s...")
		#	time.sleep(20)
		#except:
		#	print ("Unexpected error: Try to reconnect in 20s...")
		#	time.sleep(20)



	
	
if __name__ == "__main__" :
	parser = argparse.ArgumentParser(description='Run multiple servers on multiple GPUs')
	parser.add_argument('host', metavar='HOST', type=str, help='host to connect to')
	parser.add_argument('port', metavar='PORT', type=int, help='port to connect to')

	parser.add_argument("-c", "--config", help="the path for the server config file that the client sends",type=str,default="./CarlaSettings.ini") 


	parser.add_argument("-l", "--log", help="activate the log file",action="store_true") 
	parser.add_argument("-lv", "--log_verbose", help="put the log file to screen",action="store_true") 
	args = parser.parse_args()
	if args.log or args.log_verbose:
		LOG_FILENAME = 'log_manual_control.log'
		logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
		if args.log_verbose:  # set of functions to put the logging to screen


			root = logging.getLogger()
			root.setLevel(logging.DEBUG)
			ch = logging.StreamHandler(sys.stdout)
			ch.setLevel(logging.DEBUG)
			formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
			ch.setFormatter(formatter)
			root.addHandler(ch)



	use_example(args.config,port=args.port, host=args.host)

