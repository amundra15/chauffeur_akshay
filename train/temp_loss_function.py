#trying to design loss function for steering as classification problem


#def mse_branched(network_outputs,ground_truths,control_input,config):
def softmax_mse_branched(network_outputs,ground_truths,config):
#no changes in loss function as we have set number_steering_branches to 0, so the entire computation will happen only for main branch


	branches_configuration = config.branch_config # Get the branched configuration

	#ground_truth_split = tf.split(ground_truths,ground_truths.get_shape()[1],1 )

	error_vec = []

	energy_vec =[]

	print network_outputs
	#print "***************"
	for i in range(len(branches_configuration)):

		energy_branch =[]
		error_branch =[]

		print network_outputs[i]


		#******this step will probably not work with one hot method, cos u may be(if branch_config = [["Steer","Steer","Steer","Speed"]]) dividing the 3 steer components in diff parts******
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

			if target_name == 'Steer':
				#convert gt to one-hot vectors, so that cross-entropy can be applied
				target_gt_one_hot = one_hot(target_gt+1 ,3,axis=-1)	#adding 1 to target_gt converts -1,0,1 to 0,1,2, thus giving indices for corr. one_hot
				#size will change from (?, 1) to (?, 1, 3)


				#also, network structure ie prediction by network shoud be in one hot format


				#assuming the labels(gt) and logits(predicted by network) are dimensionally compatible
				cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=target_gt_one_hot, logits=network_outputs_split[j]))

				#then see how to mix this "error" with speed error


				#also, in machine_output_function should convert one-hot back to a single integer(see file for trial code)



			else:
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


		energy_vec.append(energy_branch)
		error_vec.append(error_branch)

	#exit()

	return loss_function,error_vec,energy_vec,None,branch_selection


