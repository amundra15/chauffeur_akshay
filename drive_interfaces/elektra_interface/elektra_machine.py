
import numpy as np
import cv2

import scipy

import pygame

import math
import copy
from driver import *
import logging
import tensorflow as tf
from training_manager import TrainManager
import machine_output_functions
import os

import time

import socket

from drawing_tools import *
print(cv2.__version__)


class Control:
    speed = 0
    steer = 0


camera_port = 1   # Change this to your webcam ID, or file name for your video file

ramp_frames = 30  #Number of frames to throw away while the camera adjusts to light levels

UDP_IP = "10.42.0.144"
UDP_PORT = 5009
sock = socket.socket(socket.AF_INET, # Internet
          socket.SOCK_DGRAM) # UDP


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


class ElektraMachine(Driver):



  # Initializes

  def __init__(self,gpu_number,experiment_name,drive_conf,input_method,memory_fraction=0.95):

    Driver.__init__(self)
    self._augment_left_right = drive_conf.augment_left_right
 
    self._augmentation_camera_angles = drive_conf.camera_angle 

    self._input_method = input_method
    self._recording= False    
    self._rear = False
    self.steering_direction = 0
    self._new_speed = 0
    self.hold = True
    self.resume = False


    self._resolution = drive_conf.resolution
    self._image_cut = drive_conf.image_cut


    conf_module  = __import__(experiment_name)
    self._config = conf_module.configInput()
    
    config_gpu = tf.ConfigProto()

    config_gpu.gpu_options.per_process_gpu_memory_fraction=memory_fraction
    config_gpu.gpu_options.visible_device_list=gpu_number
    self._sess = tf.Session(config=config_gpu)
   

    #self._mean_image = np.load(self._config.save_data_stats + '/meanimage.npy')  #no longer used
    #self._mean_image = np.load('data_stats/'+ self._config.dataset_name + '_meanimage.npy')

    self._train_manager =  load_system(conf_module.configTrain())


    self._sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver(tf.global_variables())
    #self._control_function =getattr(machine_output_functions, self._train_manager._config.control_mode )


    cpkt = restore_session(self._sess,saver,self._config.models_path)



  def start(self):
    #manually run motor.py

    # Starts communication with the cameras
    self.camera = cv2.VideoCapture(camera_port)
 
    # Ramp the camera - these frames will be discarded and are only used to allow v4l2 to adjust light levels, if necessary
    print("Adjusting brightness...")
    for i in xrange(ramp_frames):
      retval, temp = self.camera.read()
      #print retval   


    # Start the interface with the joystick (if using)
    if(self._input_method == 'xbox'):
      #pygame.joystick.init()
      joystick_count = pygame.joystick.get_count()
      if joystick_count >1:
        print "Please Connect Just One Joystick"
        raise 
      print "joystick count: ", joystick_count
      self.joystick = pygame.joystick.Joystick(0)
      self.joystick.init()
      print 'USE XBOX JOYSTICK...'
      #print self.joystick.get_numbuttons()
    

    #otherwise initialize pygame for keyboard 
    else:
      pygame.init()
      #clock = pygame.time.Clock()
      screen = pygame.display.set_mode((100,100))
      event=pygame.event.poll()
      print 'USE KEYBOARD...'

    

  def get_recording(self):
    return True



  def get_reset(self):
    return False

  def get_direction(self):
    return 2.0

 
  def compute_action(self,sensor,speed):

    self._old_speed = speed

    """ Get Steering """
    # receives from 1000 to 2000 
    direction = self.get_direction()

    # Just taking the center image to send to the network


    sensor = sensor[self._image_cut[0]:self._image_cut[1],:,:]

    sensor = scipy.misc.imresize(sensor,[self._config.network_input_size[0],self._config.network_input_size[1]])

    image_input = sensor.astype(np.float32)

    #print future_image

    #image_input = image_input - self._mean_image
    #print "2"
    image_input = np.multiply(image_input, 1.0 / 255.0)


    #steer,acc,brake = self._control_function(image_input,speed,direction,self._config,self._sess,self._train_manager)
    steer,_new_speed = machine_output_functions.single_branch_steer_only(image_input,self._config,self._sess,self._train_manager)
    #note: we are not training for speed as of now. so network just returns speed value as 7 always

    if steer > 0.35:
      steer = 1
    elif steer < -0.35:
      steer = -1
    else:
      steer = 0

    control = Control()
    control.speed = 7
    control.steer = steer


    human_intervention = False
    #if human wants to intervene, the corresponding steerings get priority
    if(self._input_method == 'xbox'):
      if self.joystick.get_button( 6 ):  #left
        control.steer = -1
        human_intervention = True
      elif self.joystick.get_button( 7 ): #right
        control.steer = 1
        human_intervention = True
    else:
      keys = pygame.key.get_pressed()
      if keys[pygame.K_a]:
        control.steer = -1
        human_intervention = True
      elif keys[pygame.K_d]:
        control.steer = 1
        human_intervention = True

      if keys[pygame.K_s]:   #decrease speed to zero
        self.hold = True
        self.resume = False
        print "hold"
        self._new_speed = 0
      #keys = pygame.key.get_pressed()
      if keys[pygame.K_w]:   #increase speed to max
        self.resume = True
        self.hold = False
        print "resume"
        self._new_speed = 7

    

    return control, _new_speed, human_intervention


  def get_sensor_data(self):

    # Take the actual image we want to keep
    retval, frame = self.camera.read()  # Captures a single image from the camera in PIL format

    #print retval
    r=frame.shape[0]
    c=frame.shape[1]
    frame = frame[1:r, 1:c/2] #just take the left camera image

    #opencv reads image in BGR format. convert it to RGB before inferencing
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    # get other measurements the car is making

    return frame


  
  def act(self,control):

    #sending direction to pi
    if control.steer == 0:
        MESSAGE = 'x';  
        print MESSAGE               
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    elif control.steer == 1:
        MESSAGE = 'd';  
        print MESSAGE               
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    elif control.steer == -1:
        MESSAGE = 'a';  
        print MESSAGE               
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))



    #sending speed to pi
    if(self._input_method == 'xbox'):
      #sending speed from 0 to 7, when controlling with xbox
      if(self._change != 0):   #send signal only when there is change in speed. if you send continously, turning wheels doesnt work!
        if(self._change<0):
          print "Control for decrease"
          for k in range(int(abs(self._change)/0.7)):    
            MESSAGE = '<'
            print MESSAGE
            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))  
          MESSAGE = 'w'
          print MESSAGE
          sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))          
  
        else: 
          print "Control for increase"    
          for k in range(int(abs(self._change)/0.7)):    
            MESSAGE = '>'
            print MESSAGE
            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))  
          MESSAGE = 'w'
          print MESSAGE
          sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


    else:
      #sending on/off when controlling by keyboard
      if self.hold == True:
        MESSAGE = 'h';	#hold
        print MESSAGE								
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        self.hold = False #cos we want to send the signal
      
      if self.resume == True:
        MESSAGE = 'r';	#resume
        print MESSAGE								
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        self.resume = False #cos we want to send the signal



  def end(self):
    self.camera.release()

