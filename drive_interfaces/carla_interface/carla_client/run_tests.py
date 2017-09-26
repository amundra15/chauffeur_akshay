from __future__ import print_function


import pdb
#from scene_parameters import SceneParams

from PIL import Image
import numpy as np
import json, csv

import random
import time
import sys
import argparse
import logging
from socket import error as socket_error
sys.path.append('protoc')


sys.path.append('drive_interfaces')
sys.path.append('drive_interfaces/carla_interface')
sys.path.append('drive_interfaces/carla_interface/carla_client')

sys.path.append('drive_interfaces/carla_interface/carla_client/protoc')
sys.path.append('test_interfaces')
sys.path.append('utils')
sys.path.append('dataset_manipulation')
sys.path.append('configuration')
sys.path.append('input')
sys.path.append('train')
sys.path.append('utils')
sys.path.append('input/spliter')
sys.path.append('structures')


from carla_pack_pb2 import  Scene,EpisodeStart,EpisodeReady,Control,Reward
from Manual import *
from carla_unreal import CarlaUnreal

def generate_camera_str(dic):
    camera_str = '''
[CARLA/SceneCapture/%s]
PostProcessing=%s
ImageSizeX=%d
ImageSizeY=%d
CameraFOV=%d
CameraPositionX=%d
CameraPositionY=%d
CameraPositionZ=%d
CameraRotationPitch=%d
CameraRotationRoll=%d
CameraRotationYaw=%d''' % (dic['NAME'], dic['TYPE'], dic['ImageSizeX'], dic['ImageSizeY'], 
    dic['CameraFOV'], dic['CameraPositionX'], dic['CameraPositionY'],
    dic['CameraPositionZ'], dic['CameraRotationPitch'], 
    dic['CameraRotationRoll'], dic['CameraRotationYaw'])
    
    return (dic['NAME'], camera_str)

    
def generate_conffile_from_dict(opt_dict):
    str_preamble = '''
[CARLA/Server]
UseNetworking=true
WorldPort=2000
WritePort=2001
ReadPort=2002'''

    str_level = '''
[CARLA/LevelSettings]
NumberOfVehicles=%d
NumberOfPedestrians=%d
WeatherId=%d''' % (opt_dict['VEHICLES'], opt_dict['PEDESTRIANS'], opt_dict['WEATHER'])
                
                
    str_camera_pre = '''
[CARLA/SceneCapture]
Cameras='''
              
    str_camera_pos = ''
    N = len(opt_dict['CAMERAS'])
    for c in range(N):
        (camera_name, str_camera) = generate_camera_str(opt_dict['CAMERAS'][c])
        str_camera_pos += ('\n' + str_camera)
        
        str_camera_pre += camera_name
        if(c+1 != N):
            str_camera_pre += ','
           
    str_cameras = str_camera_pre + '\n' + str_camera_pos
    str_conf = str_preamble + '\n\n' + str_level + '\n\n' + str_cameras + '\n'
    
    with open(opt_dict['EXP_NAME'], "w") as text_file:
        text_file.write(str_conf)
    

