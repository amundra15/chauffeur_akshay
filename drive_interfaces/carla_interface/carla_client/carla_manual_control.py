
from __future__ import print_function
from carla_unreal import CarlaUnreal


#from scene_parameters import SceneParams
from configcarla import *
from PIL import Image
import numpy as np

import random
import time
import sys
import argparse
import logging
from socket import error as socket_error
sys.path.append('protoc')

from carla_pack_pb2 import  Scene,EpisodeStart,EpisodeReady,Control,Reward

import pygame
from pygame.locals import *


class App:
    def __init__(self, port=2000, host='vcl-gpu1', config='./CarlaSettings.ini', resolution=(800,600), plot_depths=False,verbose=True):
        self._running = True
        self._display_surf = None
        self.port = port
        self.host = host
        self.config = config
        self.verbose = verbose
        self.resolution = resolution
        self.size = self.weight, self.height = resolution
        self.plot_depths = plot_depths

 
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        logging.debug('Started the PyGame Library')
        self._running = True
        self.step = 0
        self.prev_step = 0
        self.prev_time = time.time()
        


        #print (config.port)
        self.carla =CarlaUnreal(self.host, self.port, self.config, *self.resolution)
        self.carla.startAgent()
	self.carla.requestNewEpisode()
        scene,positions = self.carla.receiveSceneConfiguration()
        self.num_pos = len(positions)
        print ("NUM POS ",self.num_pos)
        self.carla.newEpisode(np.random.randint(self.num_pos),np.random.randint(self.num_pos))
        self.prev_restart_time = time.time()
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
    def on_loop(self):
        self.step += 1
        keys=pygame.key.get_pressed()
        gas = 0
        steer = 0
        restart = False
        pressed_keys = []
        if keys[K_LEFT]:
            steer = -1.
            pressed_keys.append('left')
        if keys[K_RIGHT]:
            pressed_keys.append('right')
            steer = 1.
        if keys[K_UP]:
            pressed_keys.append('up')
            gas = 1.
        if keys[K_DOWN]:
            pressed_keys.append('down')
            gas = -1.
        if keys[K_r]:
            pressed_keys.append('r')
            if time.time() - self.prev_restart_time > 2.:
                self.prev_restart_time = time.time()
                restart = True
        if time.time() - self.prev_restart_time < 2.:
            gas = 0.
            steer = 0.

	control = Control()
	control.gas = gas
	control.steer = steer
        self.carla.sendCommand(control)
        data = self.carla.getReward()
        pack = data[0]
        self.img_vec = data[2]
        #self.depth_vec = data[2]


        print (len(self.img_vec))
        #print pack.depth1

        
        if time.time() - self.prev_time > 1.:
            print('Step', self.step, 'FPS', float(self.step - self.prev_step) / (time.time() - self.prev_time))

            print('speed', pack.speed, 'collision', pack.collision_gen, 'collision_car', pack.collision_car, 'colision_ped', pack.collision_ped, 'pressed:', pressed_keys)
            self.prev_step = self.step
            self.prev_time = time.time()
            
        if restart:
            print('\n *** RESTART *** \n')
            self.carla.requestNewEpisode()
            scene,positions = self.carla.receiveSceneConfiguration()

            self.num_pos = len(positions)
            player_pos = np.random.randint(self.num_pos)
            goal_pos = np.random.randint(self.num_pos)

            print('  Player pos %d, goal pos %d\n' % (player_pos, goal_pos))
            self.carla.newEpisode(player_pos, goal_pos)
        
        
    def on_render(self):

        pos_x =0

        for i in range(len(self.img_vec)):
            surface = pygame.surfarray.make_surface(np.transpose(self.img_vec[i], (1,0,2)))
            self._display_surf.blit(surface,(pos_x,0))
            pos_x += self.img_vec[i].shape[1]

        pos_x =0

        if len(self.img_vec)> 0:
            pos_y =self.img_vec[0].shape[0]


        if self.plot_depths:
            for i in range(len(self.depth_vec)):
                surface = pygame.surfarray.make_surface(np.transpose(self.depth_vec[i], (1,0,2)))
                self._display_surf.blit(surface,(pos_x,pos_y))
                pos_x += self.depth_vec[i].shape[1]          
            
        pygame.display.flip()

        
    def on_cleanup(self):
        self.carla.close_conections()
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            #try:

            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()

            #except Exception:
                #   self._running = False
                #break


        self.on_cleanup()
            
                

        
 
if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description='Run multiple servers on multiple GPUs')
    parser.add_argument('host', metavar='HOST', type=str, help='host to connect to')
    parser.add_argument('port', metavar='PORT', type=int, help='port to connect to')
	

    parser.add_argument("-c", "--config", help="the path for the server config file that the client sends",type=str,default="./CarlaSettings.ini") 

    parser.add_argument("-pd", "--plot_depths", help="activate the log file",action="store_true")


    parser.add_argument("-l", "--log", help="activate the log file",action="store_true") 
    parser.add_argument("-lv", "--log_verbose", help="put the log file to screen",action="store_true") 
    args = parser.parse_args()

    print(args)

    if args.log or args.log_verbose:
        LOG_FILENAME = 'log_manual_control.log'
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
        if args.log_verbose:  # set of functions to put the logging to screen


            root = logging.getLogger()
            root.setLevel(logging.DEBUG)
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            root.addHandler(ch)
        


    theApp = App(port=args.port, host=args.host, config=args.config)
    theApp.on_execute()
    
    
    
    
