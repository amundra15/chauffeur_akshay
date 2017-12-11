#import caffe

import numpy as np
from PIL import Image     
import random
import bisect
import os.path

import h5py
import math
import sys

sys.path.append('spliter')

from spliter import Spliter

import tensorflow as tf
import matplotlib.pyplot as plt
import threading
from dataset import *

# TODO: Divide also by acceleration and Steering 


class DatasetManager(object):


  def __init__(self,config):

    """ Read all hdf5_files """
    self._images_train, self._datasets_train = self.read_all_files(config.train_db_path,config.sensor_names,config.dataset_names)

    self._images_val, self._datasets_val = self.read_all_files(config.val_db_path, config.sensor_names, config.dataset_names)

    #print '******'
    '''print len(self._images_train)     #prints number of hdf5 train files
    print len(self._datasets_train)   #prints 1
    print len(self._images_val)     #prints number of hdf5 val files
    print len(self._datasets_val)    #prints 1
    '''

    spliter = Spliter(config.sequence_size,config.sequence_stride,config.number_steering_bins)  



    divided_keys_train = spliter.divide_keys_by_labels(self._datasets_train[0][config.variable_names.index("Control")][:],config.labels_per_division,None)

    '''print '******'
    print len(divided_keys_train)   #prints 3, since in config, we set [2,2,2]
    print len(divided_keys_train[0])
    print len(divided_keys_train[1])
    print len(divided_keys_train[2])    #28397, all three are of same size'''

    self._splited_keys_train = spliter.split_by_output(self._datasets_train[0][config.variable_names.index("Steer")][:],divided_keys_train)
    #print len(self._splited_keys_train)   #prints 3


    divided_keys_val = spliter.divide_keys_by_labels(self._datasets_val[0][config.variable_names.index("Control")][:],config.labels_per_division,None) # THE NOISE IS NOW NONE, TEST THIS

    self._splited_keys_val = spliter.split_by_output( self._datasets_val[0][config.variable_names.index("Steer")][:],divided_keys_val)
    #print len(self._splited_keys_val)      #prints 3
    


    print '*****'
    
    print len(self._splited_keys_train[0])   #prints 4,when number of bins = 3
    '''print len(self._splited_keys_val[0])      #prints 4
    print len(self._splited_keys_train[1])   #prints 4
    print len(self._splited_keys_val[1])    #prints 4
    print len(self._splited_keys_train[2])   #prints 4
    print len(self._splited_keys_val[2])    #prints 4'''
    #print self._splited_keys_val[0]

    #self._splited_keys_train = self.divide_keys_by_labels(control_train,self._splited_keys_train,config.number_of_divisions,config.labels_per_division)


    '''print config.save_data_stats +'/' + 'meanimage.npy'
    if not os.path.isfile(config.save_data_stats +'/'+ 'meanimage.npy'):
      print 'Compute mean'
      mean_image = self.compute_average_number(self._images_train,self._splited_keys_train,config.image_size)
      np.save(config.save_data_stats +'/' +'meanimage.npy',mean_image)
    else:
      #with np.load(config.train_db_path + 'meanimage.npy') as data:
      data = np.load(config.save_data_stats +'/' + 'meanimage.npy')
      
      mean_image = data
      del data'''


    print max(max(max(self._splited_keys_train)))
    print 'Min ID Train'
    print min(min(min(self._splited_keys_train)))

    print 'Max Id Val'
    print max(max(max(self._splited_keys_val)))




    '''self.train = Dataset(self._splited_keys_train,self._images_train, self._datasets_train,mean_image,config,config.augment)
    

    self.validation = Dataset(self._splited_keys_val,self._images_val, self._datasets_val,mean_image,config,None)  
  '''

    #[0] added later. you may have to delete depending on case
    self.train = Dataset(self._splited_keys_train,self._images_train, self._datasets_train,config,config.augment)
    

    self.validation = Dataset(self._splited_keys_val,self._images_val, self._datasets_val,config,None)  



 
  def start_training_queueing(self,sess):

    enqueue_thread = threading.Thread(target=self.train.enqueue, args=[sess])
    enqueue_thread.isDaemon() #when exit, does not wait for thread to complete its execution
    enqueue_thread.start()

    coord = tf.train.Coordinator()
    self._threads_train = tf.train.start_queue_runners(coord=coord, sess=sess)



  def start_validation_queueing(self,sess):

    enqueue_thread = threading.Thread(target=self.validation.enqueue, args=[sess])
    enqueue_thread.isDaemon()
    enqueue_thread.start()

    coord = tf.train.Coordinator()
    self._threads_val = tf.train.start_queue_runners(coord=coord, sess=sess)


  def stop_training_queueing(self,sess):
    sess.run(self.train.queue.close(cancel_pending_enqueues=True))
    coord.request_stop()
    coord.join(self._threads_train)

  def stop_training_queueing(self,sess):
    sess.run(self.train.queue.close(cancel_pending_enqueues=True))
    coord.request_stop()
    coord.join(self._threads_train)
    


  def read_all_files(self,file_names,image_dataset_names,dataset_names):
   



    datasets_cat = [list([]) for _ in xrange(len(dataset_names))]

    images_data_cat = [list([]) for _ in xrange(len(image_dataset_names))]

    #images_cat = []


    lastidx = 0
    count =0
    #print file_names
    for cword in file_names:
      try:
          print cword
          print count
          dset = h5py.File(cword, "r")  

          for i in range(len(image_dataset_names)):
            #print image_dataset_names[i]
            x = dset[image_dataset_names[i]]
            #print x
            old_shape = x.shape[0]
            #print old_shape

            images_data_cat[i].append((lastidx, lastidx+x.shape[0], x))


          for i in range(len(dataset_names)):

            dset_to_append = dset[dataset_names[i]]


            datasets_cat[i].append( dset_to_append[:])



          
          lastidx += old_shape
          dset.flush()
          count +=1

      except IOError:
        import traceback
        exc_type, exc_value, exc_traceback  = sys.exc_info()
        traceback.print_exc()
        traceback.print_tb(exc_traceback,limit=1, file=sys.stdout)
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
        print "failed to open", cword




    for i in range(len(dataset_names)):     
      datasets_cat[i] = np.concatenate(datasets_cat[i], axis=0)
      datasets_cat[i] = datasets_cat[i].transpose((1,0))



    return images_data_cat,datasets_cat






  #no longer needed
  '''def compute_average_number(self,images,splited_keys,input_size):
    

    mean_image = np.zeros((input_size[0], input_size[1],input_size[2]))

    count_images = 1
    
    print max(max(splited_keys))

    for control_in in range(len(splited_keys)):
      for outer_n in range(0,len(splited_keys[control_in])): # for each steering.
        


        for inner_n in range(len(splited_keys[control_in][outer_n])):


          key = splited_keys[control_in][outer_n][inner_n]

          for es, ee, x in images:

            if key >= es and key < ee:
              image = np.array(x[key-es:key-es+1,:,:,:])
              break



        image = np.squeeze(image)

        mean_image += image
        count_images +=1
        print count_images



    mean_image = mean_image/(count_images-1)



    print mean_image

    return mean_image'''


