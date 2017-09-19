import sys
sys.path.append('test')
sys.path.append('configuration')
sys.path.append('input')
sys.path.append('train')
sys.path.append('utils')
sys.path.append('input/spliter')
sys.path.append('structures')



import argparse
from drive import drive
from train import train
from evaluate import evaluate  # General evaluation algorithm ( train again for a while and check network stile)
""" Also import the module testing scripts """
from test_input import test_input
from test_train import test_train

import os

import logging



if __name__ == '__main__':


  parser = argparse.ArgumentParser(description='Chauffeur')
  # General
  parser.add_argument('mode', metavar='mode',default='train', type=str, help='what kind of mode you are running')
  parser.add_argument('-g','--gpu', type=str,default="0", help='GPU NUMBER')
  parser.add_argument('-lg', '--log', help="activate the log file",action="store_true") 
  parser.add_argument('-db', '--debug', help="put the log file to screen",action="store_true") 

  # Train 
  # TODO: some kind of dictionary to change the parameters
  parser.add_argument('-e', '--experiment-name', help="The experiment name (NAME.py file should be in configuration folder, and the results will be saved to models/NAME)", default="")
  

  # Drive
  parser.add_argument('-cc', '--carla-config', help="Carla config file used for driving", default="./drive_interfaces/carla_interface/CarlaSettings.ini")
  parser.add_argument('-l', '--host', type=str, default='158.109.9.238', help='The IP where DeepGTAV is running')
  parser.add_argument('-p', '--port', default=8000, help='The port where DeepGTAV is running')  
  parser.add_argument('-pt','--path', type=str,default="../Desktop/", help='Path to Store outputs')
  parser.add_argument('-nm','--name', type=str,default="Akshay", help='Name of the person who is going to drive')
  parser.add_argument('-sc', '--show_screen',default=True, action="store_true", help='If we are showing the screen of the player')
  parser.add_argument('-res', '--resolution', default="400,300", help='If we are showing the screen of the player')
  parser.add_argument('-n', '--noise', default="None", help='Set the types of noise:  Spike or None')
  parser.add_argument('--driver', default="Human", help='Select who is driving, a human or a machine')
  parser.add_argument('-ga','--game', default="Carla", help='The game being used as interface')
  parser.add_argument('-cy','--city', default="carla_0", help='select the graph from the city being used')


  args = parser.parse_args()
  print args

  
  if args.log or args.debug:
    LOG_FILENAME = 'log_manual_control.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    if args.debug:  # set of functions to put the logging to screen


      root = logging.getLogger()
      root.setLevel(logging.DEBUG)
      ch = logging.StreamHandler(sys.stdout)
      ch.setLevel(logging.DEBUG)
      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      ch.setFormatter(formatter)
      root.addHandler(ch)
  

  res_string = args.resolution.split(',')
  resolution = []
  resolution.append(int(res_string[0]))
  resolution.append(int(res_string[1]))
  try:

    if args.mode == 'drive':

      drive(args.host,int(args.port),args.gpu,args.path,args.show_screen,resolution,args.noise,args.carla_config,args.driver,args.experiment_name,args.city,args.game,args.name)

    elif args.mode == 'train':
      #from config import *
      #config_main = configMain()
      train(args.gpu, args.experiment_name)
    elif args.mode == 'evaluate':
      evaluate(args.gpu, args.experiment_name)

    elif args.mode == 'test_input':
      test_input(args.gpu)
    elif args.mode == 'test_train':
      test_train(args.gpu)
    else: # mode == evaluate
      evaluate.evaluate(args.gpu)

  except KeyboardInterrupt:
    os._exit(1)
    exitapp = True
    raise