def load_carla_0_parameters():


    # experiment testing conditions
    weathers = [ 1, # clearNoon
                 3, # wetNoon
                 6, # HardRainNoon
                 8, # ClearSunset
            ]
    
    repetitions_per_experiment = [1, 1, 1, 1]
    
    poses_exp1 = [[38, 34],  [4, 2], [12, 10], [62, 82], [42, 50],\
              [66, 64], [78, 76],[57,59],[61,66],[35,39],\
              [12,8],[0,18],[70,72],[54,47],[47,43],\
              [42,46],[46,53],[80,74],[65,63],[81,29],\
              [83,73],[42,53],[16,19],[17,26],[68,77]]
    pedestrians_exp1 = [ 0] * len(poses_exp1)
    
    vehicles_exp1 = [ 0] * len(poses_exp1)
    
    poses_exp2 = [[37, 77], [8, 24], [62, 20], [38, 10], [21, 1],\
               [58,83],[74,67],[53,80],[73,44],[21,73],\
               [32,10],[12,28],[67,22],[80,2],[3,11],\
               [78,58],[50,81],[65,51],[81,50],[42,69] ,\
               [40,64],[59,77],[68,47],[54,40],[12,26]]
    pedestrians_exp2 = [ 0] * len(poses_exp2)
    
    vehicles_exp2 = [ 0] * len(poses_exp2)
    

    poses_exp3 = [[19,66],[79,14],[19,57],[23,1],\
                  [53,76],[42,13],[31,71],[33,5],\
                  [54,30],[10,61],[66,3],[27,12],\
                  [79,19],[2,29],[16,14],[5,57],\
                  [70,73],[46,67],[57,50],[61,49],[21,12],\
                  [51,81],[77,68],[56,65],[43,54], \
                  [29,76],[49,63],[48,61],[40,75],[25,58],\
                  [24,64],[19,50],[27,42],[81,51],[68,77],\
                  [65,56],[54,43],[76,29],[63,49],[61,48],\
                  [75,40],[58,25],[6,69],[69,6],[60,31],\
                  [31,60],[0,5],[5,0],[82,80],[80,82]]
    pedestrians_exp3 = [ 0] * len(poses_exp3)
    vehicles_exp3 = [ 0] * len(poses_exp3)
   
    poses_exp4 = [[19,66],[79,14],[19,57],[23,1],\
                  [53,76],[42,13],[31,71],[33,5],\
                  [54,30],[10,61],[66,3],[27,12],\
                  [79,19],[2,29],[16,14],[5,57],\
                  [70,73],[46,67],[57,50],[61,49],[21,12],\
                  [51,81],[77,68],[56,65],[43,54],\
                  [29,76],[49,63],[48,61],[40,75],[25,58],\
                  [24,64],[19,50],[27,42],[81,51],[68,77],\
                  [65,56],[54,43],[76,29],[63,49],[61,48],\
                  [75,40],[58,25],[6,69],[69,6],[60,31],\
                  [31,60],[0,5],[5,0],[82,80],[80,82]]


    pedestrians_exp4 = [ 50] * len(poses_exp4)
    vehicles_exp4 = [ 15] * len(poses_exp4)
    
    
    start_goal_poses = [poses_exp1, poses_exp2, poses_exp3, poses_exp4]
    pedestrians = [pedestrians_exp1, pedestrians_exp2, pedestrians_exp3, pedestrians_exp4]
    vehicles = [vehicles_exp1, vehicles_exp2, vehicles_exp3, vehicles_exp4]

    return start_goal_poses,pedestrians,vehicles,weathers, repetitions_per_experiment



def load_carla_1_parameters():

    # experiment testing conditions
    weathers = [ 1, # clearNoon
                 3, # wetNoon
                 6, # HardRainNoon
                 8, # ClearSunset
                 # Non Seen in training conditions
                 2, # Cloudy Noon
                 14 # Soft Rain Sunset
            ]
    
    repetitions_per_experiment = [1, 1, 1, 1]
    
    poses_exp1 = [[36,40],[39,35],[110,114],[7,3],[0,4],\
                [68,50],[61,59],[47,64],[147,90],[33,87],\
                [26,19],[80,76],[45,49],[55,44],[29,107],\
                [95,104],[34,84],[51,67],[22,17],[91,148],\
                [20,107],[78,70],[95,102],[68,44],[45,69]]

    pedestrians_exp1 = [ 0] * len(poses_exp1)
    
    vehicles_exp1 = [ 0] * len(poses_exp1)
    
    poses_exp2 = [[138,17],[46,16],[26,9],[42,49],[140,26],\
                [85,97],[65,133],[137,51],[76,66],[46,39],\
                [40,60],[1,28],[4,129],[121,107],[2,129],\
                [78,44],[68,85],[41,102],[95,70],[68,129],\
                [84,69],[47,79],[110,15],[130,17],[0,17]]
    pedestrians_exp2 = [ 0] * len(poses_exp2)
    
    vehicles_exp2 = [ 0] * len(poses_exp2)

    poses_exp3 = [[105,29],[27,130],[102,87],[132,27],[24,44],\
               [96,26],[34,67],[28,1],[140,134],[105,9],\
               [148,129],[65,18],[21,16],[147,97],[42,51],\
               [30,41],[18,107],[69,45],[102,95],[18,145],\
               [111,64],[79,45],[84,69],[73,31],[37,81],\
               [42,1],[1,42],[32,37],[100,137],[104,7],\
               [1,42],[37,32],[137,100],[7,104],[34,70],\
               [65,143],[64,97],[97,64],[121,85],[85,121],\
               [137,104],[104,137],[72,95],[95,72],[39,65],\
               [65,39],[96,142],[142,96],[7,115],[115,7]]

    pedestrians_exp3 = [ 0] * len(poses_exp3)
    vehicles_exp3 = [ 0] * len(poses_exp3)
    
    poses_exp4 = [[105,29],[27,130],[102,87],[132,27],[24,44],\
               [96,26],[34,67],[28,1],[140,134],[105,9],\
               [148,129],[65,18],[21,16],[147,97],[42,51],\
               [30,41],[18,107],[69,45],[102,95],[18,145],\
               [111,64],[79,45],[84,69],[73,31],[37,81],\
               [42,1],[1,42],[32,37],[100,137],[104,7],\
               [1,42],[37,32],[137,100],[7,104],[34,70],\
               [65,143],[64,97],[97,64],[121,85],[85,121],\
               [137,104],[104,137],[72,95],[95,72],[39,65],\
               [65,39],[96,142],[142,96],[7,115],[115,7]]


    pedestrians_exp4 = [ 100] * len(poses_exp4)
    vehicles_exp4 = [ 40] * len(poses_exp4)
    
    
    start_goal_poses = [poses_exp1, poses_exp2, poses_exp3, poses_exp4]
    pedestrians = [pedestrians_exp1, pedestrians_exp2, pedestrians_exp3, pedestrians_exp4]
    vehicles = [vehicles_exp1, vehicles_exp2, vehicles_exp3, vehicles_exp4]

    return start_goal_poses,pedestrians,vehicles,weathers, repetitions_per_experiment




