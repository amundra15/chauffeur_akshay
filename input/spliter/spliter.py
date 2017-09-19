class Spliter(object):

	def __init__(self,sequence_size,sequence_stride,number_steering_bins):

		self._sequence_size = sequence_size
		self._sequence_stride = sequence_stride
		self._number_steering_bins =number_steering_bins

	def order_sequence(self,steerings,keys_sequence):
    

		sequence_average = []
		#print 'keys'
		#print keys_sequence
		for i in keys_sequence:

			sampled_sequence = steerings[(i):(i +self._sequence_size)]

			sequence_average.append(sum(sampled_sequence)/len(sampled_sequence))

			#sequence_average =  get_average_over_interval_stride(steerings_train,sequence_size,stride_size)



		return [i[0] for i in sorted(enumerate(sequence_average), key=lambda x:x[1])],sequence_average

	def partition_keys_by_steering(self,steerings,keys):


		#print len(steerings)
		#print steerings
		max_steer = max(steerings)
		print 'Max Steer'
		print max_steer
		min_steer = min(steerings)
		print 'Min Steer'
		print min_steer
		#print steerings



		steerinterval =  (max_steer - min_steer)/(self._number_steering_bins)

		iter_value = min_steer + steerinterval
		iter_index = 0
		splited_keys = []
		#print 'len steerings'
		#print len(steerings)
		for i in range(0,len(steerings)):

			if steerings[i] >= iter_value:
				# We split

				splited_keys.append(keys[iter_index:i])
				iter_index=i
				iter_value = iter_value + steerinterval

				print 'split on ', i
				print len(splited_keys)


		splited_keys.append(keys[i:len(steerings)])


		return splited_keys

	def select_data_sequence(self,control,selected_data):

		#print control
		#print len(control)
		for i in range(len(control)):		#setting all the control elements to 2, so that equal division works
			control[i] = 2
		#print control

		i=0
		break_sequence =False

		count=0
		del_pos =[]
		#print "SELECTED"
		#print selected_data
		while  count*self._sequence_stride <= (len(control)-self._sequence_size):


			#print 'sequence starting on : ', count*self._sequence_stride
			for iter_sequence in range((count*self._sequence_stride),(count*self._sequence_stride)+self._sequence_size):


				#print ' control ', control[iter_sequence], ' selected ', selected_data
				# The position is one
				#print control.shape
				if control[iter_sequence] not in selected_data:
					#print control[j,iter_sequence]
					#print 'OUT'
					del_pos.append(count*self._sequence_stride)

					break_sequence =True
					break

			if break_sequence:
				break_sequence = False
				count+=1
				continue

			count+=1

		return  del_pos

	def select_data_sequence_noise(self,control,selected_data,noise_vec):

		for i in range(len(control)):		#setting all the control elements to 2, so that equal division works
			control[i] = 2


		i=0
		break_sequence =False

		count=0
		del_pos =[]
		#print "SELECTED"
		#print selected_data
		while  count*self._sequence_stride <= (len(control)-self._sequence_size):

			for iter_sequence in range((count*self._sequence_stride),(count*self._sequence_stride)+self._sequence_size):


				
				# The position is one
				#print control.shape
				if (control[iter_sequence] not in selected_data) or noise_vec[iter_sequence]:
					print iter_sequence
					#print 'OUT'
					del_pos.append(count*self._sequence_stride)

					break_sequence =True
					break

			if break_sequence:
				break_sequence = False
				count+=1
				continue

			count+=1

		return  del_pos
	""" Split the outputs keys with respect to the labels. The selected labels represents how it is going to be split """


	def divide_keys_by_labels(self,labels,selected_data,noise_vec=None):

		new_splited_array = []
		keys_for_divison =[]  # The set of all possible keys for each division
		sorted_steering_division = []



		for j in range(len(selected_data)):
	

			if noise_vec != None:
				keys_to_delete = self.select_data_sequence_noise(labels,selected_data[j],noise_vec)
			else:
				keys_to_delete = self.select_data_sequence(labels,selected_data[j])
			#print got_keys_for_divison
			keys_for_this_part = range(0,len(labels)-self._sequence_size,self._sequence_stride)


			keys_for_this_part = list(set(keys_for_this_part) - set(keys_to_delete))

			keys_for_divison.append(keys_for_this_part)



		#print keys_for_divison
		return keys_for_divison


	

	def split_by_output(self,output_to_split,divided_keys):

	#once function is called, the for loop runs 3 times


		splited_keys = []
		for i in range(len(divided_keys)):		
			# We use this keys to grab the steerings we want... divided into groups
			keys_ordered,average_outputs = self.order_sequence(output_to_split,divided_keys[i])
			# we get new keys and order steering, each steering group
			sorted_outputs = [ average_outputs[j] for j in keys_ordered]

			# We split each group...
			if len(keys_ordered) > 0:
				splited_keys_part = self.partition_keys_by_steering(sorted_outputs,divided_keys[i])#config.balances_train)
			else:
				splited_keys_part = [] 
			splited_keys.append(splited_keys_part)


		return 	splited_keys
