
import sys
import pygame

import datetime
start_time = datetime.datetime.now()

sys.path.append('carla_client')
sys.path.append('carla_client/protoc')
import socket

from carla_unreal import *
from planner import *

from Queue import Queue
from Queue import Empty
from Queue import Full
from threading import Thread
from contextlib import contextmanager
import sys, os
from driver import *

class CarlaHuman(Driver):
#class CarlaHuman(object):

	def __init__(self,use_planner=False,graph_file=None,map_file=None,augment_left_right=False):



		Driver.__init__(self)
		self._straight_button = False
		self._left_button = False
		self._right_button = False
		self._recording= False

		self._rear = False
		self.steering_direction = 0
		self._new_speed = 0
		self._augment_left_right = augment_left_right

		

	def start(self,host,port,config_path,resolution,use_planner=False,graph_file=None,map_file=None):

		self.carla =CarlaUnreal(host,port,config_path,resolution[0],resolution[1])


		self.carla.startAgent()


		self.carla.requestNewEpisode()
			
		scene,positions = self.carla.receiveSceneConfiguration()



		self.carla.newEpisode(2,0)

		self.use_planner = use_planner
		if use_planner:
			self.planner = Planner(graph_file,map_file)

		#except:
		#	print 'ERROR: Failed to connect to DrivingServer'
		#else:
		#	print 'Successfully connected to DrivingServer'

		# Now start the joystick, the actual controller 

		
		joystick_count = pygame.joystick.get_count()
		if joystick_count >1:
			print "Please Connect Just One Joystick"
			raise 

		#print joystick_count

		self.joystick = pygame.joystick.Joystick(0)
		self.joystick.init()

	'''#direction is when you or planner gives an indicator for a turn
		def _get_direction_buttons(self):
		#with suppress_stdout():
		if( self.joystick.get_button( 6)):
			
			self._left_button = False		
			self._right_button = False
			self._straight_button = False

		if( self.joystick.get_button( 5 )):
			
			self._left_button = True		
			self._right_button = False
			self._straight_button = False


		if( self.joystick.get_button( 4 )):
			self._right_button = True
			self._left_button = False
			self._straight_button = False

		if( self.joystick.get_button( 7 )):

			self._straight_button = True
			self._left_button = False
			self._right_button = False

			 	
	 	return [self._left_button,self._right_button,self._straight_button]'''

	def compute_direction_joystick(self,pos,ori,goal_pos,goal_ori):  
		
		return 2	#always return 2 cos splitting on the basis of direction as well. and this will basically overcome that.


		# BUtton 3 has priority

		'''button_vec = self._get_direction_buttons()
		if sum(button_vec) == 0: # Nothing
			return 2
		elif button_vec[0] == True: # Left
			return 3
		elif button_vec[1] == True: # RIght
			return 4
		else:
			return 5'''

	def get_recording(self):
		if( self.joystick.get_button( 2 )):
			self._recording =True
		if( self.joystick.get_button( 1 )):
			self._recording=False
		return self._recording

	def get_reset(self):
		# reset
		if( self.joystick.get_button( 8 )):
			self.carla.requestNewEpisode()
				
			scene,positions = self.carla.receiveSceneConfiguration()

			self.carla.newEpisode(2,0)


		return self._recording

	def get_noise(self,noise):
		if( self.joystick.get_button( 5 )):
			if noise ==True:
				return False
		return noise 


	def compute_action(self,speed,rewards,sensor):
		self._old_speed = speed
		global start_time

		""" Get Steering """
		#steering_axis = self.joystick.get_axis(0)
		if self.joystick.get_button( 6 ):  #left
			self.steering_direction = -1
		elif self.joystick.get_button( 7 ):	#right
			self.steering_direction = 1
		else:
			self.steering_direction = 0			#when left or right button is not pressed, bring the steering to centre

		#acc_axis = self.joystick.get_axis(2)
		#brake_axis = self.joystick.get_axis(3)
		
		if( self.joystick.get_button(3)):  #increase speed
			end_time = datetime.datetime.now()
			time_diff = (end_time - start_time).microseconds / 1000		#in milliseconds
			if time_diff > 300:	#to ensure same click isnt counted multiple times
				self._new_speed = self._old_speed + 0.7		#max speed = 7 kmph, changes in 10 steps
				self._new_speed = min(7, self._new_speed)	#restrict between 0-7
				start_time = datetime.datetime.now()
		if( self.joystick.get_button(0)):  #decrease speed
			end_time = datetime.datetime.now()
			time_diff = (end_time - start_time).microseconds / 1000
			if time_diff > 300:
				self._new_speed = self._old_speed - 0.7
				self._new_speed = max(0, self._new_speed)
				start_time = datetime.datetime.now()


		if( self.joystick.get_button( 10 )):
			self._rear =True
		if( self.joystick.get_button( 9 )):
			self._rear=False


		control = Control()
		control.steer = self.steering_direction
		#control.gas = -(acc_axis -1)/2.0
		if(self._new_speed - rewards.speed) > 0.05:
			control.gas = ((self._new_speed - rewards.speed ) /2.5) + 0.4	# accl till carla speed nearly equal to actual speed, constant added to overcome friction
		elif((self._new_speed - rewards.speed) < -0.05):
			control.gas = 0		#if required speed is less than carla speed, do nothing. car will automatically slow down due to friction
		#control.brake = -(brake_axis -1)/2.0
		#if control.brake < 0.001:
		#	control.brake = 0.0	
		control.brake = 0
		control.hand_brake = 0
		control.reverse = self._rear

		
		if self._augment_left_right: # If augment data, we generate copies of steering for left and right
			control_left = copy.deepcopy(control)
			print 'Left'
			control_left.steer = self._adjust_steering(control_left.steer,30.0,self._new_speed) # The angles are inverse.
			control_right = copy.deepcopy(control)
			print 'right'
			control_right.steer = self._adjust_steering(control_right.steer,-30.0,self._new_speed)

			return [control_left,control,control_right],self._new_speed


		else:
			return control, self._new_speed



	def get_sensor_data(self,goal_pos=None,goal_ori=None):
		message = self.carla.getReward()
		data = message[0]
		images = message[2][0]

		pos = [data.player_x,data.player_y,22 ]
		ori = [data.ori_x,data.ori_y,data.ori_z ]
		'''if self.use_planner:

			direction = self.planner.get_next_command(pos,ori,goal_pos,goal_ori)

		else:
			direction = 2.0'''



		direction = 2.0

		Reward.direction = property(lambda self: direction)

		return data,images

	
	def act(self,action):
		self.carla.sendCommand(action)