def run_experiment(opt_dict):
    carla = opt_dict['CARLA']
    width  = opt_dict['WIDTH']
    height = opt_dict['HEIGHT']
    host = opt_dict['HOST']
    port = opt_dict['PORT']
    
    output_summary = opt_dict['OUTPUT_SUMMARY']
    runnable = opt_dict['RUNNABLE']
    time_out = opt_dict['TIMEOUT']
    experiments_to_run = opt_dict['EXPERIMENTS_TO_RUN']
    pedestrians = opt_dict['PEDESTRIANS']
    vehicles = opt_dict['VEHICLES']
    repetitions_per_experiment = opt_dict['REPETITIONS']
    weathers = opt_dict['WEATHERS']
    start_goal_poses = opt_dict['START_GOAL_POSES']
    cameras = opt_dict['CAMERAS']
    
    list_stats = []
    dict_stats = {'exp_id':-1,
                  'rep':-1,
                  'weather':-1,
                  'start_point':-1,
                  'end_point':-1,
                  'result':-1,
                  'initial_distance':-1,
                  'final_distance':-1,
                  'final_time':-1,
                  'completed_turns':-1,
                  'turns_made':-1,

                 }

    dict_rewards = {

                  'collision_gen':-1,
                  'collision_ped':-1,
                  'collision_car':-1,
                  'lane_intersect':-1,
                  'sidewalk_intersect':-1,
                  'pos_x':-1,
                  'pos_y':-1
    }





    with open(output_summary, 'wb') as ofd:

        with open('rewards_file_'+output_summary,'wb' ) as rfd:

            w = csv.DictWriter(ofd, dict_stats.keys())
            w.writeheader()
            rw = csv.DictWriter(rfd, dict_rewards.keys())
            rw.writeheader()


            for experiment_id in experiments_to_run:
                poses_exp = start_goal_poses[experiment_id]
                repetitions = repetitions_per_experiment[experiment_id]
                pedestrians_exp = pedestrians[experiment_id]
                vehicles_exp = vehicles[experiment_id]
            
                # several repetitions
                for rep in range(repetitions):
                    # for the different weathers
                    for weather_cond in weathers:
                        # let's go through all the starting-goal positions of the experiment

                        for i in range(len(poses_exp)):
                            trajectory = poses_exp[i]
                            ped = pedestrians_exp[i]
                            vehic = vehicles_exp[i]
                            start_point = trajectory[0]
                            end_point = trajectory[1]
        
                            # generate conf file for these conditions
                            exp_name = "expID_%d_rep_%d_weatherCond_%d__startPoint_%d__endPoint_%d" % (experiment_id, 
                                        rep, weather_cond, start_point, end_point)
                            file_exp_name = '.' + exp_name + '.txt'
                            settings = {'EXP_NAME':file_exp_name, 'CAMERAS':cameras, 
                                        'WEATHER':weather_cond, 'PEDESTRIANS':ped, 'VEHICLES':vehic}
                            generate_conffile_from_dict(settings)
                            
                            if(carla == None):
                                carla = CarlaUnreal(host, port, file_exp_name, width, height)
                                carla.startAgent()
                            else:
                                carla.setIniFile(file_exp_name)
        
                            carla.requestNewEpisode()
                            scene, positions = carla.receiveSceneConfiguration()
                            carla.newEpisode(start_point, end_point)


                            # running the agent
                            print('======== !!!! ==========')
                            (result, reward_vec,distance_ini, final_time,distance,completed_turns,turns_made) = runnable.run_until(carla, time_out[experiment_id], positions[end_point])
                            
                            # compute stats for the experiment
                            dict_stats['exp_id'] = experiment_id
                            dict_stats['rep'] = rep
                            dict_stats['weather'] = weather_cond
                            dict_stats['start_point'] = start_point
                            dict_stats['end_point'] = end_point
                            dict_stats['result'] = result
                            dict_stats['initial_distance'] = distance_ini
                            dict_stats['final_distance'] = distance
                            dict_stats['final_time'] = final_time
                            dict_stats['completed_turns'] = completed_turns
                            dict_stats['turns_made'] = turns_made

                            for i in range(len(reward_vec)):
                                dict_rewards['collision_gen'] = reward_vec[i].collision_gen
                                dict_rewards['collision_ped'] = reward_vec[i].collision_ped
                                dict_rewards['collision_car'] = reward_vec[i].collision_car
                                dict_rewards['lane_intersect'] = reward_vec[i].road_intersect
                                dict_rewards['sidewalk_intersect'] = reward_vec[i].sidewalk_intersect
                                dict_rewards['pos_x'] = reward_vec[i].player_x
                                dict_rewards['pos_y'] = reward_vec[i].player_y


                                rw.writerow(dict_rewards)


                                          


                            # save results of the experiment
                            list_stats.append(dict_stats)
                            print (dict_stats)
                            w.writerow(dict_stats)
                            
                             
                            if(result > 0):
                                print('+++++ Target achieved in %f seconds! +++++' % final_time)
                            else:
                                print('----- Tmeout! -----')
    return list_stats

