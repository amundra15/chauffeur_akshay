import sys
sys.path.append('train')


import time
import loss_functions
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import logging

class TrainManager(object):

 
	def __init__(self,config):


		self._config = config
		
		with tf.device('/gpu:0'):
			
			self._input_images = tf.placeholder("float",shape=[None,config.image_size[0],config.image_size[1],config.image_size[2]], name="input_image")	#from configMain in experiment_name.py

			#self._input_data = []
			self._targets_data = []
			for i in range(len(self._config.targets_names)):
				self._targets_data.append(tf.placeholder(tf.float32, shape=[None, self._config.targets_sizes[i]],name="target_"+self._config.targets_names[i]))
				
			#since no brranching, there is no input data apart from images
			#for i in range(len(self._config.inputs_names)):
			#	self._input_data.append(tf.placeholder(tf.float32, shape=[None, self._config.inputs_sizes[i]],name="input_"+self._config.inputs_names[i]))
				


			#self._output_data = tf.placeholder("float",shape=[config.batch_size,config.output_size], name="output_data")
			self._dout = tf.placeholder("float",shape=[len(config.dropout)])
			self._variable_learning = tf.placeholder("float", name="learning")	#stores the learning rates


		self._global_step = tf.Variable(0, trainable=False, name="global_step")
		
		#config_gpu = tf.ConfigProto()


		self._feedDict = {}
		self._features = {}



		
  		#config_gpu.log_device_placement=True

		

		
		self._create_structure = __import__(config.network_name).create_structure


		
		self._loss_function = getattr(loss_functions, config.loss_function ) # The function to call 

	def build_network(self):

		""" Depends on the actual input """


		with tf.name_scope("Network"):
			#self._output_network,self._vis_images,self._features,self._weights = self._create_structure(tf, self._input_images,self._input_data,self._config.image_size,self._dout,self._config)
			self._output_network,self._vis_images,self._features,self._weights = self._create_structure(tf, self._input_images,self._config.image_size,self._dout,self._config)




	def build_loss(self):
		
		with tf.name_scope("Loss"):
			#self._loss,self._variable_error,self._variable_energy,self._prob_gain,self._branch \
			#= self._loss_function(self._output_network,self._targets_data,self._input_data[self._config.inputs_names.index("Control")],self._config)
			self._loss,self._variable_error,self._variable_energy,self._prob_gain,self._branch = self._loss_function(self._output_network,self._targets_data,self._config)

	

	def build_optimization(self):

		""" List of Interesting Parameters """
		#		beta1=0.7,beta2=0.85
		#		beta1=0.99,beta2=0.999
		with tf.name_scope("Optimization"):
			self._train_step = tf.train.AdamOptimizer(self._variable_learning).minimize(self._loss)
			#Note: self._loss has shape=(?, 1). ie we  are passing a tensor with loss for each image of the batch. TF would avg it and then compute gradient wrt weights





	def run_train_step(self,batch_tensor,sess,i):



		capture_time = time.time()
		batch = sess.run(batch_tensor)

		# Get the change in the learning rate]
		decrease_factor = 1
		for position in self._config.training_schedule:
			if i > position[0]:  # already got to this iteration
				decrease_factor =position[1]
				break


		self._feedDict = {self._input_images:batch[0]}

		count=1
		
		for i in range(len(self._config.targets_names)):

			self._feedDict.update({self._targets_data[i]:batch[count]})
			count+= 1



		'''for i in range(len(self._config.inputs_names)):

			self._feedDict.update({self._input_data[i]:batch[count]})	
			count+= 1'''


		self._feedDict.update({self._variable_learning: decrease_factor* self._config.learning_rate,self._dout:self._config.dropout})

		sess.run(self._train_step, feed_dict=self._feedDict)


		return time.time() - capture_time




	
	def get_train_step(self):
		return self._train_step

	def get_control_gain(self):
		return self._control_gain

	def get_prob_gain(self):
		return self._prob_gain

	def get_variable_energy(self):
		return self._variable_energy
	
	def get_branch(self):
		return self._branch


	def get_loss(self):

		return self._loss
	
	def get_variable_error(self):
		return self._variable_error

	def get_feed_dict(self):
		return self._feedDict

	def get_network_output(self):
		if self._config.branched_output:
			self._output_network = tf.concat(1,[self._output_network1,self._output_network2])
			
		return self._output_network

	def get_features(self):
		return self._features

	def get_weights(self):
		return self._weights
	
	
	


