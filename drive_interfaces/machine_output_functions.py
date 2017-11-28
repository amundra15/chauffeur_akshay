import numpy as np
import tensorflow as tf

def branched_speed(image_input,speed,control_input,config,sess,train_manager):

  
  branches = train_manager._output_network
  x = train_manager._input_images 
  dout = train_manager._dout
  input_speed = train_manager._input_data[config.inputs_names.index("Speed")]
  input_control =  train_manager._input_data[config.inputs_names.index("Control")]

  image_input = image_input.reshape((1,config.image_size[0],config.image_size[1],config.image_size[2]))

  speed = np.array(speed/config.speed_factor)

  speed = speed.reshape((1,1))

  if control_input ==2 or control_input==0.0:
    steer_net = branches[0]
  elif control_input == 3:
    steer_net = branches[2]
  elif control_input == 4:
    steer_net = branches[3]
  elif control_input == 5:
    steer_net = branches[1]

  acc_net = branches[4]
  brake_net = branches[5]
  speed_net = branches[6]  # This is hardcoded !!!!!!

  #print clip_input.shape

  #input_vec = input_vec.reshape((1,config.input_size[0]*config.input_size[1]*config.input_size[2]))


  #image_result = Image.fromarray((scipy.misc.imresize(image_input[0],(210,280,3))).astype(np.uint8))
      
      
  #image_result.save(str('saida_res.jpg'))

  feedDict = {x: image_input,input_speed:speed,dout: [1]*len(config.dropout) }


  output_steer = sess.run(steer_net, feed_dict=feedDict)
  output_acc = sess.run(acc_net, feed_dict=feedDict)
  output_speed = sess.run(speed_net, feed_dict=feedDict)
  output_brake = sess.run(brake_net, feed_dict=feedDict)


  if config.use_speed_trick:
    if speed < (4.0/config.speed_factor) and output_speed[0][0] > (4.0/config.speed_factor):  # If (Car Stooped) and ( It should not have stoped)
     output_acc[0][0] =  0.3*(4.0/config.speed_factor -speed) + output_acc[0][0]  #print "DURATION"



  
  predicted_steers = (output_steer[0][0])

  predicted_acc = (output_acc[0][0])


  predicted_brake = (output_brake[0][0])
      
  return  predicted_steers,predicted_acc,predicted_brake




#def single_branch(image_input,speed,control_input,config,sess,train_manager):
def single_branch(image_input,config,sess,train_manager): #currently used in carla_machine
  
  #branches = train_manager._output_network
  all_net = train_manager._output_network
  x = train_manager._input_images 
  dout = train_manager._dout
  #input_speed = train_manager._input_data[config.inputs_names.index("Speed")]
  #input_control =  train_manager._input_data[config.inputs_names.index("Control")]

  image_input = image_input.reshape((1,config.image_size[0],config.image_size[1],config.image_size[2]))

  #speed = np.array(speed/config.speed_factor)

  #speed = speed.reshape((1,1))

  '''if control_input ==2 or control_input==0.0:
    all_net = branches[0]
  elif control_input == 3:
    all_net = branches[2]
  elif control_input == 4:
    all_net = branches[3]
  elif control_input == 5:
    all_net = branches[1]'''


  #print clip_input.shape

  #input_vec = input_vec.reshape((1,config.input_size[0]*config.input_size[1]*config.input_size[2]))


  #image_result = Image.fromarray((scipy.misc.imresize(image_input[0],(210,280,3))).astype(np.uint8))
      
      
  #image_result.save(str('saida_res.jpg'))

  feedDict = {x: image_input,dout: [1]*len(config.dropout) }


  output_all = sess.run(all_net, feed_dict=feedDict)    #when fetches in a tensor, the fetched value will be a numpy ndarray containing the value of that tensor


  #******you will have to convert one-hot vectors back to a single steering variable*******
  #index = tf.argmax(one_hot_vector, axis=1)  #something like this


  '''print len(output_all)   #1
  print len(output_all[0])  #1
  print len(output_all[0][0]) #2
  print output_all[0][0][0]   #prints steer value
  print output_all[0][0][1]   #prints speed value'''

  '''predicted_steers = (output_all[0][0][0])
  for i in range(len(predicted_steers)):
    predicted_steers[i] = int(round(predicted_steers[i]))'''

  predicted_steers = output_all[0][0][0]
  #discrete_steers = int(round(predicted_steers))
  if predicted_steers > 0.3:
    discrete_steers = 1
  elif predicted_steers < -0.3:
    discrete_steers = -1
  else:
    discrete_steers = 0
  predicted_speed = 7   #(output_all[0][0][1])
  

  #predicted_acc = (output_all[0][1])

  #predicted_brake = (output_all[0][2])
      
  #return  predicted_steers,predicted_acc,predicted_brake
  return  predicted_steers, discrete_steers, predicted_speed


def single_branch_steer_only(image_input,config,sess,train_manager):
  
  #branches = train_manager._output_network
  all_net = train_manager._output_network
  x = train_manager._input_images 
  dout = train_manager._dout
  #input_speed = train_manager._input_data[config.inputs_names.index("Speed")]
  #input_control =  train_manager._input_data[config.inputs_names.index("Control")]

  image_input = image_input.reshape((1,config.image_size[0],config.image_size[1],config.image_size[2]))



  feedDict = {x: image_input,dout: [1]*len(config.dropout) }


  output_all = sess.run(all_net, feed_dict=feedDict)    #when fetches in a tensor, the fetched value will be a numpy ndarray containing the value of that tensor


  predicted_steers = output_all[0][0][0]
  
  #predicted_speed = (output_all[0][0][1])
  predicted_speed = 7.0   #fixing speed to max

  #predicted_acc = (output_all[0][1])

  #predicted_brake = (output_all[0][2])
      
  #return  predicted_steers,predicted_acc,predicted_brake
  return  predicted_steers,predicted_speed


#taken from felipe's chauffeur
def base_no_speed(image_input,speed,control_input,config,sess,train_manager):

  
  branches = train_manager._output_network
  x = train_manager._input_images 
  dout = train_manager._dout

  image_input = image_input.reshape((1,config.image_size[0],config.image_size[1],config.image_size[2]))

  net = branches[0]



  feedDict = {x: image_input,dout: [1]*len(config.dropout) }


  output_net = sess.run(net, feed_dict=feedDict)


  
  predicted_steers = (output_net[0][0])

      
  return  predicted_steers,None,None