def main(runnable):
    host = '158.109.9.226'
    port = 2000

    summary_file = 'summary_experiments_00.csv'
    
    # cameras setup
    width = 800
    height = 600
    fov = 100
    c_x = 170
    c_y = 0
    c_z = 150
    r_p = 0
    r_r = 0
    r_y = 0
    
    cameras = [ {'NAME':'RGB', 'TYPE':'SceneFinal', 'ImageSizeX':width, 
                 'ImageSizeY':height, 'CameraFOV':fov, 'CameraPositionX':c_x,
                 'CameraPositionY':c_y, 'CameraPositionZ':c_z,
                 'CameraRotationPitch':r_p, 'CameraRotationRoll':r_r,
                 'CameraRotationYaw':r_y},
    
               {'NAME':'Depth', 'TYPE':'Depth', 'ImageSizeX':width, 
                 'ImageSizeY':height, 'CameraFOV':fov, 'CameraPositionX':c_x,
                 'CameraPositionY':c_y, 'CameraPositionZ':c_z,
                 'CameraRotationPitch':r_p, 'CameraRotationRoll':r_r,
                 'CameraRotationYaw':r_y},
                
               {'NAME':'SEG', 'TYPE':'SemanticSegmentation', 'ImageSizeX':width, 
                 'ImageSizeY':height, 'CameraFOV':fov, 'CameraPositionX':c_x,
                 'CameraPositionY':c_y, 'CameraPositionZ':c_z,
                 'CameraRotationPitch':r_p, 'CameraRotationRoll':r_r,
                 'CameraRotationYaw':r_y}
               ]



    experiments_to_run = [0, 1, 2]
    

    start_goal_poses,pedestrians,vehicles,weathers, repetitions_per_experiment = load_carla_0_parameters()


    timeout = [60,90,150,150]
    opt_dict = {'CARLA':None, 'HOST':host, 'PORT':port, 'TIMEOUT':timeout, 
                'OUTPUT_SUMMARY':summary_file, 'RUNNABLE':runnable, 
                'CAMERAS':cameras, 'WIDTH':width, 'HEIGHT':height, 
                'WEATHERS':weathers, 'REPETITIONS':repetitions_per_experiment,
                'START_GOAL_POSES':start_goal_poses, 'PEDESTRIANS':pedestrians,
                'VEHICLES':vehicles, 'EXPERIMENTS_TO_RUN':experiments_to_run}

    # run experiments
    run_experiment(opt_dict)
            

if(__name__ == '__main__'):

    # instance your controller here
    runnable = Manual()
    main(runnable)
