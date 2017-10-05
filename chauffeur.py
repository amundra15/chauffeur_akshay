import sys
sys.path.append('test')
sys.path.append('configuration')
sys.path.append('input')
sys.path.append('train')
sys.path.append('utils')
sys.path.append('input/spliter')
sys.path.append('structures')
sys.path.append('drive_interfaces/configuration/')



import argparse
from drive import drive
from drive_elektra import drive_elektra
from train import train
from evaluate import evaluate  # General evaluation algorithm ( train again for a while and check network stile)
""" Also import the module testing scripts """
from test_input import test_input
from test_train import test_train

import os

import logging




def parse_drive_arguments(args,driver_conf):  #used only  for drive_elektra 
#override variables of elektra_drive_config if they are passed from command line


  # Carla Config
  if args.carla_config is not None:
    driver_conf.carla_config = args.carla_config


  if args.host is not None:
    driver_conf.host = args.host

  if args.port is not None:
    driver_conf.port = int(args.port)

  if args.path is not None:
    driver_conf.path = args.path

  if args.noise is not None:
    driver_conf.noise = args.noise
  if args.driver  is not None:
    driver_conf.type_of_driver = args.driver
  if args.game is not None:
    driver_conf.game = args.game
  '''if args.number_screens is not None:
    driver_conf.number_screens = args.number_screens
  if args.scale_factor is not None:
    driver_conf.scale_factor = args.scale_factor'''

  if args.resolution is not None:
    res_string = args.resolution.split(',')
    resolution = []
    resolution.append(int(res_string[0]))
    resolution.append(int(res_string[1]))
    driver_conf.resolution = resolution



  '''if args.image_cut is not None:
    cut_string = args.image_cut.split(',')
    image_cut = []
    image_cut.append(int(cut_string[0]))
    image_cut.append(int(cut_string[1]))
    driver_conf.image_cut = image_cut'''



  return driver_conf





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
  parser.add_argument('-dc', '--driver_config', help="Drive config file used for driving(just for elektra right now)", default="elektra_drive_config")
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
      if args.game == 'Elektra':  #can later be clubbed with general case(handle drive_config object)
        driver_conf_module  = __import__(args.driver_config)
        driver_conf= driver_conf_module.configDrive()
        driver_conf = parse_drive_arguments(args,driver_conf)   #****TODO: check what this does
        #drive_elektra(args.experiment_name,driver_conf,args.name,args.memory)
        drive_elektra(args.experiment_name,driver_conf,args.name)

      else:
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
