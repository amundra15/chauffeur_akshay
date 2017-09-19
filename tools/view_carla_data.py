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

#gta_surface = get_gta_map_surface()


#for 3 cameras
# ***** main loop *****
'''if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Path viewer')
  #parser.add_argument('model', type=str, help='Path to model definition json. Model weights should be on the same path.')
  parser.add_argument('--dataset', type=str, default="2016-06-08--11-46-01", help='Dataset/video clip name')
  args = parser.parse_args()





  dataset = args.dataset
  first_time = True
  count =0
  steering_pred =[]
  steering_gt =[]

  positions_to_test =  range(1,1200)
  #positions_to_test = [93,104,170,173,229,245,283,397,413,425,565,581,591]
  #positions_to_test = range(0,660)
  #positions_to_test = [617,618,619,620,622,623,624,636,637,638,639]
  #positions_to_test =  [637,638]
  #positions_to_test = [55,108,109,353,410,411,426,441,442]
  #positions_to_test = [656,657,675,676,854,855,859,860,861,902]
  path = '../AkshayData3/SeqTrain/'


  screen = ScreenManager()

  image_queue = deque()

  speed_list = []
  actions_queue = deque()

  #for 3 augmented images
  screen.start_screen([200,88],3,4)

  #for 3 augmented images
  images= [np.array([200,88,3]),np.array([200,88,3]),np.array([200,88,3])]
  actions = [Control(),Control(),Control()]


  for h_num in positions_to_test:

    print " SEQUENCE NUMBER ",h_num
    data = h5py.File(path+'data_'+ str(h_num).zfill(5) +'.h5', "r")

    #redata = h5py.File('/media/adas/012B4138528FF294/NewGTA/redata_'+ str(h_num).zfill(5) +'.h5', "r")
    #print log.keys()


    
    #save_data_stats = '../../../Data/Udacity/'

    



    # skip to highway
    for i in range(0,198,12):   #every hdf5 files containg data for 200 images




      #img = cam['X'][log['cam1_ptr'][i]].swapaxes(0,2).swapaxes(0,1)

      img_1 = np.array(data['images_center'][i]).astype(np.uint8)


      img_2 = np.array(data['images_center'][i+1]).astype(np.uint8)


      img_3 = np.array(data['images_center'][i+2]).astype(np.uint8)


      images[int(data['targets'][i][26])] =  img_1
      images[int(data['targets'][i+1][26])] =  img_2
      images[int(data['targets'][i+2][26])] =  img_3

      action_1 = Control()
      action_1.steer = data['targets'][i][0]
      action_1.gas =data['targets'][i][1]
      action_2 = Control()
      action_2.steer = data['targets'][i+1][0]
      action_2.gas =data['targets'][i+1][1]
      action_3 = Control()
      action_3.steer = data['targets'][i+2][0]
      action_3.gas =data['targets'][i+2][1]
      #print  data['targets'][i][20]
      actions[int(data['targets'][i][26])] =action_1
      actions[int(data['targets'][i+1][26])] =action_2
      actions[int(data['targets'][i+2][26])] =action_3

      direction = data['targets'][i+2][22]

      speed = data['targets'][i+2][10]
      time_use =  1.0
      car_lenght = 6
      actions[0].steer +=min(4*(math.atan((0.26*car_lenght)/(time_use*speed+0.05)))/3.1415,0.2)
      actions[2].steer -=min(4*(math.atan((0.26*car_lenght)/(time_use*speed+0.05)))/3.1415,0.2)
      print " Steer Left MIDDLE Right "
      print actions[0].steer
      print actions[1].steer
      print actions[2].steer


      #for j in range(3):
      #  screen.plot3camrc( 0,images[j],\
      #        actions[j],direction,0,\
      #        [0,0],j) #

      time.sleep(0.0)

      speed_list.append((actions[1].steer))
      #reimg = np.array(redata['images_center'][i])
      #recontrol_input = np.array(redata['control'][i][1])
      #print img
      #img = img*255
      #print img

  plt.plot(range(0,len(speed_list)),speed_list)
  
  plt.show()
  #save_gta_surface(gta_surface)'''



if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Path viewer')
  #parser.add_argument('model', type=str, help='Path to model definition json. Model weights should be on the same path.')
  parser.add_argument('--dataset', type=str, default="AkshayData3_video", help='Dataset/video clip name')
  args = parser.parse_args()





  dataset = args.dataset
  first_time = True
  count =0
  steering_pred =[]
  steering_gt =[]

  positions_to_test =  range(1,141) #total hdf5 files
  #positions_to_test = [93,104,170,173,229,245,283,397,413,425,565,581,591]
  #positions_to_test = range(0,660)
  #positions_to_test = [617,618,619,620,622,623,624,636,637,638,639]
  #positions_to_test =  [637,638]
  #positions_to_test = [55,108,109,353,410,411,426,441,442]
  #positions_to_test = [656,657,675,676,854,855,859,860,861,902]
  path = '../AkshayData3/SeqTrain/'


  screen = ScreenManager()

  image_queue = deque()

  speed_list = []

  actions_queue = deque()

  '''#for 3 augmented images
  screen.start_screen([200,88],3,4)'''
  screen.start_screen([200,88],1,4)

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
    for i in range(0,198,12):   #every hdf5 files containg data for 200 images


      #img = cam['X'][log['cam1_ptr'][i]].swapaxes(0,2).swapaxes(0,1)


      images =  np.array(data['images_center'][i]).astype(np.uint8)

      actions.steer = data['targets'][i][0]
      actions.gas = data['targets'][i][1]


      speed = data['targets'][i][10]

      #plot on screen
      screen.plot3camrc(0,images,actions,speed,[0,0],0) 

      #print '***in view_carla_data****'

      
      time.sleep(0.5) #to slow video down

      speed_list.append((actions.steer))
      #speed_list.append(speed)

      #reimg = np.array(redata['images_center'][i])
      #recontrol_input = np.array(redata['control'][i][1])
      #print img
      #img = img*255
      #print img

  plt.plot(range(0,len(speed_list)),speed_list)
  
  plt.show()
  #save_gta_surface(gta_surface)

