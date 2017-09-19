from __future__ import print_function

import pygame
from pygame.locals import *

from carlau3d import CarlaU3D
from reward_pack import RewardPack
from configcarla import configCarla

import time 
import numpy as np
import argparse

class App:
    def __init__(self, port=2000, host='vcl-gpu1'):
        self._running = True
        self._display_surf = None
        self.port = port
        self.host = host
        self.size = self.weight, self.height = 720,512
 
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.step = 0
        self.prev_step = 0
        self.prev_time = time.time()
        
        
 
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
        self.carla.control_agent(gas,steer)
        pack = self.carla.get_data()
        self.img = pack.image
        #print(dir(pack))
        
        if time.time() - self.prev_time > 1.:
            print('Step', self.step, 'FPS', float(self.step - self.prev_step) / (time.time() - self.prev_time))
            #print(dir(pack))
            print('speed', pack.speed, 'collision', pack.collision, 'collision_car', pack.collision_car, 'colision_ped', pack.collision_ped, 'pressed:', pressed_keys)
            self.prev_step = self.step
            self.prev_time = time.time()
            
        if restart:
            print('\n *** RESTART *** \n')
            player_pos = np.random.randint(self.num_pos)
            goal_pos = np.random.randint(self.num_pos)
            print('  Player pos %d, goal pos %d\n' % (player_pos, goal_pos))
            self.carla.start_new_episode(player_pos, goal_pos)
        
        
    def on_render(self):
        surface = pygame.surfarray.make_surface(np.transpose(self.img, (1,0,2)))
        self._display_surf.blit(surface,(0,0))
        pygame.display.flip()
    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
 
if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description='Run multiple servers on multiple GPUs')
    parser.add_argument('host', metavar='HOST', type=str, help='host to connect to')
    parser.add_argument('port', metavar='PORT', type=int, help='port to connect to')
    args = parser.parse_args()
    
    config =configCarla()
    config.host = args.host
    config.port = args.port
    carla =CarlaU3D(config)
    print ("STARTED U3D")
    carla.connect()
    print ("CONECTED WORLD")
    modes,scenes= carla.receive_scene_conf()
    print (" RECEIVED SCENE CONF")
    carla.select_scene_conf(modes[0],scenes[0])
    print ("SELECTED SCENE")
    possible_positions = carla.receive_episode_conf()
    print ("RECEIVED POSIBLE POSITIONS")
    print(possible_positions)
    num_pos = len(possible_positions)
    carla.connect_agent()
    carla.start_new_episode(13,47)
    carla.control_agent(-1.,0.)
    time.sleep(3.)
    carla.start_new_episode(13,47)
    carla.control_agent(-1.,0.)
    time.sleep(3.)
    gas =   [-1., 0., 1.,  0.,  0., 0., 0.]
    steer = [0.,  0., 0.,  1., -1., 0., 0.]
    for step in range(50):
        pack = carla.get_data()
        print(step, 'speed', pack.speed, 'pos', pack.player_position, 'ori', pack.ori_x, pack.ori_y, pack.ori_z)
        carla.control_agent(gas[step/10],steer[step/10])
    
    
    
