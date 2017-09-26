from __future__ import print_function
from datastream import DataStream
import socket
import time
import os, signal
import sys
import logging
import struct

sys.path.append('protoc')


import socket_util
from carla_pack_pb2 import  Scene,EpisodeStart,EpisodeReady,Control,Reward,RequestNewEpisode




class CarlaUnreal(object):

	"""
	Normal instanciation of the class, creating also the thread class responsible for receiving data
	"""
	def __init__(self,host,port,config_path,image_x=400,image_y=300):
		self._host = host
		self._port = port
		logging.debug('selected host %s' % host)
		logging.debug('selected port %s' % port)
		self._config_path = config_path
		logging.debug('set config path as port %s' % config_path)


		logging.debug('selected port %s' % port)	
		self._port_control = self._port +2
		self._port_stream = self._port +1
		#self._fps =config.fps

		self._socket_world = socket_util.pers_connect(self._host ,self._port)
		logging.debug("Connected to Unreal Server World Socket")
		self._socket_stream = 0
		self._socket_control = 0
		self._image_x =image_x
		self._image_y = image_y


		self._data_stream = DataStream(image_x,image_y)
		logging.debug("Started Unreal Client")


	def setIniFile(self,config_path):
		
		self._config_path = config_path
		logging.debug('set config path as port %s' % config_path)

	""" Starting the Agent. The image stream port
	and the control port """


	def startAgent(self):


		logging.debug("Going to Connect Stream and start thread")
		self._socket_stream = socket_util.pers_connect(self._host ,self._port_stream)

		self._socket_control = socket_util.pers_connect(self._host ,self._port_control)
		logging.debug("Control Socket Connected")

		self._data_stream.start(self._socket_stream)
		logging.debug("Streaming Thread  Started")




	def receiveSceneConfiguration(self):

		try:
			data = socket_util.get_message(self._socket_world)
			scene = Scene()
			scene.ParseFromString(data)
			logging.debug("Received Scene Configuration")

			# parsing positions
			positions = []
			number_of_positions = len(scene.positions)/8 # Every 8 bytes you have a position
			for i in range(0,number_of_positions*2,2):
				x = struct.unpack('f', scene.positions[i*4:(i+1)*4])[0]
				y = struct.unpack('f', scene.positions[(i+1)*4:(i+2)*4])[0]
				positions.append((x,y))

			return scene,positions

		except:
			logging.debug("Died When receiving configuration")
			return self.restart()




		


	def requestNewEpisode(self,ini_file=None):


		requestEpisode = RequestNewEpisode()
		if ini_file ==None: # You can send a new ini file to be open, if not open the one defined on start
			ini_path =self._config_path
		else:
			ini_path = ini_file

		with open (ini_path, "r") as myfile:
			data=myfile.read()
		logging.debug("Set the Init File")
		
		requestEpisode.init_file = data
		try:
			socket_util.send_message(self._socket_world,requestEpisode)
		except:
			logging.debug("Died When requesting new episode")
			self.restart()


		logging.debug("Send the new episode Request")



	def newEpisode(self,start_index,end_index):

		self._latest_start = start_index
		self._latest_end = end_index
		scene_init = EpisodeStart()
		scene_init.start_index = start_index
		scene_init.end_index = end_index
		try:
			socket_util.send_message(self._socket_world,scene_init)
		except:
			logging.debug("Died When confirming new episode")
			self.restart()


		logging.debug("Send the new episode Message")
		episode_ready = EpisodeReady()
		episode_ready.ready = False
		self._data_stream.clean()
		try:
			while not episode_ready.ready:
				data = socket_util.get_message(self._socket_world)
				episode_ready.ParseFromString(data)
		except:

			logging.debug("Died when trying to receive episode reading")
			self.restart()


		logging.debug("Episode is Ready")



	### **** PROTOCOL 3 ****

	def getReward(self):
		logging.debug("Got A new Reward")

		while True:
			try:
				reward_data = self._data_stream.get_the_latest_data()
				return reward_data
			except:
				logging.debug("Got an empty reward") 
			 	self.restart()

	 	return reward_data

	""" Command contains:
		Steering: -1 to 1
		Acc : -1 to 1
	"""

	def sendCommand(self,control):

		logging.debug("Send Control Comand : acc -> %f , steer %f, brake %f, hand_brake %d, gear %d" % (control.gas,control.steer,control.brake,control.hand_brake,control.reverse))
		try:
			socket_util.send_message(self._socket_control,control)
		except:

			logging.debug("Problems on sending the commands... restarting")
			self.restart() # the mensage is not resend because it likely lost its relevance.
			


	def restart(self):
		logging.debug("Trying to close clients") 
		self.close_conections()
		connected = False 
		self._data_stream._running = False
		while not connected:
			try:
				logging.debug("Trying to connect to the world thread")
				self._socket_world = socket_util.connect(self._host ,self._port)		
				connected = True
			except:
				logging.debug("Couldn't connected ... retry in 10 seconds...")
				time.sleep(10)

		self._data_stream = DataStream(self._image_x,self._image_y)
		self.startAgent()
		self.requestNewEpisode()
		scene,positions = self.receiveSceneConfiguration()
		self.newEpisode(self._latest_start,self._latest_end)
		logging.debug("restarted the world connection") 
		return scene,positions

	def stop(self):
		self.close_conections()
		connected = False 

		self._data_stream._running = False
		self._data_stream = DataStream(self._image_x,self._image_y)

	def close_conections(self):

		try:
			self._socket_world.shutdown(socket.SHUT_RDWR)
			self._socket_world.close()

			logging.debug("Close world")
		except Exception as ex:
			print (ex.message)

		try:
			self._socket_stream.shutdown(socket.SHUT_RDWR)
			self._socket_stream.close()
			logging.debug("Close Stream")
		except Exception as ex:
			print (ex.message)

		try:
			self._socket_control.shutdown(socket.SHUT_RDWR)
			self._socket_control.close()
			logging.debug("Close Control")
		except Exception as ex:
			print (ex.message)


