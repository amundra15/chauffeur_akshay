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

  positions_to_test = range(1,61) #total hdf5 files

  path = '../Desktop/27_Carla_Human__8/'


  screen = ScreenManager()

  image_queue = deque()

  speed_list = []
  steer_list = []
  noisy_steer_list = []

  actions_queue = deque()

  screen.start_screen([200,88],1,2) 


  images= np.array([200,88,3])
  actions = Control()
  

  for h_num in positions_to_test:



    print " SEQUENCE NUMBER ",h_num

    '''if h_num == 50:
      continue'''

    data = h5py.File(path+'data_'+ str(h_num).zfill(5) +'.h5', "r")


    # skip to highway
    for i in range(0,200,25):   #every hdf5 files containg data for 200 images


      images =  np.array(data['rgb'][i]).astype(np.uint8)

      camera_angle = data['targets'][i][26]
      actions.steer = data['targets'][i][0]
      actions.gas = data['targets'][i][1]
      noisy_steer = data['targets'][i][5] 
      speed = data['targets'][i][10]
      continous_steer = actions.steer
      human_intervention = data['targets'][i][27]


      #augment images from multiple cameras 
      time_use =  1.0
      car_lenght = 6.0
      extra_factor = 4.0
      threshold = 0.3
      if camera_angle > 0.0:
        camera_angle = math.radians(math.fabs(camera_angle))
        actions.steer -=min(extra_factor*(math.atan((camera_angle*car_lenght)/(time_use*speed+0.05)))/3.1415,0.6)
      else:
        camera_angle = math.radians(math.fabs(camera_angle))
        actions.steer +=min(extra_factor*(math.atan((camera_angle*car_lenght)/(time_use*speed+0.05)))/3.1415,0.6)

      if actions.steer > threshold:
        actions.steer = 1
      elif actions.steer < -threshold:
        actions.steer = -1
      else:
        actions.steer  =0



      #plot on screen
      screen.plot3camrc(0,images,actions,speed,[0,0],0,continous_steer, human_intervention) 

      
      time.sleep(0.1) #to slow video down


      steer_list.append((actions.steer))
      noisy_steer_list.append((noisy_steer))
      #speed_list.append(speed)


  plt.plot(range(0,len(noisy_steer_list)),noisy_steer_list)
  plt.plot(range(0,len(steer_list)),steer_list,'r')
  
  plt.show()
