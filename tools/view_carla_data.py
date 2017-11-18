#!/usr/bin/env python
import sys

sys.path.append('utils')
sys.path.append('configuration')


import argparse
import numpy as np
import h5py
import pygame
#import readchar
#import json
#from keras.models import

from PIL import Image
import matplotlib.pyplot as plt

import math
from drawing_tools import *
import time
import scipy
import os
import scipy
from collections import deque
from skimage.transform import resize


sys.path.append('drive_interfaces')

from screen_manager import ScreenManager

class Control:
    steer = 0
    gas =0
    brake =0
    hand_brake = 0
    reverse = 0


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Path viewer')
  #parser.add_argument('model', type=str, help='Path to model definition json. Model weights should be on the same path.')
  parser.add_argument('--dataset', type=str, default="ElektraData1_video", help='Dataset/video clip name')
  args = parser.parse_args()





  dataset = args.dataset
  first_time = True
  count =0
  steering_pred =[]
  steering_gt =[]

  positions_to_test = range(38) #total hdf5 files

  path = '../Desktop/2_Akshay_6/'


  screen = ScreenManager()

  image_queue = deque()

  speed_list = []
  steer_list = []
  noisy_steer_list = []

  actions_queue = deque()

  '''#for 3 augmented images
  screen.start_screen([200,88],3,4)'''
  screen.start_screen([200,88],1,2) 

  '''#for 3 augmented images
  images= [np.array([200,88,3]),np.array([200,88,3]),np.array([200,88,3])]
  actions = [Control(),Control(),Control()]'''

  images= np.array([200,88,3])
  actions = Control()
  

  for h_num in positions_to_test:

    print " SEQUENCE NUMBER ",h_num
    data = h5py.File(path+'data_'+ str(h_num).zfill(5) +'.h5', "r")

    #redata = h5py.File('/media/adas/012B4138528FF294/NewGTA/redata_'+ str(h_num).zfill(5) +'.h5', "r")
    #print log.keys()
    

    # skip to highway
    for i in range(0,200,25):   #every hdf5 files containg data for 200 images


      #img = cam['X'][log['cam1_ptr'][i]].swapaxes(0,2).swapaxes(0,1)


      images =  np.array(data['rgb'][i]).astype(np.uint8)

      actions.steer = data['targets'][i][0]
      actions.gas = data['targets'][i][1]
      noisy_steer = data['targets'][i][5]

      '''camera_angle = data['targets'][i][26]
      car_angle = actions.steer * 20   #car_angle is steer angle wrt road in degrees. 20 is max possible steer in degrees
      effective_angle = 4*camera_angle + car_angle
      
      print 'steer angle: ',actions.steer
      print 'car_angle: ', car_angle
      print 'camera angle: ', camera_angle
      print 'effective angle: ', effective_angle'''
      

      '''if (effective_angle >= -7.5 and effective_angle <= 7.5):  #since cameras are at -15,0 and 15, central position would correspond to this
        actions.steer = 0
      elif effective_angle > 7.5:
        actions.steer = -1.0
      else:
        actions.steer = 1.0'''

      '''if actions.steer < 0.05 and actions.steer > -0.05:  #standard
        if camera_angle < 0:
          actions.steer = 1
        elif camera_angle > 0:
          actions.steer = -1
          ########
      elif actions.steer < 0.3 and actions.steer >= 0.05:
        if camera_angle == -15:
          actions.steer = 0
        elif camera_angle < -15:
          actions.steer = 1
        else:
          actions.steer = -1
      elif actions.steer < 0.6 and actions.steer >= 0.3:
        if camera_angle == -45:
          actions.steer = 0
        else:
          actions.steer = 1
      elif actions.steer >= 0.6:
          actions.steer = 1
          #######
      elif actions.steer > -0.3 and actions.steer <= -0.05:
        if camera_angle == 15:
          actions.steer = 0
        elif camera_angle < 15:
          actions.steer = 1
        else:
          actions.steer = -1
      elif actions.steer > -0.6 and actions.steer <= -0.3:
        if camera_angle == 45:
          actions.steer = 0
        else:
          actions.steer = 1
      elif actions.steer <= -0.6:
          actions.steer = -1

      print 'steer on screen', actions.steer
      print '****************************'''


      speed = data['targets'][i][10]

      #plot on screen
      screen.plot3camrc(0,images,actions,speed,[0,0],0) 

      #print '***in view_carla_data****'

      
      time.sleep(0.3) #to slow video down

      steer_list.append((actions.steer))
      noisy_steer_list.append((noisy_steer))
      #speed_list.append(speed)

      #reimg = np.array(redata['images_center'][i])
      #recontrol_input = np.array(redata['control'][i][1])
      #print img
      #img = img*255
      #print img

  plt.plot(range(0,len(steer_list)),steer_list,'r')
  plt.plot(range(0,len(noisy_steer_list)),noisy_steer_list)
  
  plt.show()
  #save_gta_surface(gta_surface)

