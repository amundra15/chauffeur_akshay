# README #

### What is this repository for? ###

Eventual world domination by self-learned self driving cars.


### How do I get set up? ###

Installation :
Needs:
pygame ( Not for training)
curses ( Optional, for colorfull terminal debuging ) 
tensorflow 1.1 or tensorflow 1.2
numpy
hdf5
imgaug
carla_client



 ########## RUNNING ############

the toolbox has three different kinds of runs:

drive -> drive a network using one of our amazing interfaces ( carla or GTA)
train -> train a network 

evaluate -> Run the network a bit more and check the outputs.


########### TRAIN MODE ############



The first step needed is to make a configuration file.
There are plenty of configuration files provided at 
the "config" folder.
Just copy a24 file and change to your needs
On this configuration file you shoul d  ( MOVE THIS TO The chauffeur please....)s


x

To run the train mode, first increase the number of posible open files:

ulimit -Sn 8096

Then run the program for training

python2 chauffer.py train -e <experiment_name>

where the experiment name should be a configuration file.


########## DRIVE MODE ###########

python2 chauffeur.py drive --driver Machine  -l 158.109.9.226 -p 2000 -pt /data2/datasets/ -sc -e a24_ca20_boostpedals_loss -cc drive_interfaces/carla_interface/CarlaSettings.ini -cy carla_0


run corl tests:

CUDA_VISIBLE_DEVICES='0' python2 drive_interfaces/carla_interface/run_test_corl.py -e a24_ca20_boostpedals_loss -s a24_test_2_weathers_2_pos.csv -l 158.109.9.226 -p 2000 -t 0,1 -cy carla_0 -w 1,3


