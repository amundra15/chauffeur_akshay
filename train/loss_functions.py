import tensorflow as tf


#def mse_branched(network_outputs,ground_truths,control_input,config):
def mse_branched(network_outputs,ground_truths,config):
#no changes in loss function as we have set number_steering_branches to 0, so the entire computation will happen only for main branch


	branches_configuration = config.branch_config # Get the branched configuration

	#ground_truth_split = tf.split(ground_truths,ground_truths.get_shape()[1],1 )

	error_vec = []

	energy_vec =[]

	print "***************"
	print network_outputs 		
	print len(network_outputs)			#prints 1
	print network_outputs[0].get_shape()		#prints shape=(?, 2)
	print "***************"
	for i in range(len(branches_configuration)):

		energy_branch =[]
		error_branch =[]

		#if network_outputs[i].get_shape()[1] == 1: # Size 1 cannot be splited
		#	network_outputs_split = network_outputs[i]
		#else:
		print network_outputs[i]


		network_outputs_split =tf.split(network_outputs[i],network_outputs[i].get_shape()[1],1 )
		#splits (?, 2) to (?, 1), (?, 1) ie steer and speed separated

		print branches_configuration[i]
		for j in range(len(branches_configuration[i])):

			print 'split'
			print network_outputs_split[j]

			# Get the name of the target data to be taken
			target_name = branches_configuration[i][j] # name of the target
			# Get the target gt ( TODO: This should be a dictionary, I think it is more logical)
			print 'target_name: '
			print target_name

			target_gt = ground_truths[config.targets_names.index(target_name)]
			print 'target_gt: '
			print target_gt

			'''if (target_name == 'Steer' and to_print == True): 
				# Save to file
				#np.save(batch_steer.npy, target_gt )
				np.save('data_stats' +'/' +'batch_steer.npy',target_gt)
				global to_print
				to_print = False'''


			squared_dist = tf.pow(tf.subtract(target_gt, network_outputs_split[j]),2)
			dist =tf.abs(tf.subtract(target_gt,  network_outputs_split[j]))
			error_branch.append(dist)
			print 'dist'
			print dist

			'''#since number_steering_branches=0, first condition will never happen. thus writing only second condition.
			if i < config.number_steering_branches:
				branch_selection = tf.reshape(control_input[:,i],tf.shape(ground_truths[0]))
			else:
				branch_selection =tf.ones(tf.shape(target_gt))'''

			branch_selection =tf.ones(tf.shape(target_gt))
			#print branch_selection
			#print squared_dist

			variable_loss =squared_dist * branch_selection
			#print variable_loss

			print 'loss'
			print variable_loss
			energy_branch.append(variable_loss)

			#Note: Optimizer will be minimizing this loss_function
			if i==0 and j==0:
				loss_function = variable_loss*config.branch_loss_weight[i]*config.variable_weight[target_name]
			else:
				loss_function = tf.add(variable_loss*config.branch_loss_weight[i]*config.variable_weight[target_name],loss_function)
			#just adding up all the losses

		energy_vec.append(energy_branch)
		error_vec.append(error_branch)


	#exit()

	return loss_function,error_vec,energy_vec,None,branch_selection



#used in felipe's experiments
def mse_input(network_outputs,ground_truths,control_input,config):



	branches_configuration = config.branch_config # Get the branched configuration

	#ground_truth_split = tf.split(ground_truths,ground_truths.get_shape()[1],1 )

	error_vec = []

	energy_vec =[]

	print network_outputs
	for i in range(len(branches_configuration)):

		energy_branch =[]
		error_branch =[]

		#if network_outputs[i].get_shape()[1] == 1: # Size 1 cannot be splited
		#	network_outputs_split = network_outputs[i]
		#else:
		print network_outputs[i]
		network_outputs_split =tf.split(network_outputs[i],network_outputs[i].get_shape()[1],1 )


		print branches_configuration[i]
		for j in range(len(branches_configuration[i])):

			print 'split'
			print network_outputs_split[j]

			# Get the name of the target data to be taken
			target_name = branches_configuration[i][j] # name of the target
			# Get the target gt ( TODO: This should be a dictionary, I think it is more logical)
			print target_name



			target_gt = ground_truths[config.targets_names.index(target_name)]
			if i < config.inputs_sizes[config.inputs_names.index('Control')]:
				branch_selection = tf.reshape(control_input[:,i],tf.shape(ground_truths[0]))
			else:
				branch_selection =tf.ones(tf.shape(target_gt))
			print target_gt
			squared_dist = tf.pow(tf.subtract(target_gt, network_outputs_split[j]),2)
			dist =tf.abs(tf.subtract(target_gt,  network_outputs_split[j])) *branch_selection
			error_branch.append(dist)
			print 'dist'
			print dist



			variable_loss =squared_dist * branch_selection


			print 'loss'
			print variable_loss
			energy_branch.append(variable_loss)
			if i==0 and j==0:
				loss_function = variable_loss*config.branch_loss_weight[i]*config.variable_weight[target_name]
			else:
				loss_function = tf.add(variable_loss*config.branch_loss_weight[i]*config.variable_weight[target_name],loss_function)


		energy_vec.append(energy_branch)
		error_vec.append(error_branch)

	#exit()

	return loss_function,error_vec,energy_vec,None,branch_selection
