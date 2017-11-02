import numpy as np
import cv2
#import mavros_msgs as msgs

import pygame
#import getch

import datetime
start_time = datetime.datetime.now()

import copy
from driver import *
import logging

#from deeprc_callbacks import *

import socket

camera_port = 1   # Change this to your webcam ID, or file name for your video file
ramp_frames = 30  #Number of frames to throw away while the camera adjusts to light levels
#rval = True

UDP_IP = "10.42.0.144"
UDP_PORT = 5009
sock = socket.socket(socket.AF_INET, # Internet
          socket.SOCK_DGRAM) # UDP

class Control:
    speed = 0
    steer = 0


print(cv2.__version__)

class ElektraHuman(Driver):



  # Initializes
  # Do everything needed to start the system.
  def __init__(self,drive_conf,input_method):
    
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
    #self.camera




  # Start the communication process and any necessary threads or other process
  def start(self):

    # Starts the communication with raspy - do it manually now by sshing to pi and running motor.py(below code works, but cos pi has infinite loop, control never returns to execute remaining code)
    '''import subprocess
    print "start"
    subprocess.call("$HOME/chauffeur_akshay_github/drive_interfaces/elektra_interface/connect_pi.sh", shell=True)
    print "end"	 '''

    # Starts communication with the cameras
    self.camera = cv2.VideoCapture(camera_port)
 
    # Ramp the camera - these frames will be discarded and are only used to allow v4l2 to adjust light levels, if necessary
    print("Adjusting brightness...")
    for i in xrange(ramp_frames):
      retval, temp = self.camera.read()
      #print retval
    print "START DRIVING"
    
    
    # Start any background process... etc.

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

    # Joystick command to activate and deactivate record
    if(self._input_method == 'xbox'):
      if( self.joystick.get_button( 2 )):
        self._recording =True
      if( self.joystick.get_button( 1 )):
        self._recording=False

    else:
      keys = pygame.key.get_pressed()
      if keys[pygame.K_r]:
        self._recording =True
      if keys[pygame.K_t]:
        self._recording=False
    
    return self._recording



  def get_reset(self):

    #if( self.joystick.get_button( 8 )):
    # Maybe you need some kind of reset.
    return False


  def get_direction(self):

    return 2.0


  def compute_action(self,sensor,speed):


    self._old_speed = speed
    global start_time

    """ Get Steering """
    if(self._input_method == 'xbox'):
      if self.joystick.get_button( 6 ):  #left
        self.steering_direction = -1
        print "left"
      elif self.joystick.get_button( 7 ): #right
        self.steering_direction = 1
        print "right"
      else:
        self.steering_direction = 0    #when left or right button is not pressed, bring the steering to centre

    else:
      keys = pygame.key.get_pressed()
      if keys[pygame.K_a]:
        self.steering_direction = -1
        #print "left"
      elif keys[pygame.K_d]:
        self.steering_direction = 1
        #print "right"
      else:
        self.steering_direction = 0     #when left or right button is not pressed, bring the steering to centre
        #print "in zero"



    """Get Speed"""
    if(self._input_method == 'xbox'):
      if( self.joystick.get_button(3)):  #increase speed
        print "inc speed"
        end_time = datetime.datetime.now()
        time_diff = (end_time - start_time).microseconds / 1000   #in milliseconds
        if time_diff > 300: #to ensure same click isnt counted multiple times
          self._new_speed = self._old_speed + 0.7   #max speed = 7 kmph, changes in 10 steps
          self._new_speed = min(7, self._new_speed) #restrict between 0-7
          start_time = datetime.datetime.now()   
      if( self.joystick.get_button(0)):  #decrease speed
        print "dec speed"
        end_time = datetime.datetime.now()
        time_diff = (end_time - start_time).microseconds / 1000
        if time_diff > 300:
          self._new_speed = self._old_speed - 0.7
          self._new_speed = max(0, self._new_speed)
          start_time = datetime.datetime.now()

    else:
      #keys = pygame.key.get_pressed()
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

    

    '''#keys = pygame.key.get_pressed()
    if keys[pygame.K_b]:  
      self._rear = True

    #keys = pygame.key.get_pressed()
    if keys[pygame.K_n]: 
      self._rear = False

    if self._rear == True:
      print "Taking Reverse.."'''


    print "new speed:", self._new_speed
    print "direction:", self.steering_direction

    self._change = self._new_speed - self._old_speed

    control = Control()
    control.speed = self._new_speed
    control.steer = self.steering_direction

    return control, self._new_speed



  def get_sensor_data(self):

    # Take the actual image we want to keep
    retval, frame = self.camera.read()  # Captures a single image from the camera in PIL format

    #print retval
    r=frame.shape[0]
    c=frame.shape[1]
    frame = frame[1:r, 1:c/2] #just take the left camera image

    #opencv reads image in BGR format. convert it to RGB before saving
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # get other measurements the car is making

    return frame



  
  def act(self,control):		  # Send the action to the raspy

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
    pygame.quit()
