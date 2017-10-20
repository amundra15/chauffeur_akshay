
import numpy as np
import cv2

import scipy


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

ramp_frames = 15  #Number of frames to throw away while the camera adjusts to light levels

UDP_IP = "10.42.0.144"
UDP_PORT = 5007
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

  def __init__(self,gpu_number,experiment_name,drive_conf,memory_fraction=0.95):

    Driver.__init__(self)
    self._augment_left_right = drive_conf.augment_left_right
 
    self._augmentation_camera_angles = drive_conf.camera_angle 

    self._recording= False    
    self._rear = False
    self.steering_direction = 0
    self._new_speed = 0


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
    pass



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
    image_input = np.multiply(image_input, 1.0 / 127.0)


    #steer,acc,brake = self._control_function(image_input,speed,direction,self._config,self._sess,self._train_manager)
    steer,_new_speed = machine_output_functions.single_branch(image_input,self._config,self._sess,self._train_manager)



    control = Control()
    control.speed = _new_speed
    control.steer = steer

    if self._augment_left_right: # If augment data, we generate copies of steering for left and right
      control_left = copy.deepcopy(control)

      control_left.steer = self._adjust_steering(control_left.steer,self._augmentation_camera_angles,speed) # The angles are inverse.
      control_right = copy.deepcopy(control)

      control_right.steer = self._adjust_steering(control_right.steer,-self._augmentation_camera_angles,speed)

      return [control,control,control]

    else:
      return control, _new_speed


  def get_sensor_data(self):
    # Get the camera image
    camera = cv2.VideoCapture(camera_port)
 
    # Ramp the camera - these frames will be discarded and are only used to allow v4l2 to adjust light levels, if necessary
    for i in xrange(ramp_frames):
      retval, temp = camera.read()
    print("Taking image...")

    # Take the actual image we want to keep
    retval, frame = camera.read()  # Captures a single image from the camera in PIL format

    #print retval
    r=frame.shape[0]
    c=frame.shape[1]
    frame = frame[1:r, 1:c/2] #just take the left camera image

    '''file = "./test_image15.png"
    cv2.imwrite(file, frame)'''

    '''cv2.imshow('image',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()'''
 
    del(camera)  # You'll want to release the camera, otherwise you won't be able to create a new capture object until your script exits



    # get all the measurements the car is making

    return frame


  
  def act(self,action):
    #sending direction to pi
    if self.steering_direction == 0:
        MESSAGE = 'x';  
        print MESSAGE               
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    elif self.steering_direction == 1:
        MESSAGE = 'd';  
        print MESSAGE               
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    elif self.steering_direction == -1:
        MESSAGE = 'a';  
        print MESSAGE               
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    
    #sending the speed
    #you may have to define self._new_speed and self._old_speed in class definition
    change= int((self._new_speed-self._old_speed)/0.7)
  
    if(change<0):
      print "Control for decrease"
      for k in range(abs(change)):    
        MESSAGE = '<'
        print MESSAGE
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))  
      MESSAGE = 'w'
      print MESSAGE
      sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))          
  
    else: 
      print "Control for increase"    
      for k in range(abs(change)):    
        MESSAGE = '>'
        print MESSAGE
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))  
      MESSAGE = 'w'
      print MESSAGE
      sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))



  '''def compute_perception_activations(self,sensor,speed):




    sensor = sensor[self._image_cut[0]:self._image_cut[1],:,:]

    sensor = scipy.misc.imresize(sensor,[self._config.network_input_size[0],self._config.network_input_size[1]])

    image_input = sensor.astype(np.float32)

    #print future_image

    image_input = image_input - self._mean_image
    #print "2"
    image_input = np.multiply(image_input, 1.0 / 127.0)


    vbp_image =  machine_output_functions.vbp(image_input,speed,self._config,self._sess,self._train_manager)

    #min_max_scaler = preprocessing.MinMaxScaler()
    #vbp_image = min_max_scaler.fit_transform(np.squeeze(vbp_image))

    #print vbp_image.shape
    return 0.5*grayscale_colormap(np.squeeze(vbp_image),'jet') + 0.5*image_input'''
