from __future__ import print_function

from datastream import DataStream
import socket
import time
import os, signal
import sys



sys.path.append('protoc')


from socket_util import *
from carla_pack_pb2 import World, Scene,SceneInit,EpisodeStart,EpisodeReady,Control,Reward




class CarlaU3D(object):

	def __init__(self):
		pass
	# Normal instanciation of the class, creating also the thread class responsible for receiving data
	def __init__(self,config):
		self._host = config.host 
		self._port = config.port
		
		
		self._port_control = self._port +2
		self._port_stream = self._port +1
		#self._fps =config.fps

		self._socket_world = connect(self._host ,self._port)
		#self._socket_world = 0
		self._socket_stream = 0
		self._socket_control = 0
		


		self._data_stream = DataStream()
		
		

		
		
	
	def start_agent(self):
		


		print("Start STREAM")
		self._socket_stream = connect(self._host ,self._port_stream)
		self._data_stream.start(self._socket_stream)
		print("STREAM started")

		self._socket_control = connect(self._host ,self._port_control)
		#self._socket_control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self._socket_control.connect((self._host,self._port_control))
		#print("Connected to agent Server ")
		#time.sleep(20)
				


	###  **** PROTOCOL 1 **** 
			
	""" On this function we receive the information with respect to the world ( Possible scenes, possible modes) 
	That we can use to select what kind of environment we are going to train with. """
	def receive_scene_conf(self):

		data = get_message(self._socket_world)

		world = World()
		world.ParseFromString(data)
		print ("mode ", world.modes)
		print ("scene ", world.scenes)

		return world

		
		
	def select_scene_conf(self,mode,scene):
	
		scene_init = SceneInit()
		scene_init.mode = mode
		scene_init.scene = scene
		send_message(self._socket_world,scene_init)



	### **** PROTOCOL 2 ****
			
			
	def receive_episode_conf(self):


		data = get_message(self._socket_world)

		scene = Scene()
		scene.ParseFromString(data)

		print (scene.position)

		return scene	
		
	def start_new_episode(self,start_index,end_index):


		scene_init = EpisodeStart()
		scene_init.start_index = start_index
		scene_init.end_index = end_index
		send_message(self._socket_world,scene_init)
		print ("SEND NEW EPISODE")
		episode_ready = EpisodeReady()
		episode_ready.ready = False
		while not episode_ready.ready:
			data = get_message(self._socket_world)		
			episode_ready.ParseFromString(data)
			print ("GOT IT")

		print ("EPISODE READY")

		 
		
	### **** PROTOCOL 3 ****	

	def get_data(self):

		return self._data_stream.get_the_latest_data()



	def control_agent(self,acc,steer):

		control = Control()
		control.gas = acc
		control.steer = steer
		send_message(self._socket_control,control)
	
		print (" SENT COMMAND")


	def close_agent_conection(self):
		self._socket_stream.shutdown(socket.SHUT_RDWR)
		self._socket_control.shutdown(socket.SHUT_RDWR)

		self._socket_stream.close()
		self._socket_control.close()

	def close_conections(self):

		self._socket_world.shutdown(socket.SHUT_RDWR)
		self._socket_stream.shutdown(socket.SHUT_RDWR)
		self._socket_control.shutdown(socket.SHUT_RDWR)
		self._socket_world.close()
		self._socket_stream.close()
		self._socket_control.close()


