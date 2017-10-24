
import sys
import os

import socket
import scipy
import re

import math

from Queue import Queue
from Queue import Empty
from Queue import Full
from threading import Thread
import tensorflow as tf
import time

import pygame

sys.path.append('../train')
from pygame.locals import *
from socket_util import *
from carla_unreal import *
from planner import *

from sklearn import preprocessing

from codification import *

from training_manager import TrainManager
import machine_output_functions
from Runnable import *
from driver import *
from drawing_tools import *
import copy
import random

Reward.noise = property(lambda self: 0)


def restore_session(sess,saver,models_path):

  ckpt = 0
  if not os.path.exists(models_path):
    os.mkdir( models_path)
  
  ckpt = tf.train.get_checkpoint_state(models_path)
  if ckpt:
    print 'Restoring from ',ckpt.model_checkpoint_path  
    saver.restore(sess,ckpt.model_checkpoint_path)
  else:
    ckpt = 0

  return ckpt


def load_system(config):
  config.batch_size =1
  config.is_training=False

  training_manager= TrainManager(config)


  training_manager.build_network()


  """ Initializing Session as variables that control the session """
  



  return training_manager



class CarlaMachine(Runnable,Driver):


  def __init__(self,gpu_number,experiment_name,use_planner=False,graph_file=None,map_file=None,augment_left_right=False):

    Driver.__init__(self)
    conf_module  = __import__(experiment_name)
    self._config = conf_module.configInput()
    
    config_gpu = tf.ConfigProto()
    config_gpu.gpu_options.visible_device_list=gpu_number
    self._sess = tf.Session(config=config_gpu)
   
    self._augment_left_right = augment_left_right

    self._straight_button = False
    self._left_button = False
    self._right_button = False
    self._recording= False
    #self._mean_image = np.load(self._config.save_data_stats + '/meanimage.npy') #no longer used
    self._train_manager =  load_system(conf_module.configTrain())


    self._sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver(tf.global_variables())
    # load a manager to deal with test data
    self.use_planner = use_planner
    if use_planner:
      self.planner = Planner(graph_file,map_file)


    cpkt = restore_session(self._sess,saver,self._config.models_path)




  def start(self,host,port,config_path,resolution):

    self.carla =CarlaUnreal(host,port,config_path,resolution[0],resolution[1])


    self.carla.startAgent()
  

    self.carla.requestNewEpisode()
      
    scene,positions = self.carla.receiveSceneConfiguration()


    self.carla.newEpisode(0,0)


  '''def _get_direction_buttons(self):
    #with suppress_stdout():if keys[K_LEFT]:
    keys=pygame.key.get_pressed()

    if( keys[K_s]):

      self._left_button = False   
      self._right_button = False
      self._straight_button = False

    if( keys[K_a]):
      
      self._left_button = True    
      self._right_button = False
      self._straight_button = False


    if( keys[K_d]):
      self._right_button = True
      self._left_button = False
      self._straight_button = False

    if( keys[K_w]):

      self._straight_button = True
      self._left_button = False
      self._right_button = False

        
    return [self._left_button,self._right_button,self._straight_button]'''

  def compute_direction(self,pos,ori,goal_pos,goal_ori):  # This should have maybe some global position... GPS stuff
    return 2    #always return 2 cos splitting on the basis of direction as well. and this will basically overcome that.
    '''if self.use_planner:

      return self.planner.get_next_command(pos,ori,goal_pos,goal_ori)

    else:
      # BUtton 3 has priority
      if 'Control' not in set(self._config.inputs_names):
        return None

      button_vec = self._get_direction_buttons()
      if sum(button_vec) == 0: # Nothing
        return 2
      elif button_vec[0] == True: # Left
        return 3
      elif button_vec[1] == True: # RIght
        return 4
      else:
        return 5'''

    

  def get_recording(self):
    return True


  def run_step(self,data,target):

    rewards = data[0]
    sensor = data[2][0] #takes the first image
    speed = rewards.speed

    direction = self.compute_direction((rewards.player_x,rewards.player_y,22),(rewards.ori_x,rewards.ori_y,rewards.ori_z),(target[0],target[1],22),(1.0,0.02,-0.001))
    #will return 2

    """ Get Steering """

    capture_time = time.time()

    #resizing the 400,300 image to 200,100
    sensor = sensor[65:265,:,:]
    sensor = scipy.misc.imresize(sensor,[self._config.network_input_size[0],self._config.network_input_size[1]])

    image_input = sensor.astype(np.float32)

    #print future_image

    #image_input = image_input - self._mean_image
    #print "2"
    image_input = np.multiply(image_input, 1.0 / 255.0)


    #steer,acc,brake = machine_output_functions.single_branch(image_input,speed,direction,self._config,self._sess,self._train_manager)
    steer,acc,brake = machine_output_functions.single_branch(image_input,self._config,self._sess,self._train_manager)


    if brake < 0.1:
      brake =0.0
      
    control = Control()
    control.steer = steer
    control.gas =acc
    control.brake =brake

    control.hand_brake = 0
    control.reverse = 0


    return control

  def compute_action(self,speed,rewards,sensor):
    self._old_speed = speed
    
    direction = self.compute_direction((0,0,22),(0,0,1),(0,0,22),(1.0,0.02,-0.001)) #will return 2
    #sensor = sensor[1]  #contains image
    capture_time = time.time()


    sensor = sensor[0][65:265,:,:]   #sensor's first dimension contains the tuple of images from diff cameras. we have just one, and are aceessing that using [0]

    #imresize uses interpolation to resize images
    #sensor = scipy.misc.imresize(sensor,[self._config.network_input_size[0],self._config.network_input_size[1]])
    sensor = scipy.misc.imresize(sensor,[self._config.network_input_size[0],self._config.network_input_size[1],self._config.network_input_size[2]])

    image_input = sensor.astype(np.float32)

    #print future_image

    #image_input = image_input - self._mean_image
    #print "2"
    image_input = np.multiply(image_input, 1.0 / 127.0)


    steer,_new_speed = machine_output_functions.single_branch(image_input,self._config,self._sess,self._train_manager)



    control = Control()
    control.steer = steer
    if(_new_speed - rewards.speed) > 0.05:
      control.gas = ((_new_speed - rewards.speed ) /2.5) + 0.4 # accl till carla speed nearly equal to actual speed. constant added to overcome friction
    else:
      control.gas = 0   #if required speed is less than carla speed, do nothing. car will automatically slow down due to friction
    control.brake = 0
    control.hand_brake = 0
    control.reverse = 0


    if self._augment_left_right: # If augment data, we generate copies of steering for left and right
      control_left = copy.deepcopy(control)
      print 'Left'
      control_left.steer = self._adjust_steering(control_left.steer,30.0,_new_speed) # The angles are inverse.
      control_right = copy.deepcopy(control)
      print 'right'
      control_right.steer = self._adjust_steering(control_right.steer,-30.0,_new_speed)
   
      return [control_left,control,control_right], _new_speed

    else:
      return control, _new_speed

  
  # The augmentation should be dependent on speed



  def get_sensor_data(self):
    message = self.carla.getReward()
    data = message[0]
    images = message[2]

    direction = self.compute_direction(0,0,0,0)     #will return 2
    Reward.direction = property(lambda self: direction)
    return data,images


  def compute_perception_activations(self,sensor,speed):

    sensor = sensor[65:265,:,:]

    sensor = scipy.misc.imresize(sensor,[self._config.network_input_size[0],self._config.network_input_size[1]])

    image_input = sensor.astype(np.float32)

    #print future_image

    #image_input = image_input - self._mean_image
    #print "2"
    image_input = np.multiply(image_input, 1.0 / 127.0)


    vbp_image =  machine_output_functions.vbp(image_input,speed,self._config,self._sess,self._train_manager)

    #min_max_scaler = preprocessing.MinMaxScaler()
    #vbp_image = min_max_scaler.fit_transform(np.squeeze(vbp_image))

    print vbp_image.shape
    return 0.5*grayscale_colormap(np.squeeze(vbp_image),'jet') + 0.5*image_input
  
  def act(self,action):

    self.carla.sendCommand(action)