#i use this only to collect data using agent
import sys
import pygame
import socket

from carla import Carla
from carla import Measurements
from carla import Control
from planner import *
import time
from ConfigParser import ConfigParser
from Queue import Queue
from Queue import Empty
from Queue import Full
from threading import Thread
from contextlib import contextmanager
import sys, os
from driver import *
import copy
import datetime

start_time = datetime.datetime.now()
from buttons import Wheel
buttons=Wheel()

class VirtualElektraHuman(Driver):


	def __init__(self,driver_conf):



		Driver.__init__(self)
		self._straight_button = False
		self._left_button = False
		self._right_button = False
		self._recording= False
		self.steering_direction = 0
		self._new_speed = 0
		# load a manager to deal with test data
		self.use_planner = driver_conf.use_planner

		self._host = driver_conf.host
		self._port = driver_conf.port
		self._config_path = driver_conf.carla_config
		self._resolution = driver_conf.resolution
		self._autopilot = driver_conf.autopilot
		self._reset_period = driver_conf.reset_period
		self._driver_conf = driver_conf

		self._rear = False

	def start(self):

		self.carla =Carla(self._host,self._port)

		self._reset()


		if not self._autopilot:
			pygame.joystick.init()



		
			joystick_count = pygame.joystick.get_count()
			if joystick_count >1:
				print "Please Connect Just One Joystick"
				raise 

			self.joystick = pygame.joystick.Joystick(0)
			self.joystick.init()

	def _reset(self):


		config = ConfigParser()

		config.optionxform = str
		config.read(self._config_path)
		config.set('CARLA/LevelSettings','NumberOfVehicles',self._driver_conf.cars)

		config.set('CARLA/LevelSettings','NumberOfPedestrians',self._driver_conf.pedestrians)

		config.set('CARLA/LevelSettings','WeatherId',self._driver_conf.weather)

		# Write down a temporary init_file to be used on the experiments
		temp_f_name = 'p' + str(self._driver_conf.pedestrians)+'_c' + str(self._driver_conf.cars)+"_w"\
		 + str(self._driver_conf.weather) +'.ini'

		with open(temp_f_name, 'w') as configfile:
			config.write(configfile)


		self._start_time = time.time()
		self.positions= self.carla.requestNewEpisode(self._config_path)

		self._current_goal = random.randint(0,len(self.positions))

		self.carla.newEpisode(random.randint(0,len(self.positions)))
		self._dist_to_activate = random.randint(100,500)





	def get_recording(self):

		if self._autopilot:
			return True
		else:	
			if( self.joystick.get_button( buttons.record_start )):

				self._recording =True
			if( self.joystick.get_button( buttons.record_end )):
				self._recording=False

			return self._recording


	def get_reset(self):

		if self._autopilot:
			if time.time() - self._start_time > self._reset_period:

				self._reset()
			elif self._latest_data.collision_vehicles > 0.0 or self._latest_data.collision_pedestrians > 0.0 or self._latest_data.collision_other > 0.0:


				self._reset()


		else:
			if( self.joystick.get_button( buttons.reset )):


				self._reset()



	def get_noise(self,noise):
		if( self.joystick.get_button( 5 )):
			if noise ==True:
				return False

		return noise 

	def compute_direction(self,pos,ori):  
		
		return 2
	def compute_action(self,sensor,speed):
		self._old_speed = speed
		global start_time

		""" Get Steering """
		if not self._autopilot:

			if self.joystick.get_button( buttons.steer_left ):  #left
				self.steering_direction = -1
			elif self.joystick.get_button( buttons.steer_right ):	#right
				self.steering_direction = 1
			else:
				self.steering_direction = 0			#when left or right button is not pressed, bring the steering to centre

			#acc_axis = self.joystick.get_axis(2)
			#brake_axis = self.joystick.get_axis(3)
			
			if( self.joystick.get_button(buttons.more_speed)):  #increase speed
				end_time = datetime.datetime.now()
				time_diff = (end_time - start_time).microseconds / 1000		#in milliseconds
				if time_diff > 300:	#to ensure same click isnt counted multiple times
					self._new_speed = self._old_speed + 0.7		#max speed = 7 kmph, changes in 10 steps
					self._new_speed = min(7, self._new_speed)	#restrict between 0-7
					start_time = datetime.datetime.now()
			if( self.joystick.get_button(buttons.less_speed)):  #decrease speed
				end_time = datetime.datetime.now()
				time_diff = (end_time - start_time).microseconds / 1000
				if time_diff > 300:
					self._new_speed = self._old_speed - 0.7
					self._new_speed = max(0, self._new_speed)
					start_time = datetime.datetime.now()


			if( self.joystick.get_button( buttons.rear_on )):
				self._rear =True
			if( self.joystick.get_button( buttons.rear_off )):
				self._rear=False

			control = Control()
			control.steer = self.steering_direction
			#control.throttle = -(acc_axis -1)/2.0
			if(self._new_speed - speed) > 0.05:
				control.throttle = ((self._new_speed - speed ) /2.5) + 0.4	# accl till carla speed nearly equal to actual speed, constant added to overcome friction
			else:
				control.throttle = 0		#if required speed is less than carla speed, do nothing. car will automatically slow down due to friction
			#control.brake = -(brake_axis -1)/2.0
			#if control.brake < 0.001:
			#	control.brake = 0.0	
			control.brake = 0
			control.hand_brake = 0
			control.reverse = self._rear



		else:

			control = self._latest_data.ai_control
			if control.steer > 0.3:
				control.steer =1.0
			elif control.steer < -0.3:
				control.steer = -1.0
			else:
				control.steer = 0.0

		return control



	def get_sensor_data(self,goal_pos=None,goal_ori=None):

		wall_time,game_time,data,agents,image_data = self.carla.getMeasurements()


		pos = [data.transform.location.x,data.transform.location.y,22]
		ori = [data.transform.orientation.x,data.transform.orientation.y,data.transform.orientation.z]
		
		if self.use_planner:

			if sldist([data.transform.location.x,data.transform.location.y],[self.positions[self._current_goal].location.x,self.positions[self._current_goal].location.y]) < self._dist_to_activate:

				self._current_goal = random.randint(0,len(self.positions))
				self._dist_to_activate = random.randint(100,500)

			direction,_,_ = self.planner.get_next_command(pos,ori,[self.positions[self._current_goal].location.x,self.positions[self._current_goal].location.y,22],(1,0,0))
			
		else:
			direction = 2.0

		self._latest_data =data
		self._latest_agents =agents

		return wall_time,game_time,data,agents,image_data,direction


	
	def act(self,action):


		self.carla.sendCommand(action)

