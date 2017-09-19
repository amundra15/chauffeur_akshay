#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 10 19:12:37 2017

@author: german
"""
from __future__ import print_function
import time
import math

from carla_unreal import CarlaUnreal
from carla_pack_pb2 import  Scene,EpisodeStart,EpisodeReady,Control,Reward

class Runnable(object, ):
    def __init__(self, **kwargs):
        pass
    
    def run_step(self, data):
        pass

    def compute_distance(self, curr, prev, target):
        # no history info
        if(prev[0] == -1 and prev[1] == -1):
            distance = math.sqrt((curr[0] - target[0])*(curr[0] - target[0]) + (curr[1] - target[1])*(curr[1] - target[1]))
        else:
            # distance point to segment
            v1 = [target[0]-curr[0], target[1]-curr[1]]
            v2 = [prev[0]-curr[0], prev[1]-curr[1]]
            
            w1 = v1[0]*v2[0] + v1[1]*v2[1]
            w2 = v2[0]*v2[0] + v2[1]*v2[1]
            t_hat = w1 / (w2 + 1e-4)
            t_start = min(max(t_hat, 0.0), 1.0)
            
            s = [0, 0]
            s[0] = curr[0] + t_start * (prev[0] - curr[0])
            s[1] = curr[1] + t_start * (prev[1] - curr[1])
            distance = math.sqrt((s[0] - target[0])*(s[0] - target[0]) + (s[1] - target[1])*(s[1] - target[1]))

        
        return distance

    def run_until(self, carla, time_out, target):
        

        
        curr_x = -1
        curr_y = -1
        prev_x = -1
        prev_y = -1
        data = carla.getReward()
        t0 = data[0].game_timestamp
        t1=t0
        success = False
        step = 0
        accum_lane_intersect = 0.0
        accum_sidewalk_intersect = 0.0
        distance = 100000
        reward_vec=[]
        while((t1-t0) < (time_out*1000) and not success):
            data = carla.getReward()
            control = self.run_step(data,target)
            carla.sendCommand(control)


            # meassure distance to target
            reward = data[0]
            prev_x = curr_x
            prev_y = curr_y
            curr_x = reward.player_x
            curr_y = reward.player_y


            reward_vec.append(reward)

            t1 = reward.game_timestamp
            print (t1-t0)
            
            # accumulate layout related signal
            # accum_lane_intersect += reward.road_intersect
            #accum_sidewalk_intersect += reward.sidewalk_intersect
            step += 1

            distance = self.compute_distance([curr_x, curr_y], [prev_x, prev_y], target)
            # debug 
            print('[d=%f] c_x = %f, c_y = %f ---> t_x = %f, t_y = %f' % (float(distance), curr_x, curr_y, target[0], target[1]))

            if(distance < 200.0):
                success = True

            # Stop If Game Colides
            #if  reward.collision_gen > 0 or reward.collision_ped >0 or  reward.collision_car >0:
            #    success = False
            #    break


        if(success):
            return (1, reward_vec, float(t1-t0)/1000.0,distance)
        else:
            return (0, reward_vec, time_out,distance)
